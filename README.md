# jazztunes - a jazz repertoire management app

Jazztunes is an app to help jazz musicians manage their repertoire. To use it, go to [jazztunes.org](https://jazztunes.org/).

This readme focuses on technical aspects of the app of interest to developers; for a user manual, see [here](https://jwjacobson.github.io/jazztunes/).

### Tech stack
Jazztunes uses [Django 5.0](https://www.djangoproject.com/) on the back end and [htmx](https://htmx.org/) on the front end with [Bootstrap](https://getbootstrap.com/) for styling. The database is [PostgreSQL](https://www.postgresql.org/). It uses [DataTables](https://datatables.net/) for column sorting. Tests are written in [pytest](https://docs.pytest.org/en/8.2.x/). It runs on Python 3.11 or later.

### Local installation
If you want to run jazztunes locally, follow the following steps:
1. Clone this repository.
2. Navigate to the 'jazztunes' directory.
3. Create a virtual environment ```python -m venv venv''' (Windows/Linux) or ```python3 -m venv venv``` (Mac).
4. Activate the virtual environment ```.\venv\Scripts\activate``` (Windows) or ```source venv/bin/activate```
5. Install the necessary packages: ```pip install -r requirements.txt```
6. Run the program: ```python manage.py runserver ```
7. Ctrl-click on ```http://127.0.0.1:8000``` — This will open jazztunes in your default browser.
8. You can close the program by closing your browser and pressing Ctrl-C in the terminal running it.

### License
Jazztunes is [free software](https://www.fsf.org/about/what-is-free-software), released under version 3.0 of the GPL. Everyone has the right to use, modify, and distribute jazztunes subject to the [stipulations](https://github.com/jwjacobson/jazztunes/blob/main/LICENSE) of that license.
