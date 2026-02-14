from core.containers import container
from core.entities import UserEntity
from horoscope.messages import map_telegram_language


async def aget_user_language(user: UserEntity) -> str:
    """Get user's preferred language from profile, falling back to Telegram language."""
    user_profile_repo = container.horoscope.user_profile_repository()
    profile = await user_profile_repo.aget_by_telegram_uid(user.telegram_uid)
    if profile:
        return profile.preferred_language
    return map_telegram_language(user.language_code)
