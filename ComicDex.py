from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
#import requests #beginning to build API integration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date_entry = db.Column(db.DateTime, default=datetime.utcnow)
    publisher = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    volume = db.Column(db.String(200), nullable=True)

    rating = db.Column(db.Integer)
    notes = db.Column(db.Text)

    cover_url = db.Column(db.String(500))
    gcd_id = db.Column(db.Integer)

    def __repr__(self):
        return '<Book %r>' % self.id

with app.app_context():
    db.create_all()

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        book_title = request.form['title']
        book_author = request.form['author']
        book_volume = request.form['volume']
        new_book = Collection(title = book_title, author = book_author, volume = book_volume)

        try:
            db.session.add(new_book)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an error adding your book'
    else:
        books = Collection.query.order_by(Collection.date_entry).all()
        return render_template('index.html', books=books)
@app.route('/delete/<int:id>')
def delete(id):
    book_to_delete = Collection.query.get_or_404(id)

    try:
        db.session.delete(book_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was an error deleting that book'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    book_to_update = Collection.query.get_or_404(id)
    if request.method == 'POST':
        book_to_update.title = request.form['title']
        book_to_update.author = request.form['author']
        book_to_update.volume = request.form['volume']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your entry'
    else:
        return render_template('update.html', book = book_to_update)

#trying to create a path to display book details
@app.route('/book/<int:id>')
def display_info(id):
    #switched from id to title to account for larger or overlapping titles
    book = Collection.query.get_or_404(id)
    return render_template('book_details.html', book=book)



if __name__ == "__main__":
    app.run(debug=True)