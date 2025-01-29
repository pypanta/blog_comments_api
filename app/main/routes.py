from flask import abort, jsonify, request

from app import db
from app.auth.tokens import token_required
from app.models import Comment, Contact

from . import bp


@bp.route('/')
@token_required
def commetns(*args, **kwargs):
    """Get all comments"""
    top_level_comments = Comment.query.filter(Comment.parent_id == None).all()
    serialized_comments = [comment.to_dict() for comment in top_level_comments]
    if not serialized_comments:
        return jsonify(
            {'message': 'There are no any comments yet!'}
        ), 200

    return jsonify(serialized_comments), 200


@bp.route('/<string:post_id>')
def post_comments(post_id):
    """Get all comments for a specific post."""
    top_level_comments = Comment.query.filter(Comment.post_id == post_id,
                                              Comment.parent_id == None).all()
    serialized_comments = [comment.to_dict() for comment in top_level_comments]
    if not serialized_comments:
        return jsonify(
            {'message': 'There are no any comments for this post yet!'}
        ), 200

    return jsonify(serialized_comments), 200


@bp.route('/new', methods=['POST'])
def create_new_comment():
    """Create a new comment."""
    data = request.get_json()

    if not data.get('body') or not data.get('post_id'):
        return jsonify({
            'message': 'Invalid request data. "body" and "post_id" are required.'
        }), 400

    comment = Comment(**data)
    db.session.add(comment)
    db.session.commit()

    return jsonify(comment.to_dict()), 201


@bp.route('/<int:comment_id>/update', methods=['PUT'])
@token_required
def update_comment(comment_id, *args, **kwargs):
    """Edit an existing comment."""
    data = request.get_json()
    user = kwargs.get('user')

    if not data.get('body'):
        return jsonify({
            'message': 'Invalid request data. "body" is required.'}), 400

    if user.is_admin:
        comment = Comment.query.filter_by(id=comment_id).first()
    else:
        comment = Comment.query.filter_by(id=comment_id,
                                          user_id=user.id).first()

    if comment is None:
        return jsonify({'message': 'Comment not found'}), 404

    comment.body = data['body']
    db.session.commit()

    return jsonify(comment.to_dict()), 200


@bp.route('/<int:comment_id>/delete', methods=['DELETE'])
@token_required
def delete_comment(comment_id, *args, **kwargs):
    """Delete a comment."""
    user = kwargs.get('user')

    if user.is_admin:
        comment = Comment.query.filter_by(id=comment_id).first()
    else:
        comment = Comment.query.filter_by(id=comment_id,
                                          user_id=user.id).first()

    if comment is None:
        return jsonify({'message': 'Comment not found'}), 404

    db.session.delete(comment)
    db.session.commit()

    return jsonify({'message': 'Comment deleted successfully'}), 200


@bp.route('/new-contact', methods=['POST'])
def contact_me():
    data = request.get_json()

    missing_fields = []

    for field in ('name', 'email', 'subject', 'message'):
        if field not in data or not data.get(field):
            missing_fields.append(field)

    if missing_fields:
        return jsonify(
            {"message": f"[ {', '.join(missing_fields)} ] is required field(s)"}
        ), 400

    contact = Contact(**data)
    db.session.add(contact)
    db.session.commit()

    return jsonify({'message': 'Your message is successfully sent!'}), 200


@bp.route('/contacts')
@token_required
def contacts(*args, **kwargs):
    is_admin_user = kwargs.get('user').is_admin
    if not is_admin_user:
        return jsonify({'message': 'You are not authorized'}), 401

    contacts = Contact.query.filter_by(is_read=False).order_by(
        Contact.created_at.desc()).all()
    return jsonify(contacts), 200


@bp.route('/read-contact/<int:contact_id>')
def mark_contact_as_read(contact_id):
    contact = Contact.query.filter_by(id=contact_id).first()

    if contact:
        contact.is_read = True
        db.session.commit()
        return jsonify({'message': 'Success!'}), 200

    return jsonify({'message': 'Contact not found'}), 404


@bp.route('/delete-contact/<int:contact_id>')
def delete_contact(contact_id):
    contact = Contact.query.filter_by(id=contact_id).first()

    if contact:
        contact.is_read = True
        db.session.commit()
        return jsonify({'message': 'Success!'}), 200

    return jsonify({'message': 'Contact not found'}), 404
