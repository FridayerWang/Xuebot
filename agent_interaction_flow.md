## Agent Interaction Flow

- The agent greets the user and asks what subject, grade level, and topic they’d like to study.

- The user replies with something like: “Hi, I want to study [subject] for [grade level], focusing on [topic].”

- The agent uses an LLM to extract the subject, grade, and topic from the user's input. It then searches a vector store database for relevant content, which includes key concept summaries, exam requirements, and more. *(This content will be provided via a few simple documents.)*

- Based on the retrieved material, the LLM creates a structured learning path—for example, what concepts to learn first, what to build on next, and so on. This progression can be guided using in-context examples to help generate structured output.

- Using that learning path and analyzing the user's prior conversation history, the LLM evaluates their current knowledge level. It then determines what the user should practice next and at what difficulty level.

- The agent asks whether the user prefers personalized questions or official-style questions.

- If the user chooses personalized questions:
  - The LLM generates 3 questions based on the previously identified learning goal and difficulty level.

- If the user chooses official questions:
  - The system queries a relational database (not the vector database) for questions tagged with the same topic and difficulty.
  - It selects 3 questions at random. *(This database will also be constructed from a few simple files for the demo.)*

- The LLM reviews the 3 questions and selects the most suitable one.

- The selected question is presented to the user, and the agent waits for their answer.

- Once the user responds, the system compares their answer with the correct one and provides feedback:
  - Whether it was right or wrong
  - What the question tested
  - Why the answer was incorrect, if applicable

- The system then loops back to re-evaluate the next learning goal and difficulty level, repeating the cycle.
