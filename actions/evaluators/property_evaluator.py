class PropertyEvaluator:
    @staticmethod
    def calculate_property_features_score(property_data, requirements):
        """Tính điểm cho các tính năng của bất động sản"""
        score = 0
        reasons = []
        
        # Đánh giá diện tích
        try:
            # Lấy size từ raw data
            size = float(property_data.get('size', {}).get('value', 0))
            target_size = float(requirements['size'])
            
            size_diff = abs(size - target_size)
            if size_diff <= 10:
                score += 0.4
                reasons.append(f"📐 Diện tích {size}m² (rất phù hợp)")
            elif size_diff <= 20:
                score += 0.3
                reasons.append(f"📐 Diện tích {size}m² (khá phù hợp)")
            else:
                score += 0.1
                reasons.append(f"📐 Diện tích {size}m² (chấp nhận được)")
                
        except (ValueError, TypeError):
            reasons.append("❌ Không có thông tin diện tích")
            
        # Đánh giá số phòng ngủ
        try:
            # Lấy rooms từ raw data
            rooms = int(float(property_data.get('rooms', {}).get('value', 0)))
            target_rooms = int(requirements['rooms'])
            
            if rooms == target_rooms:
                score += 0.3
                reasons.append(f"🛏️ {rooms} phòng ngủ (hoàn hảo)")
            else:
                score += 0.1
                reasons.append(f"🛏️ {rooms} phòng ngủ (chấp nhận được)")
                
        except (ValueError, TypeError):
            reasons.append("❌ Không có thông tin số phòng ngủ")
            
        # Đánh giá số toilet
        try:
            # Lấy toilets từ raw data
            toilets = int(float(property_data.get('toilets', {}).get('value', 0)))
            target_toilets = int(requirements['toilets'])
            
            if toilets >= target_toilets:
                score += 0.3
                reasons.append(f"🚽 {toilets} phòng vệ sinh (tốt)")
            else:
                score += 0.1
                reasons.append(f"🚽 {toilets} phòng vệ sinh (chấp nhận được)")
                
        except (ValueError, TypeError):
            reasons.append("❌ Không có thông tin số phòng vệ sinh")
            
        return score, reasons