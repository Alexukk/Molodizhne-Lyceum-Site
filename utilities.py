import json



def load_post(post):
    with open('/Static/DB/posts.json', 'a+', encoding='utf8') as file:
        data = json.load(file)
        data += post
        json.dump(data, fp=file)
        return True