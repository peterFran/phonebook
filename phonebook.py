__author__ = 'petermeckiffe'
# all the imports
import sqlite3
from contextlib import closing
from flask import Flask, g, jsonify, request, flash, make_response
import json

# configuration
DATABASE = 'phonebook.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/', methods=['GET'])
def show_entries():
    cur = g.db.execute('select * from phonebook order by id desc')
    entries = [dict(id=row[0], forename=row[1], surname=row[2], telephone=row[3], address=row[4]) for row in cur.fetchall()]
    return make_response(json.dumps(entries), 200)

@app.route('/add', methods=['POST'])
def add_entry():
    g.db.execute('insert into phonebook (forename, surname, telephone, address) values (?, ?, ?, ?)',
                 [request.form['forename'], request.form['surname'], request.form['telephone'], request.form['address']])
    g.db.commit()
    return make_response("", 200)

@app.route('/search/<name>')
def search_entries(name):
    cur = g.db.execute('select * from phonebook WHERE surname LIKE "%{}%" order by id desc'.format(name))
    entries = [dict(id=row[0], forename=row[1], surname=row[2], telephone=row[3], address=row[4]) for row in cur.fetchall()]
    return make_response(json.dumps(entries), 200)

if __name__ == '__main__':
    app.run()