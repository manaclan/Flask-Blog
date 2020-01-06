from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from flask_flatpages.utils import pygmented_markdown
from flask import Markup


class User(UserMixin, db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self): #tells Python how to print objects of this class
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    

    def __repr__(self): #tells Python how to print objects of this class
        return '<Post {}>'.format(self.body)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), unique=True)
    slug =  db.Column(db.String(140), unique=True)
    content = db.Column(db.Text())
    published = db.Column(db.Boolean(create_constraint=True))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    def __repr__(self): #tells Python how to print objects of this class
        return '<Post {}, {}>'.format(self.title,
                                    self.published)

    def drafts(self):
        return Post.query.filter_by(published=False)

    def html_content(self):
        rendered_content = pygmented_markdown(self.content)
        return Markup(rendered_content)



    #def update_search_index(self):
    #    search_content = '\n'.join((self.title, self.content))
    #    try:
    #        fts_entry = FTSEntry.get(FTSEntry.docid == self.id)
    #    except FTSEntry.DoesNotExist:
    #        FTSEntry.create(docid=self.id, content=search_content)
    #    else:
    #        fts_entry.content = search_content
    #        fts_entry.save()

        
#class FTSEntry(FTSModel):
#    content = SearchField()
#
#    class Meta:
#        database = database
