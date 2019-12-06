from flask import render_template, request, flash, redirect, url_for
from flask_login import login_user, current_user, login_required, logout_user
from flask import Blueprint

from .forms import RegisterForm, LoginForm
from ..models.user import User
from app.api import db

users_blueprint = Blueprint('users', __name__, template_folder='templates')


@users_blueprint.route('/')
def index():
  return render_template('users/index.html')


@users_blueprint.route('/profile')
@login_required
def profile():
  return render_template('users/profile.html')


@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
  if current_user.is_authenticated:
    flash('Already registered!  Redirecting to your User Profile page...')
    return redirect(url_for('users.profile'))

  form = RegisterForm()
  if request.method == 'POST' and form.validate_on_submit():
    new_user = User(form.email.data, form.password.data)
    new_user.authenticated = True
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
    flash('Thanks for registering, {}!'.format(new_user.email))
    return redirect(url_for('users.profile'))
  return render_template('users/register.html', form=form)


@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    flash('Already logged in!  Redirecting to your User Profile page...')
    return redirect(url_for('users.profile'))

  form = LoginForm()

  if request.method == 'POST':
    if form.validate_on_submit():
      user = User.query.filter_by(email=form.email.data).first()
      if user and user.is_correct_password(form.password.data):
        user.authenticated = True
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=form.remember_me.data)
        flash('Thanks for logging in, {}!'.format(current_user.email))
        return redirect(url_for('users.profile'))

    flash('ERROR! Incorrect login credentials.')
  return render_template('users/login.html', form=form)


@users_blueprint.route('/logout')
@login_required
def logout():
  user = current_user
  user.authenticated = False
  db.session.add(user)
  db.session.commit()
  logout_user()
  flash('Goodbye!')
  return redirect(url_for('users.index'))
