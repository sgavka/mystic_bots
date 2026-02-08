from dependency_injector import containers, providers


def _create_user_repository() -> "UserRepository":
    from core.repositories import UserRepository
    return UserRepository()


class CoreContainer(containers.DeclarativeContainer):
    user_repository = providers.Singleton(_create_user_repository)


class HoroscopeContainer(containers.DeclarativeContainer):
    user_repository = providers.Dependency()


class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    core: CoreContainer = providers.Container(CoreContainer)
    horoscope: HoroscopeContainer = providers.Container(
        HoroscopeContainer,
        user_repository=core.user_repository,
    )


container = ApplicationContainer()
