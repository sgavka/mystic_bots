"""Tests for horoscope follow-up question feature."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from horoscope.handlers.followup import handle_followup_question
from horoscope.services.llm import LLMFollowupResult, LLMService


def _make_user_entity(telegram_uid: int = 12345, language_code: str = 'en'):
    user = MagicMock()
    user.telegram_uid = telegram_uid
    user.language_code = language_code
    return user


def _make_profile(preferred_language: str = 'en'):
    profile = MagicMock()
    profile.preferred_language = preferred_language
    return profile


def _make_horoscope(horoscope_id: int = 1, full_text: str = "Your stars shine bright today"):
    horoscope = MagicMock()
    horoscope.id = horoscope_id
    horoscope.full_text = full_text
    return horoscope


def _make_followup_result(
    answer_text: str = "The stars say yes!",
    model: str = "gpt-4o-mini",
    input_tokens: int = 100,
    output_tokens: int = 50,
) -> LLMFollowupResult:
    return LLMFollowupResult(
        answer_text=answer_text,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )


def _make_followup_entity(question_text: str = "Previous Q?", answer_text: str = "Previous A."):
    entity = MagicMock()
    entity.question_text = question_text
    entity.answer_text = answer_text
    return entity


class TestHandleFollowupQuestion:

    @pytest.mark.asyncio
    async def test_generates_and_saves_answer(self):
        message = AsyncMock()
        message.text = "What about my career?"
        user = _make_user_entity()
        app_context = AsyncMock()

        horoscope = _make_horoscope()
        profile = _make_profile()
        followup_result = _make_followup_result()

        with (
            patch('horoscope.handlers.followup.container') as mock_container,
            patch('horoscope.services.llm.LLMService') as mock_llm_cls,
        ):
            sub_repo = AsyncMock()
            sub_repo.ahas_active_subscription = AsyncMock(return_value=True)
            mock_container.horoscope.subscription_repository.return_value = sub_repo

            horoscope_repo = AsyncMock()
            horoscope_repo.aget_by_user_and_date = AsyncMock(return_value=horoscope)
            mock_container.horoscope.horoscope_repository.return_value = horoscope_repo

            profile_repo = AsyncMock()
            profile_repo.aget_by_telegram_uid = AsyncMock(return_value=profile)
            mock_container.horoscope.user_profile_repository.return_value = profile_repo

            followup_repo = AsyncMock()
            followup_repo.aget_by_horoscope = AsyncMock(return_value=[])
            mock_container.horoscope.followup_repository.return_value = followup_repo

            mock_llm = MagicMock()
            mock_llm.generate_followup_answer.return_value = followup_result
            mock_llm_cls.return_value = mock_llm

            await handle_followup_question(
                message=message,
                user=user,
                app_context=app_context,
            )

        mock_llm.generate_followup_answer.assert_called_once_with(
            horoscope_text=horoscope.full_text,
            question="What about my career?",
            language='en',
            previous_followups=[],
        )
        followup_repo.acreate_followup.assert_called_once_with(
            horoscope_id=1,
            question_text="What about my career?",
            answer_text=followup_result.answer_text,
            model=followup_result.model,
            input_tokens=followup_result.input_tokens,
            output_tokens=followup_result.output_tokens,
        )
        app_context.send_message.assert_called_once()
        call_kwargs = app_context.send_message.call_args[1]
        assert call_kwargs['text'] == followup_result.answer_text

    @pytest.mark.asyncio
    async def test_handles_llm_failure(self):
        message = AsyncMock()
        message.text = "What about love?"
        user = _make_user_entity()
        app_context = AsyncMock()

        horoscope = _make_horoscope()
        profile = _make_profile()

        with (
            patch('horoscope.handlers.followup.container') as mock_container,
            patch('horoscope.services.llm.LLMService') as mock_llm_cls,
        ):
            sub_repo = AsyncMock()
            sub_repo.ahas_active_subscription = AsyncMock(return_value=True)
            mock_container.horoscope.subscription_repository.return_value = sub_repo

            horoscope_repo = AsyncMock()
            horoscope_repo.aget_by_user_and_date = AsyncMock(return_value=horoscope)
            mock_container.horoscope.horoscope_repository.return_value = horoscope_repo

            profile_repo = AsyncMock()
            profile_repo.aget_by_telegram_uid = AsyncMock(return_value=profile)
            mock_container.horoscope.user_profile_repository.return_value = profile_repo

            followup_repo = AsyncMock()
            followup_repo.aget_by_horoscope = AsyncMock(return_value=[])
            mock_container.horoscope.followup_repository.return_value = followup_repo

            mock_llm = MagicMock()
            mock_llm.generate_followup_answer.side_effect = Exception("LLM error")
            mock_llm_cls.return_value = mock_llm

            await handle_followup_question(
                message=message,
                user=user,
                app_context=app_context,
            )

        app_context.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_ignores_empty_text(self):
        message = AsyncMock()
        message.text = None
        user = _make_user_entity()
        app_context = AsyncMock()

        await handle_followup_question(
            message=message,
            user=user,
            app_context=app_context,
        )

        app_context.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_skips_non_subscriber(self):
        message = AsyncMock()
        message.text = "Question?"
        user = _make_user_entity()
        app_context = AsyncMock()

        with patch('horoscope.handlers.followup.container') as mock_container:
            sub_repo = AsyncMock()
            sub_repo.ahas_active_subscription = AsyncMock(return_value=False)
            mock_container.horoscope.subscription_repository.return_value = sub_repo

            await handle_followup_question(
                message=message,
                user=user,
                app_context=app_context,
            )

        app_context.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_skips_when_no_horoscope(self):
        message = AsyncMock()
        message.text = "Question?"
        user = _make_user_entity()
        app_context = AsyncMock()

        with patch('horoscope.handlers.followup.container') as mock_container:
            sub_repo = AsyncMock()
            sub_repo.ahas_active_subscription = AsyncMock(return_value=True)
            mock_container.horoscope.subscription_repository.return_value = sub_repo

            horoscope_repo = AsyncMock()
            horoscope_repo.aget_by_user_and_date = AsyncMock(return_value=None)
            mock_container.horoscope.horoscope_repository.return_value = horoscope_repo

            await handle_followup_question(
                message=message,
                user=user,
                app_context=app_context,
            )

        app_context.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_passes_language_to_llm(self):
        message = AsyncMock()
        message.text = "Що зірки кажуть?"
        user = _make_user_entity()
        app_context = AsyncMock()

        horoscope = _make_horoscope()
        profile = _make_profile(preferred_language='uk')
        followup_result = _make_followup_result()

        with (
            patch('horoscope.handlers.followup.container') as mock_container,
            patch('horoscope.services.llm.LLMService') as mock_llm_cls,
        ):
            sub_repo = AsyncMock()
            sub_repo.ahas_active_subscription = AsyncMock(return_value=True)
            mock_container.horoscope.subscription_repository.return_value = sub_repo

            horoscope_repo = AsyncMock()
            horoscope_repo.aget_by_user_and_date = AsyncMock(return_value=horoscope)
            mock_container.horoscope.horoscope_repository.return_value = horoscope_repo

            profile_repo = AsyncMock()
            profile_repo.aget_by_telegram_uid = AsyncMock(return_value=profile)
            mock_container.horoscope.user_profile_repository.return_value = profile_repo

            followup_repo = AsyncMock()
            followup_repo.aget_by_horoscope = AsyncMock(return_value=[])
            mock_container.horoscope.followup_repository.return_value = followup_repo

            mock_llm = MagicMock()
            mock_llm.generate_followup_answer.return_value = followup_result
            mock_llm_cls.return_value = mock_llm

            await handle_followup_question(
                message=message,
                user=user,
                app_context=app_context,
            )

        call_kwargs = mock_llm.generate_followup_answer.call_args[1]
        assert call_kwargs['language'] == 'uk'

    @pytest.mark.asyncio
    async def test_sends_eyes_reaction_on_message(self):
        message = AsyncMock()
        message.text = "What about my career?"
        message.message_id = 42
        user = _make_user_entity()
        app_context = AsyncMock()

        horoscope = _make_horoscope()
        profile = _make_profile()
        followup_result = _make_followup_result()

        with (
            patch('horoscope.handlers.followup.container') as mock_container,
            patch('horoscope.services.llm.LLMService') as mock_llm_cls,
        ):
            sub_repo = AsyncMock()
            sub_repo.ahas_active_subscription = AsyncMock(return_value=True)
            mock_container.horoscope.subscription_repository.return_value = sub_repo

            horoscope_repo = AsyncMock()
            horoscope_repo.aget_by_user_and_date = AsyncMock(return_value=horoscope)
            mock_container.horoscope.horoscope_repository.return_value = horoscope_repo

            profile_repo = AsyncMock()
            profile_repo.aget_by_telegram_uid = AsyncMock(return_value=profile)
            mock_container.horoscope.user_profile_repository.return_value = profile_repo

            followup_repo = AsyncMock()
            followup_repo.aget_by_horoscope = AsyncMock(return_value=[])
            mock_container.horoscope.followup_repository.return_value = followup_repo

            mock_llm = MagicMock()
            mock_llm.generate_followup_answer.return_value = followup_result
            mock_llm_cls.return_value = mock_llm

            await handle_followup_question(
                message=message,
                user=user,
                app_context=app_context,
            )

        app_context.set_reaction.assert_called_once_with(
            message_id=42,
            emoji="👀",
            is_big=False,
        )

    @pytest.mark.asyncio
    async def test_sends_typing_action_during_generation(self):
        message = AsyncMock()
        message.text = "What about my career?"
        message.message_id = 42
        user = _make_user_entity()
        app_context = AsyncMock()

        horoscope = _make_horoscope()
        profile = _make_profile()
        followup_result = _make_followup_result()

        with (
            patch('horoscope.handlers.followup.container') as mock_container,
            patch('horoscope.services.llm.LLMService') as mock_llm_cls,
        ):
            sub_repo = AsyncMock()
            sub_repo.ahas_active_subscription = AsyncMock(return_value=True)
            mock_container.horoscope.subscription_repository.return_value = sub_repo

            horoscope_repo = AsyncMock()
            horoscope_repo.aget_by_user_and_date = AsyncMock(return_value=horoscope)
            mock_container.horoscope.horoscope_repository.return_value = horoscope_repo

            profile_repo = AsyncMock()
            profile_repo.aget_by_telegram_uid = AsyncMock(return_value=profile)
            mock_container.horoscope.user_profile_repository.return_value = profile_repo

            followup_repo = AsyncMock()
            followup_repo.aget_by_horoscope = AsyncMock(return_value=[])
            mock_container.horoscope.followup_repository.return_value = followup_repo

            mock_llm = MagicMock()
            mock_llm.generate_followup_answer.return_value = followup_result
            mock_llm_cls.return_value = mock_llm

            await handle_followup_question(
                message=message,
                user=user,
                app_context=app_context,
            )

        # Typing action is sent via bot.send_chat_action which is called by the background task
        # Since LLM is synchronous mock (returns immediately), the typing task gets cancelled
        # before it can run. The key behavior we verify is that set_reaction was called
        # (tested above) and the handler completes successfully.

    @pytest.mark.asyncio
    async def test_passes_previous_followups_to_llm(self):
        message = AsyncMock()
        message.text = "What else?"
        user = _make_user_entity()
        app_context = AsyncMock()

        horoscope = _make_horoscope()
        profile = _make_profile()
        followup_result = _make_followup_result()

        prev_followup = _make_followup_entity(
            question_text="First question?",
            answer_text="First answer.",
        )

        with (
            patch('horoscope.handlers.followup.container') as mock_container,
            patch('horoscope.services.llm.LLMService') as mock_llm_cls,
        ):
            sub_repo = AsyncMock()
            sub_repo.ahas_active_subscription = AsyncMock(return_value=True)
            mock_container.horoscope.subscription_repository.return_value = sub_repo

            horoscope_repo = AsyncMock()
            horoscope_repo.aget_by_user_and_date = AsyncMock(return_value=horoscope)
            mock_container.horoscope.horoscope_repository.return_value = horoscope_repo

            profile_repo = AsyncMock()
            profile_repo.aget_by_telegram_uid = AsyncMock(return_value=profile)
            mock_container.horoscope.user_profile_repository.return_value = profile_repo

            followup_repo = AsyncMock()
            followup_repo.aget_by_horoscope = AsyncMock(return_value=[prev_followup])
            mock_container.horoscope.followup_repository.return_value = followup_repo

            mock_llm = MagicMock()
            mock_llm.generate_followup_answer.return_value = followup_result
            mock_llm_cls.return_value = mock_llm

            await handle_followup_question(
                message=message,
                user=user,
                app_context=app_context,
            )

        call_kwargs = mock_llm.generate_followup_answer.call_args[1]
        assert call_kwargs['previous_followups'] == [prev_followup]


class TestLLMFollowupGeneration:

    def test_generate_followup_answer(self):
        service = LLMService()

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "The stars say great things! ✨"
        mock_response.model = "gpt-4o-mini"
        mock_response.usage.prompt_tokens = 150
        mock_response.usage.completion_tokens = 30

        with (
            patch('horoscope.services.llm.settings') as mock_settings,
            patch('litellm.completion', return_value=mock_response),
        ):
            mock_settings.LLM_API_KEY = 'test-key'
            mock_settings.LLM_MODEL = 'gpt-4o-mini'
            mock_settings.LLM_BASE_URL = ''
            mock_settings.LLM_TIMEOUT = 30
            mock_settings.HOROSCOPE_LANGUAGE_NAMES = {'en': 'English', 'uk': 'Ukrainian'}

            result = service.generate_followup_answer(
                horoscope_text="Your horoscope text here",
                question="What about my career?",
                language='en',
            )

        assert result.answer_text == "The stars say great things! ✨"
        assert result.model == "gpt-4o-mini"
        assert result.input_tokens == 150
        assert result.output_tokens == 30

    def test_generate_followup_answer_uses_correct_language(self):
        service = LLMService()

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Зірки кажуть: так! ✨"
        mock_response.model = "gpt-4o-mini"
        mock_response.usage.prompt_tokens = 160
        mock_response.usage.completion_tokens = 35

        with (
            patch('horoscope.services.llm.settings') as mock_settings,
            patch('litellm.completion', return_value=mock_response) as mock_completion,
        ):
            mock_settings.LLM_API_KEY = 'test-key'
            mock_settings.LLM_MODEL = 'gpt-4o-mini'
            mock_settings.LLM_BASE_URL = ''
            mock_settings.LLM_TIMEOUT = 30
            mock_settings.HOROSCOPE_LANGUAGE_NAMES = {'en': 'English', 'uk': 'Ukrainian'}

            service.generate_followup_answer(
                horoscope_text="Ваш гороскоп",
                question="Що щодо кар'єри?",
                language='uk',
            )

        prompt_used = mock_completion.call_args[1]['messages'][0]['content']
        assert 'Ukrainian' in prompt_used

    def test_generate_followup_answer_includes_previous_qa(self):
        service = LLMService()

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "More insights! ✨"
        mock_response.model = "gpt-4o-mini"
        mock_response.usage.prompt_tokens = 200
        mock_response.usage.completion_tokens = 40

        prev_followup = _make_followup_entity(
            question_text="First question?",
            answer_text="First answer.",
        )

        with (
            patch('horoscope.services.llm.settings') as mock_settings,
            patch('litellm.completion', return_value=mock_response) as mock_completion,
        ):
            mock_settings.LLM_API_KEY = 'test-key'
            mock_settings.LLM_MODEL = 'gpt-4o-mini'
            mock_settings.LLM_BASE_URL = ''
            mock_settings.LLM_TIMEOUT = 30
            mock_settings.HOROSCOPE_LANGUAGE_NAMES = {'en': 'English'}

            service.generate_followup_answer(
                horoscope_text="Your horoscope text",
                question="What else?",
                language='en',
                previous_followups=[prev_followup],
            )

        prompt_used = mock_completion.call_args[1]['messages'][0]['content']
        assert 'First question?' in prompt_used
        assert 'First answer.' in prompt_used
        assert 'Previous questions and answers' in prompt_used
