from flask import Flask, render_template, request, jsonify
from db import search_db, register_user, check_user,get_crop_guidance

app = Flask(__name__, static_folder='assets', template_folder='.')

# Serve the frontend (index.html)
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/products')
def products():
    return render_template('product.html')

@app.route('/market_places')
def marketplaces():
    return render_template('marketplaces.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/forgotpass')
def forgotpass():
    return render_template('forgotpass.html')

@app.route('/setpass')
def setpass():
    return render_template('setpass.html')

@app.route('/schema')
def schema():
    return render_template('schema.html')


@app.route('/weather')
def weather():
    return render_template('weather.html')

@app.route('/guidance')
def guide():
    return render_template('guidance.html')

@app.route('/tech')
def tech():
    return render_template('tech.html')

@app.route('/business')
def business():
    return render_template('business.html')


@app.route('/loansection')
def loan():
    return render_template('loansection.html')

# Handle search requests
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify({"error": "Empty search query"}), 400

    # Fetch data from the database or API
    results = search_db(query)  # Ensure this function returns the required fields
    return jsonify(results)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.get_json()  # Get JSON data from frontend
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not name or not email or not password:
            return jsonify({"error": "All fields are required"}), 400

        response = register_user(name, email, password)
        return jsonify(response)

    return render_template('signup.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json if request.is_json else request.form
        identifier = data.get("email")  # Use "email" as the key
        password = data.get("password")

        if not identifier or not password:
            return jsonify({"error": "Both fields are required"}), 400

        response = check_user(identifier, password)

        if response["status"] == "success":
            return jsonify({"status": "success", "redirect_url": "/"})  # Add redirection
        else:
            return jsonify({"error": "Invalid credentials"}), 401

    return render_template('login.html')


@app.route('/crop', methods=['GET', 'POST'])
def crop():
    if request.method == 'GET':
        return render_template('crop.html')

    try:
        data = request.get_json() if request.is_json else request.form
        crop_name = data.get('cropName')
        location = data.get('location')
        land_size = data.get('landSize')

        if not crop_name or not location or not land_size:
            return jsonify({"error": "All fields are required"}), 400

        guidance = get_crop_guidance(crop_name, location, land_size)

        if guidance:
            return jsonify(guidance)
        else:
            return jsonify({"error": "No guidance found for this crop and location"}), 404
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)