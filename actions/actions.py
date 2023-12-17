# actions.py

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import spacy
from datetime import datetime, timedelta
# Load spaCy model for Romanian
nlp = spacy.load('ro_core_news_sm')
import re


class ReservationForm(Action):
    def name(self) -> Text:
        return "reservation_form"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        # Logic to fill slots, extract entities, etc.

        dispatcher.utter_message(response="utter_slots_values")  # Custom response

        return []


class ValidateRestaurantForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_reservation_form"

    # @staticmethod
    # def cuisine_db() -> List[Text]:
    #     """Database of supported cuisines"""
    #
    #     return ["caribbean", "chinese", "french"]

    def validate_phone_number(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate cuisine value."""
        phone_number = slot_value.replace(" ", "")
        phone_number = phone_number.replace("(", "")
        phone_number = phone_number.replace(")", "")

        if phone_number[0] == '+':
            prefix = phone_number[:3]
            phone_number = phone_number[2:]
        elif phone_number[0] == '0' and phone_number[1] == '0':
            prefix = phone_number[:3]
            phone_number = phone_number[3:]
            print(phone_number)
        else:
            prefix = "+40"

        if phone_number.isdigit() and len(phone_number) == 10:
            return {"phone_number": prefix + phone_number}
        else:
            dispatcher.utter_message(response="utter_redo_phone_number")
            return {"phone_number": None}

    # def validate_reservation_date(
    #     self,
    #     slot_value: Any,
    #     dispatcher: CollectingDispatcher,
    #     tracker: Tracker,
    #     domain: DomainDict,
    # ) -> Dict[Text, Any]:
    #     date = slot_value
    #     print(date)
    #
    #     return {"reservation_date": date}

    def validate_reservation_time(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate cuisine value."""
        time = parse_time(slot_value)

        return {"reservation_time": time}

    def validate_party_size(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate cuisine value."""
        phone_number = slot_value

        if phone_number.isdigit() and len(phone_number) == 10:
            return {"phone_number": slot_value.capitalize()}
        else:
            return {"phone_number": None}

    def validate_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate cuisine value."""
        phone_number = slot_value

        if phone_number.isdigit() and len(phone_number) == 10:
            return {"phone_number": slot_value.capitalize()}
        else:
            return {"phone_number": None}

def parse_date(input_text):
    # Tokenize and process input
    doc = nlp(input_text.lower())

    # Initialize date_delta for relative dates
    date_delta = 0

    # Check for specific date-related terms
    for token in doc:
        if token.text in ['azi', 'astazi']:
            date_delta = 0
        elif token.text == 'maine':
            date_delta = 1
        elif token.text == 'poimaine':
            date_delta = 2
        elif token.text == 'raspoimaine':
            date_delta = 3
        elif token.text == 'in' and token.i + 1 < len(doc) and doc[token.i + 1].text.isdigit():
            date_delta = int(doc[token.i + 1].text)
        # Handle more cases...

    # Calculate the standard date
    standard_date = datetime.now() + timedelta(days=date_delta)

    # Check for specific date formats like '15 ianuarie'
    for token in doc:
        if token.text.isdigit():
            day = int(token.text)
            if 1 <= day <= 31 and token.i + 1 < len(doc) and doc[token.i + 1].text.isalpha():
                month_text = doc[token.i + 1].text
                month_mapping = {
                    'ianuarie': 1, 'februarie': 2, 'martie': 3, 'aprilie': 4, 'mai': 5, 'iunie': 6,
                    'iulie': 7, 'august': 8, 'septembrie': 9, 'octombrie': 10, 'noiembrie': 11, 'decembrie': 12
                }
                if month_text.lower() in month_mapping:
                    month = month_mapping[month_text.lower()]
                    standard_date = datetime(standard_date.year, month, day)

    # Check for specific date formats like '15.12.2023' or '15.12'
    if '.' in input_text:
        date_parts = input_text.split('.')
        if len(date_parts) >= 2 and date_parts[0].isdigit() and date_parts[1].isdigit():
            day = int(date_parts[0])
            month = int(date_parts[1])
            year = standard_date.year if len(date_parts) == 2 else int(date_parts[2])
            standard_date = datetime(year, month, day)

    if standard_date < datetime.now():
        standard_date = standard_date.replace(year=datetime.now().year + 1)

    # Format the date
    formatted_date = standard_date.strftime('%d.%m.%Y')

    return formatted_date


def parse_time(input_text):
    # Tokenize and process input
    doc = nlp(input_text.lower())

    # Initialize time_delta for relative times
    time_delta = timedelta()

    # Check for specific time-related terms
    for token in doc:
        if token.text.isdigit():
            hours = int(token.text)
            if 0 <= hours <= 23:
                time_delta = timedelta(hours=hours)

        elif token.text in ['jumate', 'jumatate']:
            time_delta += timedelta(minutes=30)

        elif token.text in ['si un sfert']:
            time_delta += timedelta(minutes=15)

        # Handle more cases...

    # Check for explicit morning or evening specification
    for i in range(len(doc) - 1):
        if doc[i].text.isdigit() and doc[i + 1].text in ['dimineata', 'seara']:
            specified_hour = int(doc[i].text)
            specified_period = doc[i + 1].text
            if specified_period == 'dimineata' and 0 <= specified_hour <= 11:
                time_delta = timedelta(hours=specified_hour)
            elif specified_period == 'seara' and 0 <= specified_hour <= 11:
                time_delta = timedelta(hours=specified_hour + 12)

    # Default to morning hours if no specific hour is specified
    if time_delta.total_seconds() == 0:
        time_delta = timedelta(hours=9)

    # Calculate the standard time
    standard_time = (datetime.now() + time_delta).time()

    return standard_time.strftime('%H:%M')
