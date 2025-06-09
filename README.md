[![Documentation Status](https://readthedocs.org/projects/jazztunes/badge/?version=latest)](https://jazztunes.readthedocs.io/en/latest/)
# jazztunes - a jazz repertoire management app

Jazztunes is a web app that helps jazz musicians manage their repertoire. To use it, go to [jazztunes.org](https://jazztunes.org/).

This readme focuses on technical aspects of the app of interest to developers; for a user manual, see [here](https://jwjacobson.github.io/jazztunes/).

### Tech stack
Jazztunes is a full-stack web app built using [Django 5.2](https://www.djangoproject.com/) on the back end and [htmx](https://htmx.org/) on the front end with [Tailwind CSS](https://tailwindcss.com/) for styling. The database is [PostgreSQL](https://www.postgresql.org/). Tables are implemented with [DataTables](https://datatables.net/) for clickable column sorting. Tests are written in [pytest](https://docs.pytest.org/en/8.2.x/). The deployed version uses Python 3.13, but it should work on Python 3.11 or later.

### Database structure
ERD coming soon!

### Local installation
Follow these instructions if you want to run jazztunes locally or develop it. Otherwise, the easiest way to use it is at [jazztunes.org](https://jazztunes.org/).

Note: these instructions assume you are using [uv](https://docs.astral.sh/uv/) for project management.
1. [Clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) this repository.
2. Navigate to the `jazztunes` directory.
3. Copy the contents of `env-template` into a file named `.env` in the project's root directory. `env-template` contains reasonable default values, but change them as needed.
4. Run `uv sync` to synchronize the project dependencies with your environment.
5. Run `uv run python manage.py migrate` to set up the database.
6. If you want to use the Public tune feature, you'll need to create a superuser: ```uv run python manage.py createsuperuser```, then set that user's ID to ADMIN_USER_ID in .env (it will be 1 if it's the first user created, otherwise 2, etc.). Tunes you create as that user will also show up on the Public page for all other users. Creating a superuser is also a good idea because it gives you access to the [Django admin](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/) interface.
8. Start the server: ```uv run python manage.py runserver ```
9. Ctrl-click on ```http://127.0.0.1:8000``` — This will open jazztunes in your default browser. You can also just navigate to that address in a browser.
10. You can close the program by closing your browser and pressing Ctrl-C in the terminal running the server.

### License
Jazztunes is [free software](https://www.fsf.org/about/what-is-free-software), released under version 3.0 of the GPL. Everyone has the right to use, modify, and distribute jazztunes subject to the [stipulations](https://github.com/jwjacobson/jazztunes/blob/main/LICENSE) of that license.
