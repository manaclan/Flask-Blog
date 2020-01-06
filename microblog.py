from app import create_app, db
from app.models import User, Post, Comment


app = create_app()


@app.shell_context_processor
def make_shell_context():#registers the function as a shell context function
    return {'db': db, 'User': User, 'Post': Post, 'Comment': Comment}