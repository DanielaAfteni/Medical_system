from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# List of microservices with their instances for round-robin
services = {
    "patient_service": ["http://patient_service:4000"],
    "doctor_service": ["http://doctor_service:5000"],
    "medical_record_service": ["http://medical_record_service:6000"],
    "appointment_service": ["http://appointment_service:7000"],
    "billing_service": ["http://billing_service:8000"]
}

# Round-robin counters for each service
counters = {service: 0 for service in services}

def get_next_instance(service_name):
    """Get the next instance of the service using round-robin"""
    instances = services[service_name]
    index = counters[service_name]
    next_instance = instances[index]
    counters[service_name] = (index + 1) % len(instances)
    return next_instance

# Patient routes
@app.route('/patients', methods=['GET'])
@app.route('/patients', methods=['POST'])
def patients():
    url = get_next_instance("patient_service") + "/patients"
    if request.method == 'GET':
        response = requests.get(url)
    elif request.method == 'POST':
        data = request.get_json()
        response = requests.post(url, json=data)
    return jsonify(response.json()), response.status_code

@app.route('/patients/<int:patient_id>', methods=['PUT', 'DELETE'])
def patient_by_id(patient_id):
    url = f"{get_next_instance('patient_service')}/patients/{patient_id}"
    
    if request.method == 'PUT':
        data = request.get_json()
        try:
            response = requests.put(url, json=data)
        except requests.exceptions.RequestException as e:
            app.logger.error(f"Error making PUT request: {e}")
            return jsonify({"error": "Failed to make PUT request"}), 500
    elif request.method == 'DELETE':
        try:
            response = requests.delete(url)
        except requests.exceptions.RequestException as e:
            app.logger.error(f"Error making DELETE request: {e}")
            return jsonify({"error": "Failed to make DELETE request"}), 500
    
    if response.status_code == 404:
        app.logger.error(f"404 Not Found at {url}")
        return jsonify({"error": "Resource not found"}), 404

    return jsonify(response.json()), response.status_code

    
# Doctor routes
@app.route('/doctors', methods=['GET'])
@app.route('/doctors', methods=['POST'])
def doctors():
    url = get_next_instance("doctor_service") + "/doctors"
    if request.method == 'GET':
        response = requests.get(url)
    elif request.method == 'POST':
        data = request.get_json()
        response = requests.post(url, json=data)
    return jsonify(response.json()), response.status_code

@app.route('/doctors/<int:doctor_id>', methods=['PUT'])
@app.route('/doctors/<int:doctor_id>', methods=['DELETE'])
def doctor_by_id(doctor_id):
    url = f"{get_next_instance('doctor_service')}/doctors/{doctor_id}"
    if request.method == 'PUT':
        data = request.get_json()
        response = requests.put(url, json=data)
    elif request.method == 'DELETE':
        response = requests.delete(url)
    return jsonify(response.json()), response.status_code

# Medical record routes
@app.route('/medical_records', methods=['GET'])
@app.route('/medical_records', methods=['POST'])
def medical_records():
    url = get_next_instance("medical_record_service") + "/medical_records"
    if request.method == 'GET':
        response = requests.get(url)
    elif request.method == 'POST':
        data = request.get_json()
        response = requests.post(url, json=data)
    return jsonify(response.json()), response.status_code

@app.route('/medical_records/<int:record_id>', methods=['PUT'])
@app.route('/medical_records/<int:record_id>', methods=['DELETE'])
def medical_record_by_id(record_id):
    url = f"{get_next_instance('medical_record_service')}/medical_records/{record_id}"
    if request.method == 'PUT':
        data = request.get_json()
        response = requests.put(url, json=data)
    elif request.method == 'DELETE':
        response = requests.delete(url)
    return jsonify(response.json()), response.status_code

# Appointment routes
@app.route('/appointments', methods=['GET'])
@app.route('/appointments', methods=['POST'])
def appointments():
    url = get_next_instance("appointment_service") + "/appointments"
    if request.method == 'GET':
        response = requests.get(url)
    elif request.method == 'POST':
        data = request.get_json()
        response = requests.post(url, json=data)
    return jsonify(response.json()), response.status_code

@app.route('/appointments/<int:appointment_id>', methods=['DELETE'])
@app.route('/appointments/<int:appointment_id>/status', methods=['PUT'])
def appointment_by_id(appointment_id):
    if request.method == 'DELETE':
        url = f"{get_next_instance('appointment_service')}/appointments/{appointment_id}"
        response = requests.delete(url)
    elif request.method == 'PUT':
        url = f"{get_next_instance('appointment_service')}/appointments/{appointment_id}/status"
        data = request.get_json()
        response = requests.put(url, json=data)
    return jsonify(response.json()), response.status_code

# Billing routes
@app.route('/bills', methods=['GET'])
@app.route('/bills', methods=['POST'])
def bills():
    url = get_next_instance("billing_service") + "/bills"
    if request.method == 'GET':
        response = requests.get(url)
    elif request.method == 'POST':
        data = request.get_json()
        response = requests.post(url, json=data)
    return jsonify(response.json()), response.status_code

@app.route('/bills/<int:bill_id>', methods=['DELETE'])
@app.route('/bills/<int:bill_id>/status', methods=['PUT'])
def bill_by_id(bill_id):
    if request.method == 'DELETE':
        url = f"{get_next_instance('billing_service')}/bills/{bill_id}"
        response = requests.delete(url)
    elif request.method == 'PUT':
        url = f"{get_next_instance('billing_service')}/bills/{bill_id}/status"
        data = request.get_json()
        response = requests.put(url, json=data)
    return jsonify(response.json()), response.status_code

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
