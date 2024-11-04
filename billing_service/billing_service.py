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

# Function to initialize the database and create the 'bills' table
def initialize_database():
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to connect to the database for initialization.")
        return

    try:
        cursor = conn.cursor()
        logger.info("Creating 'bills' table if it doesn't exist...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bills (
                id SERIAL PRIMARY KEY,
                patient_id INTEGER NOT NULL,
                appointment_id INTEGER NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                status VARCHAR(50) DEFAULT 'Pending',
                issued_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                paid_date TIMESTAMP
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

# Route to get all bills
@app.route('/bills', methods=['GET'])
def get_bills():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bills;")
        bills = cursor.fetchall()
        return jsonify(bills), 200
    except Exception as e:
        logger.error(f"Error fetching bills: {e}")
        return jsonify({"error": "Failed to fetch bills"}), 500
    finally:
        cursor.close()
        conn.close()

# Route to create a new bill
@app.route('/bills', methods=['POST'])
def create_bill():
    data = request.get_json()
    patient_id = data.get('patient_id')
    appointment_id = data.get('appointment_id')
    amount = data.get('amount')

    if not patient_id or not appointment_id or amount is None:
        return jsonify({"error": "Patient ID, Appointment ID, and Amount are required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO bills (patient_id, appointment_id, amount) VALUES (%s, %s, %s) RETURNING id;",
            (patient_id, appointment_id, amount)
        )
        bill_id = cursor.fetchone()['id']
        conn.commit()
        logger.info(f"Bill {bill_id} added: patient_id = {patient_id}, appointment_id = {appointment_id}, amount = {amount}")
        return jsonify({"id": bill_id, "message": "Bill created successfully"}), 201
    except Exception as e:
        logger.error(f"Error creating bill: {e}")
        return jsonify({"error": "Failed to create bill"}), 500
    finally:
        cursor.close()
        conn.close()

# Route to update the status of a bill (e.g., mark as paid)
@app.route('/bills/<int:bill_id>/status', methods=['PUT'])
def update_bill_status(bill_id):
    data = request.get_json()
    status = data.get('status')
    paid_date = data.get('paid_date')

    if not status:
        return jsonify({"error": "Status is required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        if status.lower() == 'paid' and paid_date:
            cursor.execute(
                "UPDATE bills SET status = %s, paid_date = %s WHERE id = %s;",
                (status, paid_date, bill_id)
            )
        else:
            cursor.execute(
                "UPDATE bills SET status = %s WHERE id = %s;",
                (status, bill_id)
            )
        conn.commit()
        logger.info(f"Bill {bill_id} update: status = {status}, paid_date = {paid_date}")
        return jsonify({"message": "Bill status updated successfully"}), 200
    except Exception as e:
        logger.error(f"Error updating bill status: {e}")
        return jsonify({"error": "Failed to update bill status"}), 500
    finally:
        cursor.close()
        conn.close()

# Route to delete a bill
@app.route('/bills/<int:bill_id>', methods=['DELETE'])
def delete_bill(bill_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bills WHERE id = %s;", (bill_id,))
        conn.commit()
        logger.info(f"Bill {bill_id} deleted")
        return jsonify({"message": "Bill deleted successfully"}), 200
    except Exception as e:
        logger.error(f"Error deleting bill: {e}")
        return jsonify({"error": "Failed to delete bill"}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
