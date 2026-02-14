from typing import TYPE_CHECKING

from dependency_injector import containers, providers

if TYPE_CHECKING:
    from core.repositories import UserRepository
    from horoscope.repositories import (
        HoroscopeRepository,
        LLMUsageRepository,
        SubscriptionRepository,
        UserProfileRepository,
    )
    from horoscope.services.horoscope import HoroscopeService
    from horoscope.services.subscription import SubscriptionService


def _create_user_repository() -> "UserRepository":
    from core.repositories import UserRepository
    return UserRepository()


def _create_user_profile_repository() -> "UserProfileRepository":
    from horoscope.repositories import UserProfileRepository
    return UserProfileRepository()


def _create_horoscope_repository() -> "HoroscopeRepository":
    from horoscope.repositories import HoroscopeRepository
    return HoroscopeRepository()


def _create_llm_usage_repository() -> "LLMUsageRepository":
    from horoscope.repositories import LLMUsageRepository
    return LLMUsageRepository()


def _create_subscription_repository() -> "SubscriptionRepository":
    from horoscope.repositories import SubscriptionRepository
    return SubscriptionRepository()


class CoreContainer(containers.DeclarativeContainer):
    user_repository = providers.Singleton(_create_user_repository)


class HoroscopeContainer(containers.DeclarativeContainer):
    user_repository = providers.Dependency()

    user_profile_repository = providers.Singleton(_create_user_profile_repository)
    horoscope_repository = providers.Singleton(_create_horoscope_repository)
    llm_usage_repository = providers.Singleton(_create_llm_usage_repository)
    subscription_repository = providers.Singleton(_create_subscription_repository)

    horoscope_service = providers.Singleton(
        lambda: _create_horoscope_service(),
    )
    subscription_service = providers.Singleton(
        lambda: _create_subscription_service(),
    )


def _create_horoscope_service() -> "HoroscopeService":
    from horoscope.services.horoscope import HoroscopeService
    return HoroscopeService(
        horoscope_repo=container.horoscope.horoscope_repository(),
        user_profile_repo=container.horoscope.user_profile_repository(),
        llm_usage_repo=container.horoscope.llm_usage_repository(),
    )


def _create_subscription_service() -> "SubscriptionService":
    from horoscope.services.subscription import SubscriptionService
    return SubscriptionService(
        subscription_repo=container.horoscope.subscription_repository(),
    )


class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    core: CoreContainer = providers.Container(CoreContainer)
    horoscope: HoroscopeContainer = providers.Container(
        HoroscopeContainer,
        user_repository=core.user_repository,
    )


container = ApplicationContainer()
