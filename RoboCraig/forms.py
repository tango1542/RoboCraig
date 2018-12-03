from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from RoboCraig.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):

        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken.  Please choose a different one')

    def validate_email(self, email):

        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email has already been registered.  Please choose another one')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')


#Attempting to make a form modeled on the above form
class SearchForm(FlaskForm):
    category = SelectField('Category', choices=[('ata','Antiques'),('ppa','Appliances'),('ara','Arts & Crafts'),('sna','ATV/UTV/SNO'),('pta','AutoParts'),
                                                ('ava','Aviation'),('baa','Baby and Kid Stuff'),('haa','Beauty and Health'),('bip','Bike Parts'),
                                                ('bia','Bikes'),('bpa','Boat Parts'),('boo','Boats'),('bka','Books') ,('bfa','Business') ,
                                                ('cta','Cars & Trucks') ,('ema','CDs/DVDs/VHSs') ,('moa','Cell Phones') ,('cla','Clothes & Acc') ,
                                                ('cba','Collectibles') ,('syp','Computer Parts') ,('sya','Computers') ,('ela','Electronics'),
                                                ('gra','Farm & Garden') ,('fua','Furniture') ,('foa','General') ,('hva','Heavy Equipment') ,('hsa','Household'),
                                                ('jwa','Jewelry') ,('maa','Materials') ,('mpa','Motorcycle Parts') ,('mca','Motorcycles') ,
                                                ('msa','Music Instruments') ,('pha','Photo & Video') ,('rva','RVs & Camp') ,('sga','Sporting'),
                                                ('tia','Tickets') ,('tla','Tools') ,('taa','Toys & Games') ,('tra','Trailers') ,
                                                ('vga','Video Gaming') ,('wta','Wheels & Tires')], validators=[DataRequired()])



    search_term = StringField('Search Term', validators=[DataRequired()])
    zip_code = StringField('Zip Code', validators=[DataRequired()])
    max_distance = StringField('Max Distance', validators=[DataRequired()])
    max_price = StringField('Max Price', validators=[DataRequired()])
    submit = SubmitField('Post')


# class Post(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#     content = db.Column(db.Text, nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#
#     def __repr__(self):
#         return f"Post('{self.title}', '{self.date_posted}')"
#
#
# class Searcher (db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     category = db.Column(db.String(20), nullable=False)
#     search_term = db.Column(db.String(50), nullable=False)
#     zip_code = db.Column(db.String(10), nullable=False)  #Might need this to be int, or validate to 5 digits
#     max_distance = db.Column(db.String(10), nullable=False)
#     max_price = db.Column(db.String(10), nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
