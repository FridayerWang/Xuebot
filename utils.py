import json
import random
import re
from typing import Dict, List, Any

from data import mock_question_db
from chains import generate_questions_chain
from config import MAX_QUESTIONS
from logger import logger

def clean_json_string(json_str):
    """
    Clean the JSON string by removing markdown code blocks and any other non-JSON content.
    """
    logger.debug(f"Cleaning JSON string: {json_str[:50]}...")
    
    # Remove markdown code block markers
    pattern = r'```(?:json)?\s*([\s\S]*?)```'
    matches = re.findall(pattern, json_str)
    
    if matches:
        logger.debug("Markdown code block detected, extracting JSON content")
        return matches[0].strip()
    
    # If no markdown blocks found, just return the original string
    return json_str.strip()

def parse_json_safely(json_str):
    """
    Safely parse a JSON string, handling various formats and errors.
    """
    cleaned_json = clean_json_string(json_str)
    logger.debug(f"Cleaned JSON for parsing: {cleaned_json[:50]}...")
    
    try:
        return json.loads(cleaned_json)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error after cleaning: {str(e)}")
        # Try a more aggressive cleaning approach as fallback
        try:
            # Try to extract anything that looks like a JSON object
            potential_json = re.search(r'\{[\s\S]*\}', cleaned_json)
            if potential_json:
                return json.loads(potential_json.group(0))
            raise e
        except Exception:
            logger.error("All JSON parsing attempts failed")
            raise

def retrieve_content(grade: str, subject: str, topic: str) -> str:
    """
    Retrieve relevant content from the knowledge base.
    In a real implementation, this would query a vector store.
    """
    logger.debug(f"Retrieving content for grade={grade}, subject={subject}, topic={topic}")
    
    # Format key to match mock database
    key = f"{grade}_{subject}_{topic}".lower().replace(" ", "_")
    logger.debug(f"Formatted key: {key}")
    
    from data import mock_knowledge_base
    content = mock_knowledge_base.get(key, "No relevant content found. Here are some general learning tips.")
    
    if key in mock_knowledge_base:
        logger.info(f"Content found for key: {key}")
    else:
        logger.warning(f"No content found for key: {key}, using default content")
    
    return content

def retrieve_questions(topic: str, difficulty: str) -> List[Dict[str, str]]:
    """
    Retrieve questions from the database.
    In a real implementation, this would query a relational database.
    """
    logger.debug(f"Retrieving questions for topic={topic}, difficulty={difficulty}")
    
    # Format key to match mock database
    topic_key = topic.lower().replace(" ", "_")
    logger.debug(f"Formatted topic key: {topic_key}")
    
    # Get questions for the topic and difficulty
    topic_questions = mock_question_db.get(topic_key, {})
    difficulty_questions = topic_questions.get(difficulty, [])
    
    if topic_key in mock_question_db:
        if difficulty in mock_question_db[topic_key]:
            logger.info(f"Found {len(difficulty_questions)} questions for topic={topic_key}, difficulty={difficulty}")
        else:
            logger.warning(f"No questions found for difficulty={difficulty} in topic={topic_key}")
    else:
        logger.warning(f"No questions found for topic={topic_key}")
    
    if not difficulty_questions:
        # Fallback to generate questions if none found
        logger.info(f"Generating questions for topic={topic}, difficulty={difficulty}")
        result = generate_questions_chain.run(topic=topic, difficulty=difficulty)
        
        try:
            parsed_result = parse_json_safely(result)
            questions = parsed_result.get("questions", [])
            logger.info(f"Successfully generated {len(questions)} questions")
            return questions
        except Exception as e:
            logger.error(f"Error parsing generated questions: {str(e)}")
            # Fallback in case of parsing issues
            logger.info("Using default fallback question")
            return [{"question": "Default question", "answer": "Default answer"}]
    
    # Return up to MAX_QUESTIONS random questions
    selected_questions = random.sample(difficulty_questions, min(MAX_QUESTIONS, len(difficulty_questions)))
    logger.debug(f"Selected {len(selected_questions)} questions from database")
    return selected_questions 