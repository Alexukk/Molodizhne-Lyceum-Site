import json



def teachers_reader():
    try:
        with open("./static/DB/teachers.json", "r", encoding='utf8') as file:
            data = json.load(file)
            return data
    except Exception:
        return 0



def administration_reader():
    try:
        with open("./static/DB/administration.json", "r", encoding='utf8') as file:
            data = json.load(file)
            return data
    except Exception:
        return 0