import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os 

from openai import OpenAI


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


class Calendar():

  openai_client = OpenAI(
      api_key='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',
      base_url='http://127.0.0.1:5000/v1'
  )

  
  def __init__(self,):

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
      creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
      else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "calendar_credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=8080)
      # Save the credentials for the next run
      with open("token.json", "w") as token:
        token.write(creds.to_json())

    try:
      self.service = build("calendar", "v3", credentials=creds)


    except HttpError as error:
      print(f"An could not build the google calendar service: {error}")


  def get_events(self, max_results=10, timeMin=datetime.datetime.utcnow().isoformat() + "Z"):
    # Call the Calendar API
    # now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    print("Google Calendar: getting the upcoming {} events"
          .format(max_results))
    events_result = (
        self.service.events()
        .list(
            calendarId="primary",
            timeMin=timeMin,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
      print("No upcoming events found.")
      return

    # Prints the start and name of the next 10 events
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      print(start, event["summary"])

    return events


  def create_event(self, event_location='', event_summary='', event_desc='',
                    start_date='', end_date='', timezone='', recurrence='',
                    ):
    event = {
      'summary': event_summary,
      'location': event_location,
      'description': event_desc,
      'start': {
        'dateTime': start_date,
        'timeZone': timezone,
      },
      'end': {
        'dateTime': end_date,
        'timeZone': timezone,
      },
      'recurrence': [
        'RRULE:FREQ=DAILY;COUNT=2'
      ],
      'attendees': [
        {'email': 'lpage@example.com'},
        {'email': 'sbrin@example.com'},
      ],
      'reminders': {
        'useDefault': True,
      },
    }

    event = self.service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))

  def get_b_read(self, user_input):
      # get whether or not to read from the vector db
      f = open('calendar_read_prompt.txt')
      prompt = f.read()
      f.close()

      completion = self.openai_client.chat.completions.create(
          model="gpt-3.5-turbo",
          messages=[
              {"role": "system", "content": prompt + user_input},
          ],
      )
      print(completion.choices[0].message.content)

      if 'yes' in completion.choices[0].message.content.lower():
          return True
      else:
          return False

  
  def get_b_write(self, user_input):
      # get whether or not to write to the vector db
      f = open('calendar_write_prompt.txt')
      prompt = f.read()
      f.close()

      completion = self.openai_client.chat.completions.create(
          model="gpt-3.5-turbo",
          messages=[
              {"role": "system", "content": prompt + user_input},
          ],
      )

      print(completion.choices[0].message.content)
      if 'yes' in completion.choices[0].message.content.lower():
          return True
      else:
          return False
