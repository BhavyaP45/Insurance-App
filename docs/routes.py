from docs import app, db, render_template, redirect, url_for, flash
from docs import login_user, logout_user, current_user, login_required
from docs.forms import RegisterForm, LoginForm
from docs.models import User,Cart
from flask import request
from docs.models import Options, Purchases
import requests, random

@app.route("/")
def index_page():
  if current_user.is_authenticated:
    cart_count = Cart.query.filter_by(owner = current_user.id).count()
  else:
    cart_count = 0
  return render_template("index.html", cart_count = cart_count)

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
    return redirect(url_for("index_page"))

@login_required #Require login before the route is set up
@app.route("/dashboard", methods = ["POST", "GET"])
# Generating random messages for the dashboard.
def dashboard_page(): 
  list_of_messages = [
    "Insure your assets today.",
    "Protect you and your loved ones today.",
    "Expect the unexpected with ICS-Insurance.",
    "Be prepared for anything that comes your way.",
    "Remain adaptable.",
  ]
  display_message = random.choice(list_of_messages)
  
  if not current_user.is_authenticated:
    return redirect(url_for("login_page"))
  approved = Purchases.query.filter_by(owner = current_user.id, status = "APPROVED").all()
  pending = Purchases.query.filter_by(owner = current_user.id, status = "PENDING").all()
  declined = Purchases.query.filter_by(owner = current_user.id, status = "DECLINED").all()
  cart_count = Cart.query.filter_by(owner = current_user.id).count()

  # calculate monthly total with 13% tax applied
  monthly_total = 0
  for item in approved:
    monthly_total += item.month_price
  monthly_total = monthly_total * 1.13
  # round monthly_total to 2 decimal places
  monthly_total = round(monthly_total, 2)

  # calculate yearly total with 13% tax applied
  yearly_total = 0
  for item in approved:
    yearly_total += item.yearly_price
  yearly_total = yearly_total * 1.13
  yearly_total = round(yearly_total, 2)

  # if approved.length is 2, discount = 10%. If approved.length is > 2, discount = 20% on the total yearly and monthly prices
  discount=0
  if len(approved) == 2:
    yearly_total = yearly_total * 0.9
    monthly_total = monthly_total * 0.9
    monthly_total = round(monthly_total, 2)
    yearly_total = round(yearly_total, 2)
    discount = 10
  elif len(approved) > 2:
    yearly_total = yearly_total * 0.8
    monthly_total = monthly_total * 0.8
    monthly_total = round(monthly_total, 2)
    yearly_total = round(yearly_total, 2)
    discount = 20
  else:
    yearly_total = yearly_total
    monthly_total = monthly_total
    monthly_total = round(monthly_total, 2)
    yearly_total = round(yearly_total, 2)
    discount = 0
  # Create a string with all the types of all approved items
  approved_types = ""
  if approved != []:
    for item in approved:
      approved_types += item.type + " + "
      # don't add + to the last item in approved_types
    approved_types = approved_types[:-3]
      
  else:
    approved_types = 0

  return render_template("dashboard.html", cart_count = cart_count,approved_types=approved_types, discount=discount, user = current_user, approved = approved, pending = pending, declined = declined, monthly_total = monthly_total, yearly_total = yearly_total, display_message = display_message)

@login_required
@app.route("/products", methods = ["POST", "GET"])
def products_page():
  # redirect to log in if user is not logged in
  options = Options.query.all()
  if not current_user.is_authenticated:
    return render_template("products.html", cart_count = None, current_user = None, options = options)
  if request.method == "POST":
    return render_template("products.html", current_user=current_user)

  cart_count = Cart.query.filter_by(owner = current_user.id).count()
  # for cart_item in cart_items:
  #   print("CART ITEM: ", cart_item.title)

  options = Options.query.all()
  return render_template("products.html", cart_count = cart_count, current_user=current_user, options=options)

@login_required
@app.route("/cart", methods = ["POST", "GET"])
def add_to_cart():
  if not current_user.is_authenticated:
    return redirect(url_for("login_page"))
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
  cart_count = Cart.query.filter_by(owner = current_user.id).count()

  # if an item with the same type property already exists in the cart, don't add it again
  for item in Cart.query.filter_by(owner = current_user.id).all():
    if item.type == type:
      flash(f"{type} Insurance is already in your cart!", category="error")
      cart = Cart.query.all()
      return render_template("products.html", cart_count = cart_count, user=current_user, options = options, cart=cart)
 
  with app.app_context():
    db.session.add(new_cart_item)
    db.session.commit()
    flash(f"Added {title} to your cart!", category="success")

  cart = Cart.query.all()
  
  return render_template("products.html", cart_count = cart_count, user=current_user, options = options, cart=cart)

@login_required
@app.route("/checkout", methods = ["POST", "GET"])
def checkout_page():
  if not current_user.is_authenticated:
    return redirect(url_for("login_page"))
  cart_items = Cart.query.filter_by(owner = current_user.id)
  cart_count = Cart.query.filter_by(owner = current_user.id).count()
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
      return redirect(url_for("dashboard_page"))
  elif request.method == "GET":
    cart_items = Cart.query.filter_by(owner = current_user.id).all()
      # calculate monthly total with 13% tax applied
  monthly_total = 0
  for item in cart_items:
    monthly_total += item.month_price
  monthly_total = monthly_total * 1.13
  # round monthly_total to 2 decimal places
  monthly_total = round(monthly_total, 2)

  # calculate yearly total with 13% tax applied
  yearly_total = 0
  for item in cart_items:
    yearly_total += item.yearly_price
  yearly_total = yearly_total * 1.13
  # round yearly_total to 2 decimal places
  yearly_total = round(yearly_total, 2)

  # if approved.length is 2, discount = 10%. If approved.length is > 2, discount = 20% on the total yearly and monthly prices
  discount=0
  if len(cart_items) == 2:
    yearly_total = yearly_total * 0.9
    monthly_total = monthly_total * 0.9
    yearly_total = round(yearly_total, 2)
    monthly_total = round(monthly_total, 2)
    discount = 10
  elif len(cart_items) > 2:
    yearly_total = yearly_total * 0.8
    yearly_total = round(yearly_total, 2)
    monthly_total = monthly_total * 0.8
    monthly_total = round(monthly_total, 2)
    discount = 20
  else:
    yearly_total = yearly_total
    yearly_total = round(yearly_total, 2)
    monthly_total = monthly_total
    monthly_total = round(monthly_total, 2)
    discount = 0
  # Create a string with all the types of all approved items
  approved_types = ""
  if cart_items != []:
    for item in cart_items:
      approved_types += item.type + " + "
      # don't add + to the last item in approved_types
    approved_types = approved_types[:-3]
      
  else:
    approved_types = 0
      
  
  return render_template("checkout.html", cart_count = cart_count, cart_items = cart_items, monthly_total = monthly_total, yearly_total = yearly_total, discount = discount, approved_types = approved_types)

@login_required
@app.route("/delete", methods=["POST", "GET"])
def delete_cart_item():
    if not current_user.is_authenticated:
     return redirect(url_for("login_page"))
    cart_item_id = request.args.get("cart_item_id")
    cart_item = Cart.query.filter_by(id=cart_item_id).first()

    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        flash(f"Deleted {cart_item.title} from your cart!", category="success")
    else:
        flash("Item not found in cart.", category="error")

    return redirect(url_for("checkout_page"))

@login_required
@app.route("/removeoption", methods = ["POST", "GET"])
def remove_insurance_option():
  if not current_user.is_authenticated:
    return redirect(url_for("login_page"))
  purchased_item_id = request.args.get("item_id")
  purchased_item = Purchases.query.filter_by(id=purchased_item_id).first()
  request_user = User.query.filter_by(id = purchased_item.owner).first()
  user_email = request_user.email_address
  admin_email = 'vangara.anirudhbharadwaj@gmail.com'
  # User.query.filter_by(isAdmin = True).first().email_address
  if purchased_item:
    url = "https://mail-sender-api1.p.rapidapi.com/"
    payload = {
      "sendto": admin_email,
      "name": "ICS Insurance Customer Service",
      "replyTo": admin_email,
      "ishtml": "true",
      "title": f"Request to Remove {purchased_item.title} from User {request_user.username}",
      "body": f"<a href=\"http://127.0.0.1:5000/admin/purchases/edit/?id={purchased_item_id}&url=/admin/purchases/\" target='_blank'>Visit Admin Panel</a>"
    }
    headers = {
      "x-rapidapi-key": "110ab4fdfemsh81953e4f0a53476p1970f4jsn593bfac55618",
      "x-rapidapi-host": "mail-sender-api1.p.rapidapi.com",
      "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    print(response.json())
    flash(f"Request to remove {purchased_item.title} has been sent to the admin!", category="success")
    return redirect(url_for("dashboard_page"))

