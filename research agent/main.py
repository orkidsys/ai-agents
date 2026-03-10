from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_agent
from tools import search_tool

load_dotenv()


class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]


# Load .env file from the same directory as this script
# load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))


llm = ChatOpenAI(model="gpt-4")


parser = PydanticOutputParser(pydantic_object=ResearchResponse)


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a helpful assistant that can help with research tasks.
            You will be given a topic and you will need to research it and provide a summary of the information.
            You will also need to provide the sources of the information and the tools used to gather the information.
            Wrap the output in this format and provide no other text \n{format_instructions}
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"), 
    ]
).partial(format_instructions=parser.get_format_instructions())
response =llm.invoke("Explain the history of Greek mythology")
print(response)


# Create agent using the new API (langchain 1.2.10+)
# Extract system prompt from the ChatPromptTemplate
system_prompt_text = """
You are a helpful assistant that can help with research tasks.
You will be given a topic and you will need to research it and provide a summary of the information.
You will also need to provide the sources of the information and the tools used to gather the information.
Wrap the output in this format and provide no other text.
"""

tools = [search_tool]
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt_text
)

# Invoke the agent directly (new API uses messages format)
raw_response = agent.invoke({"messages": [("human", "Explain the history of Greek mythology")]})


try:
    structured_response = parser.parse(raw_response.get("output")[0]["text"])
    print(structured_response)
except Exception as e:
    print(f"Error parsing response: {e}")
    structured_response = None

