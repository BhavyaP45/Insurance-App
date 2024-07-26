from docs import app, db, UserMixin, bcrypt, loginmanager, admin
from sqlalchemy.sql import func


@loginmanager.user_loader #Required property for the users to be authenticated
def load_user(user_id):
    return User.query.get(user_id)

#Create class user with Database Model, create various columns for the table
class User(db.Model, UserMixin): #Use UserMixin class to add prexisting methods
    id = db.Column(db.Integer(), primary_key = True)
    username = db.Column(db.String(length = 45), nullable = False, unique = True)
    email_address = db.Column(db.String(), unique = True, nullable = False)
    password_hash = db.Column(db.String(), nullable = False)
    isAdmin = db.Column(db.Boolean())
    insuranceSelection = db.relationship('Purchases', backref = "insurance_selection", lazy = True)
    
    #Create a password property
    @property
    def password(self):
      return self.password
    
    @password.setter #Used to set the property of password into a hashed one using bcrypt class
    def password(self, plain_text_password):
      self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')
    
    #Create a method that returns a boolean by checking an attempted password with the stored hash
    def check_password_correction(self, attempted_password):
      return bcrypt.check_password_hash(self.password_hash, attempted_password) #checks the hash password with the attempted one
    
class Purchases(db.Model):
  id = db.Column(db.Integer(), primary_key = True)
  title =  db.Column(db.String(length = 45), nullable = False)
  type =  db.Column(db.String(length = 45), nullable = False)
  purchased_date = db.Column(db.DateTime(timezone=True), default=func.now())
  yearly_price = db.Column(db.Integer(), nullable = False)
  month_price = db.Column(db.Integer(), nullable = False)
  owner = db.Column(db.Integer(), db.ForeignKey("user.id")) 
  status = db.Column(db.String(length = 45), nullable = False)
   
class Options(db.Model):
  id = db.Column(db.Integer(), primary_key = True)
  title =  db.Column(db.String(length = 45), nullable = False)
  type =  db.Column(db.String(length = 45), nullable = False)
  yearly_price = db.Column(db.Integer(), nullable = False)
  month_price = db.Column(db.Integer(), nullable = False)
  mini_description = db.Column(db.String(length = 100), nullable = False)
  description = db.Column(db.String(length = 100), nullable = False)
  colour = db.Column(db.String(length = 100), nullable = False)
  tier = db.Column(db.String(length = 100), nullable = False)

class Cart(db.Model):
  id = db.Column(db.Integer(), primary_key = True)
  title =  db.Column(db.String(length = 45), nullable = False)
  type =  db.Column(db.String(length = 45), nullable = False)
  yearly_price = db.Column(db.Integer(), nullable = False)
  month_price = db.Column(db.Integer(), nullable = False)
  mini_description = db.Column(db.String(length = 100), nullable = False)
  description = db.Column(db.String(length = 100), nullable = False)
  colour = db.Column(db.String(length = 100), nullable = False)
  tier = db.Column(db.String(length = 100), nullable = False)
  owner = db.Column(db.Integer(), db.ForeignKey("user.id"))