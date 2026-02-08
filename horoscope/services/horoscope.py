import logging
import random
from datetime import date

from asgiref.sync import sync_to_async

from core.containers import container
from horoscope.config import TEASER_LINE_COUNT
from horoscope.entities import HoroscopeEntity, UserProfileEntity
from horoscope.enums import HoroscopeType
from horoscope.utils import get_zodiac_sign

logger = logging.getLogger(__name__)

THEMES = [
    "love and relationships", "career and finances", "health and wellness",
    "personal growth", "creativity and inspiration", "travel and adventure",
    "family and home", "friendships and social life",
]

POSITIVE_PHRASES = [
    "The stars are aligned in your favor today.",
    "A wave of positive energy surrounds you.",
    "The universe is sending you encouraging signs.",
    "Cosmic forces are working to bring you joy.",
    "Today brings a fresh perspective on life.",
    "Celestial energy fills you with renewed purpose.",
    "The planets encourage bold decisions today.",
    "A harmonious alignment brings inner peace.",
]

ADVICE_PHRASES = [
    "Trust your intuition — it won't lead you astray.",
    "Take time to reflect on what truly matters.",
    "Open your heart to unexpected opportunities.",
    "Don't be afraid to step outside your comfort zone.",
    "Patience will be your greatest ally today.",
    "Focus on the present moment and let go of worries.",
    "A small act of kindness will have ripple effects.",
    "Listen more than you speak — wisdom awaits.",
    "Embrace change as a pathway to growth.",
    "Your determination will open doors you didn't know existed.",
]

DETAIL_PHRASES = [
    "In matters of {theme}, expect pleasant surprises.",
    "The alignment of the stars suggests progress in {theme}.",
    "Pay special attention to {theme} — the cosmos has plans.",
    "Your birth chart reveals important shifts in {theme}.",
    "The celestial bodies are highlighting {theme} for you.",
    "A planetary transit is bringing clarity to {theme}.",
    "The moon's influence is particularly strong in {theme}.",
    "Venus and Jupiter are combining their energy around {theme}.",
]

CLOSING_PHRASES = [
    "Remember, the stars guide but do not dictate. Your choices shape your destiny.",
    "May the cosmic energy bring you wisdom and serenity.",
    "The universe believes in you — and so should you.",
    "Let the starlight illuminate your path forward.",
    "Trust in the cosmic plan unfolding before you.",
]


def generate_horoscope_text(profile: UserProfileEntity, target_date: date) -> tuple[str, str]:
    sign = get_zodiac_sign(profile.date_of_birth)
    random.seed(f"{profile.user_telegram_uid}-{target_date.isoformat()}")

    themes = random.sample(THEMES, k=3)
    positive = random.choice(POSITIVE_PHRASES)
    advice = random.sample(ADVICE_PHRASES, k=2)
    details = [random.choice(DETAIL_PHRASES).format(theme=t) for t in themes]
    closing = random.choice(CLOSING_PHRASES)

    lines = [
        f"Horoscope for {sign} — {target_date.strftime('%B %d, %Y')}",
        f"Dear {profile.name},",
        "",
        positive,
        "",
        details[0],
        details[1],
        details[2],
        "",
        advice[0],
        advice[1],
        "",
        closing,
    ]

    full_text = "\n".join(lines)
    teaser_lines = lines[:TEASER_LINE_COUNT]
    teaser_text = "\n".join(teaser_lines) + "\n\n..."

    return full_text, teaser_text


class HoroscopeService:
    def __init__(self):
        self.horoscope_repo = container.horoscope.horoscope_repository()
        self.user_profile_repo = container.horoscope.user_profile_repository()

    def generate_for_user(
        self,
        telegram_uid: int,
        target_date: date,
        horoscope_type: str = HoroscopeType.DAILY,
    ) -> HoroscopeEntity:
        existing = self.horoscope_repo.get_by_user_and_date(
            telegram_uid=telegram_uid,
            target_date=target_date,
        )
        if existing:
            return existing

        profile = self.user_profile_repo.get_by_telegram_uid(telegram_uid)
        if not profile:
            raise ValueError(f"No profile found for user {telegram_uid}")

        full_text, teaser_text = self._generate_text(
            profile=profile,
            target_date=target_date,
        )

        horoscope = self.horoscope_repo.create_horoscope(
            telegram_uid=telegram_uid,
            horoscope_type=horoscope_type,
            target_date=target_date,
            full_text=full_text,
            teaser_text=teaser_text,
        )

        logger.info(f"Generated {horoscope_type} horoscope for user {telegram_uid} on {target_date}")
        return horoscope

    def _generate_text(
        self,
        profile: UserProfileEntity,
        target_date: date,
    ) -> tuple[str, str]:
        from horoscope.services.llm import LLMService

        llm_service = LLMService()
        if llm_service.is_configured:
            try:
                sign = get_zodiac_sign(profile.date_of_birth)
                return llm_service.generate_horoscope_text(
                    zodiac_sign=sign,
                    name=profile.name,
                    date_of_birth=profile.date_of_birth,
                    place_of_birth=profile.place_of_birth,
                    place_of_living=profile.place_of_living,
                    target_date=target_date,
                )
            except Exception as e:
                logger.warning(f"LLM generation failed, falling back to template: {e}")

        return generate_horoscope_text(
            profile=profile,
            target_date=target_date,
        )

    async def agenerate_for_user(
        self,
        telegram_uid: int,
        target_date: date,
        horoscope_type: str = HoroscopeType.DAILY,
    ) -> HoroscopeEntity:
        return await sync_to_async(self.generate_for_user)(
            telegram_uid,
            target_date,
            horoscope_type,
        )
