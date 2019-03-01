from flask import Flask, url_for, redirect
from flask import render_template
from flask import request
from flask import g

from db.db import new_article, update_article, get_article, list_articles

app = Flask(__name__)

# pages:
@app.route('/')
def hello_world():
    articles = list_articles(0)
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

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()