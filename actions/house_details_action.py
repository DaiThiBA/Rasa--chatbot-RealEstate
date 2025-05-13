from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import FollowupAction, SlotSet
import logging
import re

# Tạo logger
logger = logging.getLogger(__name__)

class ActionAskHouseDetails(Action):
    def name(self) -> Text:
        return "action_ask_house_details"

    def extract_house_info(self, text: Text, entities: List[Dict]) -> Dict:
        info = {}
        
        # Debug log
        logger.info(f"Raw text: {text}")
        logger.info(f"All entities: {entities}")
        
        if entities:
            for entity in entities:
                entity_type = entity['entity']
                entity_value = entity['value']
                logger.info(f"Processing entity: {entity_type} = {entity_value}")
                
                # Lấy giá trị có confidence cao nhất cho mỗi loại entity
                if entity_type not in info or entity.get('confidence_entity', 0) > info[f"{entity_type}_confidence"]:
                    if entity_type == 'desired_size':
                        info['desired_size'] = float(entity_value)
                        info['desired_size_confidence'] = entity.get('confidence_entity', 0)
                    else:
                        info[entity_type] = int(entity_value)
                        info[f"{entity_type}_confidence"] = entity.get('confidence_entity', 0)
                    logger.info(f"Extracted {entity_type}: {entity_value} from entity (confidence: {entity.get('confidence_entity', 0)})")

        return info

    def validate_slots(self, slot_values: Dict[Text, Any]) -> Dict[Text, Any]:
        """Validate slot values before setting"""
        validated = {}
        for slot_name, value in slot_values.items():
            if slot_name == "desired_size":
                try:
                    validated_value = float(value)
                    if validated_value <= 0:
                        logger.warning(f"Invalid size value: {value}")
                        continue
                    validated[slot_name] = validated_value
                except (TypeError, ValueError):
                    logger.warning(f"Cannot convert size to float: {value}")
                    continue
            else:
                # Các slot khác giữ nguyên giá trị
                validated[slot_name] = value
            
        return validated

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        logger.info("\n" + "="*50)
        logger.info("ActionAskHouseDetails Started")
        logger.info("="*50)
        
        # Log conversation state
        logger.info("\n=== Conversation State ===")
        logger.info(f"Active loop: {tracker.active_loop}")
        logger.info(f"Latest action: {tracker.latest_action_name}")
        logger.info(f"Latest message id: {tracker.latest_message.get('message_id')}")
        
        # Log current slots
        logger.info("\n=== Current Slots ===")
        for slot in tracker.slots:
            value = tracker.get_slot(slot)
            if value is not None:
                logger.info(f"Slot {slot}: {value}")
        
        # Log message details
        latest_message = tracker.latest_message
        text = latest_message.get('text', '')
        intent = tracker.get_intent_of_latest_message()
        entities = latest_message.get('entities', [])
        
        logger.info("\n=== Message Details ===")
        logger.info(f"Text: {text}")
        logger.info(f"Intent: {intent} (confidence: {latest_message.get('intent', {}).get('confidence')})")
        logger.info(f"Intent ranking:")
        for ranked_intent in latest_message.get('intent_ranking', []):
            logger.info(f"- {ranked_intent.get('name')}: {ranked_intent.get('confidence')}")
        
        logger.info("\n=== Entities ===")
        if entities:
            for entity in entities:
                logger.info(f"Entity: {entity.get('entity')}")
                logger.info(f"Value: {entity.get('value')}")
                logger.info(f"Confidence: {entity.get('confidence_entity')}")
                logger.info(f"Start: {entity.get('start')}, End: {entity.get('end')}")
                logger.info(f"Extractor: {entity.get('extractor')}")
                logger.info("---")
        else:
            logger.info("No entities found")

        # Process house info
        if intent == "provide_house_info":
            logger.info("\n=== Processing House Info ===")
            events = []
            
            # Extract thông tin kết hợp cả 2 cách
            house_info = self.extract_house_info(text, entities)
            
            # Set slots trực tiếp
            if 'desired_size' in house_info:
                size_value = float(house_info['desired_size'])
                events.append(SlotSet('desired_size', size_value))
                logger.info(f"Set desired_size: {size_value}")
            
            if 'desired_rooms' in house_info:
                rooms_value = int(house_info['desired_rooms'])
                events.append(SlotSet('desired_rooms', rooms_value))
                logger.info(f"Set desired_rooms: {rooms_value}")
            
            if 'desired_toilets' in house_info:
                toilets_value = int(house_info['desired_toilets'])
                events.append(SlotSet('desired_toilets', toilets_value))
                logger.info(f"Set desired_toilets: {toilets_value}")
            
            # Log results
            if events:
                logger.info("\n=== Events Generated ===")
                for event in events:
                    logger.info(f"Event type: {type(event).__name__}")
                    try:
                        event_data = {
                            'name': event.type_name,
                            'key': getattr(event, 'key', None),
                            'value': getattr(event, 'value', None)
                        }
                        logger.info(f"Event data: {event_data}")
                    except Exception as e:
                        logger.info(f"Event (raw): {event}")
                
                logger.info("Adding FollowupAction: action_ask_region_name")
                
                logger.info("\n=== Final Slots After Update ===")
                for slot in ['desired_size', 'desired_rooms', 'desired_toilets']:
                    logger.info(f"Slot {slot}: {tracker.get_slot(slot)}")
                
                return events + [FollowupAction("action_ask_region_name")]
            else:
                logger.info("\n=== No Valid House Info Found ===")
                logger.info("Asking user to try again")
                dispatcher.utter_message(text="Xin lỗi, tôi không hiểu rõ thông tin về nhà. Vui lòng thử lại.")
                return []

        logger.info("\n=== Action Completed ===")
        logger.info("No processing needed for current intent")
        logger.info("="*50 + "\n")
        return [] 