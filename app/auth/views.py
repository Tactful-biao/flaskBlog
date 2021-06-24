from flask import render_template, redirect, request, url_for, flash
from . import auth
from .forms import LoginForm, RegistrationForm
from ..models import User
from flask_login import login_user, logout_user, current_user, login_required
from .. import db
from ..email import send_email


@auth.route('/login', methods=['GET', 'POST'])
def login():
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(email=form.email.data).first()
    if user is not None and user.verify_password(form.password.data):
      login_user(user, form.remember_me.data)
      return redirect(request.args.get('next') or url_for('main.index'))
    flash('用户名或密码不正确!')
  return render_template('auth/login.html', form=form)


@auth.route('/logout')
def logout():
  logout_user()
  flash('已退出登录')
  return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
  form = RegistrationForm()
  if form.validate_on_submit():
    user = User(email=form.email.data,
                username=form.username.data,
                password=form.password.data)
    db.session.add(user)
    db.session.commit()
    token = user.generate_confirmation_token()
    send_email(user.email, '确认邮件', 'auth/email/confirm', user=user, token=token)
    flash('一封确认邮件已经发送到您的邮箱，请注意查收.')
    return redirect(url_for('main.index'))
  return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
  if current_user.confirmed:
    return redirect(url_for('main.index'))
  if current_user.confirm(token):
    db.session.commit()
    flash('已经确认账号. 谢谢！')
  else:
    flash('确认链接不正确或者超时.')
  return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
  # print(current_user.is_authenticated)
  # print(current_user.confirmed)
  # print(request.blueprint)
  # print(request.endpoint)
  if current_user.is_authenticated:
    if not current_user.confirmed and request.blueprint != 'auth' and request.endpoint != 'static':
      return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
  if current_user.is_anonymous or current_user.confirmed:
    return redirect(url_for('main.index'))

  return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
  token = current_user.generate_confirmation_token()
  send_email(current_user.email, '确认邮件', 'auth/email/confirm', user=current_user, token=token)
  flash('新的确认邮件已经发送到邮箱!')
  return redirect(url_for('main.index'))