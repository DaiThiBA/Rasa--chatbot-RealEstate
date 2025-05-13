from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
from actions.house_requirements_action import ActionProcessHouseRequirements
import logging

logger = logging.getLogger(__name__)

class ActionAskRegionName(Action):
    def name(self) -> Text:
        return "action_ask_region_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        logger.info("\n=== ActionAskRegionName Started ===")
        
        # Log current slots
        logger.info("\n=== Current Slots ===")
        for slot in ['region_name', 'area_name', 'ward_name']:
            logger.info(f"Slot {slot}: {tracker.get_slot(slot)}")

        # Get region from slot
        region_name = tracker.get_slot('region_name')
        if region_name:
            # Move to ask area
            return [FollowupAction("action_ask_area_name")]
            
        # If no region, show region request form
        dispatcher.utter_message(response="utter_ask_region_name")
        return []

class ActionAskAreaName(Action):
    def name(self) -> Text:
        return "action_ask_area_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        logger.info("\n=== ActionAskAreaName Started ===")
        
        # Get area from slot
        area_name = tracker.get_slot('area_name')
        if area_name:
            # Move to ask ward
            return [FollowupAction("action_ask_ward_name")]

        # If no area, show area request form
        dispatcher.utter_message(response="utter_ask_area_name")
        return []

class ActionAskWardName(Action):
    def name(self) -> Text:
        return "action_ask_ward_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        logger.info("\n=== ActionAskWardName Started ===")

        # Check if user wants to skip
        intent = tracker.get_intent_of_latest_message()
        if intent == 'deny':
            # Log all slots before search
            logger.info("\n=== Final Slots Before Search ===")
            logger.info(f"User Info:")
            logger.info(f"- user_name: {tracker.get_slot('user_name')}")
            logger.info(f"- user_age: {tracker.get_slot('user_age')}")
            logger.info(f"- user_marital_status: {tracker.get_slot('user_marital_status')}")
            logger.info(f"- user_income: {tracker.get_slot('user_income')}")
            logger.info(f"- customer_cluster: {tracker.get_slot('customer_cluster')}")
            
            logger.info(f"\nHouse Requirements:")
            logger.info(f"- desired_size: {tracker.get_slot('desired_size')}")
            logger.info(f"- desired_rooms: {tracker.get_slot('desired_rooms')}")
            logger.info(f"- desired_toilets: {tracker.get_slot('desired_toilets')}")
            
            logger.info(f"\nLocation Info:")
            logger.info(f"- region_name: {tracker.get_slot('region_name')}")
            logger.info(f"- area_name: {tracker.get_slot('area_name')}")
            logger.info(f"- ward_name: {tracker.get_slot('ward_name')}")
            
            return [FollowupAction("action_search_real_estate")]

        # Get ward from entity
        entities = tracker.latest_message.get('entities', [])
        for entity in entities:
            if entity.get('entity') == 'ward_name':
                ward_name = entity.get('value')
                return [
                    SlotSet('ward_name', ward_name),
                    FollowupAction("action_search_real_estate")
                ]

        # If no ward provided, show form
        dispatcher.utter_message(response="utter_ask_ward_name")
        return []

class ActionProcessLocation(Action):
    def __init__(self):
        self.house_processor = ActionProcessHouseRequirements()

    def name(self) -> Text:
        return "action_process_location"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
        # Get location slots
        region = tracker.get_slot('region_name')
        area = tracker.get_slot('area_name')

        events = []
        # Process house requirements first
        events.extend(self.house_processor.run(dispatcher, tracker, domain))

        # Persist location
        if region:
            events.append(SlotSet('region_name', region))
        if area:
            events.append(SlotSet('area_name', area))

        # Move to search
        events.append(FollowupAction("action_search_real_estate"))
        return events 