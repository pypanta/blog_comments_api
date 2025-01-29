from app import create_app, db
from app.models import Comment, Contact, User


app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Comment': Comment, 'Contact': Contact}
