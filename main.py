from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
from json_storage import load_posts
from scedule_updater import scedule_reader
from teachers import teachers_reader, administration_reader
from json_storage import save_post, delete_post_by_id

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

@app.route('/update-posts', methods=['POST'])
def posts_updater():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON received"}), 400

    if data.get("title") == "DELETE":
        post_id = data.get("id")
        if not post_id:
            return jsonify({"error": "No post id for deletion"}), 400
        try:
            delete_post_by_id(post_id)
            return jsonify({"success": "Post was deleted"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Получаем поля для добавления/обновления поста
    title = data.get("title")
    post_id = data.get("id")
    text = data.get("text")
    date = data.get("Date")

    if not all([title, post_id, text, date]):
        return jsonify({"error": "Missing one or more required fields"}), 400

    new_post = {
        "title": title,
        "id": post_id,
        "Date": date,
        "text": text
    }

    try:
        save_post(new_post)
        return jsonify({"success": "Post was added"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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


if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)  # 🔥 КРИТИЧЕСКО — иначе поток ломается!
