from flask import render_template, url_for, flash, redirect, request, abort
from RoboCraig import app, db, bcrypt
from RoboCraig.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, SearchForm
from RoboCraig.models import User, Post, Searcher
from flask_login import login_user, current_user, logout_user, login_required
from bs4 import BeautifulSoup
import urllib.request



# @app.route("/")
# @app.route("/home")
# def home():
#     posts = Post.query.all()
#     return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created.  You are now able to log in','success')
        return redirect(url_for('home_search'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home_search'))


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')


@app.route("/post/new",methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form,legend='New Post')

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

@app.route("/post/<int:post_id>/update",methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete",methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home_search'))

@app.route("/user/<string:username>")  #user/username url as the home page will only display posts from the logged in user
def user_posts(username):

    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)

    print ("current_user: " + str(current_user))
    print ("user: " + str(user))
    print ("username: " + str(username))

    if current_user == user:
        return render_template('user_posts.html', posts=posts, user=user)
    else:
        abort(403)



#Trying to get New Craigslist Search form route

@app.route("/search/new",methods=['GET', 'POST'])
@login_required
def new_search():
    form = SearchForm()
    if form.validate_on_submit():
        searcher = Searcher(category=form.category.data, search_term=form.search_term.data,
                          zip_code=form.zip_code.data, max_distance=form.max_distance.data,
                          max_price=form.max_price.data, author=current_user)
        db.session.add(searcher)
        db.session.commit()
        flash('Your search has been created!', 'success')
        return redirect(url_for('home_search'))
    return render_template('create_search.html', form=form,legend='New Post')

#making a home route for the above for search.  Modeling it after the home route

@app.route("/")
@app.route("/home")
@login_required
def home_search():
    searches = Searcher.query.all()

    #Trying to move this to the scrapedresults page.  Can move it back if it doesn't work
    # qsearches=[]
    # for search in searches:
    #     print ("This is search")
    #     print (search)
    #     baseurl = 'https://minneapolis.craigslist.org/search/' + search.category + '?query=' + search.search_term + '&search_distance=' + search.max_distance + '&postal=' + search.zip_code + '&max_price=' + search.max_price
    #     qsearches.append(baseurl)
    #     print ("This is baseurl")
    #     print (baseurl)
    #     print (search.category)
    #     print(search.search_term)
    #     print (search.zip_code)
    #     print (search.max_distance)
    #     print(search.max_price)
    #
    # #testing the porting of the info into a URL here
    # print ("This is qsearches")
    # print (qsearches)
    # for qsearch in qsearches:
    #     print ("qsearch: " + qsearch)




    craigurl = 'https://minneapolis.craigslist.org/search/bia?query=bianchi&srchType=T&hasPic=1&search_distance=6&postal=55407&min_price=5&max_price=400'
    # baseurl = 'https://minneapolis.craigslist.org/search/?query=bianchi&search_distance=6&postal=55407&min_price=5&max_price=400'

    return render_template('home.html', searches=searches, craigurl=craigurl,)

#I need this one to according to an error
@app.route("/user/<string:username>")  #user/username url as the home page will only display posts from the logged in user
def user_searches(username):

    user = User.query.filter_by(username=username).first_or_404()
    searches = Searcher.query.filter_by(author=user)

    print ("current_user: " + str(current_user))
    print ("user: " + str(user))
    print ("username: " + str(username))

    if current_user == user:
        return render_template('user_searches.html', searches=searches, user=user)
    else:
        abort(403)

#I am adding this because I was getting a search_id error
@app.route("/search/<int:search_id>")
def search(search_id):
    search = Searcher.query.get_or_404(search_id)
    return render_template('search.html', category=search.category, search=search)

#This is meant to delete searches...copied from delete posts
@app.route("/search/<int:search_id>/delete",methods=['POST'])
@login_required
def delete_search(search_id):
    search = Searcher.query.get_or_404(search_id)
    if search.author != current_user:
        abort(403)
    db.session.delete(search)
    db.session.commit()
    flash('Your search has been deleted!', 'success')
    return redirect(url_for('home_search'))

#Trying to view an individual post
@app.route("/search/<int:search_id>/update",methods=['GET', 'POST'])
@login_required
def update_search(search_id):
    search = Searcher.query.get_or_404(search_id)
    if search.author != current_user:
        abort(403)
    form = SearchForm()
    if form.validate_on_submit():

        search.category = form.category.data
        search.search_term = form.search_term.data
        search.zip_code = form.zip_code.data
        search.max_distance = form.max_distance.data
        search.max_price = form.max_price.data
        author = current_user

        # post.title = form.title.data
        # post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('home_search', search_id=search.id))
    elif request.method == 'GET':
        form.category.data = search.category
        form.search_term.data = search.search_term
        form.zip_code.data = search.zip_code
        form.max_distance.data = search.max_distance
        form.max_price.data = search.max_price

        # form.title.data = post.title
        # form.content.data = post.content
    return render_template('create_search.html', title='Update Post', form=form, legend='Update Post')

#Attempting to do the scraper route here that will actually have the results of a correct URL scraped

@app.route("/scrapedresults")
def scrapedresults():

    # Moving the section from home_search here to try to make the url strings.  Can move back if it doesn't work

    searches = Searcher.query.all()

    qsearches = []
    for search in searches:
        print("This is search")
        print(search)
        search_term_replace = search.search_term.replace(" ","+")  #Putting this here so the search term is concatenated with +'s in the craigslist request url
        print ("This is search_term_replace")
        print (search_term_replace)

        print ("This is search.category")
        print(search.category)

        baseurl = 'https://minneapolis.craigslist.org/search/' + search.category + '?query=' + search_term_replace + '&hasPic=1&search_distance=' + search.max_distance + '&postal=' + search.zip_code + '&min_price=3&max_price=' + search.max_price
        qsearches.append(baseurl)
        print("This is baseurl")
        print(baseurl)

        print(search.search_term)
        print(search.zip_code)
        print(search.max_distance)
        print(search.max_price)

    # testing the porting of the info into a URL here
    print("This is qsearches")
    print(qsearches)
    for qsearch in qsearches:
        print("qsearch: " + qsearch)

    #finished moving qsearches here



    clist = [
        'https://minneapolis.craigslist.org/search/bia?query=Cannondale&hasPic=1&search_distance=10&postal=55407&max_price=200',
        'https://minneapolis.craigslist.org/search/bia?query=Diamondback&hasPic=1&search_distance=4&postal=55407&max_price=100']

    print ("This is clist")
    print (type(clist))
    print (clist)
    print ("This is qsearches")
    print (type(qsearches))
    print (qsearches)

    titles_list = []
    prices_list_temp = []  # needed to make a temp list because bs was finding two prices on the page
    prices_list = []
    date_posted_list = []
    images_list = []  # Testing one
    new_url_list = []

    for c in qsearches:
        print (c)
        html_page = urllib.request.urlopen(c)
        soup = BeautifulSoup(html_page, "lxml")

        for post in soup.find_all('li', "result-row"):

            for po in post.find_all("a","result-title hdrlnk"):  #titles loop, works properlly
                titles_list.append(po.text)

            for price in post.find_all('span', 'result-price'):      #price loop
                prices_list_temp.append(price.text)

            for dat in post.find_all("time","result-date"):      #price loop
                date_posted_list.append(dat.text)

            for images in post.find_all("a","result-image gallery"):      #price loop
                pic_id=images['data-ids']
                cut_id = pic_id[2:19]  # This splits the returned data into just the id of the photo to be displayed
                full_pic_url = "https://images.craigslist.org/" + cut_id + "_300x300.jpg"
                images_list.append(full_pic_url)

            for url in post.find_all("a","result-title hdrlnk"):
                url_link = (url["href"])

                new_url_list.append(url_link)

    prices_list = [i for a, i in enumerate(prices_list_temp) if
                   a % 2 == 0]  # using this to get every other price because it was duplicating by finding two prices when scraping

    gaaah = list(zip(titles_list,prices_list,date_posted_list,images_list,new_url_list))



    print ("This is gaaah, and the type is right below that")
    print (gaaah)
    print (type(gaaah))

    for item in gaaah:
        print (item)
    return render_template('scrapedresults.html', clist=clist, new_url_list=new_url_list,titles_list=titles_list,prices_list=prices_list,date_posted_list=date_posted_list,images_list=images_list, gaaah=gaaah, qsearches=qsearches)

