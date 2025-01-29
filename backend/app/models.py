from .extensions import db
from sqlalchemy.dialects.postgresql import UUID

# create base model class
class BaseModel(db.Model):
    __abstract__ = True

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# User model
class User(BaseModel):
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    dive_site_ratings = db.relationship('DiveSiteRating', back_populates='user')
    animal_ratings = db.relationship('AnimalRating', back_populates='user')

# DiveSites model
class DiveSite(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    long = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    max_depth = db.Column(db.String, nullable=True)
    region = db.Column(db.String(100), nullable=True)
    cluster = db.Column(db.Integer, nullable=True)
    occurrences = db.relationship('Occurrence', back_populates='dive_site')
    dive_site_ratings = db.relationship('DiveSiteRating', back_populates='dive_site')
    categories = db.relationship('DiveSiteCategory', secondary='categories_per_dive_site', back_populates='dive_sites')

# DiveSiteCategories model
class DiveSiteCategory(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    dive_sites = db.relationship('DiveSite', secondary='categories_per_dive_site', back_populates='categories')

# Association table for Dive Sites and Categories
categories_per_dive_site = db.Table(
    'categories_per_dive_site',
    db.Column('dive_site_id', db.Integer, db.ForeignKey('dive_site.id'), primary_key=True),
    db.Column('dive_site_category_id', db.Integer, db.ForeignKey('dive_site_category.id'), primary_key=True)
)

# Animals model
class Animal(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    occurrences = db.relationship('Occurrence', back_populates='animal')
    animal_ratings = db.relationship('AnimalRating', back_populates='animal')

# Occurrences model
class Occurrence(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    dive_site_id = db.Column(db.Integer, db.ForeignKey('dive_site.id'), nullable=False)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)
    dive_site = db.relationship('DiveSite', back_populates='occurrences')
    animal = db.relationship('Animal', back_populates='occurrences')

# Dive Site Ratings model
class DiveSiteRating(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    dive_site_id = db.Column(db.Integer, db.ForeignKey('dive_site.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    user = db.relationship('User', back_populates='dive_site_ratings')
    dive_site = db.relationship('DiveSite', back_populates='dive_site_ratings')

# Animal Ratings model
class AnimalRating(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    user = db.relationship('User', back_populates='animal_ratings')
    animal = db.relationship('Animal', back_populates='animal_ratings')
    
from sqlalchemy.dialects.postgresql import ARRAY

class UserVector(db.Model):
    __tablename__ = 'user_vectors'
    user_id = db.Column(db.String, unique=True, nullable=False, primary_key=True)
    vector = db.Column(ARRAY(db.Float), nullable=False)  # Use ARRAY(db.Float) for PostgreSQL
    bias = db.Column(db.Float, nullable=False)

class ItemVector(db.Model):
    __tablename__ = 'item_vectors'
    item_id = db.Column(db.String, unique=True, nullable=False, primary_key=True)
    vector = db.Column(ARRAY(db.Float), nullable=False)  # Use ARRAY(db.Float) for PostgreSQL
    bias = db.Column(db.Float, nullable=False)