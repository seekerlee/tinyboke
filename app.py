from flask import Flask, url_for, redirect, jsonify
from flask import render_template
from flask import request
from flask import g
import bcrypt

from db.db import new_article, update_article, get_article, list_articles, get_config, set_config

app = Flask(__name__)

# pages:
@app.route('/')
def hello_world():
    page_number = request.args.get('page', 1, type = int) # page_number from 1
    print(page_number)
    articles = list_articles(page_number - 1)
    return render_template('index.jinja', articles=articles)

@app.route('/blog/create')
def create_blog():
    print('creating blog...')
    # add new article to db, and get id
    new_id = new_article()
    # redirect to editing
    return redirect(url_for('show_blog', blog_id=new_id) + '?edit')

@app.route('/blog/<int:blog_id>')
def show_blog(blog_id):
    edit = request.args.get('edit')
    # get blog from database
    article = get_article(blog_id)
    title = article["title"]
    content = article["content"]
    if edit is not None:
        print('editing blog...')
        print('editing existing blog...')
        return render_template('article-edit.jinja', title=title, content=content)
    else:
        print('reading blog...')
        return render_template('article-view.jinja', title=title, content=content)

# api:
@app.route('/blog/<int:blog_id>', methods=['POST'])
def save_blog(blog_id):
    jjson = request.get_json()
    # save to database
    update_article(blog_id, jjson['title'], jjson['summary'], jjson['content'], jjson['release'])
    return 's'

@app.route('/password', methods=['POST'])
def change_password():
    print('change_password: ')
    jjson = request.get_json()
    pass_new = jjson['passwordNew']
    pass_hashed = get_config('password')
    print('pass_new: ' + pass_new)
    print('pass_hashed: ' + str(pass_hashed))
    if ('passwordCurrent' in jjson):
        pass_input = jjson['passwordCurrent']
        print('pass_input: ' + pass_input)
        if bcrypt.checkpw(pass_input.encode('utf-8'), pass_hashed):
            print('pass match')
            new_pass_hashed = bcrypt.hashpw(pass_new.encode('utf-8'), bcrypt.gensalt())
            set_config('password', new_pass_hashed)
            return jsonify({"message" : "password updated"}), 200
        else:
            print('pass not match')
            return jsonify({"error" : "password does not match"}), 403
    elif pass_hashed is None: # when server init there's no password
        new_pass_hashed = bcrypt.hashpw(pass_new.encode('utf-8'), bcrypt.gensalt())
        set_config('password', new_pass_hashed)
        return jsonify({"message" : "password updated"}), 200
    else:
        return jsonify({"error" : "no current password provided"}), 403

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()