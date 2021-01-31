#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
      __tablename__ = 'Show'

      id = db.Column(db.Integer, primary_key=True)
      start_time = db.Column(db.DateTime())
      artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
      venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))

      artist = db.relationship('Artist', backref=db.backref('shows', cascade='all, delete'), lazy='joined')
      venue = db.relationship('Venue', backref=db.backref('shows', cascade='all, delete'), lazy='joined')

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    genres = db.Column(db.PickleType)

    def __repr__(self):
          return f'id: {self.id}, name: {self.name}, genres: {self.genres}, website: {self.website}, seeking_talent: {self.seeking_talent}, seeking_description: {self.seeking_description}'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    genres = db.Column(db.PickleType)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  areas = db.session.query(Venue.city, Venue.state).distinct().all()

  data1 = []
  for area in areas:
        venues = db.session.query(Venue.id, Venue.name).filter(Venue.city==area.city).all()
        venue_list = []
        for venue in venues:
              upcoming = db.session.query(Show.id).filter(Show.venue_id==venue.id).filter(Show.start_time > datetime.now()).all()
              venue_entry = {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(upcoming)
              }
              venue_list.append(venue_entry)
        entry = {
          "city": area.city,
          "state": area.state,
          "venues": venue_list,
        }
        data1.append(entry);

  return render_template('pages/venues.html', areas=data1);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  term = request.form.get('search_term')
  search = "%{}%".format(term)

  results = db.session.query(Venue.id, Venue.name).filter(Venue.name.ilike(search)).all()

  data = []
  for result in results:
        upcoming = db.session.query(Show.id).filter(Show.venue_id==result.id).filter(Show.start_time > datetime.now()).all()
  
        data_entry = {
          "id": result.id,
          "name": result.name,
          "num_upcoming_shows": len(upcoming)
        }
        data.append(data_entry)
  
  response1 = {
    "count": len(results),
    "data": data
  }

  return render_template('pages/search_venues.html', results=response1, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = db.session.query(Venue.id, Venue.name, Venue.genres, Venue.address, Venue.city, Venue.state, Venue.phone, Venue.website, Venue.facebook_link, Venue.seeking_talent, Venue.seeking_description, Venue.image_link).filter(Venue.id==venue_id).first()
  
  pastShows = db.session.query(Show.id, Show.artist_id, Show.start_time).filter(Show.venue_id==venue_id).filter(Show.start_time < datetime.now()).all()
  upcomingShows = db.session.query(Show.id, Show.artist_id, Show.start_time).filter(Show.venue_id==venue_id).filter(Show.start_time > datetime.now()).all()

  pastShowList = []
  for pastShow in pastShows:
        artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id==pastShow.artist_id).first()
        artistEntry = {
          "artist_id": pastShow.artist_id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": str(pastShow.start_time),
        }
        pastShowList.append(artistEntry)

  upcomingShowList = []
  for upcomingShow in upcomingShows:
        artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id==upcomingShow.artist_id).first()
        artistEntry = {
          "artist_id": upcomingShow.artist_id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": str(upcomingShow.start_time),
        }
        upcomingShowList.append(artistEntry)

  dataNew = {
    "id": venue_id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": pastShowList,
    "upcoming_shows": upcomingShowList,
    "past_shows_count": len(pastShows),
    "upcoming_shows_count": len(upcomingShows),
  }

  return render_template('pages/show_venue.html', venue=dataNew)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
      venue = Venue()
      venue.name=request.form['name']
      venue.city=request.form['city']
      venue.state=request.form['state']
      venue.address=request.form['address']
      venue.phone=request.form['phone']
      venue.genres=request.form.getlist('genres')
      venue.facebook_link=request.form['facebook_link']
      venue.image_link=request.form['image_link']
      venue.website=request.form['website']
      if(request.form['seeking_talent'] == 'True'):
            venue.seeking_talent = True
      else:
            venue.seeking_talent = False
      if(request.form['seeking_description'] != ''):
            venue.seeking_description=request.form['seeking_description']

      db.session.add(venue)
      db.session.commit()

      # on successful db insert, flash success
      flash('Venue ' + venue.name + ' was successfully listed!')
  except:
      error = True
      db.session.rollback()
      flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
  finally:
      db.session.close()

  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  try:
      Venue.query.filter_by(id=venue_id).delete()
      db.session.commit()
  except:
      db.session.rollback()
  finally:
      db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  artists = db.session.query(Artist.id, Artist.name).all()

  data1 = []
  for artist in artists:
        artist_entry = {
          "id": artist.id,
          "name": artist.name,
        }
        data1.append(artist_entry)

  return render_template('pages/artists.html', artists=data1)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  term = request.form.get('search_term')
  search = "%{}%".format(term)

  results = db.session.query(Artist.id, Artist.name).filter(Artist.name.ilike(search)).all()

  data = []
  for result in results:
        upcoming = db.session.query(Show.id).filter(Show.artist_id==result.id).filter(Show.start_time > datetime.now()).all()
  
        data_entry = {
          "id": result.id,
          "name": result.name,
          "num_upcoming_shows": len(upcoming)
        }
        data.append(data_entry)
  
  response1 = {
    "count": len(results),
    "data": data
  }

  return render_template('pages/search_artists.html', results=response1, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  artist = db.session.query(Artist.id, Artist.name, Artist.genres, Artist.city, Artist.state, Artist.phone, Artist.website, Artist.facebook_link, Artist.seeking_venue, Artist.seeking_description, Artist.image_link).filter(Artist.id==artist_id).first()
  
  pastShows = db.session.query(Show.id, Show.venue_id, Show.start_time).filter(Show.artist_id==artist_id).filter(Show.start_time < datetime.now()).all()
  upcomingShows = db.session.query(Show.id, Show.venue_id, Show.start_time).filter(Show.artist_id==artist_id).filter(Show.start_time > datetime.now()).all()

  pastShowList = []
  for pastShow in pastShows:
        venue = db.session.query(Venue.name, Venue.image_link).filter(Venue.id==pastShow.venue_id).first()
        venueEntry = {
          "venue_id": pastShow.venue_id,
          "venue_name": venue.name,
          "venue_image_link": venue.image_link,
          "start_time": str(pastShow.start_time),
        }
        pastShowList.append(venueEntry)

  upcomingShowList = []
  for upcomingShow in upcomingShows:
        venue = db.session.query(Venue.name, Venue.image_link).filter(Venue.id==upcomingShow.venue_id).first()
        venueEntry = {
          "venue_id": upcomingShow.venue_id,
          "venue_name": venue.name,
          "venue_image_link": venue.image_link,
          "start_time": str(upcomingShow.start_time),
        }
        upcomingShowList.append(venueEntry)

  dataNew = {
    "id": artist_id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": pastShowList,
    "upcoming_shows": upcomingShowList,
    "past_shows_count": len(pastShows),
    "upcoming_shows_count": len(upcomingShows),
  }

  return render_template('pages/show_artist.html', artist=dataNew)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  artistFromDB = db.session.query(Artist.id, Artist.name, Artist.genres, Artist.city, Artist.state, Artist.phone, Artist.website, Artist.facebook_link, Artist.seeking_venue, Artist.seeking_description, Artist.image_link).filter(Artist.id==artist_id).first()

  artist = {
    "id": artist_id,
    "name": artistFromDB.name,
    "genres": artistFromDB.genres,
    "city": artistFromDB.city,
    "state": artistFromDB.state,
    "phone": artistFromDB.phone,
    "website": artistFromDB.website,
    "facebook_link": artistFromDB.facebook_link,
    "seeking_venue": artistFromDB.seeking_venue,
    "seeking_description": artistFromDB.seeking_description,
    "image_link": artistFromDB.image_link,
  }

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  artist = Artist.query.get(artist_id)

  error = False
  try:
      artist.name=request.form['name']
      artist.city=request.form['city']
      artist.state=request.form['state']
      artist.phone=request.form['phone']
      artist.genres=request.form.getlist('genres')
      artist.facebook_link=request.form['facebook_link']
      artist.image_link=request.form['image_link']
      artist.website=request.form['website']
      if(request.form['seeking_venue'] == 'True'):
            artist.seeking_venue = True
      else:
            artist.seeking_venue = False
      if(request.form['seeking_description'] != ''):
            artist.seeking_description=request.form['seeking_description']

      db.session.commit()

      # on successful db insert, flash success
      flash('Venue ' + artist.name + ' was successfully updated!')
  except:
      error = True
      db.session.rollback()
      flash('An error occurred. Venue ' + artist.name + ' could not be updated.')
  finally:
      db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venueFromDB = db.session.query(Venue.id, Venue.name, Venue.genres, Venue.address, Venue.city, Venue.state, Venue.phone, Venue.website, Venue.facebook_link, Venue.seeking_talent, Venue.seeking_description, Venue.image_link).filter(Venue.id==venue_id).first()

  venue = {
    "id": venue_id,
    "name": venueFromDB.name,
    "genres": venueFromDB.genres,
    "address": venueFromDB.address,
    "city": venueFromDB.city,
    "state": venueFromDB.state,
    "phone": venueFromDB.phone,
    "website": venueFromDB.website,
    "facebook_link": venueFromDB.facebook_link,
    "seeking_talent": venueFromDB.seeking_talent,
    "seeking_description": venueFromDB.seeking_description,
    "image_link": venueFromDB.image_link,
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)

  error = False
  try:
      venue.name=request.form['name']
      venue.city=request.form['city']
      venue.state=request.form['state']
      venue.address=request.form['address']
      venue.phone=request.form['phone']
      venue.genres=request.form.getlist('genres')
      venue.facebook_link=request.form['facebook_link']
      venue.image_link=request.form['image_link']
      venue.website=request.form['website']
      if(request.form['seeking_talent'] == 'True'):
            venue.seeking_talent = True
      else:
            venue.seeking_talent = False
      if(request.form['seeking_description'] != ''):
            venue.seeking_description=request.form['seeking_description']

      db.session.commit()

      # on successful db insert, flash success
      flash('Venue ' + venue.name + ' was successfully updated!')
  except:
      error = True
      db.session.rollback()
      flash('An error occurred. Venue ' + venue.name + ' could not be updated.')
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
      artist = Artist()
      artist.name=request.form['name']
      artist.city=request.form['city']
      artist.state=request.form['state']
      artist.phone=request.form['phone']
      artist.genres=request.form.getlist('genres')
      artist.facebook_link=request.form['facebook_link']
      artist.image_link=request.form['image_link']
      artist.website=request.form['website']
      if(request.form['seeking_venue'] == 'True'):
            artist.seeking_venue = True
      else:
            artist.seeking_venue = False
      if(request.form['seeking_description'] != ''):
            artist.seeking_description=request.form['seeking_description']

      db.session.add(artist)
      db.session.commit()

      # on successful db insert, flash success
      flash('Artist ' + artist.name + ' was successfully listed!')
  except:
      error = True
      db.session.rollback()
      flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
  finally:
      db.session.close()

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  shows = db.session.query(Show.venue_id, Show.artist_id, Show.start_time).all()
  showList = []
  for show in shows:
        venue = db.session.query(Venue.id, Venue.name).filter(Venue.id==show.venue_id).first()
        artist = db.session.query(Artist.id, Artist.name, Artist.image_link).filter(Artist.id==show.artist_id).first()
        showEntry = {
          "venue_id": show.venue_id,
          "venue_name": venue.name,
          "artist_id": show.artist_id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": str(show.start_time),
        }
        showList.append(showEntry)

  return render_template('pages/shows.html', shows=showList)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  try:
      show = Show()
      show.artist_id=request.form['artist_id']
      show.venue_id=request.form['venue_id']
      show.start_time=request.form['start_time']

      db.session.add(show)
      db.session.commit()

      # on successful db insert, flash success
      flash('Show was successfully listed!')
  except:
      error = True
      db.session.rollback()
      flash('An error occurred. Show could not be listed.')
  finally:
      db.session.close()

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
