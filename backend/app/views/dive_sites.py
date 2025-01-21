from flask import Blueprint, jsonify, request, current_app #current_app includes the app context, e.g. ContentBasedFiltering
from ..models import DiveSite, DiveSiteCategory, Animal, Occurrence
from ..extensions import db
from sqlalchemy import func, or_
from sqlalchemy.orm import aliased
import uuid


dive_sites_bp = Blueprint('dive_sites_bp', __name__)

@dive_sites_bp.route('/', methods=['GET'])
def get_all_dive_sites():
    dive_sites = DiveSite.query.order_by(func.random()).all()
    return jsonify([{
        'id': site.id,
        'title': site.title,
        'latitude' : site.lat,
        'longitude' : site.long,
    } for site in dive_sites])
    
# get 10 random dive sites
@dive_sites_bp.route('/random', methods=['GET'])
def get_random_dive_sites():
    dive_sites = DiveSite.query.order_by(func.random()).limit(15).all()
    return jsonify([{
        'id': site.id,
        'title': site.title,
        'description': site.description,
        'categories': [category.to_dict() for category in site.categories],
        'latitude' : site.lat,
        'longitude' : site.long,
        'image_url' : site.image_url,
        'region' : site.region,
    } for site in dive_sites])

@dive_sites_bp.route('/search', methods=['GET'])
def search_dive_sites():
    query = request.args.get('q','')
    search_term = f"%{query}%"  # The query for fuzzy matching

    # Alias for the animal occurrences to ensure proper join
    animal_occurrences = aliased(Occurrence)
    dive_sites = DiveSite.query.join(animal_occurrences, animal_occurrences.dive_site_id == DiveSite.id).join(
        Animal, Animal.id == animal_occurrences.animal_id
    ).filter(
        or_(
            DiveSite.title.ilike(search_term),
            DiveSite.region.ilike(search_term),
            DiveSite.categories.any(DiveSiteCategory.name.ilike(search_term)),
            Animal.name.ilike(search_term)  # Now we can search animals correctly
        )
    ).limit(50).all()
    return jsonify([{
        'id': site.id,
        'title': site.title,
        'description': site.description,
        'categories': [category.to_dict() for category in site.categories],
        'latitude' : site.lat,
        'longitude' : site.long,
        'image_url' : site.image_url,
        'region' : site.region,
    } for site in dive_sites])

@dive_sites_bp.route('/<int:id>', methods=['GET'])
def get_dive_site(id):
    site = DiveSite.query.get_or_404(id)
    return jsonify({
        'id': site.id,
        'title': site.title,
        'description': site.description,
        'latitude' : site.lat,
        'longitude' : site.long,
        'categories': [category.to_dict() for category in site.categories],
        'animals': [occurrence.animal.to_dict() for occurrence in site.occurrences],
        'image_url' : site.image_url,
        'region' : site.region,
    })

@dive_sites_bp.route('/', methods=['POST'])
def create_dive_site():
    data = request.get_json()
    new_site = DiveSite(
        title=data['title'],
        lat=data['lat'],
        long=data['long'],
        url = data.get('url'),
        image_url=data.get('image_url'),
        description=data.get('description',None),
        max_depth=data.get('max_depth',None),
    )
    db.session.add(new_site)
    db.session.commit()
    return jsonify({'message': 'Dive site created'}), 201

# Route to relate a category to a dive site
@dive_sites_bp.route('/<int:id>/categories', methods=['POST'])
def add_category_to_dive_site(id):
    data = request.get_json()
    site = DiveSite.query.get_or_404(id)
    category = DiveSiteCategory.query.get_or_404(data['dive_site_category_id'])

    if category in site.categories:
        return jsonify({'message': 'Category already added to dive site'}), 400

    site.categories.append(category)
    db.session.commit()

    return jsonify({'message': 'Category added to dive site'}), 201

# Recommendations

# CONTENT BASED RECOMMENDATION Routes

# Flask Route to get recommendations for a dive site. Example request: GET /dive-sites/recommendations/2?w_cat=0.4&w_geo=0.3&w_animal=0.3&n=10
@dive_sites_bp.route('/recommendations/<int:dive_site_id>', methods=['GET'])
def recommend_for_dive_site(dive_site_id):
    w_cat = float(request.args.get('w_cat', 1/3))
    w_geo = float(request.args.get('w_geo', 1/3))
    w_animal = float(request.args.get('w_animal', 1/3))
    n = int(request.args.get('n', 10))

    if not (0 <= w_cat <= 1 and 0 <= w_geo <= 1 and 0 <= w_animal <= 1):
        return jsonify({'error': 'Weights must be between 0 and 1'}), 400

    if abs((w_cat + w_geo + w_animal) - 1) > 1e-6:
        return jsonify({'error': 'The sum of weights must be 1'}), 400

    recommendations = current_app.cbf.get_recommendations_for_a_dive_site(
        dive_site_id, w_cat=w_cat, w_geo=w_geo, w_animal=w_animal, n=10
    )

    # Get the dive sites from the database
    dive_sites = DiveSite.query.filter(DiveSite.id.in_(recommendations)).all()
    
    return jsonify([{
        'id': site.id,
        'title': site.title,
        'description': site.description,
        'categories': [category.to_dict() for category in site.categories],
        'latitude' : site.lat,
        'longitude' : site.long,
        'image_url' : site.image_url,
        'region' : site.region,
    } for site in dive_sites])

    

# Flask Route to get recommendations for a user
@dive_sites_bp.route('/recommendations/users/<string:user_id>', methods=['GET'])
def recommend_for_user(user_id):
    user_id = uuid.UUID(user_id)
    w_cat = float(request.args.get('w_cat', 1/3))
    w_geo = float(request.args.get('w_geo', 1/3))
    w_animal = float(request.args.get('w_animal', 1/3))
    n = int(request.args.get('n', 10))

    if not (0 <= w_cat <= 1 and 0 <= w_geo <= 1 and 0 <= w_animal <= 1):
        return jsonify({'error': 'Weights must be between 0 and 1'}), 400

    if abs((w_cat + w_geo + w_animal) - 1) > 1e-6:
        return jsonify({'error': 'The sum of weights must be 1'}), 400

    recommendations = current_app.cbf.get_recommendations_for_a_user(
        user_id, w_cat=w_cat, w_geo=w_geo, w_animal=w_animal, n=n
    )

     # Get the dive sites from the database
    dive_sites = DiveSite.query.filter(DiveSite.id.in_(recommendations)).all()

    return jsonify([{
        'id': site.id,
        'title': site.title,
        'description': site.description,
        'categories': [category.to_dict() for category in site.categories],
        'latitude' : site.lat,
        'longitude' : site.long,
        'image_url' : site.image_url,
        'region' : site.region,
    } for site in dive_sites])