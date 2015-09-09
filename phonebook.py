__author__ = 'petermeckiffe'
# all the imports
import sqlite3
from contextlib import closing
from flask import Flask, g, jsonify, request, flash, make_response
import json, re

# configuration
DATABASE = '/tmp/phonebook.db'
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

@app.route('/list', methods=['GET'])
def list_entries():
    cur = g.db.execute('select * from phonebook order by id desc')
    entries = [dict(id=row[0], forename=row[1], surname=row[2], telephone=row[3], address=row[4]) for row in cur.fetchall()]
    return make_response(json.dumps(entries), 200)

@app.route('/add', methods=['POST'])
def add_entry():
    if 'address' in request.form:
        addr = request.form['address']
    else:
        addr = ""
    if not valid_phone_number(request.form['telephone']):
            return make_response("Please enter valid phone number", 400)

    if is_dup(request.form['forename'], request.form['surname'], request.form['telephone'], addr):
        return make_response("", 401)

    g.db.execute('insert into phonebook (forename, surname, telephone, address) values (?, ?, ?, ?)',
                 [request.form['forename'], request.form['surname'], request.form['telephone'], addr])
    g.db.commit()
    return make_response("Success", 200)

def is_dup(forname, surname,tel, addr):
    cur = g.db.execute('select * from phonebook WHERE forename = "{}" \
    AND surname = "{}" \
    AND telephone = "{}" \
    AND address = "{}" order by id desc'.format(forname, surname,tel, addr))
    if len(list(cur.fetchall())) > 0:
        return True
    else:
        return False

@app.route('/update', methods=['PUT'])
def update_entry():
    if 'id' not in request.form:
        return make_response("", 400)
    else:
        cur = g.db.execute('select * from phonebook WHERE id = "{}"'.format(request.form['id']))
        if len(list(cur.fetchall())) == 0:
            return make_response("", 404)
    if 'address' in request.form:
        g.db.execute('update phonebook set address = "{}" where id = {}'.format(request.form['address'],request.form['id']))
    if 'forename' in request.form:
        g.db.execute('update phonebook set forename = "{}" where id = {}'.format(request.form['forename'],request.form['id']))
    if 'surname' in request.form:
        g.db.execute('update phonebook set surname = "{}" where id = {}'.format(request.form['surname'],request.form['id']))
    if 'telephone' in request.form:
        if not valid_phone_number(request.form['telephone']):
            return make_response("Please enter valid phone number", 400)
        g.db.execute('update phonebook set telephone = "{}" where id = {}'.format(request.form['telephone'],request.form['id']))

    g.db.commit()
    return make_response("Success", 200)

def valid_phone_number(telephone):
    p = re.compile('(^[+0-9]{1,3})*([0-9]{10,11}$)')
    if p.match(request.form['telephone']) is None:
        return False
    else:
        return True


@app.route('/search/<name>')
def search_entries(name):
    cur = g.db.execute('select * from phonebook WHERE surname LIKE "%{}%" order by id desc'.format(name))
    entries = [dict(id=row[0], forename=row[1], surname=row[2], telephone=row[3], address=row[4]) for row in cur.fetchall()]
    return make_response(json.dumps(entries), 200)

@app.route('/delete/<id>', methods=['DELETE'])
def delete_entry(id):
    g.db.execute('delete from phonebook where id = {}'.format(id))
    g.db.commit()
    return make_response("", 200)

if __name__ == '__main__':
    app.run()
    init_db()