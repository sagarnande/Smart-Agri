import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'os.getenv("DB_USER")',
    'database': 'Agriculture',
    'password': 'os.getenv("DB_PASSWORD")',
    'port': '5432'  # Default PostgreSQL port
}

# Function to search in PostgreSQL database
def search_db(query):
    conn = None
    results = []
    try:
        # Establish the connection
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Execute query to search schemas by name
        cursor.execute("SELECT id, scheme_name, description, eligibility_criteria, required_documents, application_link FROM agri_scheme WHERE scheme_name ILIKE %s",
                       ('%' + query + '%',))

        # Fetch the results
        results = cursor.fetchall()
        results = [{"id": row[0], "scheme_name": row[1], "description": row[2], "eligibility_criteria": row[3], "required_documents": row[4], "application_link": row[5]} for row in results]

        return results

    except Exception as e:
        print("Database Error:", e)
        return []

    finally:
        if conn:
            conn.close()

def register_user(name, email, password):
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Hash the password
        password_hash = generate_password_hash(password)

        # Insert user into the database and return the user ID
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s) RETURNING id",
            (name, email, password_hash)
        )

        user_id = cursor.fetchone()[0]  # Fetch the returned user ID
        conn.commit()
        print(f"User  registered: {user_id}, {name}, {email}")  # Debugging line
        return {"id": user_id, "name": name, "email": email, "message": "User  registered successfully"}

    except psycopg2.IntegrityError:
        conn.rollback()
        print("Email already exists")  # Debugging line
        return {"error": "Email already exists"}

    except Exception as e:
        print("Database Error:", e)  # Print the actual error
        return {"error": "Failed to register user: " + str(e)}

    finally:
        if conn:
            conn.close()

def check_user(identifier, password):
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT password FROM users WHERE email = %s",
            (identifier,)
        )
        user = cursor.fetchone()

        if user:
            print(f"User  found: {identifier}")  # Debugging line
            hashed_password = user[0]

            # Check the password
            if check_password_hash(hashed_password, password):
                return {"status": "success"}
            else:
                print("Invalid password")  # Debugging line
                return {"status": "failed"}

        print("User  not found")  # Debugging line
        return {"status": "failed"}

    except Exception as e:
        print("Database Error:", e)
        return {"error": "Login failed"}

    finally:
        if conn:
            conn.close()



def generate_guidance(soil_type, ph, temperature, fertilizer_usage, rainfall, pesticide_usage):
    """Generates dynamic farming guidance based on input parameters."""
    guidance = []

    # Soil type recommendations
    if "clay" in soil_type.lower():
        guidance.append("Clay soil has poor drainage. Consider raised beds and organic compost.")
    elif "sandy" in soil_type.lower():
        guidance.append("Sandy soil dries out quickly. Use mulch and organic matter to improve moisture retention.")

    # pH level recommendations
    if ph < 5.5:
        guidance.append("Soil is too acidic. Add lime to increase pH.")
    elif ph > 7.5:
        guidance.append("Soil is too alkaline. Use sulfur or organic compost to lower pH.")

    # Temperature considerations
    if temperature < 15:
        guidance.append("Cold weather detected. Choose frost-resistant crop varieties.")
    elif temperature > 35:
        guidance.append("High temperature detected. Use shading nets and increase irrigation.")

    # Fertilizer usage guidance
    if "nitrogen" in fertilizer_usage.lower():
        guidance.append("Use nitrogen fertilizers cautiously to avoid excessive leaf growth.")
    if "phosphorus" in fertilizer_usage.lower():
        guidance.append("Phosphorus promotes root growth. Apply at early growth stages.")

    # Rainfall impact
    if rainfall < 500:
        guidance.append("Low rainfall detected. Consider drought-resistant crops or irrigation.")
    elif rainfall > 1500:
        guidance.append("Heavy rainfall detected. Improve drainage and use raised beds.")

    # Pesticide usage guidance
    if pesticide_usage:
        guidance.append(f"Pesticide usage detected: {pesticide_usage}. Use in recommended amounts to avoid residue.")

    return " ".join(guidance) if guidance else "No specific guidance available."

def safe_float(value, default=0.0):
    """Convert a value to float safely, defaulting to a given value if conversion fails."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default 
        
def get_crop_guidance(crop_name, location, land_size):
    """Fetches crop data from the database and generates guidance dynamically."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur= conn.cursor()

        # Fetch crop details from the database
        cur.execute("""
            SELECT crop, season, soil_type, ph, temperature, fertilizer_usage, rainfall, pesticide_usage, price, state
            FROM crop_data
            WHERE crop = %s AND state = %s
        """, (crop_name, location))

        result = cur.fetchone()
        cur.close()
        conn.close()

        if result:
            crop, season, soil_type, ph, temperature, fertilizer_usage, rainfall, pesticide_usage, price, state = result

            ph = safe_float(ph, default=6.5) 
            temperature = safe_float(temperature, default=25.0) 
            rainfall = safe_float(rainfall, default=800.0)  
            price = safe_float(price, default=0.0) 

            # Generate dynamic guidance
            guidance = generate_guidance(soil_type, ph, temperature, fertilizer_usage, rainfall, pesticide_usage)
            print("Generated Guidance:", guidance) 

            return {
                "crop": crop,
                "season": season,
                "soil_type": soil_type,
                "ph": ph,
                "temperature": temperature,
                "fertilizer_usage": fertilizer_usage,
                "rainfall": rainfall,
                "pesticide_usage": pesticide_usage,
                "price": price,
                "state": state,
                "guidance": guidance if guidance else "No specific guidance available.",
                "land_size": land_size
            }
        else:
            return {"error": "No data found for the given crop and location."}

    except Exception as e:
        return {"error": str(e)}            