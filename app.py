from flask import Flask, url_for, redirect, jsonify, session
from flask import render_template
from flask import request
from flask import g
from datetime import timedelta
import os
import bcrypt

from db.db import new_article, delete_article, update_article, get_article, list_articles, get_config, set_config

app = Flask(__name__)
app.secret_key = os.urandom(16)
app.permanent_session_lifetime = timedelta(minutes=5)

# pages:
@app.route('/')
def index():
    page_number = request.args.get('page', 1, type = int) # page_number from 1
    print(page_number)
    logined = session.get('login') == True
    articles = list_articles(page_number - 1, not logined)
    site_name = get_config("site_name")
    site_desc = get_config("site_desc")
    return render_template('index.jinja', articles=articles, site_name=site_name, site_desc=site_desc, logined=logined)

@app.route('/console')
def console():
    if session.get('login') != True:
        return redirect(url_for('login'))
    site_name = get_config("site_name")
    site_desc = get_config("site_desc")
    return render_template('console.jinja', site_name=site_name, site_desc=site_desc)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        pass_input = request.form['password']
        pass_hashed = get_config('password')
        if bcrypt.checkpw(pass_input.encode('utf-8'), pass_hashed):
            session['login'] = True
            return redirect(url_for('console'))
        else:
            return render_template('login.jinja', message="login failed")
    else:
        return render_template('login.jinja')

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('login', None)
    return redirect(url_for('index'))

@app.route('/blog/create')
def create_blog():
    if session.get('login') == True:
        print('creating blog...')
        # add new article to db, and get id
        new_id = new_article()
        # redirect to editing
        return redirect(url_for('show_blog', blog_id=new_id) + '?edit')
    else:
        return redirect(url_for('index'))

@app.route('/blog/<int:blog_id>')
def show_blog(blog_id):
    edit = request.args.get('edit')
    # get blog from database
    article = get_article(blog_id)
    if edit is not None:
        if session.get('login') == True:
            print('editing blog...')
            print('editing existing blog...')
            return render_template('article-edit.jinja', article=article)
        else:
            return redirect(url_for('login'))
    else:
        print('reading blog...')
        return render_template('article-view.jinja', article=article, logined=session.get('login') == True)

# api:
@app.route('/blog/<int:blog_id>', methods=['POST'])
def save_blog(blog_id):
    if session.get('login') == True:
        jjson = request.get_json()
        # save to database
        update_article(blog_id, jjson['title'], jjson['summary'], jjson['content'], jjson['release'])
        return jsonify({"message" : "article updated"})
    else:
        return jsonify({"error" : "please login"}), 403

@app.route('/blog/<int:blog_id>', methods=['DELETE'])
def delete_blog(blog_id):
    if session.get('login') == True:
        delete_article(blog_id)
        return jsonify({"message" : "article deleted"})
    else:
        return jsonify({"error" : "please login"}), 403

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
            return jsonify({"message" : "password updated"})
        else:
            print('pass not match')
            return jsonify({"error" : "password does not match"}), 403
    elif pass_hashed is None: # when server init there's no password
        new_pass_hashed = bcrypt.hashpw(pass_new.encode('utf-8'), bcrypt.gensalt())
        set_config('password', new_pass_hashed)
        return jsonify({"message" : "password updated"}), 200
    else:
        return jsonify({"error" : "no current password provided"}), 403

@app.route('/config', methods=['POST'])
def change_config():
    if session.get('login') != True:
        return jsonify({"error" : "please login"}), 403
    jjson = request.get_json()
    site_name = jjson['siteName']
    site_desc = jjson['siteDesc']
    set_config('site_name', site_name)
    set_config('site_desc', site_desc)
    return jsonify({"message": "config updated"}), 200

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()