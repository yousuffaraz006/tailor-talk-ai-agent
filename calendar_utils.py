from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz

# Path to your downloaded JSON key file
SERVICE_ACCOUNT_FILE = 'sunlit-monolith-433309-q4-e33e8acd434c.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = 'yousuffaraz006@gmail.com'  # The calendar where bookings will happen

# Authenticate and build service
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build('calendar', 'v3', credentials=credentials)

# Get availability for the next X days
def get_available_slots(start_date, end_date, duration_minutes=30, timezone='Asia/Kolkata'):
    start = start_date.isoformat() + 'Z'
    end = end_date.isoformat() + 'Z'

    body = {
        "timeMin": start,
        "timeMax": end,
        "timeZone": timezone,
        "items": [{"id": CALENDAR_ID}]
    }

    events_result = service.freebusy().query(body=body).execute()
    busy_times = events_result['calendars'][CALENDAR_ID]['busy']

    # Build available slots (you can make this smarter later)
    slots = []
    current = start_date

    while current + timedelta(minutes=duration_minutes) <= end_date:
        conflict = False
        for b in busy_times:
            busy_start = datetime.fromisoformat(b['start'].replace('Z', '+00:00'))
            busy_end = datetime.fromisoformat(b['end'].replace('Z', '+00:00'))
            if not (current + timedelta(minutes=duration_minutes) <= busy_start or current >= busy_end):
                conflict = True
                break

        if not conflict:
            slots.append(current)

        current += timedelta(minutes=duration_minutes)

    return slots

# Book an appointment
def book_appointment(start_time, summary='Meeting with AI Agent', duration_minutes=30, timezone='Asia/Kolkata'):
    end_time = start_time + timedelta(minutes=duration_minutes)
    event = {
        'summary': summary,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': timezone,
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': timezone,
        },
    }

    created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return created_event.get('htmlLink')