import os
import time
from agent import EducationAgent
from chains import memory
from logger import logger, log_user_input, log_agent_response

# You need to set your OpenAI API key here or as an environment variable
# os.environ["OPENAI_API_KEY"] = "your-api-key"

def main():
    """Main function to run the Education Agent."""
    
    logger.info("=== Starting Education Assistant MVP ===")
    logger.info(f"OpenAI API key configured: {'Yes' if os.environ.get('OPENAI_API_KEY') else 'No'}")
    
    print("\n=== Education Assistant MVP ===\n")
    
    agent = EducationAgent()
    start_time = time.time()
    response = agent.process("")
    end_time = time.time()
    
    logger.debug(f"Initial greeting response time: {end_time - start_time:.2f} seconds")
    print("Assistant: ", response)
    
    while True:
        try:
            user_input = input("You: ")
            log_user_input(user_input)
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                logger.info("User requested to exit")
                print("Assistant: Thank you for using the Education Assistant. Goodbye!")
                break
            
            start_time = time.time()
            response = agent.process(user_input)
            end_time = time.time()
            
            logger.debug(f"Response time: {end_time - start_time:.2f} seconds")
            print("Assistant: ", response)
            
            # Update memory
            memory.chat_memory.add_user_message(user_input)
            memory.chat_memory.add_ai_message(response)
            
        except KeyboardInterrupt:
            logger.info("Program interrupted by user (KeyboardInterrupt)")
            print("\nExiting program. Goodbye!")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            print(f"An error occurred: {str(e)}")
            print("Please try again or restart the program.")
    
    logger.info("=== Education Assistant MVP ended ===")

if __name__ == "__main__":
    main() 