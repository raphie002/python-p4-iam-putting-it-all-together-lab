#!/usr/bin/env python3
# server/app.py
from flask import request, session
from flask_restful import Resource # type: ignore
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        request_json = request.get_json()
        try:
            user = User(
                username=request_json.get('username'),
                image_url=request_json.get('image_url'),
                bio=request_json.get('bio')
            )
            user.password_hash = request_json.get('password')
            
            db.session.add(user)
            db.session.commit()
            
            session['user_id'] = user.id
            return user.to_dict(), 201
        except (IntegrityError, ValueError) as e:
            return {"errors": ["validation errors"]}, 422

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            return user.to_dict(), 200
        return {"error": "Unauthorized"}, 401

class Login(Resource):
    def post(self):
        request_json = request.get_json()
        user = User.query.filter(User.username == request_json.get('username')).first()
        
        if user and user.authenticate(request_json.get('password')):
            session['user_id'] = user.id
            return user.to_dict(), 200
        return {"error": "Invalid username or password"}, 401

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session['user_id'] = None
            return {}, 204
        return {"error": "Unauthorized"}, 401

class RecipeIndex(Resource):
    def get(self):
        if session.get('user_id'):
            recipes = [recipe.to_dict() for recipe in Recipe.query.all()]
            return recipes, 200
        return {"error": "Unauthorized"}, 401

    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {"error": "Unauthorized"}, 401
            
        request_json = request.get_json()
        try:
            recipe = Recipe(
                title=request_json.get('title'),
                instructions=request_json.get('instructions'),
                minutes_to_complete=request_json.get('minutes_to_complete'),
                user_id=user_id
            )
            db.session.add(recipe)
            db.session.commit()
            return recipe.to_dict(), 201
        except (IntegrityError, ValueError) as e:
            return {"errors": ["validation errors"]}, 422

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')

if __name__ == '__main__':
    app.run(port=5555, debug=True)