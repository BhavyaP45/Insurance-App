from docs import app, db, render_template, redirect, url_for, flash
from docs import login_user, logout_user, current_user, login_required
from docs.forms import RegisterForm, LoginForm
from docs.models import User,Cart
from flask import request
from docs.models import Options, Purchases


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
  
  approved = Purchases.query.filter_by(owner = current_user.id, status = "APPROVED").all()
  pending = Purchases.query.filter_by(owner = current_user.id, status = "PENDING").all()
  declined = Purchases.query.filter_by(owner = current_user.id, status = "DECLINED").all()

  return render_template("dashboard.html", user = current_user, approved = approved, pending = pending, declined = declined)

@login_required
@app.route("/products", methods = ["POST", "GET"])
def products_page():
  if request.method == "POST":
    return render_template("products.html", current_user=current_user)

  elif request.method == "GET":
    options = Options.query.all()
    for option in options:
      print(option.title)

  cart_items = Cart.query.filter_by(owner = current_user.id).all()
  for cart_item in cart_items:
    print("CART ITEM: ", cart_item.title)

  options = Options.query.all()
  cart = Cart.query.all()
  return render_template("products.html", current_user=current_user, options=options)

@login_required
@app.route("/cart", methods = ["POST", "GET"])
def add_to_cart():
  product_id = request.args.get("product_id")
  print("PRODUCT ID: ", product_id)
  options = Options.query.all()
  option = Options.query.filter_by(id = product_id).first()
  # extract all the values from the option object
  title = option.title
  type = option.type
  yearly_price = option.yearly_price
  month_price = option.month_price
  mini_description = option.mini_description
  description = option.description
  colour = option.colour
  tier = option.tier
  
  new_cart_item = Cart(
  title=title, type=type, yearly_price=yearly_price,
  month_price=month_price, mini_description=mini_description,
  description=description, colour=colour, tier=tier, owner=current_user.id )
 
  with app.app_context():
    db.session.add(new_cart_item)
    db.session.commit()
    flash(f"Added {title} to your cart!", category="success")

  cart = Cart.query.all()
  
  return render_template("products.html", user=current_user, options = options, cart=cart)

@login_required
@app.route("/checkout", methods = ["POST", "GET"])
def checkout_page():

  cart_items = Cart.query.filter_by(owner = current_user.id)
  if request.method == "POST":
      for item in cart_items:
        id = item.id
        title = item.title
        type = item.type
        yearly_price = item.yearly_price
        month_price = item.month_price
        mini_description = item.mini_description
        description = item.description
        colour = item.colour
        tier = item.tier

        # Add to the purchases table
        new_purchase = Purchases(
          title=title, type=type, yearly_price=yearly_price,
          month_price=month_price, owner=current_user.id, status="PENDING" )
        # with app.app_context():
        db.session.add(new_purchase)
        db.session.commit()

        # Delete from the cart table
        cart_item = Cart.query.filter_by(id=id).first()
        db.session.delete(cart_item)
        db.session.commit()
        flash(f"Added {title} to your purchases!", category="success")
      
  
  return render_template("checkout.html", cart_items = cart_items)

@login_required
@app.route("/delete", methods=["POST", "GET"])
def delete_cart_item():
    cart_item_id = request.args.get("cart_item_id")
    cart_item = Cart.query.filter_by(id=cart_item_id).first()

    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        flash(f"Deleted {cart_item.title} from your cart!", category="success")
    else:
        flash("Item not found in cart.", category="error")

    return redirect(url_for("checkout_page"))
