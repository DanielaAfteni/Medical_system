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

# Function to initialize the database and create the 'medical_records' table
def initialize_database():
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to connect to the database for initialization.")
        return

    try:
        cursor = conn.cursor()
        logger.info("Creating 'medical_records' table if it doesn't exist...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medical_records (
                id SERIAL PRIMARY KEY,
                patient_id INTEGER NOT NULL,
                doctor_id INTEGER NOT NULL,
                diagnosis TEXT NOT NULL,
                treatment TEXT,
                record_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

# Route to get all medical records
@app.route('/medical_records', methods=['GET'])
def get_medical_records():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM medical_records;")
        records = cursor.fetchall()
        return jsonify(records), 200
    except Exception as e:
        logger.error(f"Error fetching medical records: {e}")
        return jsonify({"error": "Failed to fetch medical records"}), 500
    finally:
        cursor.close()
        conn.close()

# Route to add a new medical record
@app.route('/medical_records', methods=['POST'])
def add_medical_record():
    data = request.get_json()
    patient_id = data.get('patient_id')
    doctor_id = data.get('doctor_id')
    diagnosis = data.get('diagnosis')
    treatment = data.get('treatment')

    if not patient_id or not doctor_id or not diagnosis:
        return jsonify({"error": "Patient ID, Doctor ID, and Diagnosis are required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment) VALUES (%s, %s, %s, %s) RETURNING id;",
            (patient_id, doctor_id, diagnosis, treatment)
        )
        record_id = cursor.fetchone()['id']
        conn.commit()
        logger.info(f"New record {record_id} added: patient_id = {patient_id}, doctor_id = {doctor_id}, diagnosis = {diagnosis}, treatment = {treatment}")
        return jsonify({"id": record_id, "message": "Medical record added successfully"}), 201
    except Exception as e:
        logger.error(f"Error adding medical record: {e}")
        return jsonify({"error": "Failed to add medical record"}), 500
    finally:
        cursor.close()
        conn.close()

# Route to update a medical record
@app.route('/medical_records/<int:record_id>', methods=['PUT'])
def update_medical_record(record_id):
    data = request.get_json()
    diagnosis = data.get('diagnosis')
    treatment = data.get('treatment')

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE medical_records SET diagnosis = %s, treatment = %s WHERE id = %s;",
            (diagnosis, treatment, record_id)
        )
        conn.commit()
        logger.info(f"Record {record_id} updated: diagnosis = {diagnosis}, treatment = {treatment}")
        return jsonify({"message": "Medical record updated successfully"}), 200
    except Exception as e:
        logger.error(f"Error updating medical record: {e}")
        return jsonify({"error": "Failed to update medical record"}), 500
    finally:
        cursor.close()
        conn.close()

# Route to delete a medical record
@app.route('/medical_records/<int:record_id>', methods=['DELETE'])
def delete_medical_record(record_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM medical_records WHERE id = %s;", (record_id,))
        conn.commit()
        logger.info(f"Record {record_id} deleted")
        return jsonify({"message": "Medical record deleted successfully"}), 200
    except Exception as e:
        logger.error(f"Error deleting medical record: {e}")
        return jsonify({"error": "Failed to delete medical record"}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
