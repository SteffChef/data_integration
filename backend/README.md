# Guide for the Dive Finder Backend

In this section we provide detailled insight on the structure and usage of our backend solution.

## Installation

1. nativate to the backend folder

   ```bash
   cd backend
   ```

2. If not already present, create a virtual environment

   ```bash
   python3 -m venv .venv
   # or when on windows:
   python -m venv .venv
   ```

3. Activate the virtual environment

   ```bash
   source .venv/bin/activate
   # or when on windows:
   .venv\Scripts\activate

   ```

4. Install the necessary dependencies

   ```bash
   pip install -r requirements.txt
   ```

5. run the backend locally
   ```bash
   python3 app.py
   # or when on windows:
   python app.py
   ```


## Structure

### Content Based Filtering

This implements a **Content-Based Filtering** recommendation system for dive sites. It consists of several components structured within different folders.

#### **1. Service Layer** (Business Logic)
Located in `service/content-based-filtering.py`, this file contains the **core recommendation algorithm**.

##### **Purpose:**
- Loads and preprocesses data from the database.
- Converts dive site data into feature vectors.
- Computes similarity between dive sites and user preferences.
- Provides recommendation functions for both **dive sites** and **users**.

##### **Functions:**
- `_init_converted_dive_sites()`: Initializes a feature matrix for all dive sites.
- `get_recommendations_for_a_dive_site()`: Finds similar dive sites based on categories, geodata, and animal sightings.
- `get_recommendations_for_a_user()`: Creates a user profile and recommends dive sites based on their past ratings.
- `recommend()`: Core similarity computation function.
- `get_cosine_similarity()`: Computes cosine similarity for categorical and animal feature vectors.
- `get_haversine_similarity()`: Computes geolocation similarity based on Haversine distance.

##### **Tables:**
- `dive_site`: Contains general dive site information.
- `dive_site_category`: Holds predefined dive site categories.
- `categories_per_dive_site`: Maps dive sites to their respective categories.
- `animal`: Stores marine animal species data.
- `occurrence`: Links animals to dive sites.
- `dive_site_rating`: Stores user ratings for dive sites.

---

### **2. API Layer** (Endpoints & Routing)
Located in `views/dive-sites.py`, this file defines **Flask endpoints** for accessing recommendations.

#### **Endpoints:**
- **`GET /dive-sites/recommendations/<dive_site_id>`**
  - Returns recommended dive sites based on a given dive site.
  - Supports query parameters: `w_cat`, `w_geo`, `w_animal` (weights), and `n` (number of results).
  
- **`GET /dive-sites/recommendations/users/<user_id>`**
  - Returns recommended dive sites for a given user based on past ratings.
  - Supports the same query parameters as the previous endpoint.
  
---

### **3. Application Initialization**
Located in `__init__.py`, this file initializes the Flask app and loads the **Content-Based Filtering** system. The `ContentBasedFiltering` class loads all data at startup to optimize query speed.

#### **Relevant Code:**
```python
# Initialize content-based filtering with app context
with app.app_context():
    cbf = ContentBasedFiltering(db.engine)
    app.cbf = cbf  # Store it in the app context
```
#### **Purpose:**
- Ensures `ContentBasedFiltering` is available globally in the app.
- Loads necessary data from the database at startup.

