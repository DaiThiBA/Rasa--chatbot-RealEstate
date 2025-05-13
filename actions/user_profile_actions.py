from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
from .evaluators.customer_segments import CustomerSegments
from .user_profiler import UserProfiler
import logging

logger = logging.getLogger(__name__)

class ActionProcessMultipleInfo(Action):
    def name(self) -> Text:
        return "action_process_multiple_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Lấy message cuối cùng của user
        latest_message = tracker.latest_message.get('text', '')
        
        if not latest_message:
            return []

        try:
            # Trích xuất thông tin từ message
            info = self.extract_info(latest_message)
            if not info:
                return []

            # Set các slots
            return [
                SlotSet("user_name", info['name']),
                SlotSet("user_age", info['age']),
                SlotSet("user_marital_status", info['marital_status']),
                SlotSet("user_income", info['income'])
            ]
            
        except Exception as e:
            dispatcher.utter_message(text=f"Xin lỗi, có lỗi xảy ra khi xử lý thông tin: {str(e)}")
            return []

    def extract_info(self, text: Text) -> Dict[Text, Any]:
        """Trích xuất thông tin từ text"""
        import re
        
        # Tìm tên - cải thiện pattern
        name_patterns = [
            r'tên (?:là |)(\w+)',
            r'tôi (?:là |tên |)(\w+)',
            r'(?:tên |)(\w+)(?=,| \d+| tuổi)',
        ]
        
        name = None
        for pattern in name_patterns:
            name_match = re.search(pattern, text.lower())
            if name_match:
                name = name_match.group(1)
                break

        # Tìm tuổi - cải thiện pattern
        age_match = re.search(r'(\d+)(?:\s+|)(?:tuổi|t)', text.lower())
        age = age_match.group(1) if age_match else None

        # Tìm thu nhập - cải thiện pattern
        income_patterns = [
            r'thu nhập[^\d]*(\d+)',
            r'lương[^\d]*(\d+)',
            r'(\d+)[^\d]*(?:triệu|tr)',
        ]
        
        income = None
        for pattern in income_patterns:
            income_match = re.search(pattern, text.lower())
            if income_match:
                income = income_match.group(1)
                break

        # Xác định tình trạng hôn nhân - cải thiện logic
        marital_status = "độc thân"  # mặc định
        text_lower = text.lower()
        
        if "có con" in text_lower:
            marital_status = "đã kết hôn và có con"
        elif any(status in text_lower for status in ["gia đình", "kết hôn", "lập gia đình"]):
            if "chưa có con" in text_lower:
                marital_status = "đã có gia đình"
            else:
                marital_status = "đã có gia đình"

        # Kiểm tra xem có đủ thông tin không
        if all([name, age, income, marital_status]):
            return {
                'name': name.capitalize(),
                'age': age,
                'marital_status': marital_status,
                'income': income
            }
        
        return None

class ActionProcessUserProfile(Action):
    def name(self) -> Text:
        return "action_process_user_profile"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        logger.info("\n=== ActionProcessUserProfile Started ===")
        
        # Lấy slots hiện tại
        current_slots = {
            'user_name': tracker.get_slot('user_name'),
            'user_age': tracker.get_slot('user_age'), 
            'user_marital_status': tracker.get_slot('user_marital_status'),
            'user_income': tracker.get_slot('user_income'),
            'customer_cluster': tracker.get_slot('customer_cluster')
        }
        
        logger.info(f"Current slots: {current_slots}")

        # Chỉ xử lý nếu thiếu thông tin
        events = []
        if not all(current_slots.values()):
            # Lấy thông tin từ message cuối
            latest_message = tracker.latest_message
            entities = latest_message.get('entities', [])
            
            # Cập nhật slots từ entities mới
            for entity in entities:
                entity_type = entity['entity']
                entity_value = entity['value']
                
                if entity_type in ['user_name', 'user_age', 'user_marital_status', 'user_income']:
                    if not current_slots[entity_type]:  # Chỉ set nếu slot đang trống
                        events.append(SlotSet(entity_type, entity_value))
                        logger.info(f"Set {entity_type}: {entity_value}")

            # Xác định cluster nếu đủ thông tin
            if not current_slots['customer_cluster']:
                cluster = self.determine_customer_cluster(tracker)
                if cluster >= 0:
                    events.append(SlotSet('customer_cluster', cluster))
                    logger.info(f"Set customer_cluster: {cluster}")
                    # Lấy và hiển thị mô tả nhóm khách hàng
                    cluster_description = CustomerSegments.get_cluster_description(cluster)
                    dispatcher.utter_message(
                        text=f"Dựa trên thông tin của bạn, chúng tôi xác định:\n{cluster_description}\n\n")

        # Log kết quả cuối
        logger.info(f"Generated events: {events}")
        return events

    def determine_customer_cluster(self, tracker) -> int:
        """Xác định nhóm khách hàng dựa trên thông tin cá nhân"""
        
        logger.info("\n=== Determining Customer Cluster ===")
        
        # Lấy thông tin từ slots
        user_info = {
            'name': tracker.get_slot('user_name'),
            'age': tracker.get_slot('user_age'),
            'marital_status': tracker.get_slot('user_marital_status'),
            'income': tracker.get_slot('user_income')
        }
        
        logger.info(f"User info from slots: {user_info}")

        # Kiểm tra đủ thông tin cần thiết
        if not all([user_info['age'], user_info['marital_status'], user_info['income']]):
            logger.warning("Missing required user info for clustering")
            return 0

        try:
            # Chuyển đổi age và income sang số
            age = int(user_info['age'])
            income = float(user_info['income'])
            marital_status = user_info['marital_status'].lower()
            
            logger.info(f"Processed values - Age: {age}, Income: {income}, Status: {marital_status}")

            # Sử dụng UserProfiler để xác định nhóm
            age_group = UserProfiler.get_age_group(age)
            marital_status_code = UserProfiler.get_marital_status_code(marital_status)
            income_group = UserProfiler.get_income_group(income)
            
            # Xác định cluster dựa trên các nhóm
            cluster = UserProfiler.determine_cluster(age_group, marital_status_code, income_group)
            logger.info(f"Determined cluster {cluster} from: age_group={age_group}, "
                       f"marital_status={marital_status_code}, income_group={income_group}")
            
            return cluster

        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Error in determine_customer_cluster: {str(e)}")
            logger.error(f"User info that caused error: {user_info}")
            return 0