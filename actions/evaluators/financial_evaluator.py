import logging

logger = logging.getLogger(__name__)

class FinancialEvaluator:
    def __init__(self, min_price_per_m2=None, max_price_per_m2=None):
        self.min_price_per_m2 = min_price_per_m2
        self.max_price_per_m2 = max_price_per_m2

    def calculate_financial_score(self, property_data):
        """Tính điểm cho chính sách tài chính"""
        logger.info(f"Calculating financial score for property: {property_data}")
        logger.info(f"Price range: {self.min_price_per_m2} - {self.max_price_per_m2}")
        score = 0
        reasons = []
        
        # Đánh giá giá/m2 (30%) dựa trên khoảng giá của người dùng
        price_per_m2 = property_data.get('price_million_per_m2', {}).get('value')
        if price_per_m2 and self.min_price_per_m2 and self.max_price_per_m2:
            price_per_m2 = float(price_per_m2)
            if self.min_price_per_m2 <= price_per_m2 <= self.max_price_per_m2:
                score += 0.3
                reasons.append("💰 Giá/m2 nằm trong khoảng bạn mong muốn")
            elif price_per_m2 < self.min_price_per_m2:
                score += 0.25
                reasons.append("💰 Giá/m2 thấp hơn dự kiến, có thể tiết kiệm chi phí")
            else:
                # Giá cao hơn khoảng chấp nhận được
                diff = price_per_m2 - self.max_price_per_m2
                if diff <= 10:
                    score += 0.15
                    reasons.append("💰 Giá/m2 cao hơn một chút so với mong muốn")
                else:
                    score += 0.1
                    reasons.append("💰 Giá/m2 khá cao so với khoảng bạn mong muốn")

        # Đánh giá hỗ trợ tài chính (15%)
        if property_data.get('support', {}).get('value') == 'true':
            score += 0.15
            reasons.append("💰 Có hỗ trợ vay vốn ngân hàng")
        else:
            reasons.append("❌ Không có hỗ trợ vay vốn")
        
        # Đánh giá phương thức thanh toán (15%)
        if property_data.get('payment_method', {}).get('value') == 'true':
            score += 0.15
            details = property_data.get('policy_details', {}).get('value', '')
            reasons.append(f"💳 Linh hoạt phương thức thanh toán: {details}")
        else:
            reasons.append("❌ Không có phương thức thanh toán linh hoạt")
        
        # Đánh giá ưu đãi lãi suất (20%)
        if property_data.get('interest', {}).get('value') == 'true':
            score += 0.20
            reasons.append("📊 Có ưu đãi lãi suất")
        else:
            reasons.append("❌ Không có ưu đãi lãi suất")
        
        # Đánh giá chiết khấu (15%)
        if property_data.get('discount', {}).get('value') == 'true':
            score += 0.15
            reasons.append("🏷️ Có chính sách chiết khấu")
        else:
            reasons.append("❌ Không có chính sách chiết khấu")
        
        # Đánh giá cam kết lợi nhuận (20%)
        if property_data.get('profit_commitment', {}).get('value') == 'true':
            score += 0.20
            reasons.append("📈 Có cam kết lợi nhuận")
        else:
            reasons.append("❌ Không có cam kết lợi nhuận")
        
        # Đánh giá quà tặng và ưu đãi khác (15%)
        if property_data.get('gifts', {}).get('value') == 'true':
            score += 0.15
            reasons.append("🎁 Có quà tặng kèm theo")
        else:
            reasons.append("❌ Không có quà tặng kèm theo")
        
        # Thêm chi tiết chính sách nếu có
        policy_details = property_data.get('policy_details', {}).get('value')
        if policy_details:
            reasons.append(f"📝 Chi tiết chính sách: {policy_details}")
        
        return score, reasons

    # def __init__(self, min_price_per_m2, max_price_per_m2):
    #     self.min_price_per_m2 = min_price_per_m2  
    #     self.max_price_per_m2 = max_price_per_m2

    # def evaluate(self, house):
    #     price_per_m2 = house.get('price_million_per_m2')
    #     score = 0
    #     reason = ""

        # # Đánh giá dựa trên khoảng giá phù hợp với người dùng
        # if self.min_price_per_m2 <= price_per_m2 <= self.max_price_per_m2:
        #     score += 0.30
        #     reason = "Giá/m2 có thể phù hợp với khả năng tài chính"
        # elif price_per_m2 < self.min_price_per_m2:
        #     score += 0.15  # Vẫn cộng điểm vì rẻ hơn dự kiến
        #     reason = "Giá/m2 có thể thấp hơn dự kiến, tiết kiệm chi phí"
        # else:
        #     # Giá cao hơn khoảng chấp nhận được
        #     #score += max(0, 10 - (price_per_m2 - self.max_price_per_m2)/2)
        #     reason = "Giá/m2 có thể cao hơn khoảng mong muốn"

        # return {
        #     'score': score,
        #     'reason': reason
        # }