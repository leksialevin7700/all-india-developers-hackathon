from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from flask_session import Session
import random
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# MongoDB Configuration
app.config['MONGO_URI'] = 'mongodb://localhost:27017/telelaw'
app.config['SESSION_TYPE'] = 'mongodb'
app.config['SESSION_MONGODB'] = MongoClient(app.config['MONGO_URI'])
app.config['SESSION_MONGODB_DB'] = 'telelaw'
app.config['SESSION_MONGODB_COLLECTION'] = 'sessions'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SECRET_KEY'] = 'uegahhsgjrhriuwt4u3'

# Initialize MongoDB session
Session(app)

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads/profile_pics'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# MongoDB Connection
client = MongoClient(app.config["MONGO_URI"])
db = client['telelaw']
lawyers_collection = db['lawyers']
bcrypt = Bcrypt(app)

# Sample Meet Links
MEET_LINKS = [
    "https://meet.google.com/efw-nrnb-efm",
    "https://meet.google.com/puo-hsqy-mda",
    "https://meet.google.com/puo-hsqy-mda",
    "https://meet.google.com/vdm-pcrv-duf",
    "https://meet.google.com/phc-jfxq-gft"
]

# Helper function for file validation
def allowed_file(filename):
    """Check if the uploaded file is an allowed image format."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Home Route
@app.route('/')
def home():
    return render_template('home.html')


# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        specialization = request.form['specialization']
        description = request.form['description']
        experience = request.form['experience']
        
        # New fields
        phone = request.form['phone']
        bar_council_id = request.form['bar_council_id']
        cases_handled = int(request.form['cases_handled']) if request.form['cases_handled'] else 0
        successful_cases = int(request.form['successful_cases']) if request.form['successful_cases'] else 0
        expected_payment = float(request.form['expected_payment']) if request.form['expected_payment'] else 0.0
        languages_spoken = request.form['languages_spoken']
        office_address = request.form['office_address']
        consultation_types = request.form.getlist('consultation_types')
        availability_hours = request.form['availability_hours']
        # --- ADDED: total_consultations field from signup form
        total_consultations = int(request.form['total_consultations']) if request.form.get('total_consultations') else 0
        
        # Validate successful cases don't exceed total cases
        if successful_cases > cases_handled:
            flash('Successful cases cannot exceed total cases handled.', 'danger')
            return render_template('signup.html')

        # Check if email already exists
        if lawyers_collection.find_one({'email': email}):
            flash('Email already registered. Please log in.', 'warning')
            return redirect(url_for('login'))

        # Calculate success rate
        success_rate = (successful_cases / cases_handled * 100) if cases_handled > 0 else 0

        # Save lawyer details to MongoDB
        lawyers_collection.insert_one({
            'name': name,
            'email': email,
            'password': password,
            'phone': phone,
            'bar_council_id': bar_council_id,
            'specialization': specialization,
            'description': description,
            'experience': experience,
            'cases_handled': cases_handled,
            'successful_cases': successful_cases,
            'success_rate': round(success_rate, 2),
            'expected_payment': expected_payment,
            'languages_spoken': languages_spoken,
            'office_address': office_address,
            'consultation_types': consultation_types,
            'availability_hours': availability_hours,
            'meet_links': [],
            # Use the value from the form, otherwise 0
            'total_consultations': total_consultations,
            'client_rating': 'N/A',
            'active_days': 0,
            'profile_pic': None,
            'verified': False,  # For future verification system
            'rating_count': 0,
            'average_rating': 0.0
        })

        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        lawyer = lawyers_collection.find_one({'email': email})

        if lawyer and bcrypt.check_password_hash(lawyer['password'], password):
            session['user_id'] = str(lawyer['_id'])
            session['email'] = lawyer['email']
            flash("Login successful!", "success")
            return redirect(url_for('profile'))
        else:
            flash("Invalid credentials. Try again.", "danger")

    return render_template('login.html')


# Lawyer Profile Page (GET only, edit moved to /edit_profile)
@app.route('/profile')
def profile():
    if 'email' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))

    lawyer = lawyers_collection.find_one({'email': session['email']})

    # Initialize meet links if missing
    if 'meet_links' not in lawyer:
        lawyers_collection.update_one(
            {'email': session['email']},
            {'$set': {'meet_links': []}}
        )
        lawyer = lawyers_collection.find_one({'email': session['email']})

    return render_template('profile.html', lawyer=lawyer)


# Edit Profile Page (GET/POST)
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'email' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))

    lawyer = lawyers_collection.find_one({'email': session['email']})

    if request.method == 'POST':
        updated_specialization = request.form['specialization']
        updated_description = request.form['description']
        updated_experience = request.form['experience']
        updated_phone = request.form['phone']
        updated_cases_handled = int(request.form['cases_handled']) if request.form['cases_handled'] else 0
        updated_successful_cases = int(request.form['successful_cases']) if request.form['successful_cases'] else 0
        updated_expected_payment = float(request.form['expected_payment']) if request.form['expected_payment'] else 0.0
        updated_languages_spoken = request.form['languages_spoken']
        updated_office_address = request.form['office_address']
        updated_consultation_types = request.form.getlist('consultation_types')
        updated_availability_hours = request.form['availability_hours']
        # --- ADDED: total_consultations from edit profile form
        updated_total_consultations = int(request.form['total_consultations']) if request.form.get('total_consultations') else 0

        # Validate successful cases don't exceed total cases
        if updated_successful_cases > updated_cases_handled:
            flash('Successful cases cannot exceed total cases handled.', 'danger')
            return render_template('edit.html', lawyer=lawyer)

        # Calculate success rate
        success_rate = (updated_successful_cases / updated_cases_handled * 100) if updated_cases_handled > 0 else 0

        update_data = {
            'specialization': updated_specialization,
            'description': updated_description,
            'experience': updated_experience,
            'phone': updated_phone,
            'cases_handled': updated_cases_handled,
            'successful_cases': updated_successful_cases,
            'success_rate': round(success_rate, 2),
            'expected_payment': updated_expected_payment,
            'languages_spoken': updated_languages_spoken,
            'office_address': updated_office_address,
            'consultation_types': updated_consultation_types,
            'availability_hours': updated_availability_hours,
            # Include total consultations in update
            'total_consultations': updated_total_consultations
        }

        # Handle profile picture upload
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"{session['email']}_{file.filename}")
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                # Save the profile picture
                file.save(file_path)

                # Update the lawyer's profile picture in MongoDB
                update_data['profile_pic'] = f"/static/uploads/profile_pics/{filename}"

        # Update lawyer profile
        lawyers_collection.update_one(
            {'email': session['email']},
            {'$set': update_data}
        )

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template('edit.html', lawyer=lawyer)


# Add Meet Link
@app.route('/add_meet_link', methods=['POST'])
def add_meet_link():
    if 'email' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))

    # Fetch lawyer and existing links
    lawyer = lawyers_collection.find_one({'email': session['email']})
    existing_links = lawyer.get('meet_links', [])

    # Select a random Meet link
    available_links = [link for link in MEET_LINKS if link not in existing_links]

    if available_links:
        random_link = random.choice(available_links)

        # Add the new link
        lawyers_collection.update_one(
            {'email': session['email']},
            {'$push': {'meet_links': random_link}}
        )

        flash('Google Meet link added to your profile!', 'success')
    else:
        flash('No more available Meet links.', 'warning')

    return redirect(url_for('profile'))


# Remove Meet Link
@app.route('/remove_meet_link/<path:link>', methods=['POST'])
def remove_meet_link(link):
    if 'email' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))

    # Remove the specified link
    lawyers_collection.update_one(
        {'email': session['email']},
        {'$pull': {'meet_links': link}}
    )

    flash('Google Meet link removed from your profile!', 'success')
    return redirect(url_for('profile'))


# Search Lawyers Route (New feature)
@app.route('/search_lawyers')
def search_lawyers():
    specialization = request.args.get('specialization', '')
    min_experience = request.args.get('min_experience', 0, type=int)
    max_payment = request.args.get('max_payment', 0, type=float)
    language = request.args.get('language', '')
    
    # Build search query
    query = {}
    if specialization:
        query['specialization'] = {'$regex': specialization, '$options': 'i'}
    if min_experience > 0:
        query['experience'] = {'$gte': min_experience}
    if max_payment > 0:
        query['expected_payment'] = {'$lte': max_payment}
    if language:
        query['languages_spoken'] = {'$regex': language, '$options': 'i'}
    
    # Find lawyers matching criteria
    lawyers = list(lawyers_collection.find(query, {'password': 0}))  # Exclude password field
    
    return render_template('search_lawyers.html', lawyers=lawyers, 
                         specialization=specialization, min_experience=min_experience,
                         max_payment=max_payment, language=language)


# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for('home'))


# Run the Flask server
if __name__ == '__main__':
    app.run(debug=True, port=3002)