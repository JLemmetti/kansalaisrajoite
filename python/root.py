# coding=utf-8
from bottle import Bottle, HTTPError, static_file, redirect, hook, request
import restriction
import vote
import user
import beaker.middleware
from model import dburl

app = Bottle()
app.mount('/rajoite', restriction.app)
app.mount('/kannatus', vote.app)
app.mount('/kayttaja', user.app)

@app.get('/')
def index():
	return static_file('index.html', root='../static/')

@app.get('/<path:path>')
def getfile(path):
	return static_file(path, root='../static/')

session_opts = {
	'session.type': 'ext:database',
	'session.url': dburl,
	'session.auto': True,
	'session.lock_dir': '/var/lock'
}

middleware_app = beaker.middleware.SessionMiddleware(app, session_opts)
