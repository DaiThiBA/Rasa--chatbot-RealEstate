from typing import Any, Text, Dict, List
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction

class ValidateUserProfileForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_user_profile_form"

    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Text]:
        required_slots = ['user_name', 'user_age', 'user_marital_status', 'user_income']
        if not any(tracker.get_slot(slot) for slot in required_slots):
            dispatcher.utter_message(
                custom={
                    "type": "info_request",
                    "message": "Vui lòng cung cấp thông tin cá nhân:",
                    "required_info": {
                        "personal": ["Họ tên", "Tuổi", "Tình trạng hôn nhân", "Thu nhập hàng tháng"],
                        "marital_status_options": [
                            "Độc thân",
                            "Đã có gia đình",
                            "Đã kết hôn và có con"
                        ],
                        "income_note": {
                            "single": "Thu nhập cá nhân",
                            "married": "Tổng thu nhập cả hai vợ chồng"
                        }
                    },
                    "examples": [
                        "Tôi là Minh, 35 tuổi, đã có gia đình, thu nhập 50 triệu/tháng",
                        "Tôi tên Hương, 28 tuổi, độc thân, thu nhập 25 triệu",
                        "Tôi là Nam, 40 tuổi, đã kết hôn và có con, thu nhập 70 triệu/tháng"
                    ]
                }
            )
        return [slot for slot in required_slots if not tracker.get_slot(slot)]

    def validate_user_age(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        try:
            age = int(slot_value)
            if 18 <= age <= 100:
                return {"user_age": slot_value}
            dispatcher.utter_message(
                json_message={
                    "type": "validation_error",
                    "field": "user_age",
                    "message": "Tuổi phải từ 18 đến 100"
                }
            )
            return {"user_age": None}
        except ValueError:
            dispatcher.utter_message(
                json_message={
                    "type": "validation_error",
                    "field": "user_age",
                    "message": "Vui lòng nhập số tuổi hợp lệ"
                }
            )
            return {"user_age": None}

    def validate_user_marital_status(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        valid_statuses = ["độc thân", "đã có gia đình", "đã kết hôn và có con", "chưa lập gia đình"]
        if slot_value.lower() in valid_statuses:
            return {"user_marital_status": slot_value.lower()}
        dispatcher.utter_message(
            json_message={
                "type": "validation_error",
                "field": "user_marital_status",
                "message": "Vui lòng chọn một trong các trạng thái: độc thân, đã có gia đình, đã kết hôn và có con",
                "valid_options": valid_statuses
            }
        )
        return {"user_marital_status": None}

    def validate_user_income(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        try:
            income = float(slot_value)
            if 5 <= income <= 100:
                return {"user_income": slot_value}
            dispatcher.utter_message(
                json_message={
                    "type": "validation_error",
                    "field": "user_income",
                    "message": "Thu nhập phải từ 5 đến 100 triệu/tháng",
                    "range": {"min": 5, "max": 100}
                }
            )
            return {"user_income": None}
        except ValueError:
            dispatcher.utter_message(
                json_message={
                    "type": "validation_error",
                    "field": "user_income",
                    "message": "Vui lòng nhập số thu nhập hợp lệ"
                }
            )
            return {"user_income": None}

class ValidateHouseDetails(FormValidationAction):
    def name(self) -> Text:
        return "validate_house_details"

    def validate_desired_size(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        try:
            size = float(slot_value)
            return {"desired_size": size}
        except ValueError:
            return {"desired_size": None} 