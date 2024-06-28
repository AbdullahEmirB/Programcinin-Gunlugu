from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret_key'

db = SQLAlchemy(app)

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(300), nullable=False)
    text = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<Card {self.id}>'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<User {self.id}>'

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['current_user'] = user.username
            return redirect(url_for('index'))
        else:
            flash('Yanlış kullanıcı adı veya şifre')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('registration.html')

@app.route('/index')
def index():
    if 'current_user' not in session:
        return redirect(url_for('login'))
    cards = Card.query.order_by(Card.id).all()
    return render_template('index.html', cards=cards)

@app.route('/card/<int:id>')
def card(id):
    if 'current_user' not in session:
        return redirect(url_for('login'))
    card = Card.query.get(id)
    return render_template('card.html', card=card)

@app.route('/create')
def create():
    if 'current_user' not in session:
        return redirect(url_for('login'))
    return render_template('create_card.html')

@app.route('/form_create', methods=['GET', 'POST'])
def form_create():
    if 'current_user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        subtitle = request.form['subtitle']
        text = request.form['text']
        card = Card(title=title, subtitle=subtitle, text=text)
        db.session.add(card)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create_card.html')

@app.route('/delete/<int:id>', methods=['POST'])
def delete_card(id):
    if 'current_user' not in session:
        return redirect(url_for('login'))
    card = Card.query.get_or_404(id)
    db.session.delete(card)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('current_user', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
