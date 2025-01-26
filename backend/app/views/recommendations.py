from flask import jsonify, Blueprint
from sqlalchemy.sql import func
from ..models import UserVector, ItemVector, DiveSiteRating, DiveSite
from surprise import SVD, Dataset, Reader
from ..extensions import db
import pandas as pd
import numpy as np
from config import Config
import supabase
import uuid
from supabase import create_client

recommendations_bp = Blueprint('recommendations_bp', __name__)

# Routes
@recommendations_bp.route('/fit_model', methods=['POST'])
def fit_model():
    ratings = DiveSiteRating.query.all()
    ratings = [
        {
           'user_id': x.user_id,
           'dive_site_id': x.dive_site_id, 
           'rating': x.rating
        } for x in ratings
    ]
    data = pd.DataFrame(ratings)
    reader = Reader(rating_scale=(1, 5))
    dataset = Dataset.load_from_df(data[['user_id', 'dive_site_id', 'rating']], reader)
    trainset = dataset.build_full_trainset()
    svd_model = SVD(n_factors=10, n_epochs=90, reg_all=0.07, lr_all=0.0005, random_state=2)
    svd_model.fit(trainset)
    
    # Save model and vectors
    save_model_to_db(svd_model, trainset) 
    return jsonify({'message': 'Model trained and saved successfully.'})

@recommendations_bp.route('/recommend_dive_spots/<user_id>', methods=['GET'])
def recommend_dive_spots(user_id):
    # Initialize Supabase client
    SUPABASE_URL = Config.SUPABASE_URL
    SUPABASE_ANON_KEY = Config.SUPABASE_ANON_KEY
    supabaseClient = supabase.create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

    try:
        # Convert user_id to UUID
        user_id_uuid = uuid.UUID(user_id)

        # Call the Supabase function (passing the UUID user ID)
        response = supabaseClient.rpc("recommend_dive_sites", params={"puser_id": str(user_id_uuid)}).execute()

        # Return the recommendations as JSON
        if response.data:
            return jsonify(response.data), 200
        else:
            return jsonify([]), 200

    except Exception as e: 
        # If any error occurs, return the error message
        return jsonify({"error": str(e)}), 500
    
@recommendations_bp.route('/recommend_dive_regions/<user_id>', methods=['GET'])
def recommend_dive_regions(user_id):
    # Initialize Supabase client
    SUPABASE_URL = Config.SUPABASE_URL
    SUPABASE_ANON_KEY = Config.SUPABASE_ANON_KEY
    supabaseClient = supabase.create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

    try:
        # Convert user_id to UUID
        user_id_uuid = uuid.UUID(user_id)

        # Call the Supabase function (passing the UUID user ID)
        response = supabaseClient.rpc("recommend_dive_regions", params={"puser_id": str(user_id_uuid)}).execute()

        # Return the recommendations as JSON
        if response.data:
            return jsonify(response.data), 200
        else:
            return jsonify([]), 200

    except Exception as e: 
        # If any error occurs, return the error message
        return jsonify({"error": str(e)}), 500

@recommendations_bp.route('/recommend_dive_regions/<user_id>/<region>', methods=['GET'])
def recommend_dive_sites(user_id, region):
    # Initialize Supabase client
    SUPABASE_URL = Config.SUPABASE_URL
    SUPABASE_ANON_KEY = Config.SUPABASE_ANON_KEY
    supabaseClient = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

    try:
        # Convert user_id to UUID
        user_id_uuid = uuid.UUID(user_id)

        # Call the Supabase function (passing the UUID user ID and region)
        response = supabaseClient.rpc(
            "get_dive_sites_for_region",
            params={"puser_id": str(user_id_uuid), "pregion": region}
        ).execute()

        # Check if the response contains data
        if response.data:
            return jsonify(response.data), 200
        else:
            return jsonify([]), 200

    except Exception as e:
        # Handle any errors
        return jsonify({"error": str(e)}), 500
    
@recommendations_bp.route('/recommend_animals/<user_id>', methods=['GET'])
def recommend_dive_animals(user_id):
    # Initialize Supabase client
    SUPABASE_URL = Config.SUPABASE_URL
    SUPABASE_ANON_KEY = Config.SUPABASE_ANON_KEY
    supabaseClient = supabase.create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

    try:
        # Convert user_id to UUID
        user_id_uuid = uuid.UUID(user_id)

        # Call the Supabase function (passing the UUID user ID)
        response = supabaseClient.rpc("get_favorite_animals_w_dive_sites", params={"puser_id": str(user_id_uuid)}).execute()

        # Return the recommendations as JSON
        if response.data:
            return jsonify(response.data), 200
        else:
            return jsonify([]), 200

    except Exception as e: 
        # If any error occurs, return the error message
        return jsonify({"error": str(e)}), 500
    
@recommendations_bp.route('/rating_count/<user_id>', methods=['GET'])
def rating_count(user_id):
    # Initialize Supabase client
    SUPABASE_URL = Config.SUPABASE_URL
    SUPABASE_ANON_KEY = Config.SUPABASE_ANON_KEY
    supabaseClient = supabase.create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

    try:
        # Convert user_id to UUID
        user_id_uuid = uuid.UUID(user_id)

        # Call the Supabase function (passing the UUID user ID)
        response = supabaseClient.rpc("get_number_of_ratings", params={"puser_id": str(user_id_uuid)}).execute()

        # Return the recommendations as JSON
        return jsonify(response.data), 200 

    except Exception as e: 
        # If any error occurs, return the error message
        return jsonify({"error": str(e)}), 500
    
@recommendations_bp.route('/recommend_top10', methods=['GET'])
def recommend_top10():
    # Initialize Supabase client
    SUPABASE_URL = Config.SUPABASE_URL
    SUPABASE_ANON_KEY = Config.SUPABASE_ANON_KEY
    supabaseClient = supabase.create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

    try:
        # Call the Supabase function (passing the UUID user ID)
        response = supabaseClient.rpc("get_top_10_best_rated_dive_sites").execute()

        # Return the recommendations as JSON
        return jsonify(response.data), 200 

    except Exception as e: 
        # If any error occurs, return the error message
        return jsonify({"error": str(e)}), 500

def save_model_to_db(svd_model, trainset):
    """
    Saves the SVD model parameters into the database after clearing the old vectors.
    """
    # Clear existing entries in UserVector and ItemVector
    UserVector.query.delete()
    ItemVector.query.delete()
    db.session.commit()

    # Prepare user and item data
    user_data = [
        UserVector(
            user_id=trainset.to_raw_uid(user_idx),
            vector=svd_model.pu[user_idx].tolist(),  # Store as list (converted to array in SQL)
            bias=svd_model.bu[user_idx]
        )
        for user_idx in range(trainset.n_users)
    ]
    item_data = [
        ItemVector(
            item_id=trainset.to_raw_iid(item_idx),
            vector=svd_model.qi[item_idx].tolist(),  # Store as list (converted to array in SQL)
            bias=svd_model.bi[item_idx]
        )
        for item_idx in range(trainset.n_items)
    ]

    # Add new entries to the database
    db.session.bulk_save_objects(user_data)
    db.session.bulk_save_objects(item_data)
    db.session.commit()

    # print("Model successfully saved to the database.")