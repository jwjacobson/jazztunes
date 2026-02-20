from enum import IntEnum

from decouple import config

# auth
USERNAME = config("TEST_USERNAME", default="bagel")
PASSWORD = config("TEST_PASSWORD", default="secure_pwd")

# tune
SINGLE_TUNE_TITLE = "Yesterday's Tomorrows"
SINGLE_TUNE_COMPOSER = "Belderbos"
SINGLE_TUNE_KEY = "C"
SINGLE_TUNE_OTHER_KEYS = "F D-"
SINGLE_TUNE_FORM = "AABA"
SINGLE_TUNE_STYLE = "standard"
SINGLE_TUNE_METER = 4
SINGLE_TUNE_YEAR = "2024"
SINGLE_TUNE_TAGS = None
SINGLE_TUNE_KNOWLEDGE = "learning"
DATE_DISPLAY_FORMAT = "%B %-d"

class HomeColumns(IntEnum):
    TITLE = 0
    COMPOSER = 1
    KEY = 2
    OTHER_KEYS = 3
    FORM = 4
    STYLE = 5
    METER = 6
    YEAR = 7
    TAGS = 8
    KNOWLEDGE = 9
    PLAYS = 10
    LAST_PLAYED = 11
    ACTIONS = 12