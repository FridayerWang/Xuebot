import os
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory

from prompts import (
    greeting_prompt,
    extraction_prompt,
    learning_path_prompt,
    knowledge_analysis_prompt,
    question_preference_prompt,
    generate_questions_prompt,
    select_question_prompt,
    evaluate_answer_prompt
)
from config import LLM_TEMPERATURE, LLM_MODEL, OPENAI_API_KEY
from logger import logger

# Set API key if provided in config
if OPENAI_API_KEY:
    logger.info("Setting OpenAI API key from config")
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
else:
    logger.warning("OpenAI API key not provided in config, expecting it to be set in environment variables")

# Initialize the LLM
logger.info(f"Initializing LLM with model={LLM_MODEL}, temperature={LLM_TEMPERATURE}")
llm = ChatOpenAI(temperature=LLM_TEMPERATURE, model=LLM_MODEL)
memory = ConversationBufferMemory(return_messages=True)
logger.debug("Conversation memory initialized")

# Initialize chains
logger.debug("Initializing LangChain chains")
greeting_chain = LLMChain(llm=llm, prompt=greeting_prompt, memory=memory)
extraction_chain = LLMChain(llm=llm, prompt=extraction_prompt)
learning_path_chain = LLMChain(llm=llm, prompt=learning_path_prompt)
knowledge_analysis_chain = LLMChain(llm=llm, prompt=knowledge_analysis_prompt)
question_preference_chain = LLMChain(llm=llm, prompt=question_preference_prompt)
generate_questions_chain = LLMChain(llm=llm, prompt=generate_questions_prompt)
select_question_chain = LLMChain(llm=llm, prompt=select_question_prompt)
evaluate_answer_chain = LLMChain(llm=llm, prompt=evaluate_answer_prompt)
logger.info("All LangChain chains initialized successfully") 