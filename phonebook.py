__author__ = 'petermeckiffe'
# all the imports
import sqlite3
from contextlib import closing
from flask import Flask, g, request, make_response
import json, re, sys

# configuration
DATABASE = '/tmp/phonebook.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    '''Connect to DB'''
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    '''Initialise Database'''
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    '''Establish connection to DB before each query'''
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    '''Close connection to DB after each query'''
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/list', methods=['GET'])
def list_entries():
    '''List all entries in the phonebook'''
    cur = g.db.execute('select * from phonebook order by id desc')
    entries = [dict(id=row[0], forename=row[1], surname=row[2], telephone=row[3], address=row[4]) for row in cur.fetchall()]
    return make_response(json.dumps(entries), 200)

@app.route('/add', methods=['POST'])
def add_entry():
    '''Add an entry to the DB'''
    # Check if address has been provided, if no, set to blank string
    if 'address' in request.form:
        addr = request.form['address']
    else:
        addr = ""
    
    # Check if telephone number is valid
    if not valid_phone_number(request.form['telephone']):
            return make_response("Please enter valid phone number", 400)
    
    # Check if entry already exists
    if is_dup(request.form['forename'], request.form['surname'], request.form['telephone'], addr):
        return make_response("Entry already exists on the system", 409)
    
    # Add the entry to the DB
    g.db.execute('insert into phonebook (forename, surname, telephone, address) values (?, ?, ?, ?)',
                 [request.form['forename'], request.form['surname'], request.form['telephone'], addr])
    g.db.commit()
    return make_response("Success", 201)

def is_dup(forname, surname,tel, addr):
    '''Check if entry already exists, True if yes, False if no'''
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
    '''Takes ID as key, modifies properties of entry in the database, return code dependent on success'''
    # Check ID is in form
    if 'id' not in request.form:
        return make_response("Please provide a valid ID", 400)
    else:
        # Check ID exists in DB
        cur = g.db.execute('select * from phonebook WHERE id = "{}"'.format(request.form['id']))
        if len(list(cur.fetchall())) == 0:
            return make_response("Entry does not exist", 404)

    # Go through each of the fields checking if update has been requested, and updating each on the DB
    # Current solution is DB message heavy, can be improved.
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
    '''Check whether telephone number is valid. Takes telephone number as arg, returns True/False'''
    p = re.compile('(^[+0-9]{1,3})*([0-9]{10,11}$)')
    if p.match(request.form['telephone']) is None:
        return False
    else:
        return True


@app.route('/search/<name>')
def search_entries(name):
    '''Takes surname as argument, finds all entries with similar surname. Returns response that contains JSON object'''
    cur = g.db.execute('select * from phonebook WHERE surname LIKE "%{}%" order by id desc'.format(name))
    entries = [dict(id=row[0], forename=row[1], surname=row[2], telephone=row[3], address=row[4]) for row in cur.fetchall()]
    return make_response(json.dumps(entries), 200)

@app.route('/delete/<id>', methods=['DELETE'])
def delete_entry(id):
    '''Takes entry ID as argument, deletes entry from database if it exists. Returns response that contains Success or 404'''
    # Check that entry exists in database
    cur = g.db.execute('select * from phonebook WHERE id = "{}"'.format(id))
    if len(list(cur.fetchall())) == 0:
        return make_response("Entry does not exist", 404)

    # Perform delete
    g.db.execute('delete from phonebook where id = {}'.format(id))
    g.db.commit()
    return make_response("Success", 200)

# Accept a port as arg
if __name__ == '__main__':

    if len(sys.argv) > 1:
        try:
            app.run(port=int(sys.argv[1]))
        except:
            app.run()
    else:
        app.run()