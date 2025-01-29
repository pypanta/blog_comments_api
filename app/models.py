from datetime import UTC, datetime
from dataclasses import dataclass

from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.utils.timesince import timesince


@dataclass
class User(db.Model):
    id: int
    username: str
    email: str
    about: str
    is_admin: bool

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about = db.Column(db.String(250), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    comments = db.relationship('Comment', backref='user')

    def __repr__(self):
        return f"<User <{self.username}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        user = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'about': self.about,
            'is_admin': self.is_admin
        }

        return user


@dataclass
class Comment(db.Model):
    id: int
    post_id: str
    body: str
    created_at: datetime
    user_id: int
    parent_id: int

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.String(500), nullable=False, index=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    user_id = db.Column(db.Integer,
                        db.ForeignKey('user.id', ondelete='SET NULL'),
                        nullable=True)
    # Self-referencing foreign key
    parent_id = db.Column(db.Integer,
                          db.ForeignKey('comment.id', ondelete='CASCADE'),
                          nullable=True)
    # Relationship for parent comment
    # parent = db.relationship('Comment', remote_side=[id], backref='replies')
    parent = db.relationship(
        'Comment',
        remote_side=[id],
        backref=db.backref('replies', cascade="all, delete-orphan")
    )

    def __repr__(self):
        return f"<Comment> {self.id}: {self.created_at}"

    def to_dict(self, include_replies=True):
        """
        Convert the Comment object to a dictionary.
        Optionally include serialized nested replies.
        """
        if self.user:
            user = self.user.username
        else:
            user = 'Anonymous'
        comment = {
            'id': self.id,
            'post_id': self.post_id,
            'body': self.body,
            'created_at': self.created_at,
            'user': user,
            'ago': timesince(self.created_at),
        }
        # Include replies if specified
        if include_replies:
            comment['replies'] = [reply.to_dict() for reply in self.replies] if self.replies else []
        else:
            comment['replies'] = []  # Explicitly set to empty list if replies are excluded
        return comment


@dataclass
class Contact(db.Model):
    id: int
    name: str
    email: str
    subject: str
    message: str
    created_at: datetime
    is_read: bool

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True)
    email = db.Column(db.String(120), index=True)
    subject = db.Column(db.String(120), nullable=True)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    is_read = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Contact> {self.id}: {self.email}"
