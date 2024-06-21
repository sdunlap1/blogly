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

   tags = db.relationship('Tag', secondary='posts_tags', backref='posts')

   def __repr__(self):
    return f'<Post {self.title}>'

class Tag(db.Model):
  __tablename__ = 'tags'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String(50), unique=True, nullable=False)

  def __repr__(self):
    return f'<Tag {self.name}>'

class PostTag(db.Model):
  __tablename__ = 'posts_tags'

  post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True, nullable=False)
  tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True, nullable=False)

  def __repr__(self):
    return f'<PostTag post_id={self.post_id} tag_id={self.tag_id}>'

def connect_db(app):
  db.app = app
  db.init_app(app)
