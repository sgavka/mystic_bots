# PROJECT_INFO.md

<project>
  <name>Mystic Bots</name>
  <description>
    Telegram bot platform for generating personalized horoscopes. Users go through a wizard
    (name → birth date → birth place → living place), receive their first horoscope, and then
    get daily horoscopes. Free users see a teaser (few lines); subscribers get the full horoscope.
    Horoscope generation runs via Celery task queue.
  </description>
  <stack>Python 3.12+, Aiogram 3.x, Django 5.2, Pydantic 2.x, PostgreSQL 17, Redis 7, Celery, dependency-injector, Docker, uv</stack>
  <package_manager>uv</package_manager>
</project>

<user_flow>
  <wizard>
    1. Enter name
    2. Enter birth date
    3. Enter birth place
    4. Enter living place
  </wizard>
  <after_wizard>
    - User receives their first horoscope immediately
    - Daily horoscopes are generated and sent automatically
  </after_wizard>
  <monetization>
    - Free users: see a teaser (first few lines)
    - Subscribers: get the full horoscope
  </monetization>
</user_flow>

<structure>
  <root>
    <file name="CLAUDE.md">Development rules and project overview</file>
    <file name="PROJECT_INFO.md">This file — project-specific info</file>
    <file name="Makefile">Build/dev automation (all commands go through here)</file>
    <file name="docker-compose.yml">Development environment</file>
    <file name="docker-compose-prod.yml">Production environment</file>
    <file name="pyproject.toml">uv dependencies (PEP 621)</file>
    <file name="manage.py">Django management entry point</file>
  </root>

  <dir name="docs/">
    <file name="MAIN.md">Development process summary</file>
    <file name="PLAN.md">Current plan, task list, next step</file>
    <dir name="tasks/">Individual task files (TASK_{number}_{status}.md)</dir>
  </dir>

  <dir name="docker/">
    <file name="Dockerfile">Docker image definition</file>
    <file name="entrypoint.sh">Container entrypoint script</file>
  </dir>

  <dir name="config/" description="Django project config">
    <file name="settings.py">Django settings</file>
    <file name="celery.py">Celery app configuration</file>
    <file name="urls.py">URL routing</file>
    <file name="wsgi.py">WSGI application</file>
    <file name="asgi.py">ASGI application</file>
  </dir>

  <dir name="core/" description="Core app (shared across bots)">
    <file name="models.py">User, Payment, Setting models</file>
    <file name="entities.py">Pydantic entities</file>
    <file name="enums.py">BotSlug, etc.</file>
    <file name="containers.py">DI container</file>
    <file name="base_entity.py">Base Pydantic entity class</file>
    <dir name="repositories/">Data access layer</dir>
    <dir name="services/">Business logic</dir>
  </dir>

  <dir name="telegram_bot/" description="Telegram bot base app">
    <file name="bot.py">Bot factory, dispatcher setup</file>
    <file name="models.py">Bot-related Django models</file>
    <file name="entities.py">Bot-related Pydantic entities</file>
    <file name="states.py">FSM states</file>
    <dir name="handlers/">Message and callback handlers</dir>
    <dir name="middlewares/">
      <file name="bot.py">BotMiddleware</file>
      <file name="user.py">UserMiddleware, AppContextMiddleware</file>
    </dir>
    <dir name="repositories/">Data access layer</dir>
    <dir name="services/">Business logic</dir>
    <dir name="utils/">
      <file name="context.py">AppContext for message management</file>
    </dir>
    <dir name="management/commands/">
      <file name="start_bot.py">Django management command to start bot</file>
    </dir>
  </dir>

  <dir name="horoscope/" description="Horoscope bot app (main feature)">
    <file name="models.py">UserProfile, Horoscope, Subscription</file>
    <file name="entities.py">Horoscope-related Pydantic entities</file>
    <file name="enums.py">SubscriptionStatus, HoroscopeType</file>
    <file name="config.py">Horoscope app configuration</file>
    <file name="callbacks.py">Callback data structures</file>
    <file name="keyboards.py">Inline keyboard builders</file>
    <file name="states.py">FSM states (wizard)</file>
    <dir name="tasks/">
      <file name="generate_horoscope.py">Celery task for horoscope generation</file>
      <file name="send_daily_horoscope.py">Celery task for daily sending</file>
    </dir>
    <dir name="handlers/">
      <file name="wizard.py">Onboarding wizard</file>
      <file name="horoscope.py">View horoscope</file>
      <file name="subscription.py">Manage subscription</file>
      <file name="menu.py">Main menu</file>
    </dir>
    <dir name="repositories/">Data access layer</dir>
    <dir name="services/">
      <file name="horoscope.py">Generation logic</file>
      <file name="subscription.py">Subscription logic</file>
    </dir>
    <dir name="tests/">Test suite</dir>
  </dir>

  <dir name="locale/" description="i18n translations">
    <dir name="en/">English</dir>
    <dir name="uk/">Ukrainian</dir>
    <dir name="ru/">Russian</dir>
  </dir>

  <dir name="data/" description="Docker volumes">
    <dir name="postgres/">PostgreSQL data</dir>
    <dir name="redis/">Redis data</dir>
  </dir>
</structure>
