import os

from flask import Flask, render_template, jsonify, request, redirect, url_for
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from teachers import teachers_reader, administration_reader
from datetime import datetime

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Site_data.db'
db = SQLAlchemy(app)


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Article %r>' % self.id

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/info')
def info():
    return render_template('info.html')


@app.route('/create-post', methods=['POST', 'GET'])
def create_post():
    if request.method == 'POST':
        title = request.form.get('title')
        text = request.form.get('content')
        passw = request.form.get('password')

        if not title or not text:

            return "Будь ласка, заповніть усі поля.", 400
        if passw != os.getenv('POST_PASS'):
            return redirect('/')

        article = Posts(title=title, text=text)
        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/posts')
        except Exception:
            return "Помилка при додаванні статті"

    return render_template('create_post.html')


@app.route('/delete-post', methods=['POST', 'GET'])
def delete_post():
    if request.method == 'POST':
        # Отримуємо ID та пароль із форми
        post_id = request.form.get('post_id')
        passw = request.form.get('pass')

        # Перевірка пароля
        if passw != os.getenv('POST_PASS'):
            return "Неправильний пароль!", 403

        # Перевіряємо, чи існує ID і чи є він числом
        try:
            post_id = int(post_id)
        except (ValueError, TypeError):
            return "Некоректний ID поста.", 400

        post_to_delete = Posts.query.get(post_id)

        if post_to_delete:
            try:
                db.session.delete(post_to_delete)
                db.session.commit()
                return redirect(url_for('delete_post', success=True))
            except Exception:
                return "Помилка при видаленні статті.", 500
        else:
            return "Пост з таким ID не знайдено.", 404

    return render_template('delete_post.html')

@app.route('/posts')
def posts():
    return render_template('desk.html')


@app.route('/get-posts-data')
def posts_sender():
    try:

        all_posts = Posts.query.order_by(Posts.date.desc()).all()

        posts_list = []
        for post in all_posts:
            posts_list.append({
                'id': post.id,
                'title': post.title,
                'text': post.text,
                'date': post.date.strftime("%Y-%m-%d")
            })
        return jsonify(posts_list)

    except Exception as e:
        print(f"Помилка при отриманні даних постів: {e}")
        return jsonify({"error": "Внутрішня помилка сервера"}), 500

@app.route('/administration')
def admin():
    return render_template('admin.html')

@app.route('/get-administration')
def get_admins():
    return administration_reader()

@app.route('/admission')
def admission():
    return render_template('vstup.html')

@app.route('/flash-mobs')
def flash_mob():
    return render_template('flsh_mob.html')

@app.route('/schedule')
def scedule():
    return render_template('scedule.html')

@app.route('/get-schedule')
def get_scedule():
    return jsonify({'Data' : "No data yet"})

@app.route('/shelter')
def sport():
    return render_template('shelter.html')

@app.route('/achievements')
def achievements():
    return render_template('dosa.html')

@app.route('/teachers')
def teachers():
    return render_template('te.html')

@app.route('/get-teachers')
def teachers_returners():
    return teachers_reader()

# 🔧 ПРАВИЛЬНЫЙ запуск ботов


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False, use_reloader=False)