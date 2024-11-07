# import logging
# from flask import Flask, request, jsonify
# import psycopg2
# from psycopg2.extras import RealDictCursor
# import os

# # Configure the logger
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# app = Flask(__name__)

# # Function to get database configuration from environment variables
# def get_db_config():
#     return {
#         'user': os.getenv('DB_USER'),
#         'password': os.getenv('DB_PASSWORD'),
#         'host': os.getenv('DB_HOST'),
#         'database': os.getenv('DB_NAME')
#     }

# # Function to establish a connection to the database
# def get_db_connection():
#     config = get_db_config()
#     try:
#         conn = psycopg2.connect(
#             host=config['host'],
#             database=config['database'],
#             user=config['user'],
#             password=config['password'],
#             cursor_factory=RealDictCursor
#         )
#         return conn
#     except Exception as e:
#         logger.error(f"Error connecting to the database: {e}")
#         return None

# # Function to initialize the database and create the table if it doesn't exist
# def initialize_database():
#     conn = get_db_connection()
#     if not conn:
#         app.logger.error("Failed to connect to the database for initialization.")
#         return

#     try:
#         cursor = conn.cursor()
#         app.logger.info("Creating 'patients' table if it doesn't exist...")
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS patients (
#                 id SERIAL PRIMARY KEY,
#                 name VARCHAR(100) NOT NULL,
#                 age INTEGER NOT NULL,
#                 contract_info VARCHAR(255)
#             );
#         """)
#         conn.commit()
#         app.logger.info("Database initialized successfully.")
#     except Exception as e:
#         app.logger.error(f"Error initializing database: {e}")
#     finally:
#         cursor.close()
#         conn.close()

# # Initialize the database when the service starts
# initialize_database()

# # Route to get all patients
# @app.route('/patients', methods=['GET'])
# def get_patients():
#     conn = get_db_connection()
#     if not conn:
#         return jsonify({"error": "Database connection failed"}), 500

#     try:
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM patients;")
#         patients = cursor.fetchall()
#         return jsonify(patients), 200
#     except Exception as e:
#         logger.error(f"Error fetching patients: {e}")
#         return jsonify({"error": "Failed to fetch patients"}), 500
#     finally:
#         cursor.close()
#         conn.close()

# # Route to add a new patient
# @app.route('/patients', methods=['POST'])
# def add_patient():
#     data = request.get_json()
#     name = data.get('name')
#     age = data.get('age')
#     contract_info = data.get('contract_info')

#     if not name or not age:
#         return jsonify({"error": "Name and age are required"}), 400

#     conn = get_db_connection()
#     if not conn:
#         return jsonify({"error": "Database connection failed"}), 500

#     try:
#         cursor = conn.cursor()
#         cursor.execute(
#             "INSERT INTO patients (name, age, contract_info) VALUES (%s, %s, %s) RETURNING id;",
#             (name, age, contract_info)
#         )
#         patient_id = cursor.fetchone()['id']
#         conn.commit()
#         logger.info(f"Patient {patient_id} added: name = {name}, age = {age}, contract_info = {contract_info}")
#         return jsonify({"id": patient_id, "message": "Patient added successfully"}), 201
#     except Exception as e:
#         logger.error(f"Error adding patient: {e}")
#         return jsonify({"error": "Failed to add patient"}), 500
#     finally:
#         cursor.close()
#         conn.close()

# # Route to update a patient's information
# @app.route('/patients/<int:patient_id>', methods=['PUT'])
# def update_patient(patient_id):
#     data = request.get_json()
#     name = data.get('name')
#     age = data.get('age')
#     contract_info = data.get('contract_info')

#     conn = get_db_connection()
#     if not conn:
#         return jsonify({"error": "Database connection failed"}), 500

#     try:
#         cursor = conn.cursor()
#         cursor.execute(
#             "UPDATE patients SET name = %s, age = %s, contract_info = %s WHERE id = %s;",
#             (name, age, contract_info, patient_id)
#         )
#         conn.commit()
#         logger.info(f"Patient {patient_id} updated: name = {name}, age = {age}, contract_info = {contract_info}")
#         return jsonify({"message": "Patient updated successfully"}), 200
#     except Exception as e:
#         logger.error(f"Error updating patient: {e}")
#         return jsonify({"error": "Failed to update patient"}), 500
#     finally:
#         cursor.close()
#         conn.close()

# # Route to delete a patient
# @app.route('/patients/<int:patient_id>', methods=['DELETE'])
# def delete_patient(patient_id):
#     conn = get_db_connection()
#     if not conn:
#         return jsonify({"error": "Database connection failed"}), 500

#     try:
#         cursor = conn.cursor()
#         cursor.execute("DELETE FROM patients WHERE id = %s;", (patient_id,))
#         conn.commit()
#         logger.info(f"Patient {patient_id} deleted")
#         return jsonify({"message": "Patient deleted successfully"}), 200
#     except Exception as e:
#         logger.error(f"Error deleting patient: {e}")
#         return jsonify({"error": "Failed to delete patient"}), 500
#     finally:
#         cursor.close()
#         conn.close()

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=4000)


import logging
from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os

# Configure the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Function to get database configuration from environment variables
def get_db_config():
    return {
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'database': os.getenv('DB_NAME')
    }

class DatabaseConnection:
    _connection = None

    @staticmethod
    def get_connection():
        if DatabaseConnection._connection is None:
            config = get_db_config()
            try:
                DatabaseConnection._connection = psycopg2.connect(
                    host=config['host'],
                    database=config['database'],
                    user=config['user'],
                    password=config['password'],
                    cursor_factory=RealDictCursor
                )
                logger.info("Database connection established.")
            except Exception as e:
                logger.error(f"Error connecting to the database: {e}")
                return None
        return DatabaseConnection._connection

# Function to initialize the database and create the table if it doesn't exist
def initialize_database():
    conn = DatabaseConnection.get_connection()
    if not conn:
        app.logger.error("Failed to connect to the database for initialization.")
        return

    try:
        cursor = conn.cursor()
        app.logger.info("Creating 'patients' table if it doesn't exist...")
        cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS patients (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                age INTEGER NOT NULL,
                contract_info VARCHAR(255)
            );
        """)
        conn.commit()
        app.logger.info("Database initialized successfully.")
    except Exception as e:
        app.logger.error(f"Error initializing database: {e}")
    finally:
        cursor.close()

# Initialize the database when the service starts
initialize_database()

# Route to get all patients
@app.route('/patients', methods=['GET'])
def get_patients():
    conn = DatabaseConnection.get_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients;")
        patients = cursor.fetchall()
        return jsonify(patients), 200
    except Exception as e:
        logger.error(f"Error fetching patients: {e}")
        return jsonify({"error": "Failed to fetch patients"}), 500
    finally:
        cursor.close()

# Route to add a new patient
@app.route('/patients', methods=['POST'])
def add_patient():
    data = request.get_json()
    name = data.get('name')
    age = data.get('age')
    contract_info = data.get('contract_info')

    if not name or not age:
        return jsonify({"error": "Name and age are required"}), 400

    conn = DatabaseConnection.get_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO patients (name, age, contract_info) VALUES (%s, %s, %s) RETURNING id;",
            (name, age, contract_info)
        )
        patient_id = cursor.fetchone()['id']
        conn.commit()
        logger.info(f"Patient {patient_id} added: name = {name}, age = {age}, contract_info = {contract_info}")
        return jsonify({"id": patient_id, "message": "Patient added successfully"}), 201
    except Exception as e:
        logger.error(f"Error adding patient: {e}")
        return jsonify({"error": "Failed to add patient"}), 500
    finally:
        cursor.close()

# Route to update a patient's information
@app.route('/patients/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    data = request.get_json()
    name = data.get('name')
    age = data.get('age')
    contract_info = data.get('contract_info')

    conn = DatabaseConnection.get_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE patients SET name = %s, age = %s, contract_info = %s WHERE id = %s;",
            (name, age, contract_info, patient_id)
        )
        conn.commit()
        logger.info(f"Patient {patient_id} updated: name = {name}, age = {age}, contract_info = {contract_info}")
        return jsonify({"message": "Patient updated successfully"}), 200
    except Exception as e:
        logger.error(f"Error updating patient: {e}")
        return jsonify({"error": "Failed to update patient"}), 500
    finally:
        cursor.close()

# Route to delete a patient
@app.route('/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    conn = DatabaseConnection.get_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM patients WHERE id = %s;", (patient_id,))
        conn.commit()
        logger.info(f"Patient {patient_id} deleted")
        return jsonify({"message": "Patient deleted successfully"}), 200
    except Exception as e:
        logger.error(f"Error deleting patient: {e}")
        return jsonify({"error": "Failed to delete patient"}), 500
    finally:
        cursor.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
