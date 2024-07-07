#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, jsonify, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class Restaurants(Resource):
    def get(self):
        #we can use "only" or "rules" to set the return format with our to_dict()
        restaurants = [restaurant.to_dict(rules=("-restaurant_pizzas",)) for restaurant in Restaurant.query.all()]
        return make_response(jsonify(restaurants), 200)



class RestaurantById(Resource):
    def get(self, id):
        res = Restaurant.query.filter_by(id=id).one_or_none()

        # import ipdb; ipdb.set_trace()
        if res is not None:
            return make_response(res.to_dict(), 200)
        else:
            return make_response({"error": "Restaurant not found"}, 404)
    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first_or_404()
        if restaurant is not None:
            db.session.delete(restaurant)
            db.session.commit()
            return make_response('', 204)
        return make_response({"error": "Restaurant not found"}, 404)

class Pizzas(Resource):
    def get(self):
        #we can use "only" or "rules" to set the return format with our to_dict()
        pizzas = [pizza.to_dict(only=("id", "ingredients", "name")) for pizza in Pizza.query.all()]
        return make_response(jsonify(pizzas), 200)

class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()

        try:
            
            restaurant_pizza = RestaurantPizza(
                price = data["price"],
                pizza_id = data["pizza_id"],
                restaurant_id = data["restaurant_id"],
            )
        
            db.session.add(restaurant_pizza)
            db.session.commit()

            return make_response(restaurant_pizza.to_dict(), 201)
        
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)

        
    


api.add_resource(RestaurantPizzas, '/restaurant_pizzas')  
api.add_resource(Pizzas, '/pizzas')
api.add_resource(Restaurants, '/restaurants')
api.add_resource(RestaurantById, '/restaurants/<int:id>')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
