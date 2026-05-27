import os
from flask import Blueprint, render_template, request, flash, jsonify, current_app, json, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from . import db
from .models import Sketch, Like, User

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        file = request.files.get('sketch_image')

        if file and file.filename != '':
            filename = secure_filename(file.filename)

            # Use this standard way to find your folders
            # This looks for the 'static/uploads' folder relative to this file
            base_dir = os.path.dirname(os.path.abspath(__file__))
            upload_folder = os.path.join(base_dir, 'static', 'uploads')

            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

            new_sketch = Sketch(image_path=filename, user_id=current_user.id)
            db.session.add(new_sketch)
            db.session.commit()
            flash('Image Uploaded!', category='success')
        else:
            flash('No image selected!', category='error')

    # Get all sketches to display on the home page
    all_sketches = Sketch.query.all()
    return render_template("home.html", user=current_user, all_notes=all_sketches)



@views.route('/myProfile', methods=['GET', 'POST'])
@login_required
def myProfile():
    sketches = Sketch.query.filter_by(user_id=current_user.id).all()
    total_likes = sum(len(s.likes) for s in sketches)
    return render_template("myProfile.html", user=current_user, current_user_sketches=sketches, total_likes=total_likes)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    # 1. Get the data sent from JavaScript
    data = json.loads(request.data)
    noteId = data['noteId']

    # 2. Find the sketch in the database
    sketch = Sketch.query.get(noteId)

    if sketch:
        # 3. Security Check: Only the owner can delete
        if sketch.user_id == current_user.id:
            # OPTIONAL: Delete the physical file from the folder
            try:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(base_dir, 'static', 'uploads', sketch.image_path)
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file: {e}")

            # 4. Delete from database
            db.session.delete(sketch)
            db.session.commit()

    return jsonify({})  # Return an empty response to tell JS we are done

@views.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        bio = request.form.get('bio', '').strip()

        if len(bio) > 280:
            flash('Bio must be 280 characters or fewer.', category='error')
            return redirect(url_for('views.edit_profile'))

        website_url = request.form.get('website_url', '').strip()
        if website_url and not website_url.startswith(('http://', 'https://')):
            website_url = 'https://' + website_url

        instagram_handle = request.form.get('instagram_handle', '').strip().lstrip('@')

        current_user.display_name     = request.form.get('display_name', '').strip()
        current_user.bio              = bio
        current_user.location         = request.form.get('location', '').strip()
        current_user.contact_email    = request.form.get('contact_email', '').strip()
        current_user.instagram_handle = instagram_handle
        current_user.website_url      = website_url

        db.session.commit()
        flash('Profile updated.', category='success')
        return redirect(url_for('views.myProfile'))

    return render_template('edit_profile.html', user=current_user)


@views.route('/profile/<username>')
@login_required
def public_profile(username):
    profile_user = User.query.filter(User.first_name.ilike(username)).first_or_404()
    sketches = Sketch.query.filter_by(user_id=profile_user.id).all()
    total_likes = sum(len(s.likes) for s in sketches)
    return render_template('public_profile.html',
                           user=current_user,
                           profile_user=profile_user,
                           sketches=sketches,
                           total_likes=total_likes)


@views.route('/like-sketch/<sketch_id>', methods=['POST'])
@login_required
def like(sketch_id):
    sketch = Sketch.query.get_or_404(sketch_id)
    # Check if this user already liked this specific sketch
    like = Like.query.filter_by(user_id=current_user.id, sketch_id=sketch_id).first()

    if not sketch:
        return jsonify({'error': 'Sketch does not exist.'}, 400)
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        new_like = Like(user_id=current_user.id, sketch_id=sketch_id)
        db.session.add(new_like)
        db.session.commit()

    return jsonify({"likes": len(sketch.likes), "liked": current_user.id in map(lambda x: x.user_id, sketch.likes)})