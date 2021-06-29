from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp
from ..models import Role, User
from flask_pagedown.fields import PageDownField


class EditProfileForm(FlaskForm):
  name = StringField('真实姓名', validators=[Length(0, 64)])
  location = StringField('位置', validators=[Length(0, 64)])
  about_me = TextAreaField('关于我')
  submit = SubmitField('提交')


class EditProfileAdminForm(FlaskForm):
  email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
  username = StringField('用户名', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z0-9_.]*$', 0, '用户名只能是大小写字母、数字、下划线组成')])
  confirmed = BooleanField('确认')
  role = SelectField('角色', coerce=int)
  name = StringField('真实姓名', validators=[Length(0, 64)])
  location = StringField('城市', validators=[Length(0, 64)])
  about_me = TextAreaField('关于我')
  submit = SubmitField('提交')

  def __init__(self, user, *args, **kwargs):
    super(EditProfileAdminForm, self).__init__(*args, **kwargs)
    self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
    self.user = user

  def validate_email(self, field):
    if field.data != self.user.email and User.query.filter_by(email=field.data).first():
      raise ValueError('邮箱已经注册了.')

  def validate_username(self, field):
    if field.data != self.user.username and User.query.filter_by(username=field.data).first():
      raise ValueError('用户名已经被用了.')


class PostForm(FlaskForm):
  body = PageDownField('输入你的想法', validators=[DataRequired()])
  submit = SubmitField('提交')