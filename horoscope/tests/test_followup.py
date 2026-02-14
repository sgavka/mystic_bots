"""Tests for horoscope follow-up question feature."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from horoscope.handlers.followup import ask_followup_callback, handle_followup_question
from horoscope.services.llm import LLMFollowupResult, LLMService
from horoscope.states import HoroscopeStates


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


class TestAskFollowupCallback:

    @pytest.mark.asyncio
    async def test_sets_fsm_state_for_subscriber(self):
        callback = AsyncMock()
        state = AsyncMock()
        user = _make_user_entity()
        app_context = AsyncMock()

        horoscope = _make_horoscope(horoscope_id=42)
        profile = _make_profile(preferred_language='ru')

        with patch('horoscope.handlers.followup.container') as mock_container:
            sub_repo = AsyncMock()
            sub_repo.ahas_active_subscription = AsyncMock(return_value=True)
            mock_container.horoscope.subscription_repository.return_value = sub_repo

            horoscope_repo = AsyncMock()
            horoscope_repo.aget_by_user_and_date = AsyncMock(return_value=horoscope)
            mock_container.horoscope.horoscope_repository.return_value = horoscope_repo

            profile_repo = AsyncMock()
            profile_repo.aget_by_telegram_uid = AsyncMock(return_value=profile)
            mock_container.horoscope.user_profile_repository.return_value = profile_repo

            await ask_followup_callback(
                callback=callback,
                state=state,
                user=user,
                app_context=app_context,
            )

        state.set_state.assert_called_once_with(HoroscopeStates.WAITING_FOLLOWUP_QUESTION)
        state.update_data.assert_called_once_with(horoscope_id=42)
        callback.answer.assert_called_once()
        app_context.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_action_for_non_subscriber(self):
        callback = AsyncMock()
        state = AsyncMock()
        user = _make_user_entity()
        app_context = AsyncMock()

        with patch('horoscope.handlers.followup.container') as mock_container:
            sub_repo = AsyncMock()
            sub_repo.ahas_active_subscription = AsyncMock(return_value=False)
            mock_container.horoscope.subscription_repository.return_value = sub_repo

            await ask_followup_callback(
                callback=callback,
                state=state,
                user=user,
                app_context=app_context,
            )

        state.set_state.assert_not_called()
        callback.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_action_when_no_horoscope(self):
        callback = AsyncMock()
        state = AsyncMock()
        user = _make_user_entity()
        app_context = AsyncMock()

        with patch('horoscope.handlers.followup.container') as mock_container:
            sub_repo = AsyncMock()
            sub_repo.ahas_active_subscription = AsyncMock(return_value=True)
            mock_container.horoscope.subscription_repository.return_value = sub_repo

            horoscope_repo = AsyncMock()
            horoscope_repo.aget_by_user_and_date = AsyncMock(return_value=None)
            mock_container.horoscope.horoscope_repository.return_value = horoscope_repo

            await ask_followup_callback(
                callback=callback,
                state=state,
                user=user,
                app_context=app_context,
            )

        state.set_state.assert_not_called()
        callback.answer.assert_called_once()


class TestHandleFollowupQuestion:

    @pytest.mark.asyncio
    async def test_generates_and_saves_answer(self):
        message = AsyncMock()
        message.text = "What about my career?"
        state = AsyncMock()
        state.get_data = AsyncMock(return_value={'horoscope_id': 1})
        user = _make_user_entity()
        app_context = AsyncMock()

        horoscope = _make_horoscope()
        profile = _make_profile()
        followup_result = _make_followup_result()

        with (
            patch('horoscope.handlers.followup.container') as mock_container,
            patch('horoscope.services.llm.LLMService') as mock_llm_cls,
        ):
            horoscope_repo = AsyncMock()
            horoscope_repo.aget = AsyncMock(return_value=horoscope)
            mock_container.horoscope.horoscope_repository.return_value = horoscope_repo

            profile_repo = AsyncMock()
            profile_repo.aget_by_telegram_uid = AsyncMock(return_value=profile)
            mock_container.horoscope.user_profile_repository.return_value = profile_repo

            followup_repo = AsyncMock()
            mock_container.horoscope.followup_repository.return_value = followup_repo

            mock_llm = MagicMock()
            mock_llm.generate_followup_answer.return_value = followup_result
            mock_llm_cls.return_value = mock_llm

            await handle_followup_question(
                message=message,
                state=state,
                user=user,
                app_context=app_context,
            )

        mock_llm.generate_followup_answer.assert_called_once_with(
            horoscope_text=horoscope.full_text,
            question="What about my career?",
            language='en',
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
        assert call_kwargs['reply_markup'] is not None

    @pytest.mark.asyncio
    async def test_handles_llm_failure(self):
        message = AsyncMock()
        message.text = "What about love?"
        state = AsyncMock()
        state.get_data = AsyncMock(return_value={'horoscope_id': 1})
        user = _make_user_entity()
        app_context = AsyncMock()

        horoscope = _make_horoscope()
        profile = _make_profile()

        with (
            patch('horoscope.handlers.followup.container') as mock_container,
            patch('horoscope.services.llm.LLMService') as mock_llm_cls,
        ):
            horoscope_repo = AsyncMock()
            horoscope_repo.aget = AsyncMock(return_value=horoscope)
            mock_container.horoscope.horoscope_repository.return_value = horoscope_repo

            profile_repo = AsyncMock()
            profile_repo.aget_by_telegram_uid = AsyncMock(return_value=profile)
            mock_container.horoscope.user_profile_repository.return_value = profile_repo

            mock_llm = MagicMock()
            mock_llm.generate_followup_answer.side_effect = Exception("LLM error")
            mock_llm_cls.return_value = mock_llm

            await handle_followup_question(
                message=message,
                state=state,
                user=user,
                app_context=app_context,
            )

        state.clear.assert_called_once()
        app_context.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_ignores_empty_text(self):
        message = AsyncMock()
        message.text = None
        state = AsyncMock()
        user = _make_user_entity()
        app_context = AsyncMock()

        await handle_followup_question(
            message=message,
            state=state,
            user=user,
            app_context=app_context,
        )

        app_context.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_clears_state_when_horoscope_not_found(self):
        message = AsyncMock()
        message.text = "Question?"
        state = AsyncMock()
        state.get_data = AsyncMock(return_value={'horoscope_id': 999})
        user = _make_user_entity()
        app_context = AsyncMock()

        with patch('horoscope.handlers.followup.container') as mock_container:
            horoscope_repo = AsyncMock()
            horoscope_repo.aget = AsyncMock(side_effect=Exception("Not found"))
            mock_container.horoscope.horoscope_repository.return_value = horoscope_repo

            await handle_followup_question(
                message=message,
                state=state,
                user=user,
                app_context=app_context,
            )

        state.clear.assert_called_once()
        app_context.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_passes_language_to_llm(self):
        message = AsyncMock()
        message.text = "Що зірки кажуть?"
        state = AsyncMock()
        state.get_data = AsyncMock(return_value={'horoscope_id': 1})
        user = _make_user_entity()
        app_context = AsyncMock()

        horoscope = _make_horoscope()
        profile = _make_profile(preferred_language='uk')
        followup_result = _make_followup_result()

        with (
            patch('horoscope.handlers.followup.container') as mock_container,
            patch('horoscope.services.llm.LLMService') as mock_llm_cls,
        ):
            horoscope_repo = AsyncMock()
            horoscope_repo.aget = AsyncMock(return_value=horoscope)
            mock_container.horoscope.horoscope_repository.return_value = horoscope_repo

            profile_repo = AsyncMock()
            profile_repo.aget_by_telegram_uid = AsyncMock(return_value=profile)
            mock_container.horoscope.user_profile_repository.return_value = profile_repo

            followup_repo = AsyncMock()
            mock_container.horoscope.followup_repository.return_value = followup_repo

            mock_llm = MagicMock()
            mock_llm.generate_followup_answer.return_value = followup_result
            mock_llm_cls.return_value = mock_llm

            await handle_followup_question(
                message=message,
                state=state,
                user=user,
                app_context=app_context,
            )

        call_kwargs = mock_llm.generate_followup_answer.call_args[1]
        assert call_kwargs['language'] == 'uk'


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
