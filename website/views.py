from flask import Blueprint, render_template, request, flash, jsonify, url_for, redirect
from flask_login import login_required, current_user
from .models import User, Post, Item, OpenOrder, ClosedOrder, Favorite
from . import db
import json
from datetime import datetime
from sqlalchemy import update, text 

views = Blueprint("views", __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    
    posts = Post.query.order_by(Post.timestamp.desc())
    print(posts)
    return render_template("home.html", posts=posts, user=current_user)

@views.route('/search/', methods=['GET', 'POST'])
@login_required
def search():
    favorites = db.engine.execute("SELECT * FROM favorite WHERE user_id = ? ORDER BY vendor", current_user.id)
    if request.method == 'POST':
        search = request.form.get('search')
        if search:
            results = db.engine.execute("SELECT * FROM user WHERE B_name LIKE ?", search)
            results = list(results)
            return render_template("find_users.html", user=current_user, results=results)
    return render_template("find_users.html", favorites=favorites, user=current_user)

# Profile
@views.route('/user/<B_name>', methods=['GET', 'POST'])
@login_required
def profile(B_name):
    user = User.query.filter_by(B_name=B_name).first_or_404()
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc())
    favorites = db.engine.execute("SELECT * FROM favorite WHERE user_id = ?", current_user.id)
    fav_status = False
    fav_id = None
    for fav in favorites:
        if user.B_name == fav.vendor:
            fav_status = True
            fav_id = fav.id

    # Add written post to database
    if request.method == 'POST':
        post = request.form.get('post')
        if post:
            new_post = Post(data=post, user_id=current_user.id)
            db.session.add(new_post)
            db.session.commit()
            flash('Post added!', category='success')
        else:
            flash('no post')
    return render_template('user_profile.html', fav_id=fav_id, fav_status=fav_status, favorites=favorites, user=user, posts=posts)

@views.route('/edit_profile/', methods=['GET', 'POST'])
@login_required
def edit_profile():

    if request.method == 'POST':        

        if request.form.get('email'):
            email = request.form.get('email')
            if len(email) < 4:
                flash('Email must be greater than 4 characters', category='error')
            else: 
                db.engine.execute("UPDATE User SET email = ? WHERE id = ?", (email, current_user.id))

        if request.form.get('B_name'):
            B_name = request.form.get('B_name')
            if len(B_name) < 2:
                flash('Business name must be greater than 1 characters', category='error')
            else:
                db.engine.execute("UPDATE User SET B_name = ? WHERE id = ?", (B_name, current_user.id))
        
        if request.form.get('about_us'):
            about_us = request.form.get('about_us')
            db.engine.execute("UPDATE User SET about_us = ? WHERE id = ?", (about_us, current_user.id))
        
        flash('Profile Updated', category='success')
        return redirect(url_for('views.profile', B_name=B_name))

    return render_template('edit_profile.html', user=current_user)

# Orders
@views.route('/order_form/<B_name>', methods=['GET', 'POST'])
@login_required
def order_form(B_name):
    # Use of user info pulls from user we are visiting, not the current_user
    # so when order is placed, the vendor's id is logged as the user.id
    user = User.query.filter_by(B_name=B_name).first_or_404()
    if request.method =='POST':
        item_amount = request.form.getlist('order')
        i = 0
        m = 0
        while i < len(item_amount):
            if item_amount[i]:
                new_order = OpenOrder(item=user.items[i].name, price=user.items[i].price, unit=user.items[i].unit, amount=item_amount[i], r_total=(float(item_amount[i]) * float(user.items[i].price)), customer=current_user.B_name, vendor=user.B_name, vendor_id=user.id)
                db.session.add(new_order)
                db.session.commit()
                if m == 0:
                    flash('Order submitted!', category='success')
                    m += 1
            i += 1
        return redirect(url_for('views.home'))
    return render_template('order_form.html', user=user)

@views.route('/edit_order_form/', methods=['GET', 'POST'])
@login_required
def edit_order_form():
    if request.method =='POST':
        name = request.form.get('name')
        price = request.form.get('price')
        unit = request.form.get('unit')
        notes = request.form.get('notes')

        if name:
            if not price or not unit:
                flash('item must have price and unit', category='error')
            else:
                new_item = Item(user_id=current_user.id, name=name, price=price, unit=unit, notes=notes)
                db.session.add(new_item)
                db.session.commit()
                flash('Item added!', category='success')
        else:
            flash('item must be entered', category='error')
    return render_template('edit_order_form.html', user=current_user)

@views.route('/view_orders/', methods=['GET', 'POST'])
@login_required
def view_orders():

    # Query the OpenOrder database and retrieve distinct customer names with orders placed to current user
    # If current_user.B_type == 'farm':
    customers = db.engine.execute("SELECT DISTINCT customer FROM open_order WHERE vendor_id = ?", current_user.id)
    vendor_closed_orders = ClosedOrder.query.filter_by(vendor_id=current_user.id).order_by(ClosedOrder.order_completed.desc())
    item_totals = db.engine.execute("SELECT SUM(amount),item,unit FROM open_order GROUP BY item HAVING vendor_id = ?", current_user.id)
    item_totals = list(item_totals)
    customer_totals = db.engine.execute("SELECT SUM(r_total),customer FROM open_order GROUP BY customer")
    customer_totals = list(customer_totals)

    #If current_user.B_type == 'restaurant':
    customer_open_orders = OpenOrder.query.filter_by(customer=current_user.B_name).order_by(OpenOrder.order_placed.desc())
    customer_closed_orders = ClosedOrder.query.filter_by(customer=current_user.B_name).order_by(ClosedOrder.order_completed.desc())

    return render_template('view_orders.html', customer_open_orders=customer_open_orders, customer_closed_orders=customer_closed_orders, vendor_closed_orders=vendor_closed_orders, item_totals=item_totals, customer_totals=customer_totals, customers=customers, user=current_user)





# Other    
@views.route('/delete-post', methods=['POST'])
def delete_post():
    post = json.loads(request.data)
    postId = post['postId']
    post = Post.query.get(postId)
    if post:
        if post.user_id == current_user.id:
            db.session.delete(post)
            db.session.commit()
            
    return jsonify({})

@views.route('/delete-item', methods=['POST'])
def delete_item():
    item = json.loads(request.data)
    itemId = item['itemId']
    item = Item.query.get(itemId)
    if item:
        if item.user_id == current_user.id:
            db.session.delete(item)
            db.session.commit()
            
    return jsonify({})

@views.route('/complete-order', methods=['POST'])
def complete_order():

    # Get the order data from the pressed button
    open_order = json.loads(request.data)
    openOrderId = open_order['openOrderId']
    open_order = OpenOrder.query.get(openOrderId)
    
    # Check if open_order exists and copy its data into a ClosedOrder object, ready to be put in db
    if open_order:
        closed_order = ClosedOrder(open_order_id=open_order.id, item=open_order.item, price=open_order.price, unit=open_order.unit, amount=open_order.amount, r_total=open_order.r_total, order_placed=open_order.order_placed, customer=open_order.customer, vendor=open_order.vendor, vendor_id=open_order.vendor_id)
        if open_order.vendor_id == current_user.id:
            db.session.delete(open_order)
            db.session.add(closed_order)
            db.session.commit()

    return jsonify({})

@views.route('/decline-order', methods=['POST'])
def decline_order():

    # Get the order data from the pressed button
    open_order = json.loads(request.data)
    openOrderId = open_order['openOrderId']
    open_order = OpenOrder.query.get(openOrderId)
    
    # Check if open_order exists and delete it from OpenOrder table
    if open_order:
        if open_order.vendor_id == current_user.id or open_order.customer == current_user.B_name:
            db.session.delete(open_order)
            db.session.commit()

    return jsonify({})

@views.route('/fav-farm', methods=['POST'])
def fav_farm():
    farm = json.loads(request.data)
    farmId = farm['farmId']
    farm = User.query.get(farmId)
    favorite = Favorite(user_id=current_user.id, customer=current_user.B_name, vendor_id=farm.id, vendor=farm.B_name)
    if favorite:
        db.session.add(favorite)
        db.session.commit()
        flash("Farm Fav\'ed!", category='success')
            
    return jsonify({})

@views.route('/un-fav-farm', methods=['POST'])
def un_fav_farm():
    fav = json.loads(request.data)
    favId = fav['favId']
    fav = Favorite.query.get(favId)
    if fav:
        db.session.delete(fav)
        db.session.commit()
        flash("Farm Un-Fav\'ed", category='success')
            
    return jsonify({})


@views.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit() 