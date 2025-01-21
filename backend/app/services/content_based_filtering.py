
import numpy as np
import pandas as pd
import copy  # Import copy module for deepcopy
from sklearn.preprocessing import MinMaxScaler
from app.models import DiveSite, DiveSiteCategory, Animal, Occurrence, User, DiveSiteRating

class ContentBasedFiltering:

    # Initialize the Content Based Filtering Service
    def __init__(self, db_engine):
        self.db_engine = db_engine  # Set this first

        # Load data from the database
        self.dive_sites = self._load_dive_sites()
        self.categories = self._load_categories()
        self.animals = self._load_animals()
        self.user = self._load_user()

        # Initialize converted dive sites
        self.converted_dive_sites = self._init_converted_dive_sites()

        # Define constants for feature extraction
        self.feature_columns = (
            self.categories['name'].tolist() 
            + self.animals['name'].tolist()
        )

        #TODO: DELETE LATER
        # Add random location data for user
        self.user['user_lat'] = np.random.uniform(-90, 90, len(self.user))
        self.user['user_long'] = np.random.uniform(-180, 180, len(self.user))

        #print(f"Loaded {len(self.converted_dive_sites)} rows into converted_dive_sites", flush=True)

    def _load_occurrences(self):
        query = "SELECT * FROM occurrence"  # Replace with the actual table name
        return pd.read_sql(query, con=self.db_engine)
     
    def _load_categories_per_dive_site(self):
        query = "SELECT * FROM categories_per_dive_site"
        return pd.read_sql(query, con=self.db_engine)

    def _load_dive_sites(self):
        query = "SELECT * FROM dive_site"
        return pd.read_sql(query, con=self.db_engine)

    def _load_categories(self):
        query = "SELECT * FROM dive_site_category"
        return pd.read_sql(query, con=self.db_engine)

    def _load_animals(self):
        query = "SELECT * FROM animal"
        return pd.read_sql(query, con=self.db_engine)

    def _load_user(self):
        query = 'SELECT * FROM "user"'
        return pd.read_sql(query, con=self.db_engine)

    def _load_user_ratings_data(self):
        query = "SELECT * FROM dive_site_rating"
        return pd.read_sql(query, con=self.db_engine)

    def _init_converted_dive_sites(self):
        '''
        Initializes the converted dive sites DataFrame with feature vectors for each dive site.
        '''
        # Load data from the database
        occurrences = self._load_occurrences()
        categories_per_dive_site = self._load_categories_per_dive_site()

        # Precompute category and animal mappings
        category_map = categories_per_dive_site.groupby('dive_site_id')['dive_site_category_id'].apply(list).to_dict()
        animal_map = occurrences.groupby('dive_site_id')['animal_id'].apply(list).to_dict()

        # Create the base DataFrame
        converted_dive_sites = self.dive_sites.copy()

        # Prepare category columns
        category_columns = {
            cat_name: converted_dive_sites['id'].map(
                lambda x: 1 if cat_id in category_map.get(x, []) else 0
            )
            for cat_id, cat_name in zip(self.categories['id'], self.categories['name'])
        }

        # Prepare animal columns
        animal_columns = {
            animal_name: converted_dive_sites['id'].map(
                lambda x: 1 if animal_id in animal_map.get(x, []) else 0
            )
            for animal_id, animal_name in zip(self.animals['id'], self.animals['name'])
        }

        # Add category and animal columns in one operation
        converted_dive_sites = pd.concat(
            [converted_dive_sites, pd.DataFrame(category_columns), pd.DataFrame(animal_columns)],
            axis=1
        )

        # Scale latitude and longitude
        scaler = MinMaxScaler()
        converted_dive_sites[['lat_scaled', 'long_scaled']] = scaler.fit_transform(
            converted_dive_sites[['lat', 'long']]
        )

        # Add `occurences` column (vectorized)
        converted_dive_sites['occurences'] = converted_dive_sites['id'].map(
            lambda x: ', '.join(
                self.animals[self.animals['id'].isin(animal_map.get(x, []))]['name'].tolist()
            )
        )

        # Add `categories` column (vectorized)
        converted_dive_sites['categories'] = converted_dive_sites['id'].map(
            lambda x: ', '.join(
                self.categories[self.categories['id'].isin(category_map.get(x, []))]['name'].tolist()
            )
        )

        # Sort by ID and reset index
        converted_dive_sites = converted_dive_sites.sort_values(by='id').reset_index(drop=True)

        return converted_dive_sites




    ### Main recommendation functions ###

    ## Recommend dive sites similar to a given dive site id
    
    def get_recommendations_for_a_dive_site(self, dive_site_id, w_cat=1/3, w_geo=1/3, w_animal=1/3, n=10):
        """
        This function generates a recommendation based on the category & geodata of the input dive site.

        w_cat: weight for the category vector
        w_geo: weight for the geodata (lat_scaled, long_scaled) vector 
        """
        #print(f"Generating recommendations for dive site with ID {dive_site_id}...", flush=True)

        idx = dive_site_id-1 # index of the query dive site in the DataFrame


        # Query Dive Site: Get Feature Vectors
        # If a feature vector contains only zeros, we can not calculate the similarity, therefore we set the weight to 0.
        # Category vector
        query_categories_vector = self.converted_dive_sites.loc[idx, self.categories['name']].to_numpy()
        if query_categories_vector.sum() == 0:
            w_cat = 0
        # Geodata vector
        query_geodata_vector = self.converted_dive_sites.loc[idx, ['lat_scaled', 'long_scaled']].to_numpy()
        # Animal vector
        query_animal_vector = self.converted_dive_sites.loc[idx, self.animals['name']].to_numpy()
        if query_animal_vector.sum() == 0:
            w_animal = 0

        # Other Dive Sites
        
        #print(f"Queried dive site index: {idx}")

        # generate recommendations
        recommendations = self.recommend(query_categories_vector, query_geodata_vector, query_animal_vector, w_cat, w_geo, w_animal, n, ignore_idx=idx)
        
        dive_sites_indexes = [d['index'] for d in recommendations]

        # get the list of ids from the dive_sites_indexes
        dive_sites_ids = self.converted_dive_sites.loc[dive_sites_indexes, 'id'].tolist()

        """
        # return the list of titles and similarities
        recommendations_df = self.converted_dive_sites.loc[dive_sites_indexes, ['id', 'title', 'lat', 'long', 'occurences', 'categories']]
        recommendations_df[f'Similarity to dive site {dive_site_id}'] = [d['combined'] for d in recommendations]
        recommendations_df[f'Category Similarity to dive site {dive_site_id}'] = [d['category'] for d in recommendations]
        recommendations_df[f'Geodata Similarity to dive site {dive_site_id}'] = [d['geodata'] for d in recommendations] 
        recommendations_df[f'Animal Similarity to dive site {dive_site_id}'] = [d['animal'] for d in recommendations]

        pd.set_option('display.max_columns', None)
        pd.set_option('display.expand_frame_repr', False)
        print(f"Recommendations for dive site with ID {dive_site_id}:", flush=True)
        print(recommendations_df, flush=True)
        """

        return dive_sites_ids



    ## Recommend dive sites for a given user
    

    def get_recommendations_for_a_user(self, user_id, w_cat=1/3, w_geo=1/3, w_animal=1/3, n=10):

        """
        This function generates a content based recommendation for a specific user.
        It generates a feature vector for the "ideal dive site" which the given user would like based off his ratings.
        Using this feature vector (which includes category, geodata, animal data) it computes the distance to the dive sites given in the dataset.

        w_cat: weight for the category vector
        w_geo: weight for the geodata (lat_scaled, long_scaled) vector
        w_animal: weight for the animal vector 
        n: number of recommendations to return

        """
        #print(f"Generating recommendations for the user with the ID {user_id}...")

        # get the ratings and item profiles of the user
        ratings, item_profiles = self.get_item_profile_of_user(user_id)

        # generate the user profile
        user_profile = self.generate_user_profile(ratings, item_profiles)
        # normalize the user profile
        user_profile = self.normalize_user_profile(user_profile)

        # add the geodata to the user profile
        user_profile = self.add_geodata_to_user_profile(user_profile, user_id)

        # split up the user profile into the different feature vectors: category, geodata, animal
        # Category vector
        user_categories_vector = user_profile[self.categories['name']].to_numpy().flatten()
        if user_categories_vector.sum() == 0:
            w_cat = 0
        # Geodata vector
        user_geodata_vector = user_profile[['user_lat_scaled', 'user_long_scaled']].to_numpy().flatten()
        # Animal vector
        user_animal_vector = user_profile[self.animals['name']].to_numpy().flatten()
        if user_animal_vector.sum() == 0:
            w_animal = 0

        # generate recommendations
        recommendations = self.recommend(user_categories_vector, user_geodata_vector, user_animal_vector, w_cat, w_geo, w_animal, n)
        
        dive_sites_indexes = [d['index'] for d in recommendations]

        # get the list of ids from the dive_sites_indexes
        dive_sites_ids = self.converted_dive_sites.loc[dive_sites_indexes, 'id'].tolist()

        """
        # list of titles and similarities
        recommendations_df = self.converted_dive_sites.loc[dive_sites_indexes, ['id', 'title', 'lat', 'long', 'occurences', 'categories']]
        recommendations_df[f'Total Similarity'] = [d['combined'] for d in recommendations]
        recommendations_df[f'Category Similarity'] = [d['category'] for d in recommendations]
        recommendations_df[f'Geodata Similarity'] = [d['geodata'] for d in recommendations] 
        recommendations_df[f'Animal Similarity'] = [d['animal'] for d in recommendations]

        pd.set_option('display.max_columns', None)
        pd.set_option('display.expand_frame_repr', False)
        print(f"Recommendations for the user with the ID {user_id}:", flush=True)
        print(recommendations_df, flush=True)"""
       

        return dive_sites_ids


    ### Content Based Recommendation Algorithm ###

    def recommend(self, input_categories_vector, input_geodata_vector, input_animal_vector, w_cat=1/3, w_geo=1/3, w_animal=1/3, n=10, ignore_idx=None):
        """
        This is a helper function used to recommend dive sites based on input vectors. These input vectors can describe a user or a dive site.     

        CAUTION:
        If we do not have any animal data for a specific dive site, but the w_animal is not 0, we will not consider this dive site for recommendations. (same for categories and geodata)    
        """

        # Precompute dive site vectors
        # they are not ordered by dive_site_id
        dive_site_categories = self.converted_dive_sites[self.categories['name']].to_numpy() 
        dive_site_geodata = self.converted_dive_sites[['lat_scaled', 'long_scaled']].to_numpy()
        dive_site_animals = self.converted_dive_sites[self.animals['name']].to_numpy()


        # compute cosine similarities between the user feature vectors and all
        # dive sites in the catalog (except for the query dive site)
        similarities = []

        # iterate over all dive sites
        #print("Iterate over all dive sites...")
        for i in range(len(self.converted_dive_sites)):

            # Skip the query dive site
            if i == ignore_idx:
                continue

            #print(f" {i} / {len(self.converted_dive_sites)}", end="\r")

            similiarity_dict = {}
            similiarity_dict['index'] = i  
            similiarity_dict['animal'] = None
            similiarity_dict['category'] = None
            similiarity_dict['geodata'] = None
            similiarity_dict['combined'] = None

            total_weight = 0
            combined_similarity = 0

            # Category Similarity
            if w_cat != 0:
                other_categories_vector = dive_site_categories[i]
                
                if np.count_nonzero(other_categories_vector) > 0:
                    sim_cat = self.get_cosine_similarity(input_categories_vector, other_categories_vector)
                    similiarity_dict['category'] = sim_cat
                    combined_similarity += w_cat * sim_cat
                    total_weight += w_cat
                else:
                    continue

            # Geodata Similarity
            if w_geo != 0:
                other_geodata_vector = dive_site_geodata[i]
                if np.count_nonzero(other_geodata_vector) > 0:
                    sim_geo = self.get_euclidean_similarity(input_geodata_vector, other_geodata_vector)
                    similiarity_dict['geodata'] = sim_geo
                    combined_similarity += w_geo * sim_geo
                    total_weight += w_geo
                else:
                    continue

            # Animal Similarity
            if w_animal != 0:
                other_animal_vector = dive_site_animals[i]
                if np.count_nonzero(other_animal_vector) > 0:
                    sim_animal = self.get_cosine_similarity(input_animal_vector, other_animal_vector)
                    similiarity_dict['animal'] = sim_animal
                    combined_similarity += w_animal * sim_animal
                    total_weight += w_animal
                else:
                    continue

            # Normalize the similarity by total weight if any feature contributed
            if total_weight != 0:
                combined_similarity /= total_weight
                similiarity_dict['combined'] = combined_similarity
                similarities.append(similiarity_dict)
            

        # sort pairs w.r.t. combined_similarity in descending order (reverse=True)
        similarities = sorted(similarities, key=lambda x: x['combined'], reverse=True)

        # take the top n elements
        recommendations = similarities[:n]

        return recommendations

        

        
    ### Helper Functions to build User Profile ###

    
    def get_item_profile_of_user(self, user_id):
        """
        This function returns a list of item profiles and a list of ratings for the given user_id.
        """
        # make a supabase query to get the user ratings
        user_ratings = DiveSiteRating.query.filter_by(user_id=user_id).all()

        # convert the user ratings to a pandas DataFrame
        user_ratings = pd.DataFrame([rating.to_dict() for rating in user_ratings])

        item_profiles = []
        ratings = []

        for index, row in user_ratings.iterrows():
            
            rating = row['rating']
            dive_site_id = row['dive_site_id']
            item_profile = self.converted_dive_sites[self.converted_dive_sites['id'] == dive_site_id][self.feature_columns].to_numpy().flatten()
            item_profiles.append(item_profile)
            ratings.append(rating)

        ratings = np.array(ratings)
        item_profiles = np.array(item_profiles)

        # Create a DataFrame for better interpretability
        item_profiles = pd.DataFrame(item_profiles, columns=self.feature_columns)

        return ratings, item_profiles

    def generate_user_profile(self, ratings, item_profiles):
        """
        This function generates a user profile based on the given ratings and item profiles.
        """
        user_profile = None

        item_profiles = item_profiles.to_numpy()

        # option 1
        # new_ratings = ratings # normal ratings

        # option 2
        #new_ratings = ratings - ratings.mean() # mean ratings

        # option 3
        new_ratings = ratings - 2.5

        for i in range(len(item_profiles)):
            
            if user_profile is None:
                user_profile = new_ratings[i] * item_profiles[i]
            else:
                user_profile += new_ratings[i] * item_profiles[i]

        user_profile = user_profile / len(item_profiles)

        user_profile = pd.DataFrame(user_profile.reshape(1, user_profile.shape[0]), columns=self.feature_columns)
            
        return user_profile


    def normalize_user_profile(self, user_profile):
        """
        Normalize the user profile so that the highest values become 1,
        the lowest become 0, and neutral (0) values remain 0.
        """
        user_profile_array = user_profile.to_numpy().flatten()
        
        max_val = np.max(user_profile_array)
        min_val = np.min(user_profile_array)
        
        # Avoid division by zero
        if max_val == min_val:
            return user_profile  # No meaningful scaling possible
        
        # Normalize values to [0, 1]
        normalized_array = (user_profile_array - min_val) / (max_val - min_val)
        
        # Retain 0s for unimportant features
        normalized_array[user_profile_array == 0] = 0
        
        # Convert back to DataFrame
        normalized_profile = pd.DataFrame(normalized_array.reshape(1, -1), columns=user_profile.columns)
        return normalized_profile

    
    def add_geodata_to_user_profile(self, user_profile, user_id):
        """
        This function adds the user's geodata to the user profile.
        """

        user_lat = self.user.loc[self.user['id'] == user_id, 'user_lat'].values
        user_long = self.user.loc[self.user['id'] == user_id, 'user_long'].values

        # Scale the user's geodata between 0 and 1
        lat_min = -90
        lat_max = 90

        long_min = -180
        long_max = 180

        user_lat_scaled = (user_lat - lat_min) / (lat_max - lat_min)
        user_long_scaled = (user_long - long_min) / (long_max - long_min)

        # Add the scaled geodata to the user profile 
        user_profile['user_lat_scaled'] = user_lat_scaled
        user_profile['user_long_scaled'] = user_long_scaled

        return user_profile

    


    ### Similarity Functions ###

    # EUCLIDEAN SIMILARITY (for geodata)
    # Cosine similarity is not suitable for geocoordinates. We can use Euclidean similarity instead.
    def get_euclidean_similarity(self, v1, v2, max_distance=1):
        """
        Compute similarity between scaled geocoordinates using Euclidean distance.
        """
        lat1, lon1 = v1
        lat2, lon2 = v2
        distance = np.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)
        similarity = max(0, 1 - distance / max_distance)
        return similarity



    # Cosine Similarity
    def get_cosine_similarity(self, x, y):
        
        numerator = np.dot(x,y)
        denominator = np.linalg.norm(x) * np.linalg.norm(y)

        # sanity check: x and y must be non-zero vectors
        if denominator > 0:
            sim = numerator / denominator
        else:
            raise Exception("The cosine similarity is not defined for vectors containing only zeros!")

        return sim
