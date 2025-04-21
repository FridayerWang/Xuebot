# Education Assistant MVP

This is an AI-powered Education Assistant MVP built with LangChain that provides personalized learning experiences based on the user's grade level, subject, and topic.

## Features

- Extract grade level, subject, and topic from user input
- Retrieve relevant content for the topic
- Generate personalized learning paths
- Analyze user knowledge level
- Provide personalized or authoritative questions
- Evaluate user responses and provide feedback

## Project Structure

The code is organized into multiple modules:

- `main.py` - Main entry point for the application
- `agent.py` - Contains the main EducationAgent class
- `chains.py` - LangChain chain initialization
- `config.py` - Configuration settings
- `data.py` - Mock knowledge base and question database
- `prompts.py` - All prompt templates
- `utils.py` - Utility functions

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set your OpenAI API key in one of two ways:
   - As an environment variable:
     ```
     export OPENAI_API_KEY="your-api-key"
     ```
   - In the `config.py` file:
     ```python
     OPENAI_API_KEY = "your-api-key"
     ```

## Usage

1. Run the application:
   ```
   python main.py
   ```
2. Talk to the Education Assistant, telling it what grade level, subject, and topic you'd like to learn
3. Answer the assistant's questions and receive feedback
4. Enter "exit", "quit", or "bye" to end the program

## Note

- This is an MVP using mock data
- In a production environment, replace with real vector databases and relational databases
- Currently supported example topics include: "middle_school_math_geometry", "high_school_physics_mechanics", and "elementary_literature_poetry" 