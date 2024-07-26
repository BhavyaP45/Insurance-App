#Import modules and libraries that will be used throughout the different files
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_admin.contrib.sqla import ModelView

#Create app
app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')


#Create a database model
db = SQLAlchemy()
db.init_app(app)

#Bcrypt class to store hashed passwords
bcrypt = Bcrypt(app)

#Use flask_login built in login class for users
loginmanager = LoginManager(app)
loginmanager.login_view = "login_page" #When unauthorized user tries clicking the market button, gets redirected

#Obtain routes from routes.py in the docs module
from docs import routes
from docs.models import User, Purchases, Options, Cart

class AdminModelView(ModelView):
  can_edit = False
  column_exclude_list = ['password_hash', 'id']

  def is_accessible(self):
    if current_user.is_authenticated: 
        return current_user.isAdmin
          
  
  def inaccessible_callback(self, name, **kwargs):
    # redirect to login page if user doesn't have access
      return redirect(url_for('login_page'))
   
class PurchaseModelView(ModelView):
    can_delete = True
    can_edit = True
    can_create = False
    column_searchable_list = ['type', 'title']
    column_exclude_list = ['id']
    column_filters = ['purchased_date', 'type']
    form_excluded_columns = ['title', 'type', 'price', 'purchased_date', 'owner', 'yearly_price', 'month_price']
    
    
    def is_accessible(self):
      if current_user.is_authenticated: 
          return current_user.isAdmin
      
    def inaccessible_callback(self, name, **kwargs):
    # redirect to login page if user doesn't have access
      return redirect(url_for('login_page'))

class OptionsModelView(ModelView):
  can_edit = True
  column_searchable_list = ['type', 'title']
  column_filters = ['type']
  column_exclude_list = ['id']
  # form_excluded_columns = ['colour']

  def is_accessible(self):
    if current_user.is_authenticated: 
        return current_user.isAdmin
    
  def inaccessible_callback(self, name, **kwargs):
  # redirect to login page if user doesn't have access
    return redirect(url_for('login_page'))

    
class UserView(AdminIndexView):
  
  def is_visible(self):
     return False
  
  @expose('/')
  def index(self):
    return redirect("/admin/user")
  

admin = Admin(index_view=UserView())
admin.init_app(app)
admin.add_view(AdminModelView(User, db.session ))
admin.add_view(PurchaseModelView(Purchases, db.session ))
admin.add_view(OptionsModelView(Options, db.session ))
