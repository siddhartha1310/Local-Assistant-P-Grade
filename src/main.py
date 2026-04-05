import os
import sys
from loguru import logger
from dotenv import load_dotenv
from src.ui.app import SecureAssistantApp

# Load environment variables
load_dotenv()

def main():
    logger.info("Initializing Secure Local AI Assistant...")
    
    # Check for DB encryption key
    db_key = os.getenv("DB_ENCRYPTION_KEY")
    if not db_key:
        logger.error("DB_ENCRYPTION_KEY not found in .env. Exiting.")
        sys.exit(1)
        
    logger.success("Secure environment verified. Launching TUI...")
    
    # Start the Textual TUI
    app = SecureAssistantApp()
    app.run()

if __name__ == "__main__":
    main()
