import os

from flask import Flask, session,render_template,redirect,url_for,request,jsonify
from flask_session import Session
from sqlalchemy import create_engine,exc
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route('/')
def index():
    return redirect(url_for('search_page'))


@app.route("/register",methods=["GET","POST"])
def register():
    msg = None
    if 'user' in session:
        return redirect(url_for('search_page'))
    if request.method == "POST":
        try:
            username = request.form.get("username")
            password = request.form.get("password")
            result = db.execute("INSERT INTO users(username , passwords) VALUES(:n , :p)",{"n":username , "p":password})
            db.commit()
            if result.row_count() > 0:
                session['user'] = username
                return redirect(url_for('login'))
        except exc.IntegrityError:
            msg="username exists"
            db.execute("ROLLBACK")
            db.commit()
    return render_template("register.html",msg=msg)
@app.route('/login',methods=['GET','POST'])
def login():
    msg = None
    if 'user' in session:
        return redirect(url_for('search_page'))
    if request.method=="POST":
        name = request.form.get("username")
        password = request.form.get("password")
        result = db.execute("SELECT * FROM users WHERE username = :u",{"u":name}).fetchone()
        db.commit()
        if result['passwords'] == password:
            session['user'] = name
            return redirect(url_for('search_page'))
        if result is None:
            msg="username or password is incorrect"
    return render_template('login.html',msg=msg)

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect(url_for('login'))
@app.route('/search_page')
def search_page():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template("search_page.html",logged=session['user'])

@app.route('/search_page/search_result',methods=["POST"])
def search_result():
    msg = None
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == "POST": 
    
        searchbox_query = request.form.get("searchbox")
        query = '%' + searchbox_query + '%'
        books = db.execute("SELECT * FROM books WHERE isbn like :query OR title like :query OR author like :query" , {"query":query}).fetchall()
        if not books:
            msg = "no books found"
            return redirect(url_for('search_page'))

    return render_template('search_result.html',books=books)
@app.route('/book/<string:isbn>',methods=["GET","POST"])
def book_info(isbn):
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method=="POST":
        comment = request.form.get("comment")
        rating = request.form.get("rating")
        book = db.execute("INSERT INTO reviews (username, book_id, comment, rating) VALUES (:a, :b, :c, :r)", {"a": session['user'], "b": isbn, "c": comment, "r": rating})
        db.commit()

    book = db.execute("SELECT * FROM books WHERE isbn = :q", {"q": isbn}).fetchone()
    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :q1", {"q1": isbn}).fetchall()

    response = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "8Yz7mWlTcU01EJc6HuWdJw", "isbns": isbn})
    data = response.json()
    gr_rating = (data['books'][0]['average_rating'])

    return render_template("book_info.html", book_info=book, reviews=reviews, rating=gr_rating)    


@app.route("/api/<string:isbn>")
def Api(isbn):
    book=db.execute("SELECT * FROM books WHERE isbn = :i",{"i":isbn}).fetchone()

    if book is None:
        return jsonify({"Error":"invalid isbn no book found"}),404

    review = db.execute("SELECT * from reviews where book_id = :i",{"i":isbn})
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "8Yz7mWlTcU01EJc6HuWdJw", "isbns": isbn})
    return jsonify(
        {"title":book.title,
         "ISBN":book.isbn,
         "Author":book.author,
        "Publication year":book.year,
        "review count":res.json()['books'][0]['reviews_count'],
        "Average rating":res.json()['books'][0]['average_rating']}
    )











    
