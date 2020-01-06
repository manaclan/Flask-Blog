from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Comment, Post
from flask import request
from werkzeug.urls import url_parse
from app import db
from datetime import datetime
from app.main.forms import CommentForm, EditProfileForm, PostForm
from app.main import bp
from flask import current_app
import re

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
#@app.route is decorator
def index(): #view function
    form = CommentForm()
    #if form.validate_on_submit():
    #    post = Post(body=form.post.data, author=current_user)
    #    db.session.add(post)
    #    db.session.commit()
    #    flash('Your post is now live!')
    #    return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int) 
    posts = current_user.posts.paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Home', posts=posts.items, 
                            form=form, next_url=next_url, prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html',
                            title='Edit Profile',
                            form=form)

@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    comments = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=comments.next_num) \
        if comments.has_next else None
    prev_url = url_for('main.explore', page=comments.prev_num) \
        if comments.has_prev else None
    return render_template("index.html", title='Explore', comments=comments.items,
                          next_url=next_url, prev_url=prev_url)


@bp.route('/drafts/')
@login_required
def drafts():
    query = Post.drafts().order_by(Post.timestamp.desc())
    return object_list('index.html', query)


@bp.route('/create/', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        if request.form.get('title') and request.form.get('content'):
            published = False
            if request.form.get('published') =='y':
                published = True
            post = Post(
                title=request.form['title'],
                content=request.form['content'],
                published=published)
            
            if not post.slug:
                post.slug = re.sub('[^\w]+', '-', post.title.lower())
            db.session.commit()
            flash('Post created successfully.', 'success')
            if post.published:
                return redirect(url_for('main.detail', slug=post.slug))
            else:
                return redirect(url_for('main.edit', slug=post.slug))
        else:
            flash('Title and Content are required.', 'danger')
    return render_template('create.html')


@bp.route('/<slug>/')
def detail(slug):
    if current_user.is_authenticated:
        query = Post.query.all()
    else:
        query = Post.public()
    page = request.args.get('page', 1, type=int)
    comments = current_user.comments.order_by(Comment.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=comments.next_num) \
        if comments.has_next else None
    prev_url = url_for('main.user', username=user.username, page=comments.prev_num) \
        if comments.has_prev else None
    post = Post.query.filter_by(slug=slug).first_or_404()
    return render_template('detail.html', post=post,
                            comments=comments.items)


@bp.route('/<slug>/edit/', methods=['GET', 'POST'])
@login_required
def edit(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    if request.method == 'POST':
        if request.form.get('title') and request.form.get('content'):
            post.title = request.form['title']
            post.content = request.form['content']
            if request.form.get('published') =='y':
                post.published = True 
            else:
                post.published = False
            if not post.slug:
                post.slug = re.sub('[^\w]+', '-', post.title.lower())
            db.session.commit()

            flash('Post saved successfully.', 'success')
            if post.published:
                return redirect(url_for('main.detail', slug=post.slug))
            else:
                return redirect(url_for('main.edit', slug=post.slug))
        else:
            flash('Title and Content are required.', 'danger')

    return render_template('edit_post.html', post=post)


@bp.route('/create_post',  methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        if form.save.data:
            if form.title.data and form.content.data:
                slug = None
                if not slug:
                    slug = re.sub('[^\w]+', '-', form.title.data.lower())
                post = Post(
                    title=form.title.data,
                    content=form.content.data,
                    slug=slug,
                    published=form.published.data,
                    author=current_user
                )
                db.session.add(post)
                db.session.commit()
                flash('Post saved successfully.', 'success')
                return redirect(url_for('main.detail', slug=post.slug))
            else:
                flash('Title and Content are required.', 'danger')
        else:
            redirect(url_for('main.index'))
    return render_template('create_post.html', form=form)