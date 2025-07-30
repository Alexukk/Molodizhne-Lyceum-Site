from flask import Flask, render_template, redirect, jsonify
from dotenv import load_dotenv
from json_storage import load_posts
from scedule_updater import scedule_reader
load_dotenv()

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')



@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/info')
def info():
    return render_template('info.html')

# добавить логику добавления постов с бота и путь который шлет это на js
@app.route('/posts')
def posts():
    return render_template('desk.html')

@app.route('/get-posts-data')
def posts_sender():
    data = load_posts()
    return jsonify(data)



# Надо создать джсон с администрацией и его отрисовку через fetch на js, добавить путь с инфой про админов
@app.route('/administration')
def admin():
    return render_template('admin.html')

@app.route('/admission')
def admission():
    return render_template('vstup.html')

# можно добавлять новые посты через бота + новый путь
@app.route('/flash-mobs')
def flash_mob():
    return render_template('flsh_mob.html')

# тоже можно добавить замену ссылок на розклад через бота и добавить новый путь
@app.route('/scedule')
def scedule():
    return render_template('scedule.html')

@app.route('/get-schedule')
def get_scedule():
    data = scedule_reader()
    return jsonify(data)

@app.route('/shelter')
def sport():
    return render_template('shelter.html')

@app.route('/achievements') 
def achievements(): 
    return render_template('dosa.html')


# полностью переработать страницу с учителями и новый путь для js чтобы отрисовывать учителей 
@app.route('/teachers')
def teachers():
    return render_template('/te.html')


if __name__ == '__main__':
    app.run(debug=True)