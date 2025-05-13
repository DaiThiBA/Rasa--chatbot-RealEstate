from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionInitialGreeting(Action):
    def name(self) -> Text:
        return "action_initial_greeting"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(
            custom={
                "type": "greeting",
                "message": "Xin chào! Để tư vấn bất động sản phù hợp nhất, anh/chị vui lòng cung cấp các thông tin sau:",
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
        return [] 