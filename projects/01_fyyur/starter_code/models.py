from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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