LANGUAGE_NAMES = {
    'en': "English",
    'ru': "Русский",
    'uk': "Українська",
    'de': "Deutsch",
}

LANGUAGE_FLAGS = {
    'en': "🇬🇧",
    'ru': "🇷🇺",
    'uk': "🇺🇦",
    'de': "🇩🇪",
}

TRANSLATIONS = {
    # --- Wizard: language selection ---
    "wizard.choose_language": {
        "en": "🌍 Please choose your language:",
        "ru": "🌍 Пожалуйста, выберите язык:",
        "uk": "🌍 Будь ласка, оберіть мову:",
        "de": "🌍 Bitte wählen Sie Ihre Sprache:",
    },

    # --- Wizard: start ---
    "wizard.welcome_back": {
        "en": "👋 Welcome back, <b>{name}</b>!\n\nYour profile is already set up. You'll receive your daily horoscope soon ✨",
        "ru": "👋 С возвращением, <b>{name}</b>!\n\nВаш профиль уже настроен. Скоро вы получите ежедневный гороскоп ✨",
        "uk": "👋 З поверненням, <b>{name}</b>!\n\nВаш профіль вже налаштований. Скоро ви отримаєте щоденний гороскоп ✨",
        "de": "👋 Willkommen zurück, <b>{name}</b>!\n\nIhr Profil ist bereits eingerichtet. Sie erhalten bald Ihr tägliches Horoskop ✨",
    },
    "wizard.welcome": {
        "en": "✨ Welcome to <b>Mystic Horoscope</b>! ✨\n\n🔮 I'll create a personalized horoscope just for you. Let's set up your profile first.\n\nWhat is your <b>name</b>?",
        "ru": "✨ Добро пожаловать в <b>Mystic Horoscope</b>! ✨\n\n🔮 Я создам персональный гороскоп специально для вас. Давайте сначала настроим профиль.\n\nКак вас <b>зовут</b>?",
        "uk": "✨ Ласкаво просимо до <b>Mystic Horoscope</b>! ✨\n\n🔮 Я створю персональний гороскоп спеціально для вас. Спочатку налаштуємо профіль.\n\nЯк вас <b>звати</b>?",
        "de": "✨ Willkommen bei <b>Mystic Horoscope</b>! ✨\n\n🔮 Ich erstelle ein personalisiertes Horoskop nur für Sie. Lassen Sie uns zuerst Ihr Profil einrichten.\n\nWie ist Ihr <b>Name</b>?",
    },

    # --- Wizard: name step ---
    "wizard.invalid_name": {
        "en": "Please enter a valid name (2-100 characters).",
        "ru": "Пожалуйста, введите корректное имя (2-100 символов).",
        "uk": "Будь ласка, введіть коректне ім'я (2-100 символів).",
        "de": "Bitte geben Sie einen gültigen Namen ein (2-100 Zeichen).",
    },
    "wizard.ask_dob": {
        "en": "😊 Nice to meet you, <b>{name}</b>!\n\n📅 Now, please enter your <b>full date of birth</b>\nin format: <code>DD.MM.YYYY</code>\n\nExample: <code>15.03.1990</code>",
        "ru": "😊 Приятно познакомиться, <b>{name}</b>!\n\n📅 Теперь введите вашу <b>полную дату рождения</b>\nв формате: <code>ДД.ММ.ГГГГ</code>\n\nПример: <code>15.03.1990</code>",
        "uk": "😊 Приємно познайомитися, <b>{name}</b>!\n\n📅 Тепер введіть вашу <b>повну дату народження</b>\nу форматі: <code>ДД.ММ.РРРР</code>\n\nПриклад: <code>15.03.1990</code>",
        "de": "😊 Freut mich, <b>{name}</b>!\n\n📅 Bitte geben Sie Ihr <b>vollständiges Geburtsdatum</b> ein\nim Format: <code>TT.MM.JJJJ</code>\n\nBeispiel: <code>15.03.1990</code>",
    },

    # --- Wizard: DOB step ---
    "wizard.invalid_date_format": {
        "en": "Invalid date format. Please use <code>DD.MM.YYYY</code>\n\nExample: <code>15.03.1990</code>",
        "ru": "Неверный формат даты. Используйте <code>ДД.ММ.ГГГГ</code>\n\nПример: <code>15.03.1990</code>",
        "uk": "Невірний формат дати. Використовуйте <code>ДД.ММ.РРРР</code>\n\nПриклад: <code>15.03.1990</code>",
        "de": "Ungültiges Datumsformat. Bitte verwenden Sie <code>TT.MM.JJJJ</code>\n\nBeispiel: <code>15.03.1990</code>",
    },
    "wizard.dob_in_future": {
        "en": "Date of birth must be in the past. Please try again.",
        "ru": "Дата рождения должна быть в прошлом. Попробуйте ещё раз.",
        "uk": "Дата народження має бути в минулому. Спробуйте ще раз.",
        "de": "Das Geburtsdatum muss in der Vergangenheit liegen. Bitte versuchen Sie es erneut.",
    },
    "wizard.dob_too_old": {
        "en": "Please enter a valid date of birth.",
        "ru": "Пожалуйста, введите корректную дату рождения.",
        "uk": "Будь ласка, введіть коректну дату народження.",
        "de": "Bitte geben Sie ein gültiges Geburtsdatum ein.",
    },

    # --- Wizard: place of birth step ---
    "wizard.ask_place_of_birth": {
        "en": "🎯 Great! Now, please enter your <b>place of birth</b> (city).\n\nExample: <code>London</code>",
        "ru": "🎯 Отлично! Теперь введите ваше <b>место рождения</b> (город).\n\nПример: <code>Москва</code>",
        "uk": "🎯 Чудово! Тепер введіть ваше <b>місце народження</b> (місто).\n\nПриклад: <code>Київ</code>",
        "de": "🎯 Toll! Bitte geben Sie Ihren <b>Geburtsort</b> (Stadt) ein.\n\nBeispiel: <code>Berlin</code>",
    },
    "wizard.invalid_city": {
        "en": "Please enter a valid city name (2-200 characters).",
        "ru": "Пожалуйста, введите корректное название города (2-200 символов).",
        "uk": "Будь ласка, введіть коректну назву міста (2-200 символів).",
        "de": "Bitte geben Sie einen gültigen Stadtnamen ein (2-200 Zeichen).",
    },

    # --- Wizard: place of living step ---
    "wizard.ask_place_of_living": {
        "en": "📍 Almost done! Please enter your <b>current place of living</b> (city).\n\nExample: <code>New York</code>",
        "ru": "📍 Почти готово! Введите ваше <b>текущее место проживания</b> (город).\n\nПример: <code>Санкт-Петербург</code>",
        "uk": "📍 Майже готово! Введіть ваше <b>поточне місце проживання</b> (місто).\n\nПриклад: <code>Львів</code>",
        "de": "📍 Fast fertig! Bitte geben Sie Ihren <b>aktuellen Wohnort</b> (Stadt) ein.\n\nBeispiel: <code>München</code>",
    },

    # --- Wizard: profile created ---
    "wizard.profile_ready": {
        "en": (
            "✅ Your profile is ready, <b>{name}</b>!\n\n"
            "📅 Date of birth: {dob}\n"
            "🏠 Born in: {place_of_birth}\n"
            "📍 Living in: {place_of_living}\n\n"
            "🔮 Generating your first horoscope... Please wait a moment."
        ),
        "ru": (
            "✅ Ваш профиль готов, <b>{name}</b>!\n\n"
            "📅 Дата рождения: {dob}\n"
            "🏠 Место рождения: {place_of_birth}\n"
            "📍 Место проживания: {place_of_living}\n\n"
            "🔮 Генерирую ваш первый гороскоп... Пожалуйста, подождите."
        ),
        "uk": (
            "✅ Ваш профіль готовий, <b>{name}</b>!\n\n"
            "📅 Дата народження: {dob}\n"
            "🏠 Місце народження: {place_of_birth}\n"
            "📍 Місце проживання: {place_of_living}\n\n"
            "🔮 Генерую ваш перший гороскоп... Будь ласка, зачекайте."
        ),
        "de": (
            "✅ Ihr Profil ist fertig, <b>{name}</b>!\n\n"
            "📅 Geburtsdatum: {dob}\n"
            "🏠 Geburtsort: {place_of_birth}\n"
            "📍 Wohnort: {place_of_living}\n\n"
            "🔮 Ihr erstes Horoskop wird erstellt... Bitte warten Sie einen Moment."
        ),
    },

    # --- Horoscope view ---
    "horoscope.no_profile": {
        "en": "⚠️ You haven't set up your profile yet.\nSend /start to begin the onboarding wizard.",
        "ru": "⚠️ Вы ещё не настроили свой профиль.\nОтправьте /start для начала настройки.",
        "uk": "⚠️ Ви ще не налаштували свій профіль.\nНадішліть /start для початку налаштування.",
        "de": "⚠️ Sie haben Ihr Profil noch nicht eingerichtet.\nSenden Sie /start, um den Einrichtungsassistenten zu starten.",
    },
    "horoscope.not_ready": {
        "en": "⏳ Your horoscope for today is not ready yet.\nIt will be generated soon. Please check back later.",
        "ru": "⏳ Ваш гороскоп на сегодня ещё не готов.\nОн скоро будет сгенерирован. Проверьте позже.",
        "uk": "⏳ Ваш гороскоп на сьогодні ще не готовий.\nВін скоро буде згенерований. Перевірте пізніше.",
        "de": "⏳ Ihr Horoskop für heute ist noch nicht fertig.\nEs wird bald erstellt. Bitte schauen Sie später noch einmal vorbei.",
    },
    "horoscope.subscribe_cta": {
        "en": "\n\n🔒 Subscribe to see your full daily horoscope!",
        "ru": "\n\n🔒 Подпишитесь, чтобы видеть полный ежедневный гороскоп!",
        "uk": "\n\n🔒 Підпишіться, щоб бачити повний щоденний гороскоп!",
        "de": "\n\n🔒 Abonnieren Sie, um Ihr vollständiges tägliches Horoskop zu sehen!",
    },

    # --- Subscription ---
    "subscription.offer": {
        "en": (
            "⭐ Subscribe for <b>{days} days</b> of full daily horoscope access.\n\n"
            "💰 Price: <b>{price} Telegram Stars</b>\n\n"
            "Tap the button below to pay."
        ),
        "ru": (
            "⭐ Подпишитесь на <b>{days} дней</b> полного доступа к ежедневному гороскопу.\n\n"
            "💰 Цена: <b>{price} Telegram Stars</b>\n\n"
            "Нажмите кнопку ниже для оплаты."
        ),
        "uk": (
            "⭐ Підпишіться на <b>{days} днів</b> повного доступу до щоденного гороскопу.\n\n"
            "💰 Ціна: <b>{price} Telegram Stars</b>\n\n"
            "Натисніть кнопку нижче для оплати."
        ),
        "de": (
            "⭐ Abonnieren Sie für <b>{days} Tage</b> vollen Zugang zum täglichen Horoskop.\n\n"
            "💰 Preis: <b>{price} Telegram Stars</b>\n\n"
            "Tippen Sie auf die Schaltfläche unten, um zu bezahlen."
        ),
    },
    "subscription.invoice_title": {
        "en": "Horoscope Subscription",
        "ru": "Подписка на гороскоп",
        "uk": "Підписка на гороскоп",
        "de": "Horoskop-Abonnement",
    },
    "subscription.invoice_description": {
        "en": "{days}-day access to full daily horoscope",
        "ru": "Доступ к полному ежедневному гороскопу на {days} дней",
        "uk": "Доступ до повного щоденного гороскопу на {days} днів",
        "de": "{days}-tägiger Zugang zum vollständigen täglichen Horoskop",
    },
    "subscription.payment_success": {
        "en": "✅ Payment successful! Your subscription is now active.\n\n📅 Expires: {expires}\n\nUse /horoscope to see your full daily horoscope ✨",
        "ru": "✅ Оплата прошла успешно! Ваша подписка активирована.\n\n📅 Действует до: {expires}\n\nИспользуйте /horoscope для просмотра полного гороскопа ✨",
        "uk": "✅ Оплата пройшла успішно! Вашу підписку активовано.\n\n📅 Дійсна до: {expires}\n\nВикористовуйте /horoscope для перегляду повного гороскопу ✨",
        "de": "✅ Zahlung erfolgreich! Ihr Abonnement ist jetzt aktiv.\n\n📅 Gültig bis: {expires}\n\nVerwenden Sie /horoscope, um Ihr vollständiges tägliches Horoskop zu sehen ✨",
    },

    # --- Keyboard buttons ---
    "keyboard.subscribe": {
        "en": "⭐ Subscribe for full horoscope",
        "ru": "⭐ Подписаться на полный гороскоп",
        "uk": "⭐ Підписатися на повний гороскоп",
        "de": "⭐ Für vollständiges Horoskop abonnieren",
    },

    # --- Celery tasks: first horoscope ---
    "task.first_horoscope_ready": {
        "en": "🔮 Your first horoscope is ready!\n\n{text}",
        "ru": "🔮 Ваш первый гороскоп готов!\n\n{text}",
        "uk": "🔮 Ваш перший гороскоп готовий!\n\n{text}",
        "de": "🔮 Ihr erstes Horoskop ist fertig!\n\n{text}",
    },

    # --- Celery tasks: subscription reminders ---
    "task.expiry_reminder": {
        "en": "⏰ Your horoscope subscription expires in <b>{days} day(s)</b>.\n\nRenew now to keep receiving your full daily horoscope! ✨",
        "ru": "⏰ Ваша подписка на гороскоп истекает через <b>{days} дн.</b>\n\nПродлите сейчас, чтобы продолжить получать полный ежедневный гороскоп! ✨",
        "uk": "⏰ Ваша підписка на гороскоп закінчується через <b>{days} дн.</b>\n\nПоновіть зараз, щоб продовжити отримувати повний щоденний гороскоп! ✨",
        "de": "⏰ Ihr Horoskop-Abonnement läuft in <b>{days} Tag(en)</b> ab.\n\nVerlängern Sie jetzt, um weiterhin Ihr vollständiges tägliches Horoskop zu erhalten! ✨",
    },
    "task.subscription_expired": {
        "en": "⚠️ Your horoscope subscription has <b>expired</b>.\n\nYou'll now see a preview of your daily horoscope. Subscribe again to get full access! ⭐",
        "ru": "⚠️ Ваша подписка на гороскоп <b>истекла</b>.\n\nТеперь вы видите только превью гороскопа. Подпишитесь снова для полного доступа! ⭐",
        "uk": "⚠️ Ваша підписка на гороскоп <b>закінчилася</b>.\n\nТепер ви бачите лише попередній перегляд гороскопу. Підпишіться знову для повного доступу! ⭐",
        "de": "⚠️ Ihr Horoskop-Abonnement ist <b>abgelaufen</b>.\n\nSie sehen jetzt nur eine Vorschau Ihres täglichen Horoskops. Abonnieren Sie erneut für vollen Zugang! ⭐",
    },

    # --- Language command ---
    "language.current": {
        "en": "🌍 Your current language: <b>{lang_name}</b>\n\nChoose a new language:",
        "ru": "🌍 Ваш текущий язык: <b>{lang_name}</b>\n\nВыберите новый язык:",
        "uk": "🌍 Ваша поточна мова: <b>{lang_name}</b>\n\nОберіть нову мову:",
        "de": "🌍 Ihre aktuelle Sprache: <b>{lang_name}</b>\n\nWählen Sie eine neue Sprache:",
    },
    "language.changed": {
        "en": "✅ Language changed to <b>English</b> 🇬🇧",
        "ru": "✅ Язык изменён на <b>Русский</b> 🇷🇺",
        "uk": "✅ Мову змінено на <b>Українська</b> 🇺🇦",
        "de": "✅ Sprache geändert zu <b>Deutsch</b> 🇩🇪",
    },
    "language.no_profile": {
        "en": "⚠️ You haven't set up your profile yet.\nSend /start to begin.",
        "ru": "⚠️ Вы ещё не настроили профиль.\nОтправьте /start для начала.",
        "uk": "⚠️ Ви ще не налаштували профіль.\nНадішліть /start для початку.",
        "de": "⚠️ Sie haben Ihr Profil noch nicht eingerichtet.\nSenden Sie /start, um zu beginnen.",
    },

    # --- Horoscope template phrases ---
    "horoscope.header": {
        "en": "Horoscope for {sign} — {date}",
        "ru": "Гороскоп для {sign} — {date}",
        "uk": "Гороскоп для {sign} — {date}",
        "de": "Horoskop für {sign} — {date}",
    },
    "horoscope.greeting": {
        "en": "Dear {name},",
        "ru": "Дорогой(ая) {name},",
        "uk": "Дорогий(а) {name},",
        "de": "Liebe(r) {name},",
    },
}


def t(key: str, language: str, **kwargs) -> str:
    """Get translated string by key and language code, with optional formatting."""
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key

    text = entry.get(language) or entry.get('en', key)

    if kwargs:
        text = text.format(**kwargs)

    return text


SUPPORTED_LANGUAGE_CODES = {'en', 'ru', 'uk', 'de'}


def map_telegram_language(language_code: str | None) -> str:
    """Map Telegram's language_code to our supported language code."""
    if not language_code:
        return 'en'
    code = language_code.lower().split('-')[0]
    if code in SUPPORTED_LANGUAGE_CODES:
        return code
    return 'en'
