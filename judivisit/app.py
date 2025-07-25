from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# MongoDB connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/legalservices"
client = MongoClient(app.config["MONGO_URI"])
db = client['telelaw']
users_collection = db['lawyers']

# Route to display lawyer listings with search
@app.route('/')
def lawyer_listings():
    specialization = request.args.get('specialization')
    query = {"specialization": {"$regex": specialization, "$options": "i"}} if specialization else {}
    projection = {
        "name": 1, 
        "email": 1, 
        "specialization": 1, 
        "description": 1, 
        "experience": 1,
        "profile_pic": 1,
        "meet_links": 1,
        "ratings": 1  # Include ratings
    }
    lawyers = list(users_collection.find(query, projection))
    # Calculate average rating for each lawyer
    for lawyer in lawyers:
        ratings = lawyer.get("ratings", [])
        if ratings:
            lawyer["avg_rating"] = round(sum(ratings) / len(ratings), 2)
        else:
            lawyer["avg_rating"] = "No ratings yet"
    return render_template('lawyers.html', 
        lawyers=lawyers,
        specialization=specialization
    )

# Route to handle rating submission
@app.route('/rate/<lawyer_id>', methods=['POST'])
def rate_lawyer(lawyer_id):
    rating = int(request.form.get('rating'))
    users_collection.update_one(
        {"_id": ObjectId(lawyer_id)},
        {"$push": {"ratings": rating}}
    )
    return redirect(url_for('lawyer_listings'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)