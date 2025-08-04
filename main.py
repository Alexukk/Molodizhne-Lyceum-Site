from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
from json_storage import load_posts
from scedule_updater import scedule_reader
from teachers import teachers_reader, administration_reader
import os
import threading
from bot import start_admin_bot
from application_bot import start_application_bot

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

@app.route('/posts')
def posts():
    return render_template('desk.html')

@app.route('/get-posts-data')
def posts_sender():
    data = load_posts()
    return jsonify(data)

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
    data = scedule_reader()
    return jsonify(data)

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
def run_bots():
    threading.Thread(target=start_admin_bot, daemon=True).start()
    threading.Thread(target=start_application_bot, daemon=True).start()

if __name__ == '__main__':
    run_bots()
    app.run(debug=False, use_reloader=False)  # 🔥 КРИТИЧЕСКО — иначе поток ломается!
