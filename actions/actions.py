# actions.py

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ReservationForm(Action):
    def name(self) -> Text:
        return "reservation_form"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        # Logic to fill slots, extract entities, etc.
        dispatcher.utter_message(response="utter_slots_values")  # Custom response

        return []