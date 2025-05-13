from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import logging

logger = logging.getLogger(__name__)

from .form_validation import ValidateUserProfileForm
from .user_profile_actions import ActionProcessMultipleInfo, ActionProcessUserProfile
from .queries.real_estate_query import RealEstateQueries, build_location_query
from .utils.sparql_utils import fetch_data, RealEstateDataProcessor
from .evaluators.property_evaluator import PropertyEvaluator
from .evaluators.location_evaluator import LocationEvaluator
from .evaluators.financial_evaluator import FinancialEvaluator
from .evaluators.customer_segments import CustomerSegments
from .initial_greeting import ActionInitialGreeting
from .forms import ValidateLocationForm
from .house_details_action import ActionAskHouseDetails
from .location_actions import ActionAskRegionName, ActionAskAreaName, ActionAskWardName, ActionProcessLocation
from .house_requirements_action import ActionProcessHouseRequirements

# Tái xuất các class để Rasa có thể tìm thấy
ActionInitialGreeting = ActionInitialGreeting
ValidateUserProfileForm = ValidateUserProfileForm
ActionProcessMultipleInfo = ActionProcessMultipleInfo
ActionProcessUserProfile = ActionProcessUserProfile
PropertyEvaluator = PropertyEvaluator
LocationEvaluator = LocationEvaluator
FinancialEvaluator = FinancialEvaluator
CustomerSegments = CustomerSegments

#TODO:  Đã Đọc hiểu
# Xem lại thuộc tính nào để chấm điểm, thuộc tính nào để bỏ vào trong query
class ActionSearchRealEstate(Action):
    def name(self) -> Text:
        return "action_search_real_estate"

    def run(self, dispatcher, tracker, domain):
        try:
            # Get parameters
            logger.info("Getting search parameters...")
            user_lat = tracker.get_slot("work_latitude") or "10.848"
            user_lon = tracker.get_slot("work_longitude") or "106.787"
            customer_cluster = int(tracker.get_slot("customer_cluster") or "0")
            cluster_weights = CustomerSegments.get_cluster_weights(customer_cluster)
            price_range = CustomerSegments.get_price_range(customer_cluster)
            
            # Lấy khoảng giá từ price_range
            min_price_per_m2 = price_range[0] if price_range else 30
            max_price_per_m2 = price_range[1] if price_range else 50
            logger.info(f"Price range for cluster {customer_cluster}: {min_price_per_m2} - {max_price_per_m2}")

            # Add desired values
            desired_values = {
                'size': float(tracker.get_slot("desired_size") or "80"),
                'rooms': int(tracker.get_slot("desired_rooms") or "2"),
                'toilets': int(tracker.get_slot("desired_toilets") or "2")
            }

            # Get location info
            location = {
                'region_name': tracker.get_slot("region_name"),
                'area_name': tracker.get_slot("area_name"),
                'ward_name': tracker.get_slot("ward_name")
            }
            
            # Create query and execute
            endpoint_url = "http://localhost:3030/NhaTot_realestate/sparql"
            query = RealEstateQueries.get_real_estate_query(
                price_range=price_range,
                desired_size=desired_values['size'],
                location=location
            )
            results = fetch_data(endpoint_url, query)
            
            # Debug logging
            logger.info("\n=== QUERY RESULTS ===")
            logger.info(f"Number of results: {len(results['results']['bindings'])}")
            if results['results']['bindings']:
                logger.info("Sample result:")
                logger.info(results['results']['bindings'][0])
            else:
                logger.info("No results found!")

            recommendations = []
            for result in results["results"]["bindings"]:
                # Calculate scores from raw result first
                feature_score, feature_reasons = PropertyEvaluator.calculate_property_features_score(
                    result, desired_values)
                location_score, location_reasons = LocationEvaluator.calculate_location_score(
                    result, user_lat, user_lon)
                # Khởi tạo FinancialEvaluator với khoảng giá phù hợp
                financial_evaluator = FinancialEvaluator(min_price_per_m2, max_price_per_m2)
                financial_score, financial_reasons = financial_evaluator.calculate_financial_score(result)

                # Calculate weighted total score
                total_score = (
                    feature_score * cluster_weights['features_weight'] +
                    location_score * cluster_weights['location_weight'] + 
                    financial_score * cluster_weights['finance_weight']
                )

                # Then process the result
                processed_result = RealEstateDataProcessor.process_single_result(result)
                processed_result.update({
                    'total_score': total_score,
                    'feature_reasons': feature_reasons,
                    'location_reasons': location_reasons, 
                    'financial_reasons': financial_reasons
                })
                recommendations.append(processed_result)

            # Sắp xếp theo điểm số và trả về kết quả
            recommendations.sort(key=lambda x: x['total_score'], reverse=True)
            dispatcher.utter_message(
                custom={
                    "type": "real_estate_recommendations",
                    "recommendations": recommendations[:5]  # Chỉ lấy top 5
                }
            )
            return []

        except Exception as e:
            logger.error(f"Error in ActionSearchRealEstate: {str(e)}")
            logger.error(f"Traceback: ", exc_info=True)
            dispatcher.utter_message(
                custom={
                    "error": f"Lỗi khi tìm kiếm bất động sản: {str(e)}"
                }
            )
            return []

    # Dùng để giép địa chỉ thành một chuỗi
    def _format_location(self, result: Dict) -> str:
        """Format địa chỉ từ các thành phần."""
        components = []
        
        ward = result.get('ward_name', {}).get('value')
        if ward:
            components.append(ward)
            
        area = result.get('area_name', {}).get('value')
        if area:
            components.append(area)
            
        region = result.get('region_name', {}).get('value')
        if region:
            components.append(region)
            
        return ", ".join(components)
#TODO:  Đã Đọc hiểu
class ActionProcessLocation(Action):
    def name(self) -> Text:
        return "action_process_location"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        region = tracker.get_slot("region_name")
        area = tracker.get_slot("area_name") 
        ward = tracker.get_slot("ward_name")

        # Xây dựng message phản hồi
        location_msg = f"Bạn muốn tìm kiếm tại: {region}"
        if area:
            location_msg += f", {area}"
        if ward:
            location_msg += f", {ward}"

        dispatcher.utter_message(text=location_msg)
        
        # Tiếp tục flow tìm kiếm BĐS với thông tin địa điểm đã có
        return []

#TODO:  Đã Đọc hiểu
class ActionDebugSearchInfo(Action):
    def name(self) -> Text:
        return "action_debug_search_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            # Lấy thông tin người dùng
            customer_cluster = tracker.get_slot("customer_cluster")
            price_range = CustomerSegments.get_price_range(int(customer_cluster))

            # Lấy thông tin vị trí
            location = {
                'region_name': tracker.get_slot("region_name"),
                'area_name': tracker.get_slot("area_name"),
                'ward_name': tracker.get_slot("ward_name")
            }

            # Lấy thông tin nhà
            house_info = {
                'desired_size': tracker.get_slot("desired_size"),
                'desired_rooms': tracker.get_slot("desired_rooms"),
                'desired_toilets': tracker.get_slot("desired_toilets")
            }

            # Hiển thị thông tin debug
            dispatcher.utter_message(
                custom={
                    "type": "debug_info",
                    "search_parameters": {
                        "customer_info": {
                            "cluster": customer_cluster,
                            "price_range": f"{price_range[0]}-{price_range[1]} triệu/m2"
                        },
                        "location": location,
                        "house_requirements": house_info
                    }
                }
            )
            return []

        except Exception as e:
            dispatcher.utter_message(text=f"Lỗi khi hiển thị thông tin debug: {str(e)}")
            return []

# Đảm bảo Rasa có thể tìm thấy tất cả các actions
__all__ = [
    'ActionInitialGreeting',
    'ValidateUserProfileForm',
    'ValidateLocationForm',
    'ActionProcessMultipleInfo',
    'ActionProcessUserProfile',
    'ActionSearchRealEstate',
    'ActionGetLocationList',
    'ActionProcessLocation',
    'ActionDebugSearchInfo',
    'ActionAskHouseDetails',
    'ActionAskRegionName',
    'ActionAskAreaName',
    'ActionAskWardName',
    'ActionProcessHouseRequirements'
]


# 2.2. actions/user_profile_actions.py
# Xử lý thông tin profile người dùng với các class chính:
# ActionProcessMultipleInfo
# Xử lý nhiều thông tin cùng lúc từ tin nhắn người dùng
# Trích xuất: tên, tuổi, thu nhập, tình trạng hôn nhân
# Phân loại khách hàng theo nhóm
# CustomerSegments
# Phân loại khách hàng thành 3 nhóm:
# high_end (>= 50tr)
# mid_range (>= 20tr)
# budget (< 20tr)
# ActionProcessUserProfile
# Xử lý profile và đưa ra gợi ý phù hợp
# Chuyển người dùng đến bước hỏi nhu cầu nhà ở
# 2.3. actions/data/locations.py & locations.json
# Quản lý dữ liệu về các địa điểm
# Cung cấp thông tin về:
# Quận/huyện
# Phường/xã
# Các khu vực lân cận
# 2.4. actions/form_validation.py
# Kiểm tra tính hợp lệ của dữ liệu trong forms
# Xử lý các trường hợp đặc biệt
# Định dạng dữ liệu theo yêu cầu
# 2.5. actions/initial_greeting.py
# Xử lý chào hỏi ban đầu
# Thiết lập context cho cuộc hội thoại
# Thu thập thông tin cơ bản