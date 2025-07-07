from pydantic import BaseModel
from fastapi import FastAPI, Request
from agent import chat_with_agent
from datetime import datetime, timedelta
from calendar_utils import get_available_slots, book_appointment
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str

app = FastAPI()

class BookingRequest(BaseModel):
    date: str  # ISO format, e.g., 2025-03-26T14:00
    summary: str

@app.post("/available")
def check_slots(data: BookingRequest):
    start = datetime.fromisoformat(data.date)
    end = start + timedelta(hours=8)
    slots = get_available_slots(start, end)
    return {"available_slots": [dt.isoformat() for dt in slots]}

@app.post("/book")
def book(data: BookingRequest):
    start_time = datetime.fromisoformat(data.date)
    link = book_appointment(start_time, summary=data.summary)
    return {"message": "Booking confirmed", "link": link}

@app.post("/chat")
async def chat(data: ChatRequest):
    reply = chat_with_agent(data.message)
    return {"response": reply}

# @app.post("/chat")
# async def chat(request: Request):
#     data = await request.json()
#     message = data.get("message")
#     reply = chat_with_agent(message)
#     return {"response": reply}
