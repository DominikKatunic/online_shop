from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Boolean, ForeignKey, Float, DateTime, and_
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from forms import ContacForm, LoginForm, RegisterForm, ClienDataForm, AddArticle, ClientMessage
from datetime import datetime
import json
import ast

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///online_shop.db"
app.config['SECRET_KEY'] = "rgnfduigh3457re7834tztrbjnfg"

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


def admin_only(function):
    @wraps(function)
    def check_admin(*args, **kwargs):
        if current_user.is_admin:
            return function(*args, **kwargs)
        return abort(403)
    
    return check_admin


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)


class User(UserMixin, Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False)

    #Relations
    notification = relationship('Notification', back_populates='user')
    comment = relationship('Comment', back_populates='user')
    rating = relationship('Rating', back_populates='user')
    favourite = relationship('Favourite', back_populates='user')
    cart = relationship('Cart', back_populates='user')
    order = relationship('Order', back_populates='user')


class Category(Base):
    __tablename__ = 'category'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)

    #Relations
    article = relationship("Article", back_populates="category")


class Article(Base):
    __tablename__ = 'article'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    id_category: Mapped[int] = mapped_column(Integer, ForeignKey('category.id'), nullable=False)

    #Relations
    category = relationship("Category", back_populates="article")
    comment = relationship('Comment', back_populates='article')
    rating = relationship('Rating', back_populates='article')
    favourite = relationship('Favourite', back_populates='article')
    cart = relationship('Cart', back_populates='article')
    order_article = relationship('Order_article', back_populates='article')


class Notification(Base):
    __tablename__ = 'notification'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    id_user: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    #Relations
    user = relationship('User', back_populates="notification")


class Comment(Base):
    __tablename__ = 'comment'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    id_user: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False)
    id_article: Mapped[int] = mapped_column(Integer, ForeignKey('article.id'), nullable=False)

    #Relations
    user = relationship('User', back_populates="comment")
    article = relationship('Article', back_populates="comment")


class Rating(Base):
    __tablename__ = 'rating'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    id_user: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False)
    id_article: Mapped[int] = mapped_column(Integer, ForeignKey('article.id'), nullable=False)

    #Relations
    user =  relationship('User', back_populates="rating")
    article = relationship('Article', back_populates='rating')


class Favourite(Base):
    __tablename__ = 'favourite'

    id_user: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), primary_key=True)
    id_article: Mapped[int] = mapped_column(Integer, ForeignKey('article.id'), primary_key=True)

    #Relations
    user = relationship('User', back_populates='favourite')
    article = relationship('Article', back_populates='favourite')


class Cart(Base):
    __tablename__ = 'cart'

    id_user: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), primary_key=True)
    id_article: Mapped[int] = mapped_column(Integer, ForeignKey('article.id'), primary_key=True)

    #Relations
    user = relationship('User', back_populates='cart')
    article = relationship('Article', back_populates='cart')


class Card(Base):
    __tablename__ = 'card'

    id_card: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    card_number: Mapped[int] = mapped_column(Integer, nullable=False)
    expirty_date: Mapped[int] = mapped_column(Integer, nullable=False)
    security_code: Mapped[int] = mapped_column(Integer, nullable=False)
    ZIP_postal_code: Mapped[int] = mapped_column(Integer, nullable=False)

    #Relations
    order = relationship('Order', back_populates='card')


class Order(Base):
    __tablename__ = 'order'

    id_order: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_user: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False)
    first_name: Mapped[str] = mapped_column(String(150), nullable=False)
    second_name: Mapped[str] = mapped_column(String(150), nullable=False)
    country: Mapped[str] = mapped_column(String(200), nullable=False)
    address: Mapped[str] = mapped_column(String(150), nullable=False)
    phone_number: Mapped[int] = mapped_column(Integer, nullable=False)
    is_by_delivery: Mapped[bool] = mapped_column(Boolean, nullable=False)
    status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    id_card: Mapped[int] = mapped_column(Integer, ForeignKey('card.id_card'), nullable=True)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    #Relations
    user = relationship('User', back_populates='order')
    card = relationship('Card', back_populates='order')
    order_article = relationship('Order_article', back_populates='order')


class Order_article(Base):
    __tablename__ = 'order_article'

    id_article: Mapped[int] = mapped_column(Integer, ForeignKey('article.id'), primary_key=True)
    id_order: Mapped[int] = mapped_column(Integer, ForeignKey('order.id_order'), primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    #Relations
    article = relationship('Article', back_populates='order_article')
    order = relationship('Order', back_populates='order_article')


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    all_categories = db.session.execute(db.select(Category)).scalars().all()
    all_articles = db.session.execute(db.select(Article)).scalars().all()
    data_articles = []
    for article in all_articles:
        all_ratings = db.session.execute(db.select(Rating).where(Rating.id_article == article.id)).scalars().all()
        if all_ratings:
            sum = 0
            for rating in all_ratings:
                sum = sum + rating.number
            average = round(sum/len(all_ratings), 2)
        else:
            average = None
        data_articles.append({
            "id_article": article.id,
            "article_name": article.name,
            "price": article.price,
            "img_url": article.img_url,
            "average_rating": average,
            "id_category": article.id_category
        })
    return render_template('index.html', data=data_articles, categories=all_categories)


@app.route('/details/<id_article>', methods=["GET", "POST"])
def details(id_article):
    article = db.session.execute(db.select(Article).where(Article.id == id_article)).scalar()

    if not article:
        return redirect(url_for("home"))

    category = db.session.execute(db.select(Category).where(Category.id == article.id_category)).scalar()
    all_ratings = db.session.execute(db.select(Rating).where(Rating.id_article == article.id)).scalars().all()
    if all_ratings:
        sum = 0
        for rating in all_ratings:
            sum = sum + rating.number
        average = round(sum/len(all_ratings), 2)
    else:
        average = None

    comments = db.session.execute(db.select(Comment).where(Comment.id_article == article.id)).scalars().all()

    data_comments = []
    if comments:
        for comment in comments:
            user = db.session.execute(db.select(User).where(User.id == comment.id_user)).scalar()
            rating = db.session.execute(db.select(Rating).where(and_(Rating.id_user == user.id, Rating.id_article == article.id))).scalar()

            data_comments.append({
                "user_id": user.id,
                "user_name": user.name,
                "date": str(comment.date).split('.')[0],
                "comment_id": comment.id,
                "comment": comment.description,
                "rating": rating
            })

    return render_template('article_detail.html', article=article, category=category, average=average, data_comments=data_comments, num=len(data_comments))


@app.route('/register', methods=["GET", "POST"])
def register():
    registerForm = RegisterForm()
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        emails = [user.email for user in db.session.execute(db.select(User)).scalars().all()]
        names = [user.name for user in db.session.execute(db.select(User)).scalars().all()]
        if email in emails:
            flash(message="This email already exists !")
            return render_template('register.html', form=registerForm)
        if name in names:
            flash(message="This name already exists !")
            return render_template('register.html', form=registerForm)

        new_user = User(
            name=name, 
            email=email, 
            password=generate_password_hash(password, method='pbkdf2:sha256', salt_length=8),
            is_admin=False
        )

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        return redirect(url_for('home'))

    return render_template('register.html', form=registerForm)


@app.route('/login', methods=["GET", "POST"])
def login():
    login = LoginForm()

    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        emails = [user.email for user in db.session.execute(db.select(User)).scalars().all()]
        if email not in emails:
            flash(message="This email does not exists !")
            return redirect(url_for('login'))
        
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()

        if check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        
        flash(message="Incorrect password, try again")
        return redirect(url_for('login'))

    return render_template('login.html', form=login)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/add_to_cart/<id_article>')
def add_to_cart(id_article):
    item_test = db.session.execute(db.select(Cart).where(and_(Cart.id_user == current_user.id, Cart.id_article == int(id_article)))).scalar()

    if item_test:
        flash(message="This item already exists in your cart !")
        return redirect(url_for('details', id_article=int(id_article)))

    new_item = Cart(id_user=current_user.id, id_article=int(id_article))
    db.session.add(new_item)
    db.session.commit()
    return redirect(url_for('details', id_article=int(id_article)))


@app.route('/cart')
@login_required
def cart():
    id_article_list = [cart.id_article for cart in db.session.execute(db.select(Cart).where(Cart.id_user == current_user.id)).scalars().all()]
    articles = [article for article in db.session.execute(db.select(Article)).scalars().all() if article.id in id_article_list]

    data = {
        "articles": []
    }

    for article in articles:
        ratings = db.session.execute(db.select(Rating).where(Rating.id_article == article.id)).scalars().all()
        
        average = None

        if ratings:
            sum = 0
            for rating in ratings:
                    sum = sum + rating.number
            average = round(sum/len(ratings), 2)

        new_article = {
            "id": article.id,
            "name": article.name,
            "price": article.price,
            "img_url": article.img_url,
            "description": article.description,
            "id_category": article.id_category,
            "rating": average
        }

        data['articles'].append(new_article)

    return render_template('cart.html', data=data)


@app.route('/delete_from_cart/<id_article>', methods=["GET", "POST"])
@login_required
def delete_from_cart(id_article):
    delete_cart_article = db.session.execute(db.select(Cart).where(Cart.id_article == int(id_article) and Cart.id_user == current_user.id)).scalar()
    db.session.delete(delete_cart_article)
    db.session.commit()
    return redirect(url_for('cart'))


@app.route('/add_to_favourite/<id_article>', methods=["GET", "POST"])
@login_required
def add_to_favourite(id_article):
    item_test = db.session.execute(db.select(Favourite).where(and_(Favourite.id_user == current_user.id, Favourite.id_article == int(id_article)))).scalar()

    if item_test:
        flash(message="This item already exists in your favourites !")
        return redirect(url_for('details', id_article=int(id_article)))

    new_favourite = Favourite(id_user=current_user.id, id_article=int(id_article))
    db.session.add(new_favourite)
    db.session.commit()
    return redirect(url_for('details', id_article=int(id_article)))


@app.route('/favourite')
@login_required
def favourite():
    id_article_list = [favourite.id_article for favourite in db.session.execute(db.select(Favourite).where(Favourite.id_user == current_user.id)).scalars().all()]
    articles = [article for article in db.session.execute(db.select(Article)).scalars().all() if article.id in id_article_list]

    data = {
        "articles": []
    }

    for article in articles:
        ratings = db.session.execute(db.select(Rating).where(Rating.id_article == article.id)).scalars().all()
        
        average = None

        if ratings:
            sum = 0
            for rating in ratings:
                    sum = sum + rating.number
            average = round(sum/len(ratings), 2)

        new_article = {
            "id": article.id,
            "name": article.name,
            "price": article.price,
            "img_url": article.img_url,
            "description": article.description,
            "id_category": article.id_category,
            "rating": average
        }

        data['articles'].append(new_article)

    return render_template('favourite.html', data=data)


@app.route('/delete_from_favourite/<id_article>', methods=["GET", "POST"])
@login_required
def delete_from_favourite(id_article):
    delete_favourite_article = db.session.execute(db.select(Favourite).where(Favourite.id_article == int(id_article) and Favourite.id_user == current_user.id)).scalar()
    db.session.delete(delete_favourite_article)
    db.session.commit()
    return redirect(url_for('favourite'))


@app.route('/add_comment/<id_article>', methods=["GET", "POST"])
@login_required
def add_comment(id_article):
    comment = request.form['commentText']
    date = datetime.now()

    new_comment = Comment(description=comment, date=date, id_user=current_user.id, id_article=int(id_article))
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for('details', id_article=id_article))


@app.route('/delete_comment/<id_comment>', methods=["GET", "POST"])
@login_required
def delete_comment(id_comment):
    delete_comment = db.session.execute(db.select(Comment).where(Comment.id == int(id_comment))).scalar()
    id_article = delete_comment.id_article
    db.session.delete(delete_comment)
    db.session.commit()
    return redirect(url_for('details', id_article=id_article))


@app.route('/rating/<id_article>', methods=["GET", "POST"])
@login_required
def rating(id_article):
    rating = request.form['rating']

    rating_test = db.session.execute(db.select(Rating).where(and_(Rating.id_user == current_user.id, Rating.id_article == id_article))).scalar()

    if rating_test:
        flash(message="You have already rate this article")
        return redirect(url_for('details', id_article=id_article))

    new_rating = Rating(number=rating, id_user=current_user.id, id_article=id_article)
    db.session.add(new_rating)
    db.session.commit()
    return redirect(url_for('details', id_article=id_article))


@app.route('/delete_rating/<id_article>', methods=["GET", "POST"])
@login_required
def delete_rating(id_article):
    rating = db.session.execute(db.select(Rating).where(and_(Rating.id_user == current_user.id, Rating.id_article == id_article))).scalar()

    if rating:
        db.session.delete(rating)
        db.session.commit()
        return redirect(url_for('details', id_article=id_article))

    flash(message="You have not ratted this article !")
    return redirect(url_for('details', id_article=id_article))


@app.route('/client_form', methods=["GET", "POST"])
@login_required
def client_form():
    article_data = json.loads(request.form['data'])
    form = ClienDataForm()

    if article_data['articles']:
        return render_template('client_data.html', data=article_data, form=form)

    flash(message="You must have at least one article")
    return redirect(url_for('cart'))


@app.route('/paying_method', methods=["GET", "POST"])
@login_required
def paying_method():
    data = request.form['data']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    country = request.form['country']
    address = request.form['address']
    phone_number = request.form['phone_number']

    full_data = {
        "article_data": data,
        "client_data": {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "country": country,
            "address": address,
            "phone_number": phone_number
        }
    }

    return render_template('paying_method.html', full_data=json.dumps(full_data))


@app.route('/check_order/<order_data>', methods=["GET", "POST"])
@login_required
def check_order(order_data):
    data = json.loads(order_data)
    data['article_data'] = ast.literal_eval(data['article_data'])
    sending_data = json.dumps(data)
    return render_template('check_order.html', data=data, sending_data=sending_data)


@app.route('/make_order/<full_data>', methods=["GET", "POST"])
@login_required
def make_order(full_data):
    full_data = json.loads(full_data)

    new_order = Order(
        id_user=current_user.id,
        email=full_data['client_data']['email'],
        first_name=full_data['client_data']['first_name'],
        second_name=full_data['client_data']['last_name'],
        country=full_data['client_data']['country'],
        address=full_data['client_data']['address'],
        phone_number=full_data['client_data']['phone_number'],
        is_by_delivery=False,
        status=False,
        id_card=None,
        date=datetime.now()
    )
    db.session.add(new_order)
    db.session.commit()

    for article in full_data['article_data']['articles']:
        new_order_article = Order_article(
            id_article=int(article['id']),
            id_order=new_order.id_order,
            quantity=article['quantity']
        )
        
        db.session.add(new_order_article)
        db.session.commit()

    for article in full_data['article_data']['articles']:
        delete_article = db.session.execute(db.select(Cart).where(Cart.id_article == int(article['id']))).scalar()
        db.session.delete(delete_article)
        db.session.commit()

    new_notification = Notification(
        title="Order successffully made",
        description="You successfully made an order and you can see details about that order in your order history.\nWe are going to send you a new notification when delivery is going to be ready.",
        id_user=current_user.id,
        date=datetime.now()
    )

    db.session.add(new_notification)
    db.session.commit()

    return redirect(url_for('order_completed'))


@app.route('/order_completed')
@login_required
def order_completed():
    return render_template('order_completed.html')


@app.route('/ordering_history')
@login_required
def ordering_history():
    orders = db.session.execute(db.select(Order).where(Order.id_user == current_user.id).order_by(Order.date.desc())).scalars().all()
    full_data = {
        "orders": []
    }
    
    for order in orders:
        new_order = {
            "id": order.id_order,
            "date": ((str(order.date)).split("."))[0],
            "address": order.address,
            "total": 0,
            "status": order.status,
            "articles": {
                "list_articles": []
            }
        }
        order_articles_list = db.session.execute(db.select(Order_article).where(Order_article.id_order == order.id_order)).scalars().all()
        total = 0
        for article_data in order_articles_list:
            article = db.session.execute(db.select(Article).where(Article.id == article_data.id_article)).scalar()
            new_article_dict = {
                "quantity": article_data.quantity,
                "name": article.name,
                "price": article.price
            }
            new_order['articles']['list_articles'].append(new_article_dict)
            total = total + float(article.price) * int(new_article_dict['quantity'])
        new_order['articles'] = json.dumps(new_order['articles'])
        new_order['total'] = total
        full_data['orders'].append(new_order)

    return render_template('ordering_history.html', full_data=full_data)


@app.route('/order_details/<data>')
@login_required
def order_details(data):
    data = json.loads(data)

    total: float = 0
    for article in data['list_articles']:
        total += float(article['price']) * int(article['quantity'])

    return render_template('ordering_details.html', data=data['list_articles'], total=total)


@app.route('/notifications')
@login_required
def notifications():
    notification_list = db.session.execute(db.select(Notification).where(Notification.id_user == current_user.id).order_by(Notification.date.desc())).scalars().all()
    return render_template('notifications.html', data=notification_list)


@app.route('/add_article', methods=["GET", "POST"])
@login_required
@admin_only
def add_article():
    form = AddArticle()

    category_list = db.session.execute(db.select(Category)).scalars().all()
    
    if request.method == "POST":
        name = request.form['name']
        price = float(request.form['price'])
        img_url = request.form['img_url']
        description = request.form['article_description']
        category=request.form['category']

        new_article = Article(
            name=name,
            price=price,
            img_url=img_url,
            description=description,
            id_category=category
        )

        db.session.add(new_article)
        db.session.commit()

        new_notification = Notification(
            title="Created article",
            description=f"You have successfully created a new article '{new_article.name}'.\nNow everyone can see it on home page.",
            id_user=current_user.id,
            date=datetime.now()
        )

        db.session.add(new_notification)
        db.session.commit()

        return redirect(url_for('home'))
    
    return render_template('add_article.html', form=form, category_list=category_list)


@app.route('/edit_article/<id_article>', methods=["GET", "POST"])
@login_required
@admin_only
def edit_article(id_article):
    edit_article = db.session.execute(db.select(Article).where(Article.id == int(id_article))).scalar()
    category_list = db.session.execute(db.select(Category)).scalars().all()
    form = AddArticle()

    if request.method == "POST":
        edit_article.name = request.form['name']
        edit_article.price = float(request.form['price'])
        edit_article.img_url = request.form['img_url']
        edit_article.description = request.form['article_description']
        edit_article.id_category = int(request.form['category'])
        db.session.commit()

        return redirect(url_for('details', id_article=id_article))

    article_data = {
        "id": int(edit_article.id),
        "name": edit_article.name,
        "price": float(edit_article.price),
        "img_url": edit_article.img_url,
        "description": edit_article.description,
        "id_category": int(edit_article.id_category)
    }

    new_notification = Notification(
            title="Article updated",
            description=f"You have successfully updated '{edit_article.name}' article.\nNow everyone can see changes on home page and details page.",
            id_user=current_user.id,
            date=datetime.now()
        )

    db.session.add(new_notification)
    db.session.commit()

    return render_template('edit.html', form=form, article_data=article_data, category_list=category_list)


@app.route('/delete_article/<id_article>', methods=["GET", "POST"])
@login_required
@admin_only
def delete_article(id_article):
    delete_article = db.session.execute(db.select(Article).where(Article.id == int(id_article))).scalar()
    name = delete_article.name

    delete_comments = db.session.execute(db.select(Comment).where(Comment.id_article == int(id_article))).scalars().all()
    if delete_comments:
        for comment in delete_comments:
            db.session.delete(comment)
            db.session.commit()

    delete_ratings = db.session.execute(db.select(Rating).where(Rating.id_article == int(id_article))).scalars().all()
    if delete_ratings:
        for rating in delete_ratings:
            db.session.delete(rating)
            db.session.commit()

    delete_favourites = db.session.execute(db.select(Favourite).where(Favourite.id_article == int(id_article))).scalars().all()
    if delete_favourites:
        for favourite in delete_favourites:
            db.session.delete(favourite)
            db.session.commit()

    cart_delete = db.session.execute(db.select(Cart).where(Cart.id_article == int(id_article))).scalars().all()
    if cart_delete:
        for cart_article in cart_delete:
            db.session.delete(cart_article)
            db.session.commit()

    delete_order_article = db.session.execute(db.select(Order_article).where(Order_article.id_article == int(id_article))).scalars().all()
    if delete_order_article:
        for order_article in delete_order_article:
            db.session.delete(order_article)
            db.session.commit()

    db.session.delete(delete_article)
    db.session.commit()

    new_notification = Notification(
            title="Article deleted",
            description=f"You have successfully deleted '{name}' article.\nNow that article is no longer in database",
            id_user=current_user.id,
            date=datetime.now()
        )

    db.session.add(new_notification)
    db.session.commit()

    return redirect(url_for('home'))


@app.route('/clients')
@login_required
@admin_only
def clients():
    users = db.session.execute(db.select(User)).scalars().all()
    return render_template('clients.html', users=users)


@app.route('/send_message_to_client/<id_user>', methods=["GET", "POST"])
@login_required
@admin_only
def send_message_to_client(id_user):
    form = ClientMessage()
    user = db.session.execute(db.select(User).where(User.id == int(id_user))).scalar()

    if request.method == "POST":
        title = request.form['title']
        message = request.form['message']

        new_notification = Notification(
            title=title,
            description=message,
            id_user=user.id,
            date=datetime.now()
        )

        db.session.add(new_notification)
        db.session.commit()

        return redirect(url_for('clients'))

    return render_template('message_to_client.html', form=form, user=user)


@app.route('/clients_orders/<id_user>')
@login_required
@admin_only
def clients_orders(id_user):
    all_orders = [order for order in db.session.execute(db.select(Order).where(Order.id_user == int(id_user)).order_by(Order.date)).scalars().all() if order.id_user == int(id_user)]
    return render_template('clients_orders.html', all_orders=all_orders)


@app.route('/complete_clients_order/<order_id>', methods=["GET", "POST"])
@login_required
@admin_only
def complete_clients_order(order_id):
    order = db.session.execute(db.select(Order).where(Order.id_order == int(order_id))).scalar()
    
    order.status = True
    db.session.commit()

    return redirect(url_for('clients'))


@app.route('/clients_order_detail/<id_order>', methods=["GET", "POST"])
@login_required
@admin_only
def clients_order_detail(id_order):
    all_order_article = db.session.execute(db.select(Order_article).where(Order_article.id_order == int(id_order))).scalars().all()

    data = {
        "total": 0,
        "articles": []
    }

    for article_data in all_order_article:
        article = db.session.execute(db.select(Article).where(Article.id == article_data.id_article)).scalar()
        new_article_dict = {
            "quantity": article_data.quantity,
            "name": article.name,
            "price": article.price
        }
        data['total'] = data['total'] + float(article.price) * int(new_article_dict['quantity'])
        data['articles'].append(new_article_dict)

    return render_template('clients_order_details.html', data=data)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=["GET", "POST"])
def contact():
    form = ContacForm()
    if request.method == "POST":
        admin = db.session.execute(db.select(User).where(User.email == "admin@email.com")).scalar()
        
        email = request.form['email']
        message = request.form['message']

        notification = Notification(
            title=f"Message from {email}",
            description=message,
            id_user=admin.id,
            date=datetime.now()
        )

        db.session.add(notification)
        db.session.commit()

        return redirect(url_for('home'))
    return render_template('contact.html', form=form)


if __name__ == "__main__":
    app.run(debug=False, port=5002)



