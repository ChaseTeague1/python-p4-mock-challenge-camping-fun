#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return ''

class Campers(Resource):
    def get(self):
        campers = Camper.query.all()
        camper_dict = [camper.to_dict(rules=('-signups',)) for camper in campers]
        return make_response(camper_dict, 200)
    
    def post(self):
        data = request.get_json()
        try:
            camper = Camper(
                name = data['name'],
                age = data['age'],
            )
            db.session.add(camper)
            db.session.commit()
            return make_response(camper.to_dict(), 201)
        except ValueError:
            return make_response({'errors' : ['validation error']} , 400)

api.add_resource(Campers, '/campers')


class CampersById(Resource):
    def get(self, id):
        camper = Camper.query.filter(Camper.id == id).first()
        if not camper:
            return {"error" : "Camper not found"}, 404
        return make_response(camper.to_dict(), 200)
        
    def patch(self, id):
        camper = Camper.query.filter(Camper.id == id).first()
        if camper:
            data = request.get_json()
            try:
                setattr(camper, 'name', data['name'])
                setattr(camper, 'age', data['age'])
                db.session.add(camper)
                db.session.commit()

                return make_response(camper.to_dict(rules = ('-signups',)), 202)
            
            except ValueError:
                return make_response({'errors': ['validation errors']}, 400)
        else:
            return make_response({"error" : "Camper not found"}, 404)


api.add_resource(CampersById, '/campers/<int:id>')


class Activities(Resource):
    def get(self):
        activties = [activity.to_dict() for activity in Activity.query.all()]
        return make_response(activties, 200)

api.add_resource(Activities, '/activities')

class ActivitiesById(Resource):
    def delete(self, id):
        activity = Activity.query.filter(Activity.id == id).first()
        if activity:
            db.session.delete(activity)
            db.session.commit()

            body = {}
            return make_response(body, 204)
        return {'error' : 'Activity not found'} , 404
    
api.add_resource(ActivitiesById, '/activities/<int:id>')

class Signups(Resource):
    def post(self):
        data = request.get_json()
        try:
            signup = Signup(
                camper_id = data['camper_id'],
                activity_id = data['activity_id'],
                time = data['time'],
            )
            db.session.add(signup)
            db.session.commit()

            return make_response(signup.to_dict(), 201)
        except ValueError:
            return make_response({'errors' : ['validation errors']}, 400)
        
api.add_resource(Signups, '/signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
