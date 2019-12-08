import datetime

from flask import render_template, request, flash, redirect, url_for
from flask_login import login_user, current_user, login_required, logout_user
from flask import Blueprint

from app.api import db, log, config_env, parser, Resource, jsonify, request, DataStoreClient
from ..utils.celery_task import searching, cursor_searching, extract_tweet_quote
from ..models.hashtag import Hashtag
from .forms import AddHashtagForm, EditHashtagForm

hashtag_blueprint = Blueprint('hashtag', __name__, template_folder='templates')


@hashtag_blueprint.route('/hashtags')
@login_required
def hashtag_list():
  hashtag = Hashtag.query.all()
  return render_template('hashtag/hashtag_list.html', data=hashtag)


@hashtag_blueprint.route('/hashtag/add', methods=['GET', 'POST'])
@login_required
def add_hashtag():
  form = AddHashtagForm()
  if request.method == 'POST' and form.validate_on_submit():
    hashtag = Hashtag.query.filter(Hashtag.hashtag == form.hashtag.data).first()
    if not hashtag:
      new_hashtag = Hashtag(hashtag=form.hashtag.data, active=form.active.data)
      db.session.add(new_hashtag)
      db.session.commit()
      flash("Hashtag updated", "Added")
      return redirect(url_for('hashtag.hashtag_list'))
    else:
      flash("Hashtag Exist", "success")
      return redirect(url_for('hashtag.hashtag_list'))
  return render_template('hashtag/add_hashtag.html', form=form)


@hashtag_blueprint.route('/hashtag/update/<int:id>', methods=('GET', 'POST'))
@login_required
def edit_hashtag(id):
  hashtag_data = Hashtag.query.get(id)
  form = EditHashtagForm(obj=hashtag_data)
  if request.method == 'POST' and form.validate_on_submit():
    hashtag_data.hashtag = form.hashtag.data
    hashtag_data.active = form.active.data
    hashtag_data.updated_at = datetime.datetime.now()
    db.session.commit()
    flash("Hashtag updated", "success")
    return redirect(url_for('hashtag.hashtag_list'))
  return render_template('hashtag/edit_hashtag.html', form=form)


@hashtag_blueprint.route('/hashtag/delete/<int:id>', methods=['POST'])
@login_required
def delete_hashtag(id):
  if request.method == 'POST':
    new_hashtag = Hashtag.query.get(id)
    db.session.delete(new_hashtag)
    db.session.commit()
    return redirect(url_for('hashtag.hashtag_list'))

@hashtag_blueprint.route('/hashtag/<int:id>/search', methods=['GET'])
@login_required
def search_hashtag(id):
  hashtag = Hashtag.query.get(id)
  if hashtag:
    searching.apply_async(args=[hashtag.hashtag])
    cursor_searching.apply_async(args=[hashtag.hashtag])
    return redirect(url_for('hashtag.hashtag_list'))
  return redirect(url_for('hashtag.hashtag_list'))

@hashtag_blueprint.route('/hashtag/extract_quote', methods=['GET'])
@login_required
def extract_quote():
  task = extract_tweet_quote.apply_async(args=["tweets"])
  return redirect(url_for('hashtag.hashtag_list'))