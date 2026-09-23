from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_entry = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Book %r>' % self.id


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        book_content = request.form['content']
        new_book = Collection(content = book_content)

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
        book_to_update.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your entry'
    else:
        return render_template('update.html', book_to_update = book_to_update)

if __name__ == "__main__":
    app.run(debug=True)