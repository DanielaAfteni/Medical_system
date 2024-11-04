from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to get database configuration from environment variables
def get_db_config():
    return {
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'database': os.getenv('DB_NAME')
    }

# Function to establish a connection to the database
def get_db_connection():
    config = get_db_config()
    try:
        conn = psycopg2.connect(
            host=config['host'],
            database=config['database'],
            user=config['user'],
            password=config['password'],
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        logger.error(f"Error connecting to the database: {e}")
        return None

# Function to initialize the database and create the 'doctors' table
def initialize_database():
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to connect to the database for initialization.")
        return

    try:
        cursor = conn.cursor()
        logger.info("Creating 'doctors' table if it doesn't exist...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                specialty VARCHAR(100) NOT NULL,
                experience_years INTEGER NOT NULL
            );
        """)
        conn.commit()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
    finally:
        cursor.close()
        conn.close()

# Initialize the database when the service starts
initialize_database()

# Route to get all doctors
@app.route('/doctors', methods=['GET'])
def get_doctors():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM doctors;")
        doctors = cursor.fetchall()
        return jsonify(doctors), 200
    except Exception as e:
        logger.error(f"Error fetching doctors: {e}")
        return jsonify({"error": "Failed to fetch doctors"}), 500
    finally:
        cursor.close()
        conn.close()

# Route to add a new doctor
@app.route('/doctors', methods=['POST'])
def add_doctor():
    data = request.get_json()
    name = data.get('name')
    specialty = data.get('specialty')
    experience_years = data.get('experience_years')

    if not name or not specialty or not experience_years:
        return jsonify({"error": "Name, specialty, and experience years are required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO doctors (name, specialty, experience_years) VALUES (%s, %s, %s) RETURNING id;",
            (name, specialty, experience_years)
        )
        doctor_id = cursor.fetchone()['id']
        conn.commit()
        logger.info(f"Patient {doctor_id} added: name = {name}, specialty = {specialty}, experience_years = {experience_years}")
        return jsonify({"id": doctor_id, "message": "Doctor added successfully"}), 201
    except Exception as e:
        logger.error(f"Error adding doctor: {e}")
        return jsonify({"error": "Failed to add doctor"}), 500
    finally:
        cursor.close()
        conn.close()

# Route to update a doctor's information
@app.route('/doctors/<int:doctor_id>', methods=['PUT'])
def update_doctor(doctor_id):
    data = request.get_json()
    name = data.get('name')
    specialty = data.get('specialty')
    experience_years = data.get('experience_years')

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE doctors SET name = %s, specialty = %s, experience_years = %s WHERE id = %s;",
            (name, specialty, experience_years, doctor_id)
        )
        conn.commit()
        logger.info(f"Patient {doctor_id} updated: name = {name}, specialty = {specialty}, experience_years = {experience_years}")
        return jsonify({"message": "Doctor updated successfully"}), 200
    except Exception as e:
        logger.error(f"Error updating doctor: {e}")
        return jsonify({"error": "Failed to update doctor"}), 500
    finally:
        cursor.close()
        conn.close()

# Route to delete a doctor
@app.route('/doctors/<int:doctor_id>', methods=['DELETE'])
def delete_doctor(doctor_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM doctors WHERE id = %s;", (doctor_id,))
        conn.commit()
        logger.info(f"Doctor {doctor_id} deleted")
        return jsonify({"message": "Doctor deleted successfully"}), 200
    except Exception as e:
        logger.error(f"Error deleting doctor: {e}")
        return jsonify({"error": "Failed to delete doctor"}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
