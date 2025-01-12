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

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about = db.Column(db.String(250), nullable=True)
    comments = db.relationship('Comment', backref='user')

    def __repr__(self):
        return f"<User <{self.username}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


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
        comment = {
            'id': self.id,
            'post_id': self.post_id,
            'body': self.body,
            'created_at': self.created_at,
            'user': self.user if self.user else 'Anonymous',
            'ago': timesince(self.created_at),
        }
        # Include replies if specified
        if include_replies:
            comment['replies'] = [reply.to_dict() for reply in self.replies] if self.replies else []
        else:
            comment['replies'] = []  # Explicitly set to empty list if replies are excluded
        return comment
