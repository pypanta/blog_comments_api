from flask import abort, jsonify, request
from . import bp
from app import db
from app.models import Comment


@bp.route('/')
def commetns():
    comments = Comment.query.all()
    return jsonify(comments), 200


@bp.route('/<string:post_id>')
def post_comments(post_id):
    """Get all comments for a specific post."""
    comments = Comment.query.filter_by(post_id=post_id).all()
    top_level_comments = Comment.query.filter(Comment.parent_id == None).all()
    serialized_comments = [comment.to_dict() for comment in top_level_comments]
    if not serialized_comments:
        # abort(404, description='No comments found for the requested post')
        return jsonify(
            {'message': 'There are no any comments for this post yet!'}
        ), 200

    return jsonify(serialized_comments), 200


@bp.route('/new', methods=['POST'])
def create_new_comment():
    """Create a new comment."""
    data = request.get_json()

    if not data or not data.get('body') or not data.get('post_id'):
        abort_message = """
            Invalid request data. "body" and "post_id" are required."""
        abort(400, description=abort_message)

    comment = Comment(**data)
    db.session.add(comment)
    db.session.commit()

    return jsonify(comment.to_dict()), 201


@bp.route('/<int:comment_id>/update', methods=['PUT'])
def update_comment(comment_id):
    """Edit an existing comment."""
    data = request.get_json()

    if not data or not data.get('body'):
        abort(400, description='Invalid request data. "body" is required.')

    comment = Comment.query.filter_by(id=comment_id).first()

    if comment is None:
        abort(404, description='Comment not found')

    comment.body = data['body']
    db.session.commit()

    return jsonify(comment.to_dict()), 200


@bp.route('/<int:comment_id>/delete', methods=['DELETE'])
def delete_comment(comment_id):
    """Delete a comment."""
    comment = Comment.query.filter_by(id=comment_id).first()

    if comment is None:
        abort(404, description='Comment not found')

    db.session.delete(comment)
    db.session.commit()

    return jsonify(
        {
            'message': 'Comment deleted successfully',
            'comment': comment.to_dict()
        }), 200
