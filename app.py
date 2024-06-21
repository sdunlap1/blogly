"""Blogly application."""

import psycopg2
from flask import Flask, redirect, render_template, request, url_for
from models import db, connect_db, User, Post, Tag, PostTag

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

def create_database():
    conn = psycopg2.connect(dbname='postgres', user='stephend', password='your_password')
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'blogly'")
    exists = cur.fetchone()
    if not exists:
        cur.execute('CREATE DATABASE blogly')
    cur.close()
    conn.close()

create_database()
connect_db(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect('/users')

@app.route('/users')
def list_users():
    users = User.query.order_by(User.last_name, User.first_name).all()
    return render_template('users.html', users=users)

@app.route('/users/new', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        image_url = request.form['image_url'] or None

        new_user = User(first_name=first_name, last_name=last_name, image_url=image_url)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/users')
    
    return render_template('new_user.html')

@app.route('/users/<int:user_id>')
def show_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user_detail.html', user=user)

@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.image_url = request.form['image_url'] or None

        db.session.commit()

        return redirect(url_for('show_user', user_id=user.id))

    return render_template('edit_user.html', user=user)

@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect('/users')

@app.route('/users/<int:user_id>/posts/new', methods=['GET', 'POST'])
def add_post(user_id):
    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        tag_ids = request.form.getlist('tags')

        new_post = Post(title=title, content=content, user_id=user_id)
        for tag_id in tag_ids:
            tag = Tag.query.get(tag_id)
            if tag:
                new_post.tags.append(tag)
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('show_user', user_id=user_id))

    return render_template('new_post.html', user=user, tags=tags)

@app.route('/posts/<int:post_id>')
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post)

@app.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        tag_ids = request.form.getlist('tags')

        post.tags = []
        for tag_id in tag_ids:
            tag = Tag.query.get(tag_id)
            if tag:
                post.tags.append(tag)
        db.session.commit()
        return redirect(url_for('show_post', post_id=post.id))

    return render_template('edit_post.html', post=post, tags=tags)

@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    user_id = post.user_id
    db.session.delete(post)
    db.session.commit()

    return redirect(url_for('show_user', user_id=user_id))

# Tag Routes
@app.route('/tags')
def list_tags():
    next_url = request.args.get('next')
    print(f"Next URL in list_tags: {next_url}")  # Add this line to print the next URL
    tags = Tag.query.all()
    return render_template('list_tags.html', tags=tags, next=next_url)

@app.route('/tags/new', methods=['GET', 'POST'])
def add_tag():
    next_url = request.args.get('next', url_for('list_tags'))
    print(f"Next URL in add_tag (GET): {next_url}")  # Debugging line
    if request.method == 'POST':
        next_url = request.form.get('next', url_for('list_tags'))
        print(f"Next URL in add_tag (POST): {next_url}")  # Debugging line
        name = request.form['name']
        if Tag.query.filter_by(name=name).first():
            # Handle the case where the tag already exists
            error = f'Tag "{name}" already exists.'
            posts = Post.query.all()
            return render_template('new_tag.html', posts=posts, next=next_url, error=error)
        new_tag = Tag(name=name)
        db.session.add(new_tag)
        db.session.commit()
        return redirect(url_for('list_tags', next=next_url))  # Ensure redirect with next URL
    posts = Post.query.all()
    return render_template('new_tag.html', posts=posts, next=next_url)

@app.route('/tags/<int:tag_id>')
def show_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    return render_template('show_tag.html', tag=tag)

@app.route('/tags/<int:tag_id>/edit', methods=['GET', 'POST'])
def edit_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    if request.method == 'POST':
        tag.name = request.form['name']
        tag.posts = []
        for post_id in request.form.getlist('posts'):
            post = Post.query.get(post_id)
            tag.posts.append(post)
        db.session.commit()
        return redirect(url_for('list_tags'))
    posts = Post.query.all()
    return render_template('edit_tag.html', tag=tag, posts=posts)

@app.route('/tags/<int:tag_id>/delete', methods=['POST'])
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    return redirect(url_for('list_tags'))
