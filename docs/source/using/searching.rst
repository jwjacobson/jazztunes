.. _searching:

Searching your repertoire
=========================

The **Home**, **Play**, and **Browse** pages all contain a search box with robust functionality.

Basic search
----------------

By default, every field is searched for your search term. If you enter multiple terms, the search uses AND logic to combine them. For example, if you search ``monk`` you will see all tunes with monk in any fields (usually composer). If you search ``monk bud``, you will only see "In Walked Bud," since that is the only tune that contains both terms.

Jazz composer names have built-in substitutions using their nicknames or first names, so searching ``miles`` will return Miles Davis tunes, ``bird`` will return Charlie Parker tunes, etc. Note that in a default search, the nickname term will also searched in other fields, so ``bird`` will also return the tune "Bye Bye Blackbird." If you want **only** tunes composed by Charlie Parker, use a field-specific search (see below).  

The default search is often sufficient, since the contents of the fields tend to be specific to that field: the search term ``love`` probably only refers to the contents of the Title field, ``Golson`` to the composer field, etc. However, some terms and fields are trickier. If you want to search for the key of Ab using the default search, your query ``Ab`` will also pick up any song forms containing the sequence AB, which is almost all of them. For such cases you can use field-specific search.

Field-specific search
----------------------
You can use the format ``field:term`` to search a specific field. Currently supported fields are **title**, **composer**, **key** (the Key column, i.e., a tune's main key), **keys** (both the Key and Other Keys columns), **form**, **style**, **meter**, **year**, and **tags**.

Term exclusion
---------------
Use a ``-`` before a term to exclude it from the search results. This can also be used on a field-specific search: for example, ``-meter:4`` will return all tunes not in 4.

Timespan filtering: Haven't Played In
--------------------------------------
The **haven't played in** dropdown lets you filter by how long it's been since you've played a tune. This allows you to easily target tunes at the highest risk of being forgotten.

.. note:: Timespan filtering is one of the most useful parts of the app!
