from flask import render_template, session, redirect, url_for, abort, flash, request, current_app, make_response
from datetime import datetime

from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm
from .. import db
from ..models import User, Role, Permission, Post
from flask_login import login_required, current_user
from ..decorators import admin_required, permission_required


@main.route('/', methods=['GET', 'POST'])
def index():
  form = PostForm()
  if current_user.can(Permission.WRITE) and form.validate_on_submit():
    post = Post(body=form.body.data, author=current_user._get_current_object())
    db.session.add(post)
    return redirect(url_for('.index'))
  show_followed = False
  if current_user.is_authenticated:
    show_followed = bool(request.cookies.get('show_followed', ''))
  if show_followed:
    query = current_user.followed_posts
  else:
    query = Post.query
  page = request.args.get('page', 1, type=int)
  pagination = query.order_by(Post.timestamp.desc()).paginate(page,
               per_page=current_app.config['FLASK_POSTS_PER_PAGE'], error_out=False)
  posts = pagination.items
  return render_template("index.html", form=form, posts=posts, pagination=pagination)


@main.route('/user/<username>')
def user(username):
  user = User.query.filter_by(username=username).first()
  if user is None:
    abort(404)
  page = request.args.get('page', 1, type=int)
  pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
    page, per_page=current_app.config['FLASK_POSTS_PER_PAGE'], error_out=False)
  posts = pagination.items
  return render_template('user.html', user=user, posts=posts, pagination=pagination)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
  form = EditProfileForm()
  if form.validate_on_submit():
    current_user.name = form.name.data
    current_user.location = form.location.data
    current_user.about_me = form.about_me.data
    db.session.add(current_user)
    flash('你的信息已更新!')
    return redirect(url_for('.user', username=current_user.username))
  form.name.data = current_user.name
  form.location.data = current_user.location
  form.about_me.data = current_user.about_me
  return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
  user = User.query.get_or_404(id)
  form = EditProfileAdminForm(user=user)
  if form.validate_on_submit():
    user.email = form.email.data
    user.username = form.username.data
    user.confirmed = form.confirmed.data
    user.role = Role.query.get(form.role.data)
    user.name = form.name.data
    user.location = form.location.data
    user.about_me = form.about_me.data
    db.session.add(user)
    db.session.commit()
    flash('信息已经更新')
    return redirect(url_for('.user', username=user.username))
  form.email.data = user.email
  form.username.data = user.username
  form.confirmed.data = user.confirmed
  form.role.data = user.role_id
  form.name.data = user.name
  form.location.data = user.location
  form.about_me.data = user.about_me
  return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<int:id>')
def post(id):
  post = Post.query.get_or_404(id)
  return render_template('post.html', posts=[post])


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
  post = Post.query.get_or_404(id)
  if current_user != post.author and not current_user.can(Permission.ADMIN):
    abort(403)
  form = PostForm()
  if form.validate_on_submit():
    post.body = form.body.data
    db.session.add(post)
    flash('文章已经更新.')
    return redirect(url_for('.post', id=post.id))
  form.body.data = post.body
  return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
  user = User.query.filter_by(username=username).first()
  if user is None:
    flash('非法用户', 'danger')
    return redirect(url_for('.index'))
  if current_user.is_following(user):
    flash('你已经关注了该用户', 'warning')
    return redirect(url_for('.user', username=username))
  current_user.follow(user)
  flash('你正在关注 %s' % username, 'success')
  return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
  user = User.query.filter_by(username=username).first()
  if user is None:
    flash('非法用户', 'danger')
    return redirect(url_for('.index'))
  if not current_user.is_following(user):
    flash('你没有关注该用户', 'danger')
    return redirect(url_for('.user', username=username))
  current_user.unfollow(user)
  db.session.commit()
  flash('你取消关注了 %s' % username, 'success')
  return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
  user = User.query.filter_by(username=username).first()
  if user is None:
    flash('非法用户', 'danger')
    return redirect(url_for('.index'))
  page = request.args.get('page', 1, type=int)
  pagination = user.followers.paginate(page, per_page=current_app.config['FLASK_POSTS_PER_PAGE'], error_out=False)
  follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items]
  return render_template('followers.html', user=user, title='Followers of', endpoint='.followers', pagination=pagination, follows=follows)


@main.route('/followed_by/<username>')
def followed_by(username):
  user = User.query.filter_by(username=username).first()
  if user is None:
    flash('非法用户', 'danger')
    return redirect(url_for('.index'))
  page = request.args.get('page', 1, type=int)
  pagination = user.followed.paginate(page, per_page=current_app.config['FLASK_POSTS_PER_PAGE'], error_out=False)
  follows = [{'user': item.followed, 'timestamp': item.timestamp} for item in pagination.items]
  return render_template('followers.html', user=user, title='Followed by', endpoint='.followed_by', pagination=pagination, follows=follows)


@main.route('/all')
@login_required
def show_all():
  resp = make_response(redirect(url_for('.index')))
  resp.set_cookie('show_followed', '', max_age=30*24*60*60)
  return resp


@main.route('/followed')
@login_required
def show_followed():
  resp = make_response(redirect(url_for('.index')))
  resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
  return resp