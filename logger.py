import logging
import os
import sys
from datetime import datetime
from config import LOG_LEVEL, CONSOLE_LOG_LEVEL, FILE_LOG_LEVEL, LOG_FORMAT, LOG_DIR

# Get log level constants from string names
def get_log_level(level_name):
    return {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }.get(level_name, logging.INFO)

# Create logs directory if it doesn't exist
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configure logging
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = os.path.join(LOG_DIR, f'education_agent_{timestamp}.log')

# Create logger
logger = logging.getLogger('education_agent')
logger.setLevel(get_log_level(LOG_LEVEL))

# Create console handler with the configured log level
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(get_log_level(CONSOLE_LOG_LEVEL))

# Create file handler which logs even debug messages
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(get_log_level(FILE_LOG_LEVEL))

# Create formatter and add it to the handlers
formatter = logging.Formatter(LOG_FORMAT)
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

def log_state_change(old_state, new_state):
    """Log state transitions"""
    logger.info(f"State transition: {old_state} -> {new_state}")

def log_user_input(user_input):
    """Log user input"""
    logger.info(f"User input: {user_input}")

def log_agent_response(response):
    """Log agent response"""
    logger.info(f"Agent response: {response[:100]}..." if len(response) > 100 else f"Agent response: {response}")

def log_json_result(step_name, json_data):
    """Log JSON results from various steps"""
    if len(json_data) > 500:
        logger.debug(f"{step_name} result: {json_data[:500]}...")
    else:
        logger.debug(f"{step_name} result: {json_data}")

def log_error(error_msg, exception=None):
    """Log errors"""
    if exception:
        logger.error(f"{error_msg}: {str(exception)}", exc_info=True)
    else:
        logger.error(error_msg)

logger.info("Logging system initialized") 