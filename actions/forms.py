from typing import Text, List, Any, Dict
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.types import DomainDict

class ValidateLocationForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_location_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["region_name", "area_name", "ward_name"]

    async def extract_region_name(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        text_of_last_user_message = tracker.latest_message.get("text")
        return {"region_name": text_of_last_user_message}

    async def extract_area_name(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        text_of_last_user_message = tracker.latest_message.get("text")
        if text_of_last_user_message.lower() in ["không cần", "không cần tìm quận huyện"]:
            return {"area_name": None}
        return {"area_name": text_of_last_user_message}

    async def extract_ward_name(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        text_of_last_user_message = tracker.latest_message.get("text")
        if text_of_last_user_message.lower() in ["không cần", "không cần tìm phường xã"]:
            return {"ward_name": None}
        return {"ward_name": text_of_last_user_message}

    async def validate_region_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if not slot_value:
            dispatcher.utter_message(text="Bạn muốn tìm kiếm ở Tỉnh/Thành phố nào?")
            return {"region_name": None}
        return {"region_name": slot_value}

    async def validate_area_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value and slot_value.lower() in ["không cần", "không cần tìm quận huyện"]:
            return {"area_name": None}
        return {"area_name": slot_value}

    async def validate_ward_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value and slot_value.lower() in ["không cần", "không cần tìm phường xã"]:
            return {"ward_name": None}
        return {"ward_name": slot_value} 