from docs import app, db, render_template, redirect, url_for, flash
from docs import login_user, logout_user, current_user, login_required
from docs.forms import RegisterForm, LoginForm
from docs.models import User


@app.route("/")
def index_page():
  return render_template("index.html")

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
    
    if current_user.isAdmin:
      return redirect('/admin')
    
    return redirect(url_for("dashboard_page"))
  if form.errors != {}: #.errors Stores all the errors from the form (If there are no errors from the validations)
      for err_msg in form.errors.values():
        flash(f'There was an error with creating a user: {err_msg}', category = "error")

  return render_template("register.html", form = form)


@app.route("/login", methods = ["POST", "GET"])
def login_page():
  form = LoginForm()
  if form.validate_on_submit():
    try: 
      attempted_user = User.query.filter_by(username = form.username.data).first()

      if attempted_user and attempted_user.check_password_correction(form.password.data):
        login_user(attempted_user)
        flash(f'Welcome Back {attempted_user.username}', category="success")
        if current_user.isAdmin:
          return redirect("/admin")
        return redirect(url_for("dashboard_page"))
      else:
        flash("User name and password are not matched!", category= "error")

    except:
      flash("Something Went Wrong", category = "error")

  return render_template("login.html", form = form)

@login_required #Execute before setting up the route 
@app.route('/logout', methods = ["POST","GET"])
def logout_page():
    logout_user()
    flash("Success! Logged out!", category= "success")
    return redirect(url_for("login_page"))

@login_required #Require login before the route is set up
@app.route("/dashboard", methods = ["POST", "GET"])
def dashboard_page():
  
  return render_template("dashboard.html", user = current_user)


