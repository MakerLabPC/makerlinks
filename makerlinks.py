import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
	render_template, flash

# create makerlinks application
app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
	DATABASE = os.path.join(app.root_path, 'makerlinks-dev.db'),
	DEBUG = True,
	APP_NAME = "MakerLinks",
	SECRET_KEY = 'development key',
	USERNAME = 'admin',
	PASSWORD = 'default'
))
app.config.from_envvar('MAKERLINKS_SETTINGS', silent = True)

def connect_db():
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row
	return rv

def get_db():
	if not hasattr(g, 'sqlite_db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db

def init_db():
	with app.app_context():
		db = get_db()
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

@app.teardown_appcontext
def close_db(error):
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()

@app.route('/')
def show_links():
	db = get_db()
	cur = db.execute('select link, submitter from links order by id desc')
	links = cur.fetchall()
	return render_template('show_links.html', links=links)

@app.route('/add', methods=['POST'])
def add_link():
	db = get_db()
	db.execute('insert into links (link, submitter) values (?, ?)',
					[request.form['link'], request.form['submitter']])
	db.commit()
	flash('New link was successfully posted')
	return redirect(url_for('show_links'))

if __name__ == "__main__":
	if not os.path.exists(app.config['DATABASE']):
		init_db()
	app.run()
