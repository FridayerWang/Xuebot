import json
from typing import Dict, List, Optional, Any

from chains import (
    greeting_chain, 
    extraction_chain, 
    learning_path_chain,
    knowledge_analysis_chain,
    question_preference_chain,
    select_question_chain,
    evaluate_answer_chain,
    memory
)
from utils import retrieve_content, retrieve_questions, parse_json_safely
from logger import (
    logger, 
    log_state_change, 
    log_user_input, 
    log_agent_response, 
    log_json_result,
    log_error
)

class EducationAgent:
    """Education Agent class that orchestrates the learning flow."""
    
    def __init__(self):
        self.state = "greeting"
        self.grade = None
        self.subject = None
        self.topic = None
        self.content = None
        self.learning_path = None
        self.next_topic = None
        self.difficulty = None
        self.current_question = None
        self.current_answer = None
        self.knowledge_level = None
        logger.info("EducationAgent initialized")
        
    def process(self, user_input: str) -> str:
        """Process user input based on current state and return response."""
        
        log_user_input(user_input)
        logger.debug(f"Current state: {self.state}")
        
        if self.state == "greeting":
            # Initial greeting or extracting grade/subject/topic
            if not user_input or user_input.strip() == "":
                # First interaction, just greet
                logger.debug("First interaction, sending greeting")
                response = greeting_chain.run(chat_history="")
                old_state = self.state
                self.state = "extract_info"
                log_state_change(old_state, self.state)
                log_agent_response(response)
                return response
            else:
                # Extract information from user input
                logger.debug("Extracting information from user input")
                extraction_result = extraction_chain.run(user_input=user_input)
                log_json_result("Extraction", extraction_result)
                
                try:
                    extracted_info = parse_json_safely(extraction_result)
                    self.grade = extracted_info.get("grade")
                    self.subject = extracted_info.get("subject")
                    self.topic = extracted_info.get("topic")
                    
                    logger.debug(f"Extracted info - Grade: {self.grade}, Subject: {self.subject}, Topic: {self.topic}")
                    
                    if self.grade and self.subject and self.topic:
                        # Retrieve content
                        logger.debug("Retrieving content from knowledge base")
                        self.content = retrieve_content(self.grade, self.subject, self.topic)
                        logger.debug(f"Retrieved content: {self.content[:100]}...")
                        
                        # Plan learning path
                        logger.debug("Planning learning path")
                        learning_path_result = learning_path_chain.run(content=self.content)
                        log_json_result("Learning path", learning_path_result)
                        
                        try:
                            self.learning_path = parse_json_safely(learning_path_result)
                            # Analyze knowledge and determine next practice
                            logger.debug("Analyzing user knowledge")
                            analysis_result = knowledge_analysis_chain.run(
                                learning_path=json.dumps(self.learning_path),
                                chat_history=str(memory.chat_memory.messages)
                            )
                            log_json_result("Knowledge analysis", analysis_result)
                            
                            analysis = parse_json_safely(analysis_result)
                            self.knowledge_level = analysis.get("knowledge_level")
                            self.next_topic = analysis.get("next_topic")
                            self.difficulty = analysis.get("difficulty")
                            
                            logger.debug(f"Knowledge level: {self.knowledge_level}, Next topic: {self.next_topic}, Difficulty: {self.difficulty}")
                            
                            # Ask for question preference
                            old_state = self.state
                            self.state = "ask_preference"
                            log_state_change(old_state, self.state)
                            
                            response = question_preference_chain.run(
                                next_topic=self.next_topic,
                                difficulty=self.difficulty
                            )
                            log_agent_response(response)
                            return response
                        except Exception as e:
                            log_error("Error parsing learning path JSON", e)
                            response = "I'm sorry, I encountered an issue while processing the learning path. Could you please tell me again what you'd like to learn?"
                            log_agent_response(response)
                            return response
                    else:
                        response = "I didn't fully understand what you want to learn. Please clearly tell me the grade level, subject, and specific topic, for example 'I want to learn middle school math geometry'."
                        log_agent_response(response)
                        return response
                except Exception as e:
                    log_error("Error parsing extraction JSON", e)
                    response = "I'm sorry, I had trouble understanding your request. Please clearly specify the grade level, subject, and topic you'd like to learn."
                    log_agent_response(response)
                    return response
                
        elif self.state == "extract_info":
            # Extract information from user input
            logger.debug("Extracting information from user input")
            extraction_result = extraction_chain.run(user_input=user_input)
            log_json_result("Extraction", extraction_result)
            
            try:
                extracted_info = parse_json_safely(extraction_result)
                self.grade = extracted_info.get("grade")
                self.subject = extracted_info.get("subject")
                self.topic = extracted_info.get("topic")
                
                logger.debug(f"Extracted info - Grade: {self.grade}, Subject: {self.subject}, Topic: {self.topic}")
                
                if self.grade and self.subject and self.topic:
                    # Retrieve content
                    logger.debug("Retrieving content from knowledge base")
                    self.content = retrieve_content(self.grade, self.subject, self.topic)
                    logger.debug(f"Retrieved content: {self.content[:100]}...")
                    
                    # Plan learning path
                    logger.debug("Planning learning path")
                    learning_path_result = learning_path_chain.run(content=self.content)
                    log_json_result("Learning path", learning_path_result)
                    
                    try:
                        self.learning_path = parse_json_safely(learning_path_result)
                        # Analyze knowledge and determine next practice
                        logger.debug("Analyzing user knowledge")
                        analysis_result = knowledge_analysis_chain.run(
                            learning_path=json.dumps(self.learning_path),
                            chat_history=str(memory.chat_memory.messages)
                        )
                        log_json_result("Knowledge analysis", analysis_result)
                        
                        analysis = parse_json_safely(analysis_result)
                        self.knowledge_level = analysis.get("knowledge_level")
                        self.next_topic = analysis.get("next_topic")
                        self.difficulty = analysis.get("difficulty")
                        
                        logger.debug(f"Knowledge level: {self.knowledge_level}, Next topic: {self.next_topic}, Difficulty: {self.difficulty}")
                        
                        # Ask for question preference
                        old_state = self.state
                        self.state = "ask_preference"
                        log_state_change(old_state, self.state)
                        
                        response = question_preference_chain.run(
                            next_topic=self.next_topic,
                            difficulty=self.difficulty
                        )
                        log_agent_response(response)
                        return response
                    except Exception as e:
                        log_error("Error parsing learning path JSON", e)
                        response = "I'm sorry, I encountered an issue while processing the learning path. Could you please tell me again what you'd like to learn?"
                        log_agent_response(response)
                        return response
                else:
                    response = "I didn't fully understand what you want to learn. Please clearly tell me the grade level, subject, and specific topic, for example 'I want to learn middle school math geometry'."
                    log_agent_response(response)
                    return response
            except Exception as e:
                log_error("Error parsing extraction JSON", e)
                response = "I'm sorry, I had trouble understanding your request. Please clearly specify the grade level, subject, and topic you'd like to learn."
                log_agent_response(response)
                return response
                
        elif self.state == "ask_preference":
            # Process the user's question preference
            logger.debug(f"Processing question preference: {user_input}")
            
            if "personalized" in user_input.lower():
                # Generate personalized questions
                logger.debug("Generating personalized questions")
                from chains import generate_questions_chain
                questions_result = generate_questions_chain.run(
                    topic=self.next_topic,
                    difficulty=self.difficulty
                )
                log_json_result("Generated questions", questions_result)
                
                try:
                    parsed_result = parse_json_safely(questions_result)
                    questions = parsed_result.get("questions", [])
                    logger.debug(f"Successfully parsed {len(questions)} questions")
                except Exception as e:
                    log_error("Error parsing generated questions", e)
                    # Fallback in case of parsing issues
                    questions = [
                        {"question": f"This is a question about {self.next_topic}", "answer": "This is a sample answer"}
                    ]
                    logger.debug("Using fallback question")
            else:
                # Retrieve questions from database
                logger.debug("Retrieving questions from database")
                questions = retrieve_questions(self.topic, self.difficulty)
                logger.debug(f"Retrieved {len(questions)} questions")
            
            # Select the most appropriate question
            logger.debug("Selecting the most appropriate question")
            select_result = select_question_chain.run(
                questions=json.dumps(questions),
                user_level=self.knowledge_level,
                topic=self.next_topic
            )
            log_json_result("Question selection", select_result)
            
            try:
                selected = parse_json_safely(select_result)
                self.current_question = selected.get("selected_question")
                self.current_answer = selected.get("answer")
                
                logger.debug(f"Selected question: {self.current_question}")
                
                # Present the question to the user
                old_state = self.state
                self.state = "await_answer"
                log_state_change(old_state, self.state)
                
                response = f"Please answer the following question:\n\n{self.current_question}"
                log_agent_response(response)
                return response
            except Exception as e:
                log_error("Error parsing question selection", e)
                # Fallback in case of parsing issues
                self.current_question = questions[0]["question"]
                self.current_answer = questions[0]["answer"]
                
                old_state = self.state
                self.state = "await_answer"
                log_state_change(old_state, self.state)
                
                response = f"Please answer the following question:\n\n{self.current_question}"
                log_agent_response(response)
                return response
                
        elif self.state == "await_answer":
            # Evaluate the user's answer
            logger.debug(f"Evaluating user's answer to: {self.current_question}")
            user_answer = user_input
            
            evaluation_result = evaluate_answer_chain.run(
                question=self.current_question,
                correct_answer=self.current_answer,
                user_answer=user_answer
            )
            log_json_result("Answer evaluation", evaluation_result)
            
            try:
                evaluation = parse_json_safely(evaluation_result)
                is_correct = evaluation.get('is_correct', False)
                logger.debug(f"Evaluation result - Correct: {is_correct}")
                
                # Provide feedback
                feedback = f"""Evaluation result:
                
{'✓ Correct!' if is_correct else '✗ Incorrect.'}

Feedback: {evaluation.get('feedback')}

Explanation: {evaluation.get('explanation')}

Improvement tips: {evaluation.get('tips_for_improvement')}
                """
                
                # Update the state to determine next practice
                old_state = self.state
                self.state = "determine_next"
                log_state_change(old_state, self.state)
                
                # Analyze knowledge again with updated chat history
                logger.debug("Re-analyzing user knowledge after answer")
                analysis_result = knowledge_analysis_chain.run(
                    learning_path=json.dumps(self.learning_path),
                    chat_history=str(memory.chat_memory.messages)
                )
                log_json_result("Updated knowledge analysis", analysis_result)
                
                try:
                    analysis = parse_json_safely(analysis_result)
                    self.knowledge_level = analysis.get("knowledge_level")
                    self.next_topic = analysis.get("next_topic")
                    self.difficulty = analysis.get("difficulty")
                    
                    logger.debug(f"Updated knowledge level: {self.knowledge_level}, Next topic: {self.next_topic}, Difficulty: {self.difficulty}")
                    
                    # Ask for question preference for next round
                    old_state = self.state
                    self.state = "ask_preference"
                    log_state_change(old_state, self.state)
                    
                    response = feedback + "\n\n" + question_preference_chain.run(
                        next_topic=self.next_topic,
                        difficulty=self.difficulty
                    )
                    log_agent_response(response)
                    return response
                except Exception as e:
                    log_error("Error parsing updated knowledge analysis", e)
                    response = feedback + "\n\nWould you like to continue learning? Please tell me what you'd like to learn."
                    log_agent_response(response)
                    return response
            except Exception as e:
                log_error("Error parsing answer evaluation", e)
                feedback = "Thank you for your answer. The correct answer is: " + self.current_answer
                
                old_state = self.state
                self.state = "determine_next"
                log_state_change(old_state, self.state)
                
                response = feedback + "\n\nWould you like to continue learning? Please tell me what you'd like to learn."
                log_agent_response(response)
                return response
        
        elif self.state == "determine_next":
            logger.debug("Determining next step")
            # Reset the process and start over
            old_state = self.state
            self.state = "greeting"
            log_state_change(old_state, self.state)
            
            response = self.process(user_input)
            return response
        
        else:
            # Fallback
            logger.warning(f"Unknown state encountered: {self.state}")
            old_state = self.state
            self.state = "greeting"
            log_state_change(old_state, self.state)
            
            response = "I'm sorry, I got a bit lost. Let's start over. What grade level, subject, and topic would you like to learn?"
            log_agent_response(response)
            return response 