import logging
from datetime import date

from config import settings
from horoscope.config import TEASER_LINE_COUNT
from horoscope.translations import LANGUAGE_NAMES

logger = logging.getLogger(__name__)

HOROSCOPE_PROMPT = """You are a mystical astrologer who writes personalized daily horoscopes.

Write a personalized horoscope for the following person:
- Name: {name}
- Zodiac sign: {zodiac_sign}
- Date of birth: {date_of_birth}
- Place of birth: {place_of_birth}
- Current place of living: {place_of_living}
- Horoscope date: {target_date}

Guidelines:
- Start with a header line: "Horoscope for {zodiac_sign} — {target_date_formatted}"
- Address the person by name on the second line: "Dear {name},"
- Write 8-12 lines of horoscope content covering love, career, health, and personal growth
- End with an inspiring closing thought
- Keep the tone warm, positive, and mystical
- Use emojis throughout the text to make it more engaging (stars, zodiac symbols, hearts, sparkles, etc.)
- Do NOT use markdown formatting, just plain text with emojis
- Each section should be a separate line
- IMPORTANT: Write the entire horoscope in {language_name}"""


class LLMService:
    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.model = settings.LLM_MODEL
        self.base_url = settings.LLM_BASE_URL or None
        self.timeout = settings.LLM_TIMEOUT

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    def generate_horoscope_text(
        self,
        zodiac_sign: str,
        name: str,
        date_of_birth: date,
        place_of_birth: str,
        place_of_living: str,
        target_date: date,
        language: str = 'en',
    ) -> tuple[str, str]:
        import litellm

        language_name = LANGUAGE_NAMES.get(language, 'English')

        prompt = HOROSCOPE_PROMPT.format(
            name=name,
            zodiac_sign=zodiac_sign,
            date_of_birth=date_of_birth.strftime('%B %d, %Y'),
            place_of_birth=place_of_birth,
            place_of_living=place_of_living,
            target_date=target_date.isoformat(),
            target_date_formatted=target_date.strftime('%B %d, %Y'),
            language_name=language_name,
        )

        response = litellm.completion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            api_key=self.api_key,
            api_base=self.base_url,
            timeout=self.timeout,
            max_tokens=1000,
        )

        full_text = response.choices[0].message.content.strip()

        lines = full_text.split("\n")
        teaser_lines = lines[:TEASER_LINE_COUNT]
        teaser_text = "\n".join(teaser_lines) + "\n\n..."

        logger.info(f"Generated LLM horoscope for {name} ({zodiac_sign}) on {target_date} in {language_name}")
        return full_text, teaser_text
