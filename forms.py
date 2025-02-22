from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField

class ContacForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    message = CKEditorField("Message", validators=[DataRequired()])

    submit = SubmitField("Send")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])

    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])

    submit = SubmitField("Register")


class ClienDataForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    country = StringField("Country", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    phone_number = StringField("Phone", validators=[DataRequired()])

    submit = SubmitField("Go to payment")

class AddArticle(FlaskForm):
    name = StringField("Name of article", validators=[DataRequired()])
    price = StringField("Price of article", validators=[DataRequired()])
    category = StringField("Article category", validators=[DataRequired()])
    img_url = StringField("Image URL", validators=[DataRequired()])
    article_description = CKEditorField("Article description", validators=[DataRequired()])

    submit = SubmitField("Add")

class ClientMessage(FlaskForm):
    title = StringField("Enter a title", validators=[DataRequired()])
    message = CKEditorField("Type your message", validators=[DataRequired()])

    submit = SubmitField("Send")
