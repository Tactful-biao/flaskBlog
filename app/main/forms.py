from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class NameForm(FlaskForm):
  name = StringField('请输入姓名', validators=[DataRequired()])
  submit = SubmitField('提交')


class EditProfileForm(FlaskForm):
  name = StringField('真实姓名', validators=[Length(0, 64)])
  location = StringField('位置', validators=[Length(0, 64)])
  about_me = TextAreaField('关于我')
  submit = SubmitField('提交')
