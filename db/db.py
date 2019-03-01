import sqlite3
# import atexit
import time
from flask import g

DATABASE = 'database.db'
PAGESIZE = 5

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE, check_same_thread=False)
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

def new_article():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("select IFNULL(max(id), 0) max_id from article")
    r = cur.fetchone()
    new_id = r['max_id'] + 1
    cur.execute("insert into article(id, time_created) values (?, ?)", (new_id, int(time.time())))
    conn.commit()
    return new_id

def update_article(blog_id, title, summary, content, release=False):
    print(title)
    conn = get_db()
    cur = conn.cursor()
    cur.execute("update article set title = ?, summary = ?, content = ?, ralease = ?, time_last_modified = ? where id = ?", (title, summary, content, release, int(time.time()), blog_id))
    conn.commit()

def get_article(blog_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("select * from article where id = ?", (blog_id,))
    r = cur.fetchone()
    print(r)
    return r

def list_articles(page_number): #page_number start from 0
    offset = page_number * PAGESIZE
    conn = get_db()
    cur = conn.cursor()
    cur.execute("select id, title, summary, ralease, time_created, time_last_modified from article order by time_created desc LIMIT ? OFFSET ?", (PAGESIZE, offset))
    r = cur.fetchall()
    print(r)
    return r


# def close_connection():
#     print('close_connection')
#     conn = get_db()
#     if conn is not None:
#         conn.close()
    
# atexit.register(close_connection)