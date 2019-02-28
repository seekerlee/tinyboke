import sqlite3
# import atexit
import time
from flask import g

DATABASE = 'database.db'
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def check_tables():
    conn = sqlite3.connect(DATABASE)
    TABLE_ARTICLE = """
    CREATE TABLE if not exists "article" (
        "id" INTEGER,
        "title" TEXT,
        "summary" TEXT,
        "content" TEXT,
        "ralease" INTEGER DEFAULT 0,
        "time_created" INTEGER,
        "time_last_modified" INTEGER,
        PRIMARY KEY("id")
    )"""
    cur = conn.cursor()
    cur.execute(TABLE_ARTICLE)
    conn.commit()
    conn.close()

check_tables()

def add(a, b):
    """This program adds two
    numbers and return the result"""

    result = a + b
    return result

def new_article():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("select IFNULL(max(id), 0) max_id from article where id=1")
    r = cur.fetchone()
    new_id = r['max_id'] + 1
    cur.execute("insert into article(id, time_created) values (?, ?)", (new_id, time.time()))
    conn.commit()
    return new_id

def update_article(blog_id, title, summary, content, release=False):
    print(title)
    conn = get_db()
    cur = conn.cursor()
    cur.execute("update article set title = ?, summary = ?, content = ?, ralease = ?, time_last_modified = ? where id = ?", (title, summary, content, release, time.time(), blog_id))
    conn.commit()

# def close_connection():
#     print('close_connection')
#     conn = get_db()
#     if conn is not None:
#         conn.close()
    
# atexit.register(close_connection)