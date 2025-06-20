from decouple import config

USERNAME = config("TEST_USERNAME")
PASSWORD = config("TEST_PASSWORD")
OFFSET = config("LAST_PLAYED_OFFSET")
HEADLESS = False
