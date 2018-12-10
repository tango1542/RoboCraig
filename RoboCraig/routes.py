from flask import render_template, url_for, flash, redirect, request, abort
from RoboCraig import app, db, bcrypt
from RoboCraig.forms import RegistrationForm, LoginForm, UpdateAccountForm,SearchForm
from RoboCraig.models import User,Searcher
from flask_login import login_user, current_user, logout_user, login_required
from bs4 import BeautifulSoup
import urllib.request


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:    #If the user is authenticted, they will be redirected to their saved searches
        return redirect(url_for('user_searches'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')     #This is creating the hashed password using bcryp
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)      #Creating the user object from the form data
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created.  You are now able to log in','success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)       #uses login_user method to login user
            # next_page = request.args.get('next')
            # return redirect(next_page) if next_page else redirect(url_for('user_searches',username=user.username))
            return redirect(url_for('user_searches',username=user.username))        #if they are properly logged in, they are sent to the saved searches route
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')      #if login is unsuccessful, they are sent back to the login
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()    #using the flask login module to logout
    return redirect(url_for('landing'))


@app.route("/account", methods=['GET','POST'])
@login_required
def account():
    form=UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Account',username=current_user.username, form=form)


@app.route("/users/<string:username>")  #This is the main home route for a logged in user.  It will display their saved searches
def user_searches(username):
    # Dictionary is to display the actual search category name instead of the 3 letter code that goes in a Craigslist URL
    choices = {'ata': 'Antiques', 'ppa': 'Appliances', 'ara': 'Arts & Crafts', 'sna': 'ATV/UTV/SNO', 'pta': 'AutoParts',
               'ava': 'Aviation',
               'baa': 'Baby and Kid Stuff', 'haa': 'Beauty and Health', 'bip': 'Bike Parts',
               'bia': 'Bikes', 'bpa': 'Boat Parts', 'boo': 'Boats', 'bka': 'Books', 'bfa': 'Business',
               'cta': 'Cars & Trucks', 'ema': 'CDs/DVDs/VHSs', 'moa': 'Cell Phones', 'cla': 'Clothes & Acc',
               'cba': 'Collectibles', 'syp': 'Computer Parts', 'sya': 'Computers', 'ela': 'Electronics',
               'gra': 'Farm & Garden', 'fua': 'Furniture', 'foa': 'General', 'hva': 'Heavy Equipment',
               'hsa': 'Household',
               'jwa': 'Jewelry', 'maa': 'Materials', 'mpa': 'Motorcycle Parts', 'mca': 'Motorcycles',
               'msa': 'Music Instruments', 'pha': 'Photo & Video', 'rva': 'RVs & Camp', 'sga': 'Sporting',
               'tia': 'Tickets', 'tla': 'Tools', 'taa': 'Toys & Games', 'tra': 'Trailers',
               'vga': 'Video Gaming', 'wta': 'Wheels & Tires'}
    user = User.query.filter_by(username=username).first_or_404()  #giving the function the username attribute returns the username of the current_user
    searches = Searcher.query.filter_by(author=user)   #Using this username, it retrieves a list of their Searcher objects
    if current_user == user:        #Will only render the template if the user is logged in.  Otherwise, they receive a 403
        return render_template('user_searches.html', searches=searches, user=user, username=username,choices=choices)
    else:
        abort(403)


@app.route("/search/new",methods=['GET', 'POST'])       #This route is for creating a new_search
@login_required
def new_search():
    form = SearchForm()     #creating a new SearchForm object
    if form.validate_on_submit():       #From Flask-WTF forms, validate_on_submit will validate the form
        searcher = Searcher(category=form.category.data, search_term=form.search_term.data,     #If the form is valid, it is put into the database and committed
                          zip_code=form.zip_code.data, max_distance=form.max_distance.data,
                          max_price=form.max_price.data, author=current_user)
        db.session.add(searcher)
        db.session.commit()
        flash('Your search has been created!', 'success')
        return redirect(url_for('user_searches', username=current_user.username))
    return render_template('create_search.html', form=form,legend='New Post',username=current_user.username)  #If the form is not valid, the user stays on the create_serach page


@app.route("/")     #This is the route for the non-logged in user.
def landing():
    if current_user.is_authenticated:       #A logged in user would be redirected to their home_search route
        return redirect(url_for('user_searches',username=current_user.username))
    else:       #An unauthenticated user would get to the main greeting page
        return render_template('landing.html')


@app.route("/home")         #This route displays all saved searches from all users.  It is currently active, but will become inactive for the live project
         #Regardless, only a logged in user can view this page
def home_search():
    searches = Searcher.query.all()         #Does a query for all Searcher objects
    return render_template('home.html', searches=searches)


#This is needed to get the search
@app.route("/search/<int:search_id>")
def search(search_id):
    search = Searcher.query.get_or_404(search_id)
    return render_template('search.html', category=search.category, search=search)


@app.route("/search/<int:search_id>/delete",methods=['POST'])
@login_required
def delete_search(search_id):       #The delete search route takes the search id for the search and deletes that object
    search = Searcher.query.get_or_404(search_id)
    if search.author != current_user:
        abort(403)
    db.session.delete(search)
    db.session.commit()
    flash('Your search has been deleted!', 'success')
    return redirect(url_for('user_searches', username=current_user.username))


@app.route("/search/<int:search_id>/update",methods=['GET', 'POST'])    #This route is for updating the search
@login_required
def update_search(search_id):       #After being passed the search_id, this function updates a saved search
    search = Searcher.query.get_or_404(search_id)
    if search.author != current_user:
        abort(403)
    form = SearchForm()
    if form.validate_on_submit():

        search.category = form.category.data        #If the update form is validated, the search_term will be updated
        search.search_term = form.search_term.data
        search.zip_code = form.zip_code.data
        search.max_distance = form.max_distance.data
        search.max_price = form.max_price.data
        author = current_user


        db.session.commit()     #The updated search is committed to the database
        flash('Your post has been updated!', 'success')
        return redirect(url_for('user_searches', search_id=search.id,username=current_user.username))    #They then get sent back to the saved_searches
    elif request.method == 'GET':       #If the page is requested, it will pre-populate the form data
        form.category.data = search.category
        form.search_term.data = search.search_term
        form.zip_code.data = search.zip_code
        form.max_distance.data = search.max_distance
        form.max_price.data = search.max_price

    return render_template('create_search.html', title='Update Post', form=form, legend='Update Post')


@app.route("/search_results/<string:username>")     #This route takes constructs the URL(s), and parses them using Beautiful Soup
def scrapedresults(username):

    user = User.query.filter_by(username=username).first_or_404()       #This gets the current user from the db
    searches = Searcher.query.filter_by(author=user)        #This gets all of the current users saved searchs from the db

    search_term_rep_list = []       #Can maybe delete

    catz=[]
    constructed_urls = []       #This will be the list where completed URLs are contained
    for search in searches:
        print("This is search: " + str(search))
        search_term_replace = search.search_term.replace(" ","+")  #Putting this here so the search term is concatenated with +'s in the craigslist request url
        print ("This is search_term_replace: " + str(search_term_replace))
        search_term_rep_list.append(search_term_replace)    #Putting the formatted search terms into the list
        print ("This is search.category: " + str(search.category))

        #This is the URL request to Craigslist which contain variable names
        baseurl = 'https://minneapolis.craigslist.org/search/' + search.category + '?query=' + search_term_replace + '&srchType=T&hasPic=1&search_distance=' + search.max_distance + '&postal=' + search.zip_code + '&min_price=3&max_price=' + search.max_price
        constructed_urls.append(baseurl)        #Putting the completed urls into the contructed_urls list
        print("This is baseurl: " + baseurl)

        print("search.search_term" + str(search.search_term) + " search.zip_code: " + str(search.zip_code) + " search.max_distance: " + str(search.max_distance) + " search.max_price: " + str(search.max_price))

    print("This is constructed_urls list: ")
    for url in constructed_urls:
        print("url: " + url)

    print ("This is constructed_urls")
    print (constructed_urls)

    #Making lists of the five items that need to be zipped together to create a list of lists
    titles_list = []
    prices_list_temp = []  # needed to make a temp list because bs was finding two prices on the page
    date_posted_list = []
    images_list = []
    new_url_list = []
    term_list = []     #This list will be able to pass the name of the search to the saved search

    for url in constructed_urls:        #for each url in the saved_searches, Beautiful Soup will take it and scrape the HTML
        print ("This is url")
        print (url)
        html_page = urllib.request.urlopen(url)
        soup = BeautifulSoup(html_page, "lxml")
        term = soup.find("input",{'name':'query'})['value']     #Getting the input box from BS4 to be able to get the name of the search
        print ("This is term: " + term)

        for post in soup.find_all('li', "result-row"):
            term_list.append(term)

            # query.flatinput.ui - autocomplete - input.ui - autocomplete - loading

            for po in post.find_all("a","result-title hdrlnk"):  #titles loop, works properly
                titles_list.append(po.text)

            for price in post.find_all('span', 'result-price'):      #price loop
                prices_list_temp.append(price.text)

            for dat in post.find_all("time","result-date"):      #date posted loop
                date_posted_list.append(dat.text)

            for images in post.find_all("a","result-image gallery"):      #image id loop
                pic_id=images['data-ids']
                cut_id = pic_id[2:19]  # This splits the returned data into just the id of the photo to be displayed
                full_pic_url = "https://images.craigslist.org/" + cut_id + "_300x300.jpg"   #This is the full url for the image
                images_list.append(full_pic_url)

            for url in post.find_all("a","result-title hdrlnk"):        #anchor link
                url_link = (url["href"])
                new_url_list.append(url_link)

    print ("This is term_list")
    print (term_list)
    prices_list = [i for a, i in enumerate(prices_list_temp) if a % 2 == 0]  # using this to get every other price because it was duplicating by finding two prices when scraping

    #This is the list of lists being zipped together to create saved_searches
    zipped_searches = list(zip(titles_list,prices_list,date_posted_list,images_list,new_url_list,term_list))

    for item in zipped_searches:
        print (item)

    if current_user == user:
        return render_template('search_results.html',zipped_searches=zipped_searches,username=username)     #Directed to search_results page, passing on the zipped_searches
    else:
        abort (403)

