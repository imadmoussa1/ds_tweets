import datetime

from flask import render_template, request, flash, redirect, url_for
from flask_login import login_user, current_user, login_required, logout_user
from flask import Blueprint

from app.api import db, log, config_env, parser, Resource, jsonify, request, DataStoreClient

from ..models.trend import Trend

trend_blueprint = Blueprint('trend', __name__, template_folder='templates')


@trend_blueprint.route('/trends')
@login_required
def trend_list():
  trend = Trend.query.all()
  return render_template('trend/trend_list.html', data=trend)
