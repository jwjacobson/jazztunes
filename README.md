[![Documentation Status](https://readthedocs.org/projects/jazztunes/badge/?version=latest)](https://jazztunes.readthedocs.io/en/latest/)
# jazztunes - a jazz repertoire management app

Jazztunes is an app to help jazz musicians manage their repertoire. To use it, go to [jazztunes.org](https://jazztunes.org/).

This readme focuses on technical aspects of the app of interest to developers; for a user manual, see [here](https://jwjacobson.github.io/jazztunes/).

### Tech stack
Jazztunes uses [Django 5.0](https://www.djangoproject.com/) on the back end and [htmx](https://htmx.org/) on the front end with [Bootstrap](https://getbootstrap.com/) for styling. The database is [PostgreSQL](https://www.postgresql.org/). It uses [DataTables](https://datatables.net/) for column sorting. Tests are written in [pytest](https://docs.pytest.org/en/8.2.x/). It runs on Python 3.11 or later.

### Local installation
If you want to run jazztunes locally, take the following steps:
1. Clone this repository.
2. Navigate to the 'jazztunes' directory.
3. Create a virtual environment ```python -m venv venv''' (Windows/Linux) or ```python3 -m venv venv``` (Mac).
4. Activate the virtual environment ```.\venv\Scripts\activate``` (Windows) or ```source venv/bin/activate```
5. Install the necessary packages: ```pip install -r requirements.txt```
6. Create a .env file in the root directory with the variables (I've supplied a file, env-template, that shows what you need and has some default values)
7. If you want to use the Public tune feature, you'll need to create a superuser: ```python manage.py createsuperuser```, then set that user's ID to ADMIN_USER_ID in .env (it will be 1 if it's the first user created, otherwise 2, etc.). Then tunes you create as that user will also show up on the Public page. Creating a superuser is also a good idea because it gives you access to the [Django admin](https://docs.djangoproject.com/en/5.0/ref/contrib/admin/) interface.
8. Run the program: ```python manage.py runserver ```
9. Ctrl-click on ```http://127.0.0.1:8000``` — This will open jazztunes in your default browser.
10. You can close the program by closing your browser and pressing Ctrl-C in the terminal running it.

### License
Jazztunes is [free software](https://www.fsf.org/about/what-is-free-software), released under version 3.0 of the GPL. Everyone has the right to use, modify, and distribute jazztunes subject to the [stipulations](https://github.com/jwjacobson/jazztunes/blob/main/LICENSE) of that license.
