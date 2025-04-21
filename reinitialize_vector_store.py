#!/usr/bin/env python3
"""
Utility script to reinitialize the vector store database.
This script clears any existing data and adds fresh documents from mock data.
"""

import os
import sys
import shutil
from pathlib import Path

# Import configuration
from config import VECTOR_STORE_DIR, USE_VECTOR_STORE
from logger import logger

def clear_vector_store():
    """Clear existing vector store data by removing the directory."""
    try:
        if os.path.exists(VECTOR_STORE_DIR):
            logger.info(f"Removing existing vector store directory: {VECTOR_STORE_DIR}")
            shutil.rmtree(VECTOR_STORE_DIR)
            logger.info("Vector store directory successfully removed")
            return True
        else:
            logger.info(f"Vector store directory {VECTOR_STORE_DIR} does not exist. Nothing to clean.")
            return True
    except Exception as e:
        logger.error(f"Error clearing vector store: {str(e)}")
        return False

def main():
    """Main function to reinitialize the vector store."""
    if not USE_VECTOR_STORE:
        logger.error("Vector store is disabled in configuration. Set USE_VECTOR_STORE=true in .env file")
        return 1

    logger.info("Starting vector store reinitialization")
    
    # Step 1: Clear existing vector store
    if not clear_vector_store():
        logger.error("Failed to clear vector store. Aborting reinitialization.")
        return 1
    
    # Step 2: Reinitialize vector store
    try:
        from data import initialize_vector_store
        
        logger.info("Initializing fresh vector store")
        if initialize_vector_store():
            logger.info("Vector store successfully reinitialized")
            return 0
        else:
            logger.error("Failed to initialize vector store")
            return 1
    except Exception as e:
        logger.error(f"Error during vector store reinitialization: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 