# coding=utf-8
from bottle import Bottle, HTTPError, request
import model
import bcrypt
import datetime
from utils import session_user, jsonplugin
from sqlalchemy.orm.exc import NoResultFound

app = Bottle()
app.install(model.plugin)
app.install(jsonplugin)

@app.post('/rekisteroidy')
def register(db):
	email = request.forms.get('email')
	name = request.forms.get('name')
	password = request.forms.get('password')
	city = request.forms.get('city')
	
	if not password or len(password) < 8:
		return HTTPError(400, 'Bad request')
	
	if not email or len(email) == 0:
		return HTTPError(400, 'Bad request')
	
	if db.query(model.User).filter_by(email=email).first():
		return HTTPError(409, 'Conflict')
	
	user = model.User()
	user.email = email
	
	if name and len(name) > 0:
		user.name = name
	
	if city and len(city) > 0:
		user.city = city
	
	user.password = bcrypt.hashpw(password, bcrypt.gensalt())
	db.add(user)

@app.post('/login')
def login(db):
	email = request.forms.get('email')
	password = request.forms.get('password')
	
	if not email or not password:
		return HTTPError(400, 'Bad request')
	
	user = db.query(model.User).filter_by(email=email).first()
	
	if user and bcrypt.hashpw(password, user.password.encode('utf-8')) == user.password:
		session = request.environ['beaker.session']
		session['user_id'] = user.id
		return user.toDict()
	else:
		return HTTPError(401, 'Unauthorized')

@app.post('/logout')
def logout(db):
	session = request.environ.get('beaker.session')
	
	if session:
		session.delete()
	else:
		return HTTPError(401, 'Unauthorized')

@app.get('/')
def my_data(db):
	user = session_user(request, db)
	
	if user:
		return user.toDict()
	else:
		return {}

@app.get('/<id:int>')
def read_user(db, id):
	try:
		user = session_user(request, db)
		is_admin = user and user.admin
		
		if not is_admin:
			return HTTPError(401, 'Unauthorized')
		
		item = db.query(model.User).filter_by(id=id).one()
		return item.toDict(True)
	except NoResultFound:
		return HTTPError(404, 'Not found')
