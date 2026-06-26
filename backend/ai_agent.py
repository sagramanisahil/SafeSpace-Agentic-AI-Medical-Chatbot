from langchain_core.tools import tool
from tools import query_medgemma, call_emergency
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent
from config import GROQ_API_KEY
import time

@tool
def ask_mental_health_specialist(query: str) -> str:
    """
    Generate a therapeutic response using the MedGemma model.
    Use this for all general user queries, mental health questions, emotional concerns,
    or to offer empathetic, evidence-based guidance in a conversational tone.
    """
    return query_medgemma(query)


@tool
def emergency_call_tool() -> None:
    """
    Place an emergency call to the safety helpline's phone number via Twilio.
    Use this only if the user expresses suicidal ideation, intent to self-harm,
    or describes a mental health emergency requiring immediate help.
    """
    call_emergency()


@tool
def find_nearby_therapists_by_location(location: str) -> str:
    """
    Finds and returns a list of licensed therapists near the specified location.

    Args:
        location (str): The name of the city or area in which the user is seeking therapy support.

    Returns:
        str: A newline-separated string containing therapist names and contact info.
    """
    return (
        f"Here are some therapists near {location}, {location}:\n"
        "- Dr. Ayesha Kapoor - +1 (555) 123-4567\n"
        "- Dr. James Patel - +1 (555) 987-6543\n"
        "- MindCare Counseling Center - +1 (555) 222-3333"
    )


# Step1: Create an AI Agent & Link to backend
tools = [ask_mental_health_specialist, emergency_call_tool, find_nearby_therapists_by_location]
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.2,
    groq_api_key=GROQ_API_KEY,
    max_tokens=500
)
graph = create_react_agent(llm, tools=tools)

SYSTEM_PROMPT = """
You are an AI engine supporting mental health conversations with warmth and vigilance.
You have access to three tools:

1. `ask_mental_health_specialist`: Use this tool to answer all emotional or psychological queries with therapeutic guidance.
2. `locate_therapist_tool`: Use this tool if the user asks about nearby therapists or if recommending local professional help would be beneficial.
3. `emergency_call_tool`: Use this immediately if the user expresses suicidal thoughts, self-harm intentions, or is in crisis.

Always take necessary action. Respond kindly, clearly, and supportively.
"""

def parse_response(inputs, retries=2):
    tool_called_name = "None"
    final_response = None

    for attempt in range(retries + 1):
        try:
            stream = graph.stream(inputs, stream_mode="updates")
            for s in stream:
                print(f"DEBUG: {s}")  # keep this to verify

                if not isinstance(s, dict):
                    continue

                tool_data = s.get('tools')
                if tool_data:
                    messages = tool_data.get('messages', [])
                    for msg in messages:
                        tool_called_name = getattr(msg, 'name', 'None')

                agent_data = s.get('agent')
                if agent_data:
                    messages = agent_data.get('messages', [])
                    for msg in messages:
                        if hasattr(msg, 'content'):
                            if isinstance(msg.content, str) and msg.content:
                                final_response = msg.content
                            elif isinstance(msg.content, list):
                                for block in msg.content:
                                    if isinstance(block, dict) and block.get('type') == 'text':
                                        final_response = block.get('text', '')
            break

        except Exception as e:
            print(f"REAL ERROR: {e}")
            if attempt < retries:
                time.sleep(2)
            else:
                final_response = "I'm having trouble. Please try again."

    return tool_called_name, final_response


"""if __name__ == "__main__":
    while True:
        user_input = input("User: ")
        print(f"Received user input: {user_input[:200]}...")
        inputs = {"messages": [("system", SYSTEM_PROMPT), ("user", user_input)]}
        stream = graph.stream(inputs, stream_mode="updates")
        tool_called_name, final_response = parse_response(stream)
        print("TOOL CALLED: ", tool_called_name)
        print("ANSWER: ", final_response)"""
        