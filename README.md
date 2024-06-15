# jazztunes - a jazz repertoire management app

### Why build this app?
An important part of learning to play jazz is memorizing tunes, usually taken from the canon of [jazz](https://en.wikipedia.org/wiki/List_of_jazz_standards) and [popular](https://en.wikipedia.org/wiki/Great_American_Songbook) standard songs.
These can number less than 10 for the beginning student, up to 100 or more for more advanced students, to hundreds or even over a thousand for professionals. Shared knowledge of a common set of tunes allows jazz musicians to successfully make music together with little to no preparation and is a distinctive feature of the artform.

My own experience learning to play jazz has included a fair amount of frustration in trying to grow my repertoire. Tunes have to be regularly integrated into practice so that they enter long-term memory. This isn't difficult when one only knows a few tunes, but as my own repertoire approached the 100-tune threshold, I had difficulty keeping them all straight, and it often felt that for every new tune I learned, another one would slip out of the rotation and be forgotten, necessitating tiresome relearning. I have talked to enough other players to know that this issue is not unique to me; it is a general problem for jazz musicians, at least at the student and amateur level.

Jazztunes helps to solve this problem by allowing you keep track of all the tunes you know, search and sort them by various criteria, and, crucially, see when you last played a tune, so you know which ones you need to revisit.

### How to use jazztunes
Jazztunes is a web app; if you'd like to use it, go to [jazztunes.org](https://jazztunes.org/) and create an account! It is and always will be free. If you'd prefer to run jazztunes locally for any reason, you can find instructions further down. Here I'll focus on the different sections of the app.

#### Home
This page displays your repertoire. You can use the search box up top to filter results You can also click the header of any column to sort by that column, and shift-click to sort by multiple columns. The Actions column on the far right has buttons to "play" (mark a tune's "last played" field with today's date), edit, or delete a tune. Be careful with delete; there's no way to get a deleted tune back!

If you're in another part of the app and want to get to the home page, just click "jazztunes" on the left side of the navbar.

#### Create
This is the form for adding a new tune to your repertoire. The only thing you're required to put is a title; everything else can be left blank at your discretion.

#### Play
This page will help you if you're not sure what tune you want to play. It selects a random tune matching your search criteria, which you can choose to play or reject. If you reject the offered tune, you'll be offered another until there are no more that match the criteria. Doing a blank search will return your entire repertoire.

#### Public
This page consists of precreated "public" tunes that you can copy into your repertoire by clicking the Take button. Right now it has 200 tunes but I hope to make it more comprehensive eventually. Let me know if you find any mistakes!

#### Searching tunes
The Home, Play, and Public pages all have a search box. Terms are searched across all fields. It uses AND logic if you put in more than one term. For example, if you search ```monk``` you'll get all your Monk tunes, but if you search ```monk bud``` you'll only get "In Walked Bud" (if it's in your repertoire). Searches are not case sensitive.

Out of respect, all the jazz composers are indexed by last name, but there's also nickname substitution working behind the scenes. This means, for example, that Miles Davis is listed as "Davis" in the Composer column, but if you search ```miles``` you will still get all his tunes. Other "nicknamed" jazz composers include Duke Ellington ("duke"), Bud Powell ("bud"), Charlie Parker ("bird"), etc., covering at least everyone in the Public database with a standard nickname. Let me know if I've missed any.

The "Haven't played in" dropdown on the Home and Play pages lets you filter by how recently you've played tunes. So if you select "a day," you'll get back all the tunes you haven't played in the last day (which should be most of your repertoire). The more you keep your plays updated, the more useful this feature is.

You can exclude a term from your search by using a minus sign just before the term. So the search ```-blues``` will exclude tunes  containing "blues" in any field from your search.

You can now search specific fields using the format ```field:term```. This is especially useful when searching for keys and forms. Currently supported fields are title, composer, key (just the "Key" column, the tune's main key), *keys* (both "Key" and "Other Keys"), form, style, meter, and year. Most fields have relatively exclusive content types, which means you can do a lot with just basic search (e.g., if you search "love," that term will only be relevant to the Title field.) Keys are more difficult, since they have a lot of overlap with other fields. Before, if you searched "Ab" for the key Ab, you would also get any titles or composers containing "ab" as well as most of the standard song forms (AABA etc.) Now you can just search for the key or keys.

### App focus, or what this app is *not*
Inspired by the Unix philosophy of "do one thing and do it well", the focus of this app is repertoire management. It is not a general practice app, and it is not a tune *learning* app. There are plenty of other apps and resources that fulfill those functions. The app assumes the user has access to the materials they need to learn a tune (recordings, sheet music, etc.) outside of the app itself. What the app offers is easy and intuitive access to all tunes known by the user based on any desired criteria.

### Tech stack
Jazztunes uses [Django](https://www.djangoproject.com/) on the back end and [htmx](https://htmx.org/) on the front end with [Bootstrap](https://getbootstrap.com/) for styling. The database is [PostgreSQL](https://www.postgresql.org/). It uses [DataTables](https://datatables.net/) for column sorting.

### Local installation
If you want to run jazztunes locally, you'll need at least Python 3.11. Follow the following steps:
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
