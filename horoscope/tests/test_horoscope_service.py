from datetime import date

import pytest

from horoscope.utils import get_zodiac_sign
from horoscope.services.horoscope import generate_horoscope_text
from horoscope.config import TEASER_LINE_COUNT
from horoscope.entities import UserProfileEntity


class TestGetZodiacSign:
    @pytest.mark.parametrize("dob,expected", [
        (date(1990, 1, 1), "Capricorn"),
        (date(1990, 1, 19), "Capricorn"),
        (date(1990, 1, 20), "Aquarius"),
        (date(1990, 2, 18), "Aquarius"),
        (date(1990, 2, 19), "Pisces"),
        (date(1990, 3, 20), "Pisces"),
        (date(1990, 3, 21), "Aries"),
        (date(1990, 4, 19), "Aries"),
        (date(1990, 4, 20), "Taurus"),
        (date(1990, 5, 20), "Taurus"),
        (date(1990, 5, 21), "Gemini"),
        (date(1990, 6, 20), "Gemini"),
        (date(1990, 6, 21), "Cancer"),
        (date(1990, 7, 22), "Cancer"),
        (date(1990, 7, 23), "Leo"),
        (date(1990, 8, 22), "Leo"),
        (date(1990, 8, 23), "Virgo"),
        (date(1990, 9, 22), "Virgo"),
        (date(1990, 9, 23), "Libra"),
        (date(1990, 10, 22), "Libra"),
        (date(1990, 10, 23), "Scorpio"),
        (date(1990, 11, 21), "Scorpio"),
        (date(1990, 11, 22), "Sagittarius"),
        (date(1990, 12, 21), "Sagittarius"),
        (date(1990, 12, 22), "Capricorn"),
        (date(1990, 12, 31), "Capricorn"),
    ])
    def test_zodiac_sign(self, dob: date, expected: str):
        assert get_zodiac_sign(dob) == expected

    def test_zodiac_sign_boundary_jan_20(self):
        assert get_zodiac_sign(date(2000, 1, 20)) == "Aquarius"
        assert get_zodiac_sign(date(2000, 1, 19)) == "Capricorn"

    def test_zodiac_sign_boundary_dec_22(self):
        assert get_zodiac_sign(date(2000, 12, 22)) == "Capricorn"
        assert get_zodiac_sign(date(2000, 12, 21)) == "Sagittarius"


class TestGenerateHoroscopeText:
    def _make_profile(self, telegram_uid: int = 12345) -> UserProfileEntity:
        from datetime import datetime
        return UserProfileEntity(
            user_telegram_uid=telegram_uid,
            name="Test User",
            date_of_birth=date(1990, 5, 15),
            place_of_birth="London",
            place_of_living="Berlin",
            preferred_language="en",
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1),
        )

    def test_deterministic_output(self):
        profile = self._make_profile()
        target = date(2024, 6, 15)

        text1, teaser1 = generate_horoscope_text(profile=profile, target_date=target)
        text2, teaser2 = generate_horoscope_text(profile=profile, target_date=target)

        assert text1 == text2
        assert teaser1 == teaser2

    def test_different_dates_produce_different_output(self):
        profile = self._make_profile()

        text1, _ = generate_horoscope_text(profile=profile, target_date=date(2024, 6, 15))
        text2, _ = generate_horoscope_text(profile=profile, target_date=date(2024, 6, 16))

        assert text1 != text2

    def test_different_users_produce_different_output(self):
        target = date(2024, 6, 15)

        text1, _ = generate_horoscope_text(
            profile=self._make_profile(telegram_uid=111),
            target_date=target,
        )
        text2, _ = generate_horoscope_text(
            profile=self._make_profile(telegram_uid=222),
            target_date=target,
        )

        assert text1 != text2

    def test_teaser_is_shorter_than_full_text(self):
        profile = self._make_profile()
        full_text, teaser_text = generate_horoscope_text(
            profile=profile,
            target_date=date(2024, 6, 15),
        )

        assert len(teaser_text) < len(full_text)

    def test_teaser_line_count(self):
        profile = self._make_profile()
        _, teaser_text = generate_horoscope_text(
            profile=profile,
            target_date=date(2024, 6, 15),
        )

        # Teaser is first N lines + "\n\n..."
        teaser_lines = teaser_text.split("\n")
        # Remove trailing "..." and empty line
        content_lines = [line for line in teaser_lines if line != "..."]
        # First TEASER_LINE_COUNT lines + blank line + "..."
        assert len(content_lines) <= TEASER_LINE_COUNT + 1

    def test_full_text_contains_zodiac_sign(self):
        profile = self._make_profile()
        full_text, _ = generate_horoscope_text(
            profile=profile,
            target_date=date(2024, 6, 15),
        )

        assert "Taurus" in full_text  # May 15 = Taurus

    def test_full_text_contains_user_name(self):
        profile = self._make_profile()
        full_text, _ = generate_horoscope_text(
            profile=profile,
            target_date=date(2024, 6, 15),
        )

        assert "Test User" in full_text

    def test_russian_language_output(self):
        profile = self._make_profile()
        full_text, _ = generate_horoscope_text(
            profile=profile,
            target_date=date(2024, 6, 15),
            language="ru",
        )

        assert "Гороскоп" in full_text
        assert "Test User" in full_text

    def test_ukrainian_language_output(self):
        profile = self._make_profile()
        full_text, _ = generate_horoscope_text(
            profile=profile,
            target_date=date(2024, 6, 15),
            language="uk",
        )

        assert "Гороскоп" in full_text

    def test_german_language_output(self):
        profile = self._make_profile()
        full_text, _ = generate_horoscope_text(
            profile=profile,
            target_date=date(2024, 6, 15),
            language="de",
        )

        assert "Horoskop" in full_text
