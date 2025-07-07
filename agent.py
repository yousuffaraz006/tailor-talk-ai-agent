from langchain.agents.agent_types import AgentType
from google.api_core.exceptions import ResourceExhausted
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, Tool
from calendar_utils import get_available_slots, book_appointment
from datetime import datetime, timedelta
from dotenv import load_dotenv
from datetime import datetime
import pytz
import os

load_dotenv()  # Load environment variables from .env file

os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')

# Set up your model (replace with actual API keys and config)
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", max_output_tokens=1024, temperature=0, google_api_key=os.getenv('GOOGLE_API_KEY'))

# Tool: Check available slots
def get_slots_tool(date_str: str) -> str:
  date = datetime.fromisoformat(date_str)
  slots = get_available_slots(date, date + timedelta(hours=8))
  return "\n".join([slot.strftime('%Y-%m-%d %H:%M') for slot in slots])

# Tool: Book appointment
def book_tool(date_str: str) -> str:
  dt = datetime.fromisoformat(date_str)
  link = book_appointment(dt, summary="Meeting with AI Agent")
  return f"Booking confirmed: {link}"

# Register tools
tools = [
  Tool(name="CheckCalendar",
    func=get_slots_tool,
    description="Use this to check available slots on a specific date. Input format: 'YYYY-MM-DDTHH:MM'"),
  Tool(name="BookSlot",
    func=book_tool,
    description="Use this to book a meeting. Input format: 'YYYY-MM-DDTHH:MM'")
]

IST = pytz.timezone("Asia/Kolkata")
current_time = datetime.now(IST).strftime("%Y-%m-%d %H:%M %Z")

TAILORTALK_CONTEXT = f"""
You are TailorTalk's AI Assistant.

TailorTalk is a luxury fashion-tech company. You assist clients in checking available consultation slots and booking appointments with our CEO, Yousuf Faraz.

The current date and time is: {current_time}.
Appointments are available only between 9 AM to 5 PM, Monday to Friday, in IST (Indian Standard Time).

You MUST respond in the following format:
Thought: your reasoning  
Action: the name of the tool (CheckCalendar or BookSlot)  
Action Input: the input to the tool  
When you're finished and no action is needed, return only the final answer as plain text.

IMPORTANT:
- Before booking, confirm the user's name and email.
- Ask them to confirm the date, time, name, and email by replying with 'yes' or 'no'.
- Do NOT proceed to booking unless the user confirms.
- When booking, title the event as "Meeting with (user's name)" and invite the user's email.

Be concise, professional, and add light humor only if the user is informal or joking.
Stick to the output format above EXACTLY.
"""

# Create the agent
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True, agent_kwargs={"system_message": TAILORTALK_CONTEXT}, handle_parsing_errors=True)

def chat_with_agent(user_input: str) -> str:
  prompt = f"{TAILORTALK_CONTEXT}\n\nUser: {user_input}"
  try:
    return agent.run(prompt)
  except ResourceExhausted:
    return "Sorry, the AI service has reached its quota limit. Please try again later."
  except Exception as e:
    return f"Something went wrong: {str(e)}"