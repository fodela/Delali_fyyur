#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.policy import default
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
from models import *


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')  #### NEEDS UPCOMING SHOW
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  
  data = []

  # get unique location -> location is city and state
  locations = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()
  
  for location in locations:
    city = location[0],
    state = location[1],
    venues = [{'id': venue.id, 
            'name': venue.name,
            "num_upcoming_shows":Show.query.filter(Show.start_time > datetime.now() , Show.venue_id == venue.id).count()} 
            for venue in Venue.query.with_entities(Venue.id,Venue.name).filter(Venue.city == city, Venue.state == state).all()
            ]
    data.append(
      {
        'city':city,
        'state':state,
        'venues': venues
        }
      )
    # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # search for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term','')
  results = Venue.query.filter(Venue.name.ilike(f"%{search_term}%"))

  response={
    "count": results.count(),
    "data": [{
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": Show.query.filter(Show.start_time > datetime.now() , Show.venue_id == result.id).count()
    }
    for result in results
    ]
  }

  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: <DONE> replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)

  past_shows = Show.query.filter(Show.start_time < datetime.now(), Show.venue_id == venue_id).all()

  num_past_shows = Show.query.filter(Show.start_time < datetime.now(), Show.venue_id == venue_id).count()

  upcoming_shows = Show.query.filter(Show.start_time > datetime.now(), Show.venue_id == venue_id).all()

  num_upcoming_shows = Show.query.filter(Show.start_time > datetime.now(), Show.venue_id == venue_id).count()
  

  data = {
    'id' : venue.id,
    'name' : venue.name,
    'city' : venue.city, 
    'state' : venue.state,
    'address' : venue.address,
    'phone' : venue.phone,
    'genres' : venue.genres,
    'image_link' : venue.image_link,
    'facebook_link' : venue.facebook_link,
    'website_link' : venue.website_link,
    'seeking_talent' : venue.seeking_talent,
    'seeking_description' : venue.seeking_description,
    "past_shows": [{
      "artist_id": past_show.artist_id,
      "artist_name": Artist.query.with_entities(Artist.name).filter_by(id = past_show.id).first().name,
      "artist_image_link":Artist.query.with_entities(Artist.image_link).filter_by(id = past_show.id).first().image_link,
      "start_time": str(past_show.start_time)
    }
    for past_show in past_shows
    ],
    "upcoming_shows": [{
      "artist_id": upcoming_show.artist_id,
      "artist_name": Artist.query.with_entities(Artist.name).filter_by(id = upcoming_show.id).first().name,
      "artist_image_link":Artist.query.with_entities(Artist.image_link).filter_by(id = upcoming_show.id).first().image_link,
      "start_time": str(upcoming_show.start_time)
    }
    for upcoming_show in upcoming_shows
    ],

    "past_shows_count": num_past_shows,
    "upcoming_shows_count": num_upcoming_shows,
    }

  flash(data)
  for d in data:
   print(f'{d} = {data[d]} \n--------------- \n')

  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  
  # data = list(filter(lambda d: d['id'] == venue_id, [data]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO:<DONE> modify data to be the data object returned from db insertion
  form = VenueForm()

  


  try:

    venue = Venue(
      name = form.name.data.strip(),
      city = form.city.data.strip(),
      state = form.state.data.strip(),
      address = form.address.data.strip(),
      phone = form.phone.data.strip(),
      genres = form.genres.data,
      image_link = form.image_link.data.strip(),
      facebook_link = form.facebook_link.data.strip(),
      website_link = form.website_link.data.strip(),
      seeking_talent = form.seeking_talent.data,
      seeking_description = form.seeking_description.data.strip()
                  )

    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')


    # TODO:<DONE> on unsuccessful db insert, flash an error instead.
  except:
    db.session.rollback()
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

  finally:
      db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue was successfully deleted!')

  except:
    db.session.rollback()
    flash('An error occurred. Venue could not be deleted.')

  finally:
    db.session.close()


  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('venues'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO:<DONE> replace with real data returned from querying the database
  data = []
  # get all artists
  artists = Artist.query.with_entities(Artist.id,Artist.name)

  # create each artist
  for artist in artists:
    data.append(
      {
        'id': artist.id,
        'name' : artist.name
      }
    )

  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  results = Artist.query.filter(Artist.name.ilike(f"%{search_term}%"))

  response={
    "count": results.count(),
    "data": [{
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": Show.query.filter(Show.start_time > datetime.now() , Show.artist_id == result.id).count()
    }
    for result in results
    ]
  }
  
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   },{
  #     "id": 2,
  #     "name": "Fo",
  #     "num_upcoming_shows": 1,
  #   }
  #   ]
  # }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO:<DONE> replace with real artist data from the artist table, using artist_id

  artist = Artist.query.get(artist_id)
    
  past_shows = Show.query.filter(Show.start_time < datetime.now() , artist_id == artist_id).all()

  num_past_shows = Show.query.filter(Show.start_time < datetime.now() , artist_id == artist_id).count()

  upcoming_shows = Show.query.filter(Show.start_time > datetime.now() , artist_id == artist_id).all()

  num_upcoming_shows = Show.query.filter(Show.start_time > datetime.now() , artist_id == artist_id).count()

  data = {
    'id' : artist.id,
    'name' : artist.name,
    'city' : artist.city, 
    'state' : artist.state,
    'phone' : artist.phone,
    'genres' : artist.genres,
    'image_link' : artist.image_link,
    'facebook_link' : artist.facebook_link,
    'website_link' : artist.website_link,
    'seeking_venue' : artist.seeking_venues,
    'seeking_description' : artist.seeking_description,
    "past_shows": [{
      "artist_id": past_show.artist_id,
      "artist_name": Artist.query.with_entities(Artist.name).filter_by(id = past_show.id).first().name,
      "artist_image_link":Artist.query.with_entities(Artist.image_link).filter_by(id = past_show.id).first().image_link,
      "start_time": str(past_show.start_time)
    }
    for past_show in past_shows
    ],
     "upcoming_shows": [{
      "artist_id": upcoming_show.artist_id,
      "artist_name": Artist.query.with_entities(Artist.name).filter_by(id = upcoming_show.id).first().name,
      "artist_image_link":Artist.query.with_entities(Artist.image_link).filter_by(id = upcoming_show.id).first().image_link,
      "start_time": str(upcoming_show.start_time)
    }
    for upcoming_show in upcoming_shows
    ],
    "past_shows_count": num_past_shows,
    "upcoming_shows_count": num_upcoming_shows,
    }
#   data1={
#     "id": 4,
#     "name": "Guns N Petals",
#     "genres": ["Rock n Roll"],
#     "city": "San Francisco",
#     "state": "CA",
#     "phone": "326-123-5000",
#     "website": "https://www.gunsnpetalsband.com",
#     "facebook_link": "https://www.facebook.com/GunsNPetals",
#     "seeking_venue": True,
#     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
#     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
#     "past_shows": [{
#       "venue_id": 1,
#       "venue_name": "The Musical Hop",
#       "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
#       "start_time": "2019-05-21T21:30:00.000Z"
#     }],
#     "upcoming_shows": [],
#     "past_shows_count": 1,
#     "upcoming_shows_count": 0,
#   }
#   data2={
#     "id": 5,
#     "name": "Matt Quevedo",
#     "genres": ["Jazz"],
#     "city": "New York",
#     "state": "NY",
#     "phone": "300-400-5000",
#     "facebook_link": "https://www.facebook.com/mattquevedo923251523",
#     "seeking_venue": False,
#     "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
#     "past_shows": [{
#       "venue_id": 3,
#       "venue_name": "Park Square Live Music & Coffee",
#       "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
#       "start_time": "2019-06-15T23:00:00.000Z"
#     }],
#     "upcoming_shows": [],
#     "past_shows_count": 1,
#     "upcoming_shows_count": 0,
#   }
#   data3={
#     "id": 6,
#     "name": "The Wild Sax Band",
#     "genres": ["Jazz", "Classical"],
#     "city": "San Francisco",
#     "state": "CA",
#     "phone": "432-325-5432",
#     "seeking_venue": False,
#     "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
#     "past_shows": [],
#     "upcoming_shows": [{
#       "venue_id": 3,
#       "venue_name": "Park Square Live Music & Coffee",
#       "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
#       "start_time": "2035-04-01T20:00:00.000Z"
#     }, {
#       "venue_id": 3,
#       "venue_name": "Park Square Live Music & Coffee",
#       "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
#       "start_time": "2035-04-08T20:00:00.000Z"
#     }, {
#       "venue_id": 3,
#       "venue_name": "Park Square Live Music & Coffee",
#       "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
#       "start_time": "2035-04-15T20:00:00.000Z"
#     }],
#     "past_shows_count": 0,
#     "upcoming_shows_count": 3,
#   }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

# #  Update
# #  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO:<DONE> populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  data = {
    'id' : artist.id,
    'name' : artist.name,
    'city' : artist.city, 
    'state' : artist.state,
    'phone' : artist.phone,
    'genres' : artist.genres,
    'image_link' : artist.image_link,
    'facebook_link' : artist.facebook_link,
    'website_link' : artist.website_link,
    'seeking_venue' : artist.seeking_venues,
    'seeking_description' : artist.seeking_description,    
    }
  
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO:<DONE> take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    form = ArtistForm()
    
    artist = Artist.query.get(artist_id)

    artist.name = form.name.data.strip()
    artist.city = form.city.data.strip()
    artist.state = form.state.data
    artist.phone = form.phone.data.strip()
    artist.genres = form.genres.data.strip()
    artist.facebook_link = form.facebook_link.data.strip()
    artist.image_link = form.image_link.data.strip()
    artist.website_link = form.website_link.data.strip()
    artist.seeking_venues = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data.strip()

    db.session.commit()
    flash('Artist was successfully edited!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist could not be listed.')

  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO:<DONE> populate form with values from venue with ID <venue_id>

  venue = Venue.query.get(venue_id)

  data = {
    'id' : venue.id,
    'name' : venue.name,
    'city' : venue.city, 
    'state' : venue.state,
    'phone' : venue.phone,
    'genres' : venue.genres,
    'image_link' : venue.image_link,
    'facebook_link' : venue.facebook_link,
    'website_link' : venue.website_link,
    'seeking_talent' : venue.seeking_talent,
    'seeking_description' : venue.seeking_description,    
    }

  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    form = ArtistForm()
    
    venue = Venue.query.get(venue_id)

    venue.name = form.name.data.strip()
    venue.city = form.city.data.strip()
    venue.state = form.state.data
    venue.address = form.address.data.strip()
    venue.phone = form.phone.data.strip()
    venue.genres = form.genres.data.strip()
    venue.facebook_link = form.facebook_link.data.strip()
    venue.image_link = form.image_link.data.strip()
    venue.website_link = form.website_link.data.strip()
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data.strip()

    db.session.commit()
    flash('Artist was successfully edited!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist could not be listed.')

  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: <Done> insert form data as a new Venue record in the db, instead
  # TODO: <Done> modify data to be the data object returned from db insertion
 
  try:
    form = ArtistForm()

    artist = Artist(
      name = form.name.data.strip(),
      city = form.city.data.strip(),
      state = form.state.data,
      phone = form.phone.data.strip(),
      genres = form.genres.data,
      image_link = form.image_link.data.strip(),
      facebook_link = form.facebook_link.data.strip(),
      website_link = form.website_link.data.strip(),
      seeking_venues = form.seeking_venue.data,
      seeking_description = form.seeking_description.data.strip()
    )


    db.session.add(artist)
    db.session.commit()

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO:<Done> on unsuccessful db insert, flash an error instead.
  except Exception as e:
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')

    flash(e)
    db.session.rollback()

  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all()

  data = [
    {
    "venue_id": show.venue_id,
    "venue_name":  Venue.query.with_entities(Venue.name).filter_by(id = show.venue_id).first().name,
      "artist_image_link":Artist.query.with_entities(Artist.image_link).filter_by(id = show.venue.id).first(),
    "artist_id":show.artist_id,
    "artist_name":  Artist.query.with_entities(Artist.name).filter_by(id = show.artist_id).first().name,
      "artist_image_link":Artist.query.with_entities(Artist.image_link).filter_by(id = show.artist_id).first(),
    "start_time": str(show.start_time)
  }
  for show in shows
  ]

  


  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO:<DONE> insert form data as a new Show record in the db, instead
  try:
    form = ShowForm()

    artist_id = form.artist_id.data
    venue_id = form.venue_time.data
    start_time = form.start_time.data

    show = Show(artist_id=artist_id,venue_id=venue_id,start_time=start_time)

    db.session.add(show)
    db.session.commit()

    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
  # TODO:<DONE> on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
    db.session.rollback()
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()

  return render_template('pages/home.html')



@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
