from flask import jsonify, request, url_for, abort
from app import db
from app.base.models import User, Poem
from app.api import bp
from app.api.auth import token_auth, basic_auth
from app.api.errors import bad_request


@bp.route('/poems/stamp_used/<int:id>', methods=['PUT'])
@token_auth.login_required
def stamp_used_poem(id):
    if token_auth.current_user().id != 1:
        abort(403)
    poem = Poem.query.get_or_404(id)
    data = request.get_json() or {}
    try:
        poem.stamp_used(data['used'])
    except KeyError:
        poem.stamp_used()
    db.session.commit()
    return jsonify(poem.to_dict())


@bp.route('/poems/stampUsed/<int:id>', methods=['GET'])
@token_auth.login_required
def get_poem(id):
    return jsonify(Poem.query.get_or_404(id).to_dict())


@bp.route('/poems/approved', methods=['GET'])
@token_auth.login_required
def get_approved_poems():
    if token_auth.current_user().id != 1:
        abort(403)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Poem.to_collection_dict(Poem.query.filter(Poem.approved==1, Poem.used==0), page, per_page, 'api.get_approved_poems')
    return jsonify(data)


@bp.route('/poems/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_poem(id):
    if token_auth.current_user().id != 1:
        abort(403)
    poem = Poem.query.get_or_404(id)
    data = request.get_json() or {}
    poem.from_dict(data)
    db.session.commit()
    return jsonify(poem.to_dict())


@bp.route('/poems', methods=['POST'])
@token_auth.login_required
def create_poem():
    if token_auth.current_user().id != 1:
        abort(403)
    data = request.get_json() or {}
    if 'body' not in data:
        return bad_request('must include body field')
    if Poem.query.filter_by(body=data['body']).first():
        return bad_request('Poem already in database.')
    poem = Poem()
    poem.from_dict(data)
    db.session.add(poem)
    db.session.commit()
    response = jsonify(poem.to_dict())
    response.status_code = 201
    #response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response


#@token_auth.login_required
@bp.route('/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    return jsonify(User.query.get_or_404(id).to_dict())


@bp.route('/users', methods=['GET'])
@token_auth.login_required
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(User.query, page, per_page, 'api.get_users')
    return jsonify(data)


@bp.route('/users', methods=['POST'])
@token_auth.login_required
def create_user():
    data = request.get_json() or {}
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return bad_request('must include username, email and password fields')
    if User.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response

@bp.route('/users/delete/<int:id>', methods=['PUT'])
def delete_user(id):
    if token_auth.current_user().id != 1:
        abort(403)
    return None

@bp.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    if token_auth.current_user().id != id:
        abort(403)
    user = User.query.get_or_404(id)
    data = request.get_json() or {}
    if 'username' in data and data['username'] != user.username and \
            User.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')
    if 'email' in data and data['email'] != user.email and \
            User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    user.from_dict(data, new_user=False)
    db.session.commit()
    return jsonify(user.to_dict())
