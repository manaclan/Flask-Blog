from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
#from wtforms.validators import DataRequired
from wtforms.validators import ValidationError, DataRequired, Length
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')


class CommentForm(FlaskForm):
    comment = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')

class PostForm(FlaskForm):
    title = TextAreaField('Title', validators=[
        DataRequired(), Length(min=1, max=140)])
    content = TextAreaField(
        'Content', 
        validators=[DataRequired()],
        render_kw={'style':'height: 300px; width: 500px;'}
        )
    published = BooleanField('Published?')
    save = SubmitField('Save', render_kw={'class': 'btn btn-primary'})
    cancel = SubmitField('Cancel')