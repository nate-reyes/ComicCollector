from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests #beginning to build API integration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date_entry = db.Column(db.DateTime, default=datetime.utcnow)
    publisher = db.Column(db.String(200), nullable=True)
    creative_team = db.Column(db.Text, nullable=True)
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
    #     book_title = request.form['title']
    #     book_author = request.form['author']
    #     book_volume = request.form['volume']
    #     new_book = Collection(
    #         title = book_title,
    #         author = book_author,
    #         volume = book_volume
    #     )
        gcd_url = request.form['gcd_url']

        print(type(gcd_url))
        print(gcd_url)
        response = requests.get(
            gcd_url,
            headers={"Accept": "application/json"}
        )

        issue_data = response.json()

        print(issue_data['series_name'])
        print(issue_data['title'])
        print(issue_data['number'])

        api_title = issue_data['series_name']
        api_volume = issue_data['volume']
        api_cover_url = issue_data['cover']

        api_creative_team = "placeholder"

        new_book = Collection(
            title = api_title,
            volume = api_volume,
            creative_team = api_creative_team,
            cover_url = api_cover_url
        )
        try:
            db.session.add(new_book)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return f'There was an error adding your book {e}'
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
    #switched from title to id to account for larger or overlapping titles
    book = Collection.query.get_or_404(id)
    return render_template('book_details.html', book=book)


@app.route('/search')
def search():
    search_query = request.args.get('query')
    
    url = f"https://www.comics.org/api/series/name/{search_query}/"

    
    response = requests.get(
        url,
        headers={"Accept": "application/json"})
    
    data = response.json()
    
    results = []

    for item in data['results']:
        results.append({
            'title': item['name'],
            'volume': item['year_began'],
            'gcd_url': item['active_issues'][0]
        })
    return render_template('search_results.html', query=search_query, results=results)

if __name__ == "__main__":
    app.run(debug=True)