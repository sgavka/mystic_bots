import logging
import random
from datetime import date

from asgiref.sync import sync_to_async

from core.containers import container
from horoscope.config import TEASER_LINE_COUNT
from horoscope.entities import HoroscopeEntity, UserProfileEntity
from horoscope.enums import HoroscopeType
from horoscope.translations import t
from horoscope.utils import get_zodiac_sign

logger = logging.getLogger(__name__)

THEMES = {
    "en": [
        "love and relationships", "career and finances", "health and wellness",
        "personal growth", "creativity and inspiration", "travel and adventure",
        "family and home", "friendships and social life",
    ],
    "ru": [
        "любовь и отношения", "карьера и финансы", "здоровье и самочувствие",
        "личностный рост", "творчество и вдохновение", "путешествия и приключения",
        "семья и дом", "дружба и общение",
    ],
    "uk": [
        "кохання та стосунки", "кар'єра та фінанси", "здоров'я та самопочуття",
        "особистісний розвиток", "творчість та натхнення", "подорожі та пригоди",
        "сім'я та дім", "дружба та спілкування",
    ],
    "de": [
        "Liebe und Beziehungen", "Karriere und Finanzen", "Gesundheit und Wohlbefinden",
        "persönliches Wachstum", "Kreativität und Inspiration", "Reisen und Abenteuer",
        "Familie und Zuhause", "Freundschaften und soziales Leben",
    ],
}

POSITIVE_PHRASES = {
    "en": [
        "The stars are aligned in your favor today.",
        "A wave of positive energy surrounds you.",
        "The universe is sending you encouraging signs.",
        "Cosmic forces are working to bring you joy.",
        "Today brings a fresh perspective on life.",
        "Celestial energy fills you with renewed purpose.",
        "The planets encourage bold decisions today.",
        "A harmonious alignment brings inner peace.",
    ],
    "ru": [
        "Звёзды сегодня на вашей стороне.",
        "Волна позитивной энергии окутывает вас.",
        "Вселенная посылает вам ободряющие знаки.",
        "Космические силы работают, чтобы принести вам радость.",
        "Сегодня день свежих взглядов на жизнь.",
        "Небесная энергия наполняет вас новой целью.",
        "Планеты поощряют смелые решения сегодня.",
        "Гармоничное расположение звёзд дарит внутренний покой.",
    ],
    "uk": [
        "Зорі сьогодні на вашому боці.",
        "Хвиля позитивної енергії оточує вас.",
        "Всесвіт надсилає вам підбадьорливі знаки.",
        "Космічні сили працюють, щоб принести вам радість.",
        "Сьогодні день свіжих поглядів на життя.",
        "Небесна енергія наповнює вас новою метою.",
        "Планети заохочують сміливі рішення сьогодні.",
        "Гармонійне розташування зірок дарує внутрішній спокій.",
    ],
    "de": [
        "Die Sterne stehen heute zu Ihren Gunsten.",
        "Eine Welle positiver Energie umgibt Sie.",
        "Das Universum sendet Ihnen ermutigende Zeichen.",
        "Kosmische Kräfte arbeiten daran, Ihnen Freude zu bringen.",
        "Heute bringt eine frische Perspektive auf das Leben.",
        "Himmlische Energie erfüllt Sie mit neuem Sinn.",
        "Die Planeten ermutigen heute zu mutigen Entscheidungen.",
        "Eine harmonische Ausrichtung bringt inneren Frieden.",
    ],
}

ADVICE_PHRASES = {
    "en": [
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
    ],
    "ru": [
        "Доверьтесь интуиции — она вас не подведёт.",
        "Найдите время для размышлений о действительно важном.",
        "Откройте сердце неожиданным возможностям.",
        "Не бойтесь выходить из зоны комфорта.",
        "Терпение будет вашим лучшим союзником сегодня.",
        "Сосредоточьтесь на настоящем моменте и отпустите тревоги.",
        "Маленький добрый поступок создаст волну добра.",
        "Слушайте больше, чем говорите — мудрость ждёт.",
        "Примите перемены как путь к росту.",
        "Ваша решимость откроет двери, о которых вы не знали.",
    ],
    "uk": [
        "Довіртеся інтуїції — вона вас не підведе.",
        "Знайдіть час для роздумів про справді важливе.",
        "Відкрийте серце несподіваним можливостям.",
        "Не бійтеся виходити із зони комфорту.",
        "Терпіння буде вашим найкращим союзником сьогодні.",
        "Зосередьтеся на теперішньому моменті та відпустіть тривоги.",
        "Маленький добрий вчинок створить хвилю добра.",
        "Слухайте більше, ніж говоріть — мудрість чекає.",
        "Прийміть зміни як шлях до зростання.",
        "Ваша рішучість відкриє двері, про які ви не знали.",
    ],
    "de": [
        "Vertrauen Sie Ihrer Intuition — sie wird Sie nicht in die Irre führen.",
        "Nehmen Sie sich Zeit, über das nachzudenken, was wirklich zählt.",
        "Öffnen Sie Ihr Herz für unerwartete Möglichkeiten.",
        "Haben Sie keine Angst, Ihre Komfortzone zu verlassen.",
        "Geduld wird heute Ihr größter Verbündeter sein.",
        "Konzentrieren Sie sich auf den Moment und lassen Sie Sorgen los.",
        "Eine kleine freundliche Geste wird Wellen schlagen.",
        "Hören Sie mehr zu, als Sie sprechen — Weisheit erwartet Sie.",
        "Begrüßen Sie Veränderung als Weg zum Wachstum.",
        "Ihre Entschlossenheit wird Türen öffnen, von denen Sie nicht wussten.",
    ],
}

DETAIL_PHRASES = {
    "en": [
        "In matters of {theme}, expect pleasant surprises.",
        "The alignment of the stars suggests progress in {theme}.",
        "Pay special attention to {theme} — the cosmos has plans.",
        "Your birth chart reveals important shifts in {theme}.",
        "The celestial bodies are highlighting {theme} for you.",
        "A planetary transit is bringing clarity to {theme}.",
        "The moon's influence is particularly strong in {theme}.",
        "Venus and Jupiter are combining their energy around {theme}.",
    ],
    "ru": [
        "В вопросах {theme} ожидайте приятных сюрпризов.",
        "Расположение звёзд предвещает прогресс в {theme}.",
        "Обратите особое внимание на {theme} — у космоса есть планы.",
        "Ваша натальная карта показывает важные сдвиги в {theme}.",
        "Небесные тела выделяют для вас {theme}.",
        "Планетарный транзит приносит ясность в {theme}.",
        "Влияние Луны особенно сильно в {theme}.",
        "Венера и Юпитер объединяют свою энергию вокруг {theme}.",
    ],
    "uk": [
        "У питаннях {theme} очікуйте приємних сюрпризів.",
        "Розташування зірок передвіщає прогрес у {theme}.",
        "Зверніть особливу увагу на {theme} — у космосу є плани.",
        "Ваша натальна карта показує важливі зрушення у {theme}.",
        "Небесні тіла виділяють для вас {theme}.",
        "Планетарний транзит приносить ясність у {theme}.",
        "Вплив Місяця особливо сильний у {theme}.",
        "Венера і Юпітер об'єднують свою енергію навколо {theme}.",
    ],
    "de": [
        "In Sachen {theme} erwarten Sie angenehme Überraschungen.",
        "Die Ausrichtung der Sterne deutet auf Fortschritt in {theme} hin.",
        "Achten Sie besonders auf {theme} — der Kosmos hat Pläne.",
        "Ihr Geburtshoroskop zeigt wichtige Veränderungen in {theme}.",
        "Die Himmelskörper heben {theme} für Sie hervor.",
        "Ein planetarischer Transit bringt Klarheit in {theme}.",
        "Der Einfluss des Mondes ist besonders stark in {theme}.",
        "Venus und Jupiter vereinen ihre Energie rund um {theme}.",
    ],
}

CLOSING_PHRASES = {
    "en": [
        "Remember, the stars guide but do not dictate. Your choices shape your destiny.",
        "May the cosmic energy bring you wisdom and serenity.",
        "The universe believes in you — and so should you.",
        "Let the starlight illuminate your path forward.",
        "Trust in the cosmic plan unfolding before you.",
    ],
    "ru": [
        "Помните, звёзды направляют, но не диктуют. Ваш выбор определяет вашу судьбу.",
        "Пусть космическая энергия принесёт вам мудрость и покой.",
        "Вселенная верит в вас — и вы должны верить в себя.",
        "Пусть звёздный свет освещает ваш путь вперёд.",
        "Доверьтесь космическому плану, разворачивающемуся перед вами.",
    ],
    "uk": [
        "Пам'ятайте, зорі спрямовують, але не диктують. Ваш вибір визначає вашу долю.",
        "Нехай космічна енергія принесе вам мудрість і спокій.",
        "Всесвіт вірить у вас — і ви повинні вірити в себе.",
        "Нехай зоряне світло освітлює ваш шлях уперед.",
        "Довіртеся космічному плану, що розгортається перед вами.",
    ],
    "de": [
        "Denken Sie daran: Die Sterne leiten, aber bestimmen nicht. Ihre Entscheidungen formen Ihr Schicksal.",
        "Möge die kosmische Energie Ihnen Weisheit und Gelassenheit bringen.",
        "Das Universum glaubt an Sie — und das sollten Sie auch.",
        "Lassen Sie das Sternenlicht Ihren Weg nach vorne erhellen.",
        "Vertrauen Sie auf den kosmischen Plan, der sich vor Ihnen entfaltet.",
    ],
}


def generate_horoscope_text(
    profile: UserProfileEntity,
    target_date: date,
    language: str = 'en',
) -> tuple[str, str]:
    sign = get_zodiac_sign(profile.date_of_birth)
    random.seed(f"{profile.user_telegram_uid}-{target_date.isoformat()}")

    lang_themes = THEMES.get(language, THEMES['en'])
    lang_positive = POSITIVE_PHRASES.get(language, POSITIVE_PHRASES['en'])
    lang_advice = ADVICE_PHRASES.get(language, ADVICE_PHRASES['en'])
    lang_details = DETAIL_PHRASES.get(language, DETAIL_PHRASES['en'])
    lang_closing = CLOSING_PHRASES.get(language, CLOSING_PHRASES['en'])

    themes = random.sample(lang_themes, k=3)
    positive = random.choice(lang_positive)
    advice = random.sample(lang_advice, k=2)
    details = [random.choice(lang_details).format(theme=t_) for t_ in themes]
    closing = random.choice(lang_closing)

    header = t("horoscope.header", language, sign=sign, date=target_date.strftime('%d.%m.%Y'))
    greeting = t("horoscope.greeting", language, name=profile.name)

    lines = [
        header,
        greeting,
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
            language=profile.preferred_language,
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
        language: str = 'en',
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
                    language=language,
                )
            except Exception as e:
                logger.warning(f"LLM generation failed, falling back to template: {e}")

        return generate_horoscope_text(
            profile=profile,
            target_date=target_date,
            language=language,
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
