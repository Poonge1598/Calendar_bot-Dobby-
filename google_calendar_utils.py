from datetime import datetime,timedelta
#from front_end import service

# Retrieving events from the primary calendar with flexible parameters
def get_events(service,start_time=None, end_time=None, max_results=30, time_zone='Europe/Paris'):
    
    # Set default values for start_time and end_time if not provided
    if not start_time:
        start_time = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    if not end_time:
        end_time = (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"

    # Call the Calendar API to retrieve events
    call_output = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start_time,
            timeMax=end_time,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
            timeZone=time_zone
        )
        .execute()
    )

    # Extract the events from the response
    events = call_output.get("items", [])

    # events_str_list = []
    # for event in events:
    #     # Extract the event information
    #     event_id = event.get("id")
    #     start = event.get("start", {}).get("dateTime", event.get("start", {}).get("date"))
    #     end = event.get("end", {}).get("dateTime", event.get("end", {}).get("date"))
    #     summary = event.get("summary", "No Title")
    #     description = event.get("description", "No Description")
    #     location = event.get("location", "No Location")

    #     # Format the event into a string
    #     event_str = f"Event: {summary}\nID: {event_id}\nStart: {start}\nEnd: {end}\nDescription: {description}\nLocation: {location}"
    #     events_str_list.append(event_str)

    # # Concatenate the events into a string
    # events_str = "\n___\n".join(events_str_list)

    return events


def move_event(service,event_id, new_start_time, new_end_time):
    # Build the event details with the new times
    event_details = {
        "start": {"dateTime": new_start_time, "timeZone": "Europe/Paris"},
        "end": {"dateTime": new_end_time, "timeZone": "Europe/Paris"}
    }

    # Call the Calendar API to update the event
    updated_event = (service.events().patch(calendarId="primary", eventId=event_id, body=event_details).execute())

    return {"status": updated_event["status"]}

def delete_event(service,event_id):
    try:
        deleted_event=service.events().delete(calendarId="primary", eventId=event_id).execute()
        return {"status": deleted_event["status"]}
    except Exception as e:
        return {"status": "Error", "message": str(e)}

def add_event(service,meeting_name, start_time, duration_minutes=60, reminder_minutes=60):
    # Calculate end time based on start time and duration
    #start_dt = datetime.fromisoformat(start_time)
    start_dt = datetime.strptime(start_time.rstrip('Z'), "%Y-%m-%dT%H:%M:%S")
    end_dt = start_dt + timedelta(minutes=duration_minutes)
    end_time = end_dt.isoformat()

    # Build the event details
    event_details = {
        "summary": meeting_name,
        "start": {"dateTime": start_time, "timeZone": "Europe/Paris"},
        "end": {"dateTime": end_time, "timeZone": "Europe/Paris"},
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": reminder_minutes}
            ]
        }
    }
    
    print(f'event_details:{event_details}')

    # Call the Calendar API to create a new event
    created_event = (
        service.events()
        .insert(calendarId="primary", body=event_details)
        .execute()
    )

    return {"status": created_event["status"]}

# Define function dictionary
function_dict = {
    'get_events': get_events,
    'add_event': add_event,
    'move_event': move_event,
    'delete_event':delete_event
}

# Define tools
tools = [
    {
        'type': 'function',
        'function': {
            'name': 'get_events',
            'description': 'Retrieves events from the Google Calendar with specified details.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'start_time': {'type': 'string', 'description': 'Start time of the range in ISO 8601 format (e.g., "2024-06-10T00:00:00Z")'},
                    'end_time': {'type': 'string', 'description': 'End time of the range in ISO 8601 format (e.g., "2024-06-12T00:00:00Z")'},
                    'max_results': {'type': 'integer', 'description': 'Maximum number of results to retrieve', 'default': 10},
                    'time_zone': {'type': 'string', 'description': 'Time zone of the events', 'default': 'Europe/Paris'}
                },
                'required': []
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'add_event',
            'description': 'Adds a new event to the Google Calendar with specified details.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'meeting_name': {'type': 'string', 'description': 'Name of the meeting'},
                    'start_time': {'type': 'string', 'description': 'Start time of the meeting in ISO 8601 format (e.g., "2024-06-10T09:00:00Z")'},
                    'duration_minutes': {'type': 'integer', 'description': 'Duration of the meeting in minutes', 'default': 60},
                    'reminder_minutes': {'type': 'integer', 'description': 'Reminder time before the meeting in minutes', 'default': 60}
                },
                'required': ['meeting_name', 'start_time']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'delete_event',
            'description': 'Deletes an event from the Google Calendar based on event ID.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'event_id': {'type': 'string', 'description': 'The ID of the event to be deleted'}
                },
                'required': ['event_id']
            }
        }
    }
    ,
    {
        'type': 'function',
        'function': {
            'name': 'move_event',
            'description': 'Moves an existing event to a new start and end time.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'event_id': {'type': 'string', 'description': 'ID of the event to be moved'},
                    'new_start_time': {'type': 'string', 'description': 'New start time of the event in ISO 8601 format (e.g., "2024-06-11T10:00:00Z")'},
                    'new_end_time': {'type': 'string', 'description': 'New end time of the event in ISO 8601 format (e.g., "2024-06-11T11:00:00Z")'}
                },
                'required': ['event_id', 'new_start_time', 'new_end_time']
            }
        }
    }
]



