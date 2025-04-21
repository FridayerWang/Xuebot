from langchain.prompts import PromptTemplate

# Greeting prompt
greeting_prompt = PromptTemplate(
    input_variables=["chat_history"],
    template="""You are an AI educational assistant. If this is the beginning of the conversation, 
greet the user in a friendly manner and ask them what grade level, subject, and topic they would like to learn.
    
Chat history:
{chat_history}

Your response:"""
)

# Extract grade, subject, and topic
extraction_prompt = PromptTemplate(
    input_variables=["user_input"],
    template="""Extract the grade level, subject, and topic information from the following user input. 
Return in JSON format. If any information is missing, set the corresponding value to null.

User input: {user_input}

Please output the following JSON format:
```json
{{
    "grade": "extracted grade",
    "subject": "extracted subject",
    "topic": "extracted topic"
}}
```"""
)

# Learning path planning
learning_path_prompt = PromptTemplate(
    input_variables=["content"],
    template="""Based on the following content, plan a structured learning path. 
This should be a progressive learning plan from basics to advanced concepts.

Content: {content}

Please output the following JSON format:
```json
{{
    "learning_path": [
        {{"step": 1, "topic": "subtopic1", "description": "description"}},
        {{"step": 2, "topic": "subtopic2", "description": "description"}},
        {{"step": 3, "topic": "subtopic3", "description": "description"}}
    ]
}}
```"""
)

# Analyze user knowledge and determine next practice
knowledge_analysis_prompt = PromptTemplate(
    input_variables=["learning_path", "chat_history"],
    template="""Based on the following learning path and the user's conversation history, 
analyze the user's knowledge level and determine what they should practice next and at what difficulty.

Learning path: {learning_path}

Conversation history:
{chat_history}

Please output the following JSON format:
```json
{{
    "knowledge_level": "beginner/intermediate/advanced",
    "next_topic": "next topic to practice",
    "difficulty": "easy/medium/hard",
    "reasoning": "your analysis reasoning"
}}
```"""
)

# Ask user about question preference
question_preference_prompt = PromptTemplate(
    input_variables=["next_topic", "difficulty"],
    template="""You will be studying "{next_topic}" at a "{difficulty}" difficulty level.

Would you like personalized generated questions or authoritative questions from our database? Please respond with "personalized" or "authoritative"."""
)

# Generate personalized questions
generate_questions_prompt = PromptTemplate(
    input_variables=["topic", "difficulty"],
    template="""Please generate 3 educational questions for the following topic and difficulty level, with detailed answers:

Topic: {topic}
Difficulty: {difficulty}

Please output the following JSON format:
```json
{{
    "questions": [
        {{"question": "question1", "answer": "detailed answer1"}},
        {{"question": "question2", "answer": "detailed answer2"}},
        {{"question": "question3", "answer": "detailed answer3"}}
    ]
}}
```"""
)

# Select the most appropriate question
select_question_prompt = PromptTemplate(
    input_variables=["questions", "user_level", "topic"],
    template="""From the following 3 questions, select the most appropriate one for the user's current level and learning topic:

User level: {user_level}
Learning topic: {topic}
Question list:
{questions}

Please output the following JSON format:
```json
{{
    "selected_question": "selected question",
    "answer": "question's answer",
    "reasoning": "reason for selecting this question"
}}
```"""
)

# Evaluate user's answer
evaluate_answer_prompt = PromptTemplate(
    input_variables=["question", "correct_answer", "user_answer"],
    template="""Evaluate the user's answer to the following question:

Question: {question}
Correct answer: {correct_answer}
User's answer: {user_answer}

Please output the following JSON format:
```json
{{
    "is_correct": true/false,
    "feedback": "detailed feedback explaining correct or incorrect points",
    "explanation": "what knowledge point this question tests and the solution approach",
    "tips_for_improvement": "suggestions for improvement"
}}
```"""
) 