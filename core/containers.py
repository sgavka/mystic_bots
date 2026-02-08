from dependency_injector import containers, providers


def _create_user_repository() -> "UserRepository":
    from core.repositories import UserRepository
    return UserRepository()


def _create_user_profile_repository() -> "UserProfileRepository":
    from horoscope.repositories import UserProfileRepository
    return UserProfileRepository()


def _create_horoscope_repository() -> "HoroscopeRepository":
    from horoscope.repositories import HoroscopeRepository
    return HoroscopeRepository()


def _create_subscription_repository() -> "SubscriptionRepository":
    from horoscope.repositories import SubscriptionRepository
    return SubscriptionRepository()


class CoreContainer(containers.DeclarativeContainer):
    user_repository = providers.Singleton(_create_user_repository)


class HoroscopeContainer(containers.DeclarativeContainer):
    user_repository = providers.Dependency()

    user_profile_repository = providers.Singleton(_create_user_profile_repository)
    horoscope_repository = providers.Singleton(_create_horoscope_repository)
    subscription_repository = providers.Singleton(_create_subscription_repository)


class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    core: CoreContainer = providers.Container(CoreContainer)
    horoscope: HoroscopeContainer = providers.Container(
        HoroscopeContainer,
        user_repository=core.user_repository,
    )


container = ApplicationContainer()
