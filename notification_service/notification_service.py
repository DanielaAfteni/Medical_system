from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Route to mimic sending a notification
@app.route('/send-notification', methods=['POST'])
def send_notification():
    data = request.get_json()
    email = data.get('email')
    amount = data.get('amount')

    if not email or amount is None:
        return jsonify({"error": "Email and Amount are required"}), 400

    try:
        # Mimic sending a notification
        logger.info(f"Notification sent to {email}: 'You have a pending bill of amount {amount}.'")
        return jsonify({"message": "Notification sent successfully"}), 200
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        return jsonify({"error": "Failed to send notification"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
