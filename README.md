# edu_bot
Child-Tutoring Agent with Continuous Q&amp;A, Storytelling, and Adaptive Encouragement\

This is a question-and-answer conversational bot designed for children's learning. This chatbot uses curriculum materials or question-and-answer pairs used by kindergarten teachers to create a preschool education chatbot. The curriculum materials can be uploaded to the agent in PDF or Word documents, and the agent uses RAG to search its knowledge base.
The agent can proactively ask questions to children (in both Chinese and English). After multiple rounds of conversation, it evaluates the child, summarizes the results, and provides guidance on the next step in their learning plan.

1. The agent waits for the child to ask a question. If it receives the question within 3 seconds, it searches the vector knowledge base to obtain the answer and then uses the Thousand Questions model to answer the question.
2. The maximum waiting time is 3 seconds. If the agent waits for 3 seconds and still hasn't received a text message, meaning it receives an empty string after 3 seconds, the agent searches the knowledge base for the question and proactively asks the child a question. Alternatively, the agent suggests, "Let me tell you a fun story," then searches the knowledge base for the story, proactively tells it to the child, and then asks the child a question.

The following process is as follows:
1. If the child answers the question, the agent determines whether the answer is good or not based on the text of the child's response. The agent determines the quality of the child's answer by comparing the text of the child's response to the standard answer. If the answer is good, the agent provides praise and refrains from asking more questions next time. If the answer is poor, the agent provides the correct answer, encourages the child to keep working on it, and may ask more questions next time to help the child retain the answer.
2. If the child doesn't answer the question, for example, if the agent waits for 3 seconds and still hasn't received a text, it will proactively say, "Let me tell you another story," then begin telling the story or ask another question, etc. If it still hasn't received a text after 3 seconds, it will exit the conversation and say something like, "Call me if you need anything."
All references to a 3-second wait time are for a maximum of 3 seconds. For example, if a text message is received after 1 second, it will immediately proceed to the next step.

The overall process is an endless loop: similarity scoring, encouragement and correction, then proactive questioning, waiting for answers, and so on.

The children's recitation, as well as all input and output involved, is done through text, without voice.

Please design the database tables. Four or five tables will suffice, using MySQL. Keep it simple, just enough to accomplish the above tasks. 
1. Create a detailed flowchart.
2. In the MySQL database design, clearly describe the function of each table and the meaning of each field.
3. Provide a specific solution.
4. Provide the code directory structure, for example, the data directory should contain knowledge base documents, etc.
5. Provide detailed, executable code, implemented in Python, and run it to display the results.
