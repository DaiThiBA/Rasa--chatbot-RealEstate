from math import radians, sin, cos, sqrt, atan2

class LocationEvaluator:
    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """Tính khoảng cách giữa 2 điểm dựa trên tọa độ (theo km)"""
        R = 6371  # Bán kính trái đất (km)
        
        lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c
        
        return distance

    @staticmethod
    def calculate_location_score(property_data, user_lat, user_lon):
        score = 0
        reasons = []
        
        # # 1. Đánh giá khoảng cách (40%)
        # try:
        #     # Lấy tọa độ từ trường geo
        #     geo = property_data.get('geo', {}).get('value', '')
        #     if geo:
        #         property_lat, property_lon = map(float, geo.split(','))
                
        #         distance = LocationEvaluator.calculate_distance(
        #             float(user_lat), float(user_lon),
        #             property_lat, property_lon
        #         )
                
        #         if distance <= 1:
        #             score += 0.4
        #             reasons.append("📍 Rất gần vị trí mong muốn (dưới 1km)")
        #         elif distance <= 3:
        #             score += 0.3
        #             reasons.append("📍 Khá gần vị trí mong muốn (dưới 3km)")
        #         elif distance <= 5:
        #             score += 0.2
        #             reasons.append("📍 Gần vị trí mong muốn (dưới 5km)")
        #         else:
        #             score += 0.1
        #             reasons.append(f"📍 Cách vị trí mong muốn {distance:.1f}km")
        # except:
        #     reasons.append("❌ Không có thông tin vị trí")

        # 2. Đánh giá tiện ích nội khu (30%)
        facilities = property_data.get('facilities', {}).get('value', '[]')
        try:
            facility_list = eval(facilities)
            if facility_list:
                facility_score = min(len(facility_list) * 0.1, 0.3)
                score += facility_score
                facility_text = ", ".join(facility_list)
                reasons.append(f"🏢 Tiện ích nội khu: {facility_text}")
        except:
            reasons.append("❌ Không có thông tin tiện ích nội khu")

        # 3. Đánh giá tiện ích xung quanh (30%) 
        surroundings = property_data.get('surroundings', {}).get('value', '[]')
        try:
            surrounding_list = eval(surroundings)
            if surrounding_list:
                surrounding_score = min(len(surrounding_list) * 0.1, 0.3)
                score += surrounding_score
                surrounding_text = ", ".join(surrounding_list)
                reasons.append(f"🌳 Tiện ích lân cận: {surrounding_text}")
        except:
            reasons.append("❌ Không có thông tin tiện ích lân cận")

        return score, reasons