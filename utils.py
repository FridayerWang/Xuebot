import json
import random
import re
from typing import Dict, List, Any
import os

from data import mock_question_db
from chains import generate_questions_chain
from config import MAX_QUESTIONS, USE_VECTOR_STORE
from logger import logger

# Import vector store only when enabled
if USE_VECTOR_STORE:
    try:
        from vector_store import vector_store
        VECTOR_STORE_AVAILABLE = True
    except ImportError:
        logger.warning("Vector store module import failed, falling back to mock data")
        VECTOR_STORE_AVAILABLE = False
else:
    VECTOR_STORE_AVAILABLE = False
    logger.info("Vector store disabled by configuration, using mock data only")

# Define metadata keys consistently
QUESTION_TYPE_KEY = "type"
QUESTION_DIFFICULTY_KEY = "difficulty"
QUESTION_ANSWER_KEY = "answer"
QUESTION_TOPIC_KEY = "topic" # Assuming topic is also stored in metadata for potential filtering

def clean_json_string(json_str: str) -> str:
    """Clean a string that should contain a JSON object."""
    # Remove markdown code block markers if present
    cleaned_json = re.sub(r'^```json|^```|```$', '', json_str, flags=re.MULTILINE).strip()
    
    # Remove any "json" text at the beginning of the string (sometimes GPT adds this)
    cleaned_json = re.sub(r'^json\s*', '', cleaned_json, flags=re.MULTILINE).strip()
    
    return cleaned_json

def parse_json_safely(json_str: str) -> Dict[str, Any]:
    """
    Safely parse a JSON string, trying different cleaning approaches if necessary.
    
    Args:
        json_str: String containing JSON
        
    Returns:
        Parsed JSON as a dictionary
    """
    try:
        cleaned_json = clean_json_string(json_str)
        return json.loads(cleaned_json)
    except json.JSONDecodeError as e:
        logger.warning(f"Error parsing JSON: {str(e)}. Trying alternate parsing approach.")
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
    Retrieve relevant content from the knowledge base using Chroma vector store.
    Falls back to mock database if vector store is not available.
    
    Args:
        grade: Grade level (e.g., "middle_school", "high_school")
        subject: Subject area (e.g., "math", "physics")
        topic: Specific topic (e.g., "geometry", "mechanics")
        
    Returns:
        Retrieved content as a string
    """
    logger.debug(f"Retrieving content for grade={grade}, subject={subject}, topic={topic}")
    
    # Format the search query
    search_query = f"{grade} {subject} {topic}"
    
    # Format key to match mock database (for fallback)
    key = f"{grade}_{subject}_{topic}".lower().replace(" ", "_")
    logger.debug(f"Formatted key: {key}")
    
    # Try using vector store if available
    if VECTOR_STORE_AVAILABLE:
        try:
            logger.info("Using Chroma vector store for content retrieval")
            
            # First try with metadata search
            documents = vector_store.search_by_metadata(
                grade=grade.lower(),
                subject=subject.lower(),
                topic=topic.lower(),
                k=2
            )
            
            # If no results with metadata, try semantic search
            if not documents:
                logger.debug("No results with metadata search, trying semantic search")
                documents = vector_store.search(search_query, k=2)
            
            if documents:
                # Combine content from retrieved documents
                contents = [doc.page_content for doc in documents]
                combined_content = "\n".join(contents)
                logger.info(f"Found {len(documents)} documents in vector store")
                return combined_content
            else:
                logger.warning("No documents found in vector store, falling back to mock database")
        except Exception as e:
            logger.error(f"Error retrieving from vector store: {str(e)}")
            logger.warning("Falling back to mock database")
    
    # Fallback to mock database
    from data import mock_knowledge_base
    content = mock_knowledge_base.get(key, "No relevant content found. Here are some general learning tips.")
    
    if key in mock_knowledge_base:
        logger.info(f"Content found in mock database for key: {key}")
    else:
        logger.warning(f"No content found for key: {key}, using default content")
    
    return content

def retrieve_questions(topic: str, difficulty: str) -> List[Dict[str, str]]:
    """
    Retrieve questions related to the topic and difficulty.
    Uses ChromaDB vector store if available and configured, otherwise falls back.
    """
    logger.debug(f"Retrieving questions for topic='{topic}', difficulty='{difficulty}'")
    
    questions = []
    
    if VECTOR_STORE_AVAILABLE:
        try:
            logger.info(f"Attempting to retrieve questions from vector store for topic='{topic}', difficulty='{difficulty}'")
            
            # Reverting filter to use $and as suggested by error messages for multiple conditions
            metadata_filter = {
                "$and": [
                    {QUESTION_TYPE_KEY: "question"},
                    {QUESTION_DIFFICULTY_KEY: difficulty.lower()} 
                ]
            }
            
            # Perform similarity search with filter
            # Access the underlying Langchain Chroma object for filtering capability
            search_results: List[Document] = vector_store.vector_store.similarity_search(
                query=topic, # Use topic for semantic relevance
                k=MAX_QUESTIONS, 
                filter=metadata_filter
            )
            
            if search_results:
                logger.info(f"Found {len(search_results)} potential questions in vector store")
                questions = [
                    {
                        "question": doc.page_content, 
                        "answer": doc.metadata.get(QUESTION_ANSWER_KEY, "Answer not found in metadata")
                    } 
                    for doc in search_results
                ]
                # Ensure we don't exceed MAX_QUESTIONS after potential duplicates or formatting issues
                questions = questions[:MAX_QUESTIONS] 
                logger.debug(f"Formatted {len(questions)} questions from vector store results.")
            else:
                logger.warning(f"No questions found in vector store matching filters: {metadata_filter}")

        except Exception as e:
            logger.error(f"Error retrieving questions from vector store: {str(e)}")
            logger.warning("Falling back to generation or mock data due to vector store error.")
            # Proceed to fallback mechanisms below
    
    # Fallback 1: If vector store search failed or yielded no results
    if not questions:
        logger.info(f"No questions retrieved from vector store (or store unavailable/error), attempting generation.")
        # Fallback to generate questions if none found/retrieved
        result = generate_questions_chain.run(topic=topic, difficulty=difficulty)
        try:
            parsed_result = parse_json_safely(result)
            questions = parsed_result.get("questions", [])
            if questions:
                 logger.info(f"Successfully generated {len(questions)} questions")
                 # Ensure we don't exceed MAX_QUESTIONS from generation either
                 questions = questions[:MAX_QUESTIONS]
            else:
                 logger.warning("Question generation yielded no questions.")
        except Exception as e:
            logger.error(f"Error parsing generated questions: {str(e)}")
            # Fallback in case of parsing issues during generation
            questions = [] # Ensure questions list is empty before final fallback

    # Fallback 2: If vector store is disabled OR generation failed
    if not questions and not VECTOR_STORE_AVAILABLE:
        logger.warning("Vector store disabled and generation failed/disabled, falling back to mock database.")
        # Format key to match mock database
        topic_key = topic.lower().replace(" ", "_")
        logger.debug(f"Formatted topic key for mock DB: {topic_key}")
        
        # Get questions for the topic and difficulty from mock DB
        topic_questions = mock_question_db.get(topic_key, {})
        difficulty_questions = topic_questions.get(difficulty, [])
        
        if difficulty_questions:
            logger.info(f"Found {len(difficulty_questions)} questions in mock DB for topic={topic_key}, difficulty={difficulty}")
            # Return up to MAX_QUESTIONS random questions from mock DB
            questions = random.sample(difficulty_questions, min(MAX_QUESTIONS, len(difficulty_questions)))
        else:
            logger.warning(f"No questions found in mock DB for topic={topic_key}, difficulty={difficulty}")
            
    # Final Fallback: If absolutely nothing works, return a default placeholder
    if not questions:
         logger.error("All question retrieval methods (vector store, generation, mock DB) failed. Using default fallback question.")
         questions = [{"question": f"Could not find or generate questions for {topic} ({difficulty}). Please try a different topic.", "answer": "N/A"}]

    logger.debug(f"Final selected questions count: {len(questions)}")
    return questions 