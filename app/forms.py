from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField, FileField, PasswordField,BooleanField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, NumberRange, Email, EqualTo


class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0)])
    image = FileField('Product Image')  # Optional file upload
    submit = SubmitField('Submit')


class SignupForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class CheckoutForm(FlaskForm):
    fullname = StringField('Full Name', validators=[DataRequired()])
    address = StringField('Complete Address', validators=[DataRequired()])
    contact = StringField('Contact Number', validators=[DataRequired()])
    payment_method = StringField('Payment Method', default='Cash on Delivery (COD)', render_kw={'readonly': True})
    confirm_order = BooleanField('I confirm this order', validators=[DataRequired()])
    submit = SubmitField('Place Order')