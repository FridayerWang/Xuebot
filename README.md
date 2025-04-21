# Education Assistant MVP

This is an AI-powered Education Assistant MVP built with LangChain that provides personalized learning experiences based on the user's grade level, subject, and topic.

## Features

- Extract grade level, subject, and topic from user input
- Retrieve relevant content for the topic
- Generate personalized learning paths
- Analyze user knowledge level
- Provide personalized or authoritative questions
- Evaluate user responses and provide feedback
- Vector storage using Chroma DB for efficient semantic search

## Project Structure

The code is organized into multiple modules:

- `main.py` - Main entry point for the application
- `agent.py` - Contains the main EducationAgent class
- `chains.py` - LangChain chain initialization
- `config.py` - Configuration settings
- `data.py` - Mock knowledge base and question database
- `prompts.py` - All prompt templates
- `utils.py` - Utility functions
- `vector_store.py` - Chroma DB vector store implementation
- `.env` - Environment variables configuration

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set your OpenAI API key in one of three ways:
   - In the `.env` file:
     ```
     OPENAI_API_KEY="your-api-key"
     ```
   - As an environment variable:
     ```
     export OPENAI_API_KEY="your-api-key"
     ```
   - In the `config.py` file:
     ```python
     OPENAI_API_KEY = "your-api-key"
     ```

## Environment Variables

The project uses a `.env` file for easy configuration. Available variables:

```
# OpenAI API Key - Required
OPENAI_API_KEY=""

# Vector Store Configuration
USE_VECTOR_STORE=true

# Chroma DB Settings 
VECTOR_STORE_DIR="./chroma_db"
EMBEDDING_MODEL="all-MiniLM-L6-v2"

# Logging Configuration
LOG_LEVEL="DEBUG"
CONSOLE_LOG_LEVEL="INFO"
FILE_LOG_LEVEL="DEBUG"
```

## Usage

1. Run the application:
   ```
   python main.py
   ```
2. Talk to the Education Assistant, telling it what grade level, subject, and topic you'd like to learn
3. Answer the assistant's questions and receive feedback
4. Enter "exit", "quit", or "bye" to end the program

## Vector Store Configuration

The project now uses Chroma DB as a vector store for efficient content retrieval. You can configure vector store settings in the `.env` file or `config.py`:

- `USE_VECTOR_STORE`: Enable or disable the vector store (defaults to True)
- `VECTOR_STORE_DIR`: Directory for storing the vector database
- `EMBEDDING_MODEL`: The embedding model to use (defaults to "BAAI/bge-large-en-v1.5")

To disable the vector store and use only the mock data, set in your `.env` file:

```
USE_VECTOR_STORE=false
```

## Available Educational Content

The database includes a variety of educational topics across different grade levels:

### Elementary Level
- Math: Addition, Subtraction
- Literature: Poetry

### Middle School Level
- Math: Geometry
- Science: Cells
- English: Grammar

### High School Level
- Math: Algebra
- Physics: Mechanics
- Biology: Genetics
- Chemistry: Periodic Table
- Literature: Shakespeare

### College Level
- Calculus: Limits
- Physics: Electromagnetism

Each topic includes descriptive content and related questions of varying difficulty levels.

## Note

- This is an MVP using mock data that is automatically ingested into the vector store
- In a production environment, replace with real documents and data sources
- The system supports additional topics beyond those listed above by generating content and questions on demand

## Chatbot Web Interface

A simple web-based interface has been added to interact with the Education Assistant.

### Setup and Running

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the web application:
   ```
   python app.py
   ```

3. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

### Features

- Interactive chat interface
- Real-time responses from the Education Agent
- Mobile-friendly design
- Typing indicators
- Auto-resizing text input
- Fallback responses if the backend API is unavailable

### Technical Details

- Frontend: HTML, CSS, JavaScript
- Backend: Flask
- Integration with the existing Education Agent

### Screenshots

![Chatbot Interface](screenshots/chatbot_interface.png) 