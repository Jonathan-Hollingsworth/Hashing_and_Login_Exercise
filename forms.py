from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, TextAreaField
from wtforms.validators import InputRequired, Length

class UserRegisterForm(FlaskForm):
    "Form template for registering as a user"

    username = StringField("Username", validators=[InputRequired("You must include a username"), Length(max=20, message="Username exceeds 20 character limit")])

    password = PasswordField("Password", validators=[InputRequired("You must include a password")])

    email = EmailField("Email", validators=[Length(max=50, message="Email exceeds 50 character limit"), InputRequired("You must include an email")])

    first_name = StringField("First Name", validators=[InputRequired("Please input your first name"), Length(max=30, message="Your first name exceeds the 30 character limit")])

    last_name = StringField("Last Name", validators=[InputRequired("Please input your last name"), Length(max=30, message="Your last name exceeds the 30 character limit")])

class UserLoginForm(FlaskForm):
    "Form template for logging in as a user"

    username = StringField("Username", validators=[InputRequired("You must include a username")])

    password = PasswordField("Password", validators=[InputRequired("You must include a password")])

class FeedbackForm(FlaskForm):
    "Form structure for creating/editing a piece of feedback"

    title = StringField("Title", validators=[InputRequired("You must include a title"), Length(max=100, message="Title exceeds the 100 character limit")])

    content = TextAreaField("Content", [InputRequired("Please add content to your feedback")])