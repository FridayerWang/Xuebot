from flask import Flask, render_template, request, jsonify
from agent import EducationAgent
from logger import logger
import os

app = Flask(__name__)
agent = EducationAgent()

@app.route('/')
def index():
    """Render the chatbot interface."""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process user message and return bot response."""
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    logger.info(f"Received message: {user_message}")
    try:
        # Process the message using the agent
        response = agent.process(user_message)
        return jsonify({'response': response})
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Education Assistant Web App")
    # Use environment variable for port if available (useful for deployment)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 