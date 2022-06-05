# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

from email.policy import default
from pickle import NONE
import dateutil.parser
import babel
from flask import (
  Flask, 
  render_template, 
  request, 
  Response, 
  flash, 
  redirect, 
  url_for
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
#  Models.
# ----------------------------------------------------------------------------#
from models import *


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"

    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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
  
  locations = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()

  # loop through every unique location and assign the various variables
  # Using list comprehensions -> for loop and append to the data list in one step
  data= [{
    'city': location[0],
    'state': location[1],
    'venues': [{
            # declare the various properties of venue while
            'id': venue.id, 
            'name': venue.name,
            "num_upcoming_shows":Show.query.filter(Show.start_time > datetime.now() , Show.venue_id == venue.id).count()} 
            #looping through all the venues in the various location
            for venue in Venue.query.with_entities(Venue.id,Venue.name).filter(Venue.city == location[0], Venue.state == location[1]).all()
            ]

    }
    # loop through the various city and state and create a unique instance of city and state
    for location in locations
  ]

  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():

  search_term = request.form.get('search_term','')
  results = Venue.query.filter(Venue.name.ilike(f"%{search_term}%"))

  # Using list comprehension
  response={
    "count": results.count(),
    "data": [{
      "id": result.id,
      "name": result.name,
      # add list of all upcoming shows of the venue
      "num_upcoming_shows": Show.query.filter(Show.start_time > datetime.now() , Show.venue_id == result.id).count()
    }
    for result in results
    ]
  }

  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
 

  venue = Venue.query.get(venue_id)



  past_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()

  upcoming_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()

  past_shows_count =db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).count()
  
  upcoming_shows_count = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).count()

  

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
      "artist_name": past_show.artist.name,
      "artist_image_link":past_show.artist.image_link,
      "start_time": str(past_show.start_time)
    }
    for past_show in past_shows_query

    ],
    
    "upcoming_shows": [{
      "artist_id": upcoming_show.artist_id,
      "artist_name": upcoming_show.artist.name,
      "artist_image_link":upcoming_show.artist.image_link,
      "start_time": str(upcoming_show.start_time)
    }
    for upcoming_show in upcoming_shows_query
    ],

    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
    }


  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
 
  
  #Using flask_wtf form
  form = VenueForm()

  # Ensuring all or none principle of transactions using try except finally -> if there is an error the database will not be updated
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


    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    print(sys.exc_info())

  finally:
      db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash(f'Venue was successfully deleted!')

  except:
    db.session.rollback()
    flash(f'An error occurred. Venue  could not be deleted.')
    print(sys.exc_info())

  finally:
    db.session.close()


  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
 

  # get only id and name column of all artists
  artists = Artist.query.with_entities(Artist.id,Artist.name)

  # create each artist
  data = [{

      'id': artist.id,
      'name' : artist.name
  }
      for artist in artists
  ]

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  
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
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  

  artist = Artist.query.get(artist_id)

  past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()

  upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()

  past_shows_count =db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).count()
  
  upcoming_shows_count = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).count()


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


    # loop through the past_shows_query and  
    "past_shows": [{
      "venue_id": past_show.venue_id,
      "venue_name": past_show.venue.name,
      "venue_image_link":past_show.venue.image_link,
      "start_time": str(past_show.start_time)
    }
    for past_show in past_shows_query
    ],

     "upcoming_shows": [{
      "venue_id": upcoming_show.venue_id,
      "venue_name": upcoming_show.venue.name,
      "venue_image_link":upcoming_show.venue.image_link,
      "start_time": str(upcoming_show.start_time)
    }
    for upcoming_show in upcoming_shows_query
    ],
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
    }
  

  return render_template('pages/show_artist.html', artist=data)

# #  Update
# #  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

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
  
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  
  try:
    form = ArtistForm()
    
    artist = Artist.query.get(artist_id)

    artist.name = form.name.data.strip()
    artist.city = form.city.data.strip()
    artist.state = form.state.data
    artist.phone = form.phone.data.strip()
    artist.genres = form.genres.data
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
    print(sys.exc_info())

  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  

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

  
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  
  try:
    form = VenueForm()
    
    venue = Venue.query.get(venue_id)

    venue.name = form.name.data.strip()
    venue.city = form.city.data.strip()
    venue.state = form.state.data
    venue.address = form.address.data.strip()
    venue.phone = form.phone.data.strip()
    venue.genres = form.genres.data
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
    print(sys.exc_info())
    

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
    
  except:
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    print(sys.exc_info())

    db.session.rollback()

  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()

  data = [
    {
    "venue_id": show.venue_id,
    "venue_name":  Venue.query.with_entities(Venue.name).filter_by(id = show.venue_id).first().name,
      "artist_image_link":Artist.query.with_entities(Artist.image_link).filter_by(id = show.venue.id).first(),
    "artist_id":show.artist_id,
    "artist_name":  Artist.query.with_entities(Artist.name).filter_by(id = show.artist_id).first().name,
      "artist_image_link":Artist.query.with_entities(Artist.image_link).filter_by(id = show.artist_id).first().image_link,
    #convert datetime to string
    "start_time": str(show.start_time)
  }
  for show in shows
  ]

  


  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  try:
    form = ShowForm()

    artist_id = form.artist_id.data
    venue_id = form.venue_id.data
    start_time = form.start_time.data

    show = Show(artist_id=artist_id,venue_id=venue_id,start_time=start_time)

    db.session.add(show)
    db.session.commit()

    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except Exception as e:
    flash(e)
  
    flash('An error occurred. Show could not be listed.')

    print(sys.exc_info())

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
