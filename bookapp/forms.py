from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, FloatField
from wtforms.validators import Email, DataRequired, EqualTo, Length

class RegForm(FlaskForm):
   fullname = StringField("Firstname",validators=[DataRequired(message="The firstname is a must")])
   email = StringField("Email",validators=[Email(message="Invalid Email Format"),DataRequired(message="Email must be supplied"),Length(min=5,message="Email is too short")])
   pwd = PasswordField("Enter Password",validators=[DataRequired()])
   confpwd = PasswordField("Confirm Password",validators=[EqualTo('pwd',message="let the two password match")])
   btnsubmit = SubmitField("Register!")

class DpForm(FlaskForm):
   dp = FileField("Upload a Profile Picture",validators=[FileRequired(),FileAllowed(['jpg','png','jpeg'])])
   btnupload = SubmitField("Upload Picture")

class ProfileForm(FlaskForm):
   fullname = StringField("Fullname",validators=[DataRequired(message="The fullname is a must")])
   btnsubmit = SubmitField("Upload Profile!")

class ContactForm(FlaskForm):
  email = StringField("Email",validators=[Email(message="Invalid Email Format"),DataRequired(message="Email must be supplied"),Length(min=5,message="Email is too short")])
  btnsubmit = SubmitField("Submit Form")


class DonForm(FlaskForm):
  fullname = StringField("Fullname",validators=[DataRequired(message="The fullname is a must")])
  email = StringField("Email",validators=[Email(message="Invalid Email Format"),DataRequired(message="Email must be supplied"),Length(min=5,message="Email is too short")])
  amt = FloatField("Specify Amount",validators=[DataRequired()])
  btnsubmit = SubmitField("Submit")
