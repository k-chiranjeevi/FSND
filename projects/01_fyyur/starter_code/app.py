#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from dateutil import parser


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


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    show = db.relationship('Show', backref='Venue', lazy=True)
    
    

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    show = db.relationship('Show', backref='Artist', lazy=True)
    
class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    

    

    
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

@app.route('/venues')
def venues():
  data = []
  locations = set()
  venues = Venue.query.all()
  for venue in venues:
    locations.add((venue.city, venue.state))
  for location in locations:
    data.append({
      "city": location[0],
      "state": location[1],
      "venues": []
    })
  for venue in venues:
    num_upcoming_shows = 0
    shows = Show.query.filter_by(venue_id=venue.id).all()
    now = datetime.now()
    for show in shows:
      if show.start_time > now:
        num_upcoming_shows += 1
    for location in data:
      if venue.state == location['state'] and venue.city == location['city']:
        location['venues'].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": num_upcoming_shows
        })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term','')
  result = Venue.query.filter(Venue.name.ilike(f'{search_term}%'))
  response = {
    "count": result.count(),
    "data": result
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.filter_by(id=venue_id).first()
  upcoming_show = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).all()
  past_show = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).all()

    # get all shows for given venue
  

    # returns upcoming shows
  def upcoming_shows():
    upcoming = []
    
    

        # if show is in future, add show details to upcoming
    for show in upcoming_show:
      if show.start_time > datetime.now():
        upcoming.append({
          "artist_id": show.artist_id,
          "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
          "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
          "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
       
        })
    return upcoming

    # returns past shows
  def past_shows():
    
    past = []

        # if show is in past, add show details to past
    for show in past_show :
      if show.start_time < datetime.now():
        past.append({
          "artist_id": show.artist_id,
          "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
          "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
          "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        })  
      
    return past

    # data for given venue
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "facebook_link": venue.facebook_link,
    "image_link": venue.image_link,
    "past_shows": past_shows(),
    "upcoming_shows": upcoming_shows(),
    "past_shows_count": len(past_shows()),
    "upcoming_shows_count": len(upcoming_shows())
  }

    # return template with venue data
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  phone = request.form.get('phone')
  genres = request.form.get('genres')
  image_link = request.form.get('image_link')
  facebook_link = request.form.get('facebook_link')
  
  
  venue = Venue(name = name, city = city, state = state, phone = phone, genres = genres, facebook_link = facebook_link, image_link = image_link)
  db.session.add(venue)
  db.session.commit()
  
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = db.session.query(Venue).filter_by(id=venue_id).first()
    name = venue.name
    db.session.delete(venue)
    db.session.commit()
    flash('Venue, ' + name + ' successfully deleted.')
  except:
    flash('Something went wrong. ' + name + ' could not be deleted.')
  return render_template('pages/home.html')

  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[]
  artist = Artist.query.all()
  for a in artist:
    data.append(a)
  return render_template('pages/artists.html', artists=data)



# Search artists
@app.route('/artists/search', methods=['POST'])
def search_artists():
  data = []
  artists = []
  search_term = request.form.get("search_term").lower()
  for artist in db.session.query(Artist).with_entities(Artist.id, Artist.name).all():
    if search_term in artist.name.lower():
      artists.append(artist)
  for artist in artists:
        # Filter artist upcoming shows
    upcoming_shows = Show.query.filter_by(artist_id=artist.id).filter(Show.start_time > datetime.utcnow().isoformat()).all()
    
    data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len(upcoming_shows)
    })
    response = {
        "count": len(artists),
        "data": data
    }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.filter_by(id=artist_id).first()

    # get all shows matching artist id
  artist = Artist.query.get(artist_id)
  now= datetime.datetime.utcnow()
  artist.upcoming_shows_count = db.session.query(Artist).join(Show, Show.artist_id == Artist.id).filter(Show.artist_id == artist_id, Show.start_time > now).count()
  artist.upcoming_shows = db.session.query(Artist).join(Show, Show.artist_id == Artist.id).filter(Show.artist_id == artist_id, Show.start_time > now).all()
  artist.past_shows_count = db.session.query(Artist).join(Show, Show.artist_id == Artist.id).filter(Show.artist_id == artist_id, Show.start_time < now).count()
  artist.past_shows = db.session.query(Artist).join(Show, Show.artist_id == Artist.id).filter(Show.artist_id == artist_id, Show.start_time > now).all()  

    # return artist page with data
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = db.session.query(Artist).filter_by(id=artist_id).first()
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.seeking_description.data = artist.seeking_description
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  form.website.data = artist.website
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = db.session.query(Artist).filter_by(id=artist_id).first()
  if artist:
    try:
      artist.name = form.name.data,
      artist.city = form.city.data,
      artist.state = form.state.data,
      artist.phone = form.phone.data,
      artist.seeking_description = form.seeking_description.data,
      artist.facebook_link = form.facebook_link.data,
      artist.website = form.website.data,
      artist.genres = form.genres.data
       # add to database
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] +
                  ' was successfully updated.')
    except:
        flash('Something went wrong. Artist ' +
        request.form['name'] + ' could not be updated.')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  form = VenueEditForm()
  venue = db.session.query(Venue).filter_by(id=venue_id).first()
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.seeking_description.data = venue.seeking_description
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  form.website.data = venue.website
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = db.session.query(Venue).filter_by(id=venue_id).first()
  if venue:
    try:
      venue.name = form.name.data,
      venue.city = form.city.data,
      venue.state = form.state.data,
      venue.address = form.address.data,
      venue.phone = form.phone.data,
      venue.seeking_description = form.seeking_description.data,
      venue.image_link = form.image_link.data,
      venue.facebook_link = form.facebook_link.data,
      venue.website = form.website.data,
      venue.genres = form.genres.data
            # add to database
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] +
                  ' was successfully updated.')
    except:
      flash('Something went wrong. Venue ' +
                  request.form['name'] + ' could not be updated.')
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  phone = request.form.get('phone')
  genres = request.form.get('genres')
  image_link = request.form.get('image_link')
  facebook_link = request.form.get('facebook_link')
  artist = Artist(name = name, city = city, state = state, phone = phone, genres = genres, image_link = image_link, facebook_link = facebook_link)
  db.session.add(artist)
  db.session.commit()
  
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
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
  shows = Show.query.all()

  data = []

    # get venue and artist information for each show
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
      "artist_id": show.artist_id,
      "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
      "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
      "start_time": datetime.strptime(str(show, show.start_time))
    })
    data.append(show)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
        # get user input data from form
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']

        # create new show with user data
    show = Show(artist_id=artist_id, venue_id=venue_id,start_time=start_time)

                    
        # add show and commit session
    db.session.add(show)
    db.session.commit()

        # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
        # rollback if exception
      db.session.rollback()

      flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  
  # on successful db insert, flash success
  flash('Show was successfully listed!')
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
