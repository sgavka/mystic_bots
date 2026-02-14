from datetime import date

import pytest

from horoscope.utils import get_zodiac_sign


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
