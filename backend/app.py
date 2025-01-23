from flask import Flask, jsonify
from flask_cors import CORS
import json
import random
from sqlalchemy import func
from app.models import DiveSite
from app.models import DiveSiteRating

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": ["http://localhost:3000","https://data-integration-ten.vercel.app"]}})

@app.route('/sites', methods=['GET'])
def get_dive_sites():
    with open('assets/dive_sites.json', 'r') as file:
        data = json.load(file)
    return jsonify(data), 200

@app.route('/sites/<id>', methods=['GET'])
def get_dive_site_by_id(id):
    with open('assets/dive_sites.json', 'r') as file:
        data = json.load(file)
        # find the site with the given id
        site = next((site for site in data if site['id'] == int(id)), None)
    return jsonify(site), 200

@app.route('/recommendations/for_you', methods=['GET'])
def get_recommendations_for_you():
    with open('assets/dive_sites.json', 'r') as file:
        data = json.load(file)
        # select 5 random recommendations
        data = random.sample(data, 7)
    return jsonify(data), 200

@app.route('/recommendations/popular', methods=['GET'])
def get_recommendations_popular():
    with open('assets/dive_sites.json', 'r') as file:
        data = json.load(file)
        # select 5 random recommendations
        data = random.sample(data, 7)
    return jsonify(data), 200

if __name__ == '__main__':
    app.run(debug=True)