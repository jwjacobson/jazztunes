[![Documentation Status](https://readthedocs.org/projects/jazztunes/badge/?version=latest)](https://jazztunes.readthedocs.io/en/latest/)
[![Python](https://img.shields.io/badge/python-3.14-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-6.0-green)](https://www.djangoproject.com/)
[![License: GPL v3](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
# jazztunes - a jazz repertoire management app

Jazztunes is a web app that helps jazz musicians manage and gain insights into their repertoires. To use it, go to [jazztunes.org](https://jazztunes.org/).

This readme focuses on technical aspects of the app of interest to developers; for a user manual, see [here](https://jazztunes.readthedocs.io/en/).

### Tech stack
Jazztunes is a full-stack web app built using [Django 5](https://www.djangoproject.com/) on the back end and [htmx](https://htmx.org/) on the front end with [Tailwind CSS](https://tailwindcss.com/) for styling. The database is [PostgreSQL](https://www.postgresql.org/). Tables are implemented with [DataTables](https://datatables.net/) for clickable column sorting. Tests are written in [pytest](https://docs.pytest.org/en/8.2.x/) and [Playwright](https://playwright.dev/python/docs/intro). The deployed version uses Python 3.14.

### Database structure
ERD coming soon!

### Local installation
Follow these instructions if you want to run jazztunes locally or develop it. Otherwise, the easiest way to use it is at [jazztunes.org](https://jazztunes.org/).

Note: these instructions assume you are using [uv](https://docs.astral.sh/uv/) for project management.
1. [Clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) this repository.
2. Navigate to the `jazztunes` directory.
3. Copy the contents of `env-template` into a file named `.env` in the project's root directory. `env-template` contains reasonable default values, but change them as needed.
4. Install dependencies: `uv sync`.
5. Set up the database: `uv run python manage.py migrate`.
6. If you want to use the Public tune feature, you'll need to create a superuser: ```uv run python manage.py createsuperuser```, then set that user's ID to ADMIN_USER_ID in `.env` (it will be 1 if it's the first user created, otherwise 2, etc.). Tunes you create as the superuser will show up on the Public page for all other users. Creating a superuser is also a good idea because it gives you access to the [Django admin](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/) interface.
7. Start the server: ```uv run python manage.py runserver```
8. Ctrl-click on ```http://127.0.0.1:8000``` — This will open jazztunes in your default browser. You can also just navigate to that address in a browser.
9. You can close the program by closing your browser and pressing `Ctrl-C` in the terminal running the server.

### Running the tests
Jazztunes includes unit tests written in [pytest](https://docs.pytest.org/en/stable/) and end-to-end tests which use [Playwright](https://playwright.dev/python/docs/intro). If you are contributing to Jazztunes, please (1) run the tests, to make sure your contributions don't break anything; and (2) write tests covering your contribution, if applicable. Or perhaps you'd just like to contribute some tests! Tests can be found in the `tests` directory at the root of the project.

Run all the tests:
```bash
uv run pytest
```

Run only the unit tests:
```bash
uv run pytest -k unit
```
Note: the `-k` option can be used to match any pattern in directory, file, or test names!

Run the tests in "headed" mode (for end-to-end tests only -- a browser will open and you can watch it go through the steps):
```bash
uv run pytest -k e2e --headed
```

See the respective docs for many more options when running tests.


### License
Jazztunes is [free software](https://www.fsf.org/about/what-is-free-software), released under version 3.0 of the GPL. Everyone has the right to use, modify, and distribute jazztunes subject to the [stipulations](https://github.com/jwjacobson/jazztunes/blob/main/LICENSE) of that license.
