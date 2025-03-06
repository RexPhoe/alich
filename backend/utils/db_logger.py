import logging
import time
from functools import wraps
from flask import request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('database')

# Configure file handler
file_handler = logging.FileHandler('database.log')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def log_database_query(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        # Log request details
        logger.info(f"Database Query Started - Endpoint: {request.endpoint}")
        logger.info(f"Method: {request.method}")
        logger.info(f"Arguments: {kwargs}")
        
        try:
            # Execute the database query
            result = f(*args, **kwargs)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Log successful response
            logger.info(f"Query completed successfully in {execution_time:.2f} seconds")
            if hasattr(result, '__len__'):
                logger.info(f"Results returned: {len(result)}")
            
            return result
            
        except Exception as e:
            # Log error details
            logger.error(f"Database error occurred: {str(e)}")
            logger.error(f"Query failed after {time.time() - start_time:.2f} seconds")
            raise
            
    return decorated_function

def log_query_details(query, params=None):
    """Log specific query details"""
    logger.info(f"SQL Query: {query}")
    if params:
        logger.info(f"Parameters: {params}")

def log_error(error, context=None):
    """Log database errors with context"""
    error_message = f"Database Error: {str(error)}"
    if context:
        error_message += f" | Context: {context}"
    logger.error(error_message)