from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
import logging

logger = logging.getLogger(__name__)

class ActionProcessHouseRequirements(Action):
    def name(self) -> Text:
        return "action_process_house_requirements"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
        # Get house requirement slots
        size = tracker.get_slot('desired_size')
        rooms = tracker.get_slot('desired_rooms')
        toilets = tracker.get_slot('desired_toilets')

        events = []
        # Persist house requirements
        if size:
            events.append(SlotSet('desired_size', float(size)))
        if rooms:
            events.append(SlotSet('desired_rooms', int(rooms)))
        if toilets:
            events.append(SlotSet('desired_toilets', int(toilets)))

        return events 