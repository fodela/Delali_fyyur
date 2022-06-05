# import configured database from app.py
from app import db

from datetime import datetime


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
      return f"<Venue | {self.id}  {self.name} Image: {self.image_link} >"

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):

    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venues = db.Column(db.Boolean(), default=False, nullable=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):

	    return f"<Artist | ID: {self.id} Name: {self.name}>"


class Show(db.Model):
    __table__name = 'Show'
    id = db.Column(
		db.Integer, 
		primary_key=True)
    start_time = db.Column(
		db.DateTime, 
		nullable=False, 
		default=datetime.utcnow
		)
    venue_id = db.Column(
		db.Integer, 
		db.ForeignKey('Venue.id'), 
		nullable=False
		)
    artist_id = db.Column(
		db.Integer, 
		db.ForeignKey('Artist.id'), 
		nullable=False)

    def __repr__(self):
        return f"<Show | id: {self.id} venue: {self.venue_id} artist: {self.artist_id}>"