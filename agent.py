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
        self.asked_questions_this_topic = []
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
                    self.asked_questions_this_topic = []
                    
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
                            if self.next_topic and self.topic and self.next_topic.lower() != self.topic.lower():
                                logger.info(f"Topic changing from {self.topic} to {self.next_topic}. Resetting asked questions.")
                                self.asked_questions_this_topic = []
                                self.topic = self.next_topic
                            self.difficulty = analysis.get("difficulty")
                            
                            logger.debug(f"Knowledge level: {self.knowledge_level}, Next topic: {self.next_topic}, Difficulty: {self.difficulty}")
                            
                            # Directly retrieve and select authoritative question
                            logger.debug("Directly retrieving authoritative questions from database")
                            questions = retrieve_questions(self.next_topic, self.difficulty)
                            logger.debug(f"Retrieved {len(questions)} questions")
                            
                            if not questions:
                                log_error("Failed to retrieve or generate any questions.", None)
                                response = "I couldn't find or generate any suitable questions for the topic. Please try specifying the topic again or try a different topic."
                                self.state = "greeting" # Reset state
                                log_agent_response(response)
                                return response
                            
                            # Select the most appropriate question
                            logger.debug("Selecting the most appropriate question")
                            select_result = select_question_chain.run(
                                questions=json.dumps(questions),
                                user_level=self.knowledge_level,
                                topic=self.next_topic,
                                asked_questions=json.dumps(self.asked_questions_this_topic)
                            )
                            log_json_result("Question selection", select_result)
                            
                            try:
                                selected = parse_json_safely(select_result)
                                self.current_question = selected.get("selected_question")
                                self.current_answer = selected.get("answer")
                                
                                if not self.current_question:
                                    # Fallback if selection fails. Try selecting the first *unasked* question.
                                    logger.warning("Question selection did not return a question, using first available unasked question.")
                                    unasked_questions = [q for q in questions if q.get("question") not in self.asked_questions_this_topic]
                                    if unasked_questions:
                                        self.current_question = unasked_questions[0].get("question", "Error retrieving question.")
                                        self.current_answer = unasked_questions[0].get("answer", "Error retrieving answer.")
                                    else:
                                        # If ALL retrieved questions were already asked (should be rare with DB), log error and maybe fallback differently
                                        logger.error("All retrieved questions have already been asked for this topic/difficulty!")
                                        # Handle this case - maybe force generation or indicate completion?
                                        # For now, just use the first question again, but log error
                                        self.current_question = questions[0].get("question", "Error retrieving question.") if questions else "Error: No question available."
                                        self.current_answer = questions[0].get("answer", "Error retrieving answer.") if questions else "N/A"
                                    
                                # Add the selected question to the asked list
                                if self.current_question not in self.asked_questions_this_topic:
                                    self.asked_questions_this_topic.append(self.current_question)
                                
                                logger.debug(f"Selected question: {self.current_question}")
                                
                                # Present the question to the user
                                old_state = self.state
                                self.state = "await_answer"
                                log_state_change(old_state, self.state)
                                
                                response = f"Please answer the following question:\n\n{self.current_question}"
                                log_agent_response(response)
                                return response
                            except Exception as e:
                                log_error("Error parsing question selection or no questions available", e)
                                # Fallback in case of parsing issues or no questions
                                fallback_question = questions[0] if questions else {"question": "Error: No question available.", "answer": "N/A"}
                                self.current_question = fallback_question["question"]
                                # Ensure fallback question is also added to asked list if possible
                                if self.current_question not in self.asked_questions_this_topic and self.current_question != "Error: No question available.":
                                    self.asked_questions_this_topic.append(self.current_question)
                                self.current_answer = fallback_question["answer"]
                                
                                old_state = self.state
                                self.state = "await_answer"
                                log_state_change(old_state, self.state)
                                
                                response = f"Please answer the following question:\n\n{self.current_question}"
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
                self.asked_questions_this_topic = []
                
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
                        if self.next_topic and self.topic and self.next_topic.lower() != self.topic.lower():
                            logger.info(f"Topic changing from {self.topic} to {self.next_topic}. Resetting asked questions.")
                            self.asked_questions_this_topic = []
                            self.topic = self.next_topic
                        self.difficulty = analysis.get("difficulty")
                        
                        logger.debug(f"Knowledge level: {self.knowledge_level}, Next topic: {self.next_topic}, Difficulty: {self.difficulty}")
                        
                        # Directly retrieve and select authoritative question
                        logger.debug("Directly retrieving authoritative questions from database")
                        questions = retrieve_questions(self.next_topic, self.difficulty)
                        logger.debug(f"Retrieved {len(questions)} questions")
                        
                        if not questions:
                            log_error("Failed to retrieve or generate any questions.", None)
                            response = "I couldn't find or generate any suitable questions for the topic. Please try specifying the topic again or try a different topic."
                            self.state = "greeting" # Reset state
                            log_agent_response(response)
                            return response
                        
                        # Select the most appropriate question
                        logger.debug("Selecting the most appropriate question")
                        select_result = select_question_chain.run(
                            questions=json.dumps(questions),
                            user_level=self.knowledge_level,
                            topic=self.next_topic,
                            asked_questions=json.dumps(self.asked_questions_this_topic)
                        )
                        log_json_result("Question selection", select_result)
                        
                        try:
                            selected = parse_json_safely(select_result)
                            self.current_question = selected.get("selected_question")
                            self.current_answer = selected.get("answer")
                            
                            if not self.current_question:
                                # Fallback if selection fails. Try selecting the first *unasked* question.
                                logger.warning("Question selection did not return a question, using first available unasked question.")
                                unasked_questions = [q for q in questions if q.get("question") not in self.asked_questions_this_topic]
                                if unasked_questions:
                                    self.current_question = unasked_questions[0].get("question", "Error retrieving question.")
                                    self.current_answer = unasked_questions[0].get("answer", "Error retrieving answer.")
                                else:
                                    # If ALL retrieved questions were already asked (should be rare with DB), log error and maybe fallback differently
                                    logger.error("All retrieved questions have already been asked for this topic/difficulty!")
                                    # Handle this case - maybe force generation or indicate completion?
                                    # For now, just use the first question again, but log error
                                    self.current_question = questions[0].get("question", "Error retrieving question.") if questions else "Error: No question available."
                                    self.current_answer = questions[0].get("answer", "Error retrieving answer.") if questions else "N/A"
                                
                            # Add the selected question to the asked list
                            if self.current_question not in self.asked_questions_this_topic:
                                self.asked_questions_this_topic.append(self.current_question)
                            
                            logger.debug(f"Selected question: {self.current_question}")
                            
                            # Present the question to the user
                            old_state = self.state
                            self.state = "await_answer"
                            log_state_change(old_state, self.state)
                            
                            response = f"Please answer the following question:\n\n{self.current_question}"
                            log_agent_response(response)
                            return response
                        except Exception as e:
                            log_error("Error parsing question selection or no questions available", e)
                            # Fallback in case of parsing issues or no questions
                            fallback_question = questions[0] if questions else {"question": "Error: No question available.", "answer": "N/A"}
                            self.current_question = fallback_question["question"]
                            # Ensure fallback question is also added to asked list if possible
                            if self.current_question not in self.asked_questions_this_topic and self.current_question != "Error: No question available.":
                                self.asked_questions_this_topic.append(self.current_question)
                            self.current_answer = fallback_question["answer"]
                            
                            old_state = self.state
                            self.state = "await_answer"
                            log_state_change(old_state, self.state)
                            
                            response = f"Please answer the following question:\n\n{self.current_question}"
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
                    if self.next_topic and self.topic and self.next_topic.lower() != self.topic.lower():
                        logger.info(f"Topic changing from {self.topic} to {self.next_topic}. Resetting asked questions.")
                        self.asked_questions_this_topic = []
                        self.topic = self.next_topic
                    self.difficulty = analysis.get("difficulty")
                    
                    logger.debug(f"Updated knowledge level: {self.knowledge_level}, Next topic: {self.next_topic}, Difficulty: {self.difficulty}")
                    
                    # Directly retrieve and select the next authoritative question
                    logger.debug("Directly retrieving next authoritative question")
                    questions = retrieve_questions(self.next_topic, self.difficulty)
                    logger.debug(f"Retrieved {len(questions)} questions for next round")

                    if not questions:
                        log_error("Failed to retrieve or generate any questions for the next round.", None)
                        response = feedback + "\n\nI couldn't find or generate any more questions for this topic. Would you like to try a different topic?"
                        self.state = "greeting" # Reset state
                        log_agent_response(response)
                        return response

                    # Select the most appropriate question
                    logger.debug("Selecting the most appropriate next question")
                    select_result = select_question_chain.run(
                        questions=json.dumps(questions),
                        user_level=self.knowledge_level,
                        topic=self.next_topic,
                        asked_questions=json.dumps(self.asked_questions_this_topic)
                    )
                    log_json_result("Next question selection", select_result)
                    
                    try:
                        selected = parse_json_safely(select_result)
                        self.current_question = selected.get("selected_question")
                        self.current_answer = selected.get("answer")
                        
                        if not self.current_question:
                            # Fallback if selection fails. Try selecting the first *unasked* question.
                            logger.warning("Next question selection did not return a question, using first available unasked question.")
                            unasked_questions = [q for q in questions if q.get("question") not in self.asked_questions_this_topic]
                            if unasked_questions:
                                self.current_question = unasked_questions[0].get("question", "Error retrieving question.")
                                self.current_answer = unasked_questions[0].get("answer", "Error retrieving answer.")
                            else:
                                # If ALL retrieved questions were already asked (should be rare with DB), log error and maybe fallback differently
                                logger.error("All retrieved questions have already been asked for this topic/difficulty!")
                                # Handle this case - maybe force generation or indicate completion?
                                # For now, just use the first question again, but log error
                                self.current_question = questions[0].get("question", "Error retrieving question.") if questions else "Error: No question available."
                                self.current_answer = questions[0].get("answer", "Error retrieving answer.") if questions else "N/A"
                            
                        # Add the selected question to the asked list
                        if self.current_question not in self.asked_questions_this_topic:
                            self.asked_questions_this_topic.append(self.current_question)
                        
                        logger.debug(f"Selected next question: {self.current_question}")
                        
                        # Present the next question to the user
                        old_state = self.state # Should be 'determine_next' before this block
                        self.state = "await_answer" 
                        log_state_change(old_state, self.state) # Log transition from determine_next -> await_answer
                        
                        response = feedback + f"\n\nPlease answer the next question:\n\n{self.current_question}"
                        log_agent_response(response)
                        return response
                    except Exception as e:
                        log_error("Error parsing next question selection or no questions available", e)
                        # Fallback in case of parsing issues or no questions
                        fallback_question = questions[0] if questions else {"question": "Error: No question available.", "answer": "N/A"}
                        self.current_question = fallback_question["question"]
                        # Ensure fallback question is also added to asked list if possible
                        if self.current_question not in self.asked_questions_this_topic and self.current_question != "Error: No question available.":
                            self.asked_questions_this_topic.append(self.current_question)
                        self.current_answer = fallback_question["answer"]
                        
                        old_state = self.state # Should be 'determine_next'
                        self.state = "await_answer"
                        log_state_change(old_state, self.state)
                        
                        response = feedback + f"\n\nPlease answer the next question:\n\n{self.current_question}"
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