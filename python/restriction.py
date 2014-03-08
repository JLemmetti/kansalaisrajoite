# coding=utf-8
from bottle import Bottle, HTTPError, request
from sqlalchemy.orm.exc import NoResultFound

import model
from utils import session_user, jsonplugin


app = Bottle()
app.install(model.plugin)
app.install(jsonplugin)


@app.get('/<id:int>')
def read_one(db, id):
    try:
        user = session_user(request, db)
        is_admin = user and user.admin

        item = db.query(model.Restriction).filter_by(id=id).one()

        if not item.approved and user != item.user and not is_admin:
            return HTTPError(403, 'Forbidden')

        return item.toDict(is_admin, user)
    except NoResultFound:
        return HTTPError(404, 'Not found')


@app.get('/')
def read_all(db):
    user = session_user(request, db)
    is_admin = user and user.admin

    if is_admin:
        items = db.query(model.Restriction)
    elif user:
        items = db.query(model.Restriction).filter(
            (model.Restriction.approved) |
            (model.Restriction.user == user))
    else:
        items = db.query(model.Restriction).filter(
            model.Restriction.approved)

    return {'restrictions': [i.toDict(is_admin, user) for i in items]}


@app.post('/')
def create(db):
    user = session_user(request, db)

    if not user:
        return HTTPError(401, 'Unauthorized')

    item = model.Restriction()
    item.title = request.forms.get('title')
    item.body = request.forms.get('body')
    item.user = user
    item.user_name = user.name
    item.user_city = user.city

    db.add(item)
    db.flush()

    return {'id': item.id, 'title': item.title}


@app.delete('/<id:int>')
def delete(db, id):
    try:
        user = session_user(request, db)
        is_admin = user and user.admin

        if not user:
            return HTTPError(401, 'Unauthorized')

        item = db.query(model.Restriction).filter_by(id=id).one()

        if user != item.user and not is_admin:
            return HTTPError(403, 'Forbidden')

        db.delete(item)
    except NoResultFound:
        return HTTPError(404, 'Not found')


@app.post('/<id:int>/vahvista')
def approve(db, id):
    try:
        user = session_user(request, db)
        is_admin = user and user.admin

        if not is_admin:
            return HTTPError(403, 'Forbidden')

        item = db.query(model.Restriction).filter_by(id=id).one()
        item.approved = not item.approved
        item.approver = user
    except NoResultFound:
        return HTTPError(404, 'Not found')
