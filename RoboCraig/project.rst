Project Summary
===============

Project Outline
---------------

Craiglist is a good free posting site.  However, sorting through results, remembering to serach, and re-entering search details can be tedious.

I wanted to make an app where you could automatically save those searches, and it would search those results for you.



Creating the app
----------------
This app was relatively straightforward.  I took the foundation from our previous Flask app of the Encylopedia, and integrated it with how I wanted to use it with RoboCraig.

I used two models...Users, and Searches.  The Searches DB would be a foreign key in the Users table, so you would be able to identify the searches by the User ID.

I used Flask WTF Forms for most of the input forms, as well as for validation of any user input.

Instead of saving actual scraped Craigslist results, I simply saved the searches.  The Craigslist results would constantly be updating.  But if the search parameters were saved, it would just redo a search of those saved items.

It was a little tricky to accomplish the user specific views.  For those routes, I would use the login_required decorator, and the User ID woudl be appended to the end of the URL.

For the scraped_results route, the user's saved search would build out a Craigslist URL.  Then the Beautiful Soup Module would scrape that information from the Craigslist page that is returned.  The specific items that Beautiful Soup would be looking for were put into lists.  Then, those multiple lists with all of the scraped data are zipped together to create one specific returned item.
