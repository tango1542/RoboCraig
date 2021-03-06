from RoboCraig import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    searches = db.relationship('Searcher', backref = 'author', lazy=True)       #This is noting that there is a reference to the Searcher object

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Searcher (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(20), nullable=False)
    search_term = db.Column(db.String(50), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)  #Might need this to be int, or validate to 5 digits
    max_distance = db.Column(db.String(10), nullable=False)
    max_price = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)       #This is making a reference to the user_id in the users table

    def __repr__(self):
        return f"Search('{self.category}','{self.search_term}', '{self.zip_code}','{self.max_distance}','{self.max_price}')"