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

# Function to initialize the database and create the 'appointments' table
def initialize_database():
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to connect to the database for initialization.")
        return

    try:
        cursor = conn.cursor()
        logger.info("Creating 'appointments' table if it doesn't exist...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id SERIAL PRIMARY KEY,
                patient_id INTEGER NOT NULL,
                doctor_id INTEGER NOT NULL,
                appointment_date TIMESTAMP NOT NULL,
                status VARCHAR(50) DEFAULT 'Scheduled'
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

# Route to get all appointments
@app.route('/appointments', methods=['GET'])
def get_appointments():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM appointments;")
        appointments = cursor.fetchall()
        return jsonify(appointments), 200
    except Exception as e:
        logger.error(f"Error fetching appointments: {e}")
        return jsonify({"error": "Failed to fetch appointments"}), 500
    finally:
        cursor.close()
        conn.close()

# Route to book a new appointment
@app.route('/appointments', methods=['POST'])
def book_appointment():
    data = request.get_json()
    patient_id = data.get('patient_id')
    doctor_id = data.get('doctor_id')
    appointment_date = data.get('appointment_date')

    if not patient_id or not doctor_id or not appointment_date:
        return jsonify({"error": "Patient ID, Doctor ID, and Appointment Date are required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO appointments (patient_id, doctor_id, appointment_date) VALUES (%s, %s, %s) RETURNING id;",
            (patient_id, doctor_id, appointment_date)
        )
        appointment_id = cursor.fetchone()['id']
        conn.commit()
        logger.info(f"Appointment {appointment_id} added: patient_id = {patient_id}, doctor_id = {doctor_id}, appointment_date = {appointment_date}")
        return jsonify({"id": appointment_id, "message": "Appointment booked successfully"}), 201
    except Exception as e:
        logger.error(f"Error booking appointment: {e}")
        return jsonify({"error": "Failed to book appointment"}), 500
    finally:
        cursor.close()
        conn.close()

# Route to cancel an appointment
@app.route('/appointments/<int:appointment_id>', methods=['DELETE'])
def cancel_appointment(appointment_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM appointments WHERE id = %s;", (appointment_id,))
        conn.commit()
        logger.info(f"Appointment {appointment_id} deleted")
        return jsonify({"message": "Appointment canceled successfully"}), 200
    except Exception as e:
        logger.error(f"Error canceling appointment: {e}")
        return jsonify({"error": "Failed to cancel appointment"}), 500
    finally:
        cursor.close()
        conn.close()

# Route to update the status of an appointment
@app.route('/appointments/<int:appointment_id>/status', methods=['PUT'])
def update_appointment_status(appointment_id):
    data = request.get_json()
    status = data.get('status')

    if not status:
        return jsonify({"error": "Status is required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE appointments SET status = %s WHERE id = %s;",
            (status, appointment_id)
        )
        conn.commit()
        logger.info(f"Appointment {appointment_id} updated: status = {status}")
        return jsonify({"message": "Appointment status updated successfully"}), 200
    except Exception as e:
        logger.error(f"Error updating appointment status: {e}")
        return jsonify({"error": "Failed to update appointment status"}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000)
