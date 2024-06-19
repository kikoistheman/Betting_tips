from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from groq_api import api_key

def summarize_betting_tips():
    # Open txt file and read the text
    with open("transcript.txt", "r") as file:
        text = file.read()

    system = "your a youtube betting tips video  summery  the text from user and tell him all the text the betting tips and the match names and also the dates if possible"
    human = "{text}"
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

    chain = prompt | ChatGroq(temperature=0, groq_api_key=api_key, model_name="mixtral-8x7b-32768")
    text = chain.invoke({"text": text})
        
    output = text.content
    
    return output

# Example usage:

