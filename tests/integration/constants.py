from decouple import config

DOMAIN = "http://127.0.0.1:8000/"
LOGIN_SUFFIX = "accounts/login/?next=/"
LOGIN_URL = "http://127.0.0.1:8000/accounts/login/?next=/"
USERNAME = config("TEST_USERNAME")
PASSWORD = config("TEST_PASSWORD")
