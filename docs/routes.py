from docs import app, db, render_template, redirect, url_for
from docs import login_user, logout_user, current_user, login_required
from docs.forms import RegisterForm, LoginForm
from docs.models import User

@app.route("/")
def index_page():
  return 

@app.route("/register", methods = ["POST", "GET"])
def register_page():
  form = RegisterForm()
  if form.validate_on_submit():
    #Create user and add entry to the database
    user_to_create = User(username = form.username.data, email_address = form.email_address.data, \
                          password = form.password.data, isAdmin = form.isAdminField.data)
    with app.app_context():
      db.session.add(user_to_create)
      db.session.commit()
      login_user(user_to_create)

    return redirect(url_for("dashboard_page"))
  
  return render_template("register.html", form = form)


@app.route("/login")
def login_page():
  form = LoginForm()
  if form.validate_on_submit():
    try: 
      attempted_user = User.query.filter_by(username = form.username.data).first()

      if attempted_user and attempted_user.check_password_correction(form.password.data):
        login_user(attempted_user)

        return redirect(url_for("dashboard_page"))
    
    except:
      print("Something went wrong")

  return render_template("login.html", form = form)

@login_required #Require login before the route is set up
@app.route("/dashboard")
def dashboard_page():
  return render_template("dashboard.html")