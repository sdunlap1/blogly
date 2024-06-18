"""Models for Blogly."""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
  __tablename__ = 'users'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  first_name = db.Column(db.String(50), nullable=False)
  last_name = db.Column(db.String(50), nullable=False)
  image_url = db.Column(db.String(255), nullable=False, default='https://via.placeholder.com/150')
  
  posts = db.relationship('Post', backref='user', cascade='all, delete-orphan')
  
  def __repr__(self):
    return f'<User {self.first_name} {self.last_name}>'

  def get_full_name(self):
    return f'{self.first_name} {self.last_name}'

class Post(db.Model):
   __tablename__ = 'posts'

   id = db.Column(db.Integer, primary_key=True, autoincrement=True)
   title = db.Column(db.String(100), nullable=False)
   content = db.Column(db.Text, nullable=False)
   created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
   user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

   def __repr__(self):
    return f'<Post {self.title} by User {self.user.id}>'

def connect_db(app):
  db.app = app
  db.init_app(app)
