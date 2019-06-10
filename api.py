from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py
api = Api(app)

class get_entries(Resource):
    def get(self):
        db = get_db()
        cur = db.execute('select title, text from entries order by id desc')
        columns = [column[0] for column in cur.description]
        entries = cur.fetchall()
        results = []
        for entry in entries:
            results.append(dict(zip(columns, entry)))
        return {'data': results }

class post_entries(Resource):
    def post(self):
        if not session.get('logged_in'):
            abort(401)
        parser = reqparse.RequestParser()
        parser.add_argument('title')
        parser.add_argument('text')
        args = parser.parse_args()
        db = get_db()
        db.execute('insert into entries (title, text) values (?, ?)',[args['title'], args['text']])
        db.commit()
        return {'message' : 'New entry was successfully posted'}
    

class login(Resource):
    def post(self):
        display = {'message':'You were logged in'}
        parser = reqparse.RequestParser()
        parser.add_argument('username')
        parser.add_argument('password')
        args = parser.parse_args()

        if args['username'] != app.config['USERNAME']:
            display = {'message' : 'Invalid username'}
        elif args['password'] != app.config['PASSWORD']:
            display = {'message' : 'Invalid password'}
        else:
            session['logged_in'] = True
        return display

class logout(Resource):
    def get(self):
        session.pop('logged_in', None)
        return {'message' : 'You were logged out'}

class Test(Resource):
    def get(self):
        return{'tisteng':'this is tist'}    

#Define routes
api.add_resource(get_entries, '/get-entries')
api.add_resource(post_entries, '/post-entries')
api.add_resource(login, '/login')
api.add_resource(logout, '/logout')
api.add_resource(Test, '/test')

#Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=5000)
