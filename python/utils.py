# coding=utf-8
import model
import json
import datetime
import random
import string
from bottle import JSONPlugin

def session_user(request, db):
	session = request.environ.get('beaker.session')
	if not session:
		print 'beaker.session not available'
		return None
	
	user_id = session.get('user_id')
	
	if not user_id:
		return None
	
	return db.query(model.User).filter_by(id=user_id).first()

def gen_token():
	return ''.join(random.choice(string.ascii_letters + string.digits) for x in range(32))

class JsonEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, datetime.datetime):
			return int(obj.strftime('%s'))
		if isinstance(obj, datetime.date):
			return int(obj.strftime('%s'))
		return json.JSONEncoder.default(self, obj)

jsonplugin = JSONPlugin(json_dumps=lambda s: json.dumps(s, cls=JsonEncoder))
