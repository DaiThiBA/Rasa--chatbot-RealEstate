class CustomerSegments:
    @staticmethod
    def get_cluster_weights(cluster):
        """Trả về trọng số đánh giá cho từng nhóm khách hàng dựa trên phân tích dữ liệu
        
        Trọng số được tính toán từ dữ liệu thực tế:
        Cluster    VT(Vị trí)  MT(Môi trường)  TC(Tài chính)  ĐNN(Đặc điểm nhà)
        0         76.90        89.07           91.30          75.33
        1         84.56        87.45           85.00          80.98
        2         75.28        91.85           86.39          75.56
        3         82.19        86.67           78.13          82.92
        4         71.88        93.33           71.25          66.25
        5         65.31        81.94           87.19          82.64
        """
        weights = {
            # Cluster 0: "Gia đình trẻ ổn định" (27.47%)
            0: {
                'location_weight': 0.2309,     # 76.90/332.60
                'environment_weight': 0.2678,   # 89.07/332.60
                'finance_weight': 0.2745,      # 91.30/332.60 (Tài chính)
                'features_weight': 0.2268       # 75.33/332.60
            },
            # Cluster 1: "Gia đình trung niên khá giả" (18.68%)
            1: {
                'location_weight': 0.2498,     # 84.56/338.00
                'environment_weight': 0.2587,   # 87.45/338.00
                'finance_weight': 0.2515,      # 85.00/338.00
                'features_weight': 0.2400       # 80.98/338.00
            },
            # Cluster 2: "Độc thân thu nhập thấp" (9.89%)
            2: {
                'location_weight': 0.2289,     # 75.28/329.07
                'environment_weight': 0.2791,   # 91.85/329.07
                'finance_weight': 0.2626,      # 86.39/329.07
                'features_weight': 0.2294       # 75.56/329.07
            },
            # Cluster 3: "Gia đình giàu có" (8.79%)
            3: {
                'location_weight': 0.2498,     # 82.19/329.89
                'environment_weight': 0.2627,   # 86.67/329.89
                'finance_weight': 0.2368,      # 78.13/329.89
                'features_weight': 0.2507       # 82.92/329.89
            },
            # Cluster 4: "Gia đình trẻ thu nhập thấp" (8.79%)
            4: {
                'location_weight': 0.2373,     # 71.88/302.71
                'environment_weight': 0.3083,   # 93.33/302.71
                'finance_weight': 0.2354,      # 71.25/302.71
                'features_weight': 0.2190       # 66.25/302.71
            },
            # Cluster 5: "Độc thân trẻ có tích lũy" (26.37%)
            5: {
                'location_weight': 0.2062,     # 65.31/317.08
                'environment_weight': 0.2585,   # 81.94/317.08
                'finance_weight': 0.2750,      # 87.19/317.08
                'features_weight': 0.2603       # 82.64/317.08
            }
        }
        return weights.get(cluster, weights[0])

    @staticmethod
    def get_price_range(cluster):
        """Trả về khoảng giá phù hợp cho từng nhóm (triệu/m2)"""
        ranges = {
            0: (9, 14),     # Gia đình trẻ ổn định
            1: (15, 20),    # Gia đình trung niên khá giả
            2: (5, 8),      # Độc thân thu nhập thấp
            3: (33, 38),    # Gia đình giàu có
            4: (5, 8),      # Gia đình trẻ thu nhập thấp
            5: (5, 8)       # Độc thân trẻ có tích lũy
        }
        return ranges.get(cluster, ranges[0])

    @staticmethod
    def get_cluster_description(cluster):
        """Trả về mô tả cho từng nhóm khách hàng"""
        descriptions = {
            0: "👤‍👩‍👦 Nhóm gia đình trẻ ổn định (27.47%)\n- Đã lập gia đình, chưa có con\n- Độ tuổi 36-45\n- Thu nhập 36-45 triệu/tháng\n- Quan tâm đến tài chính và môi trường sống",
            1: "👨‍👩‍👧‍👦 Nhóm gia đình trung niên khá giả (18.68%)\n- Đã lập gia đình, có con\n- Độ tuổi 46-55\n- Thu nhập 36-45 triệu/tháng\n- Cân bằng các yếu tố",
            2: "👤 Nhóm độc thân thu nhập thấp (9.89%)\n- Độc thân\n- Tuổi dưới 25\n- Thu nhập 5-15 triệu/tháng\n- Ưu tiên môi trường và tài chính",
            3: "💎 Nhóm gia đình giàu có (8.79%)\n- Đã lập gia đình, có con\n- Độ tuổi 36-45\n- Thu nhập 46-70 triệu/tháng\n- Cân bằng các yếu tố cao cấp",
            4: "👨‍👩‍👦‍👦 Nhóm gia đình trẻ thu nhập thấp (8.79%)\n- Đã lập gia đình, có con\n- Độ tuổi 46-55\n- Thu nhập 5-15 triệu/tháng\n- Ưu tiên môi trường sống",
            5: "💼 Nhóm độc thân trẻ có tích lũy (26.37%)\n- Độc thân\n- Độ tuổi 26-35\n- Thu nhập 26-35 triệu/tháng\n- Ưu tiên tài chính và đặc điểm nhà"
        }
        return descriptions.get(cluster, descriptions[0])

    @staticmethod
    def identify_cluster(user_info):
        """Xác định phân khúc khách hàng dựa trên thông tin cá nhân"""
        age = int(user_info.get('age', 0))
        income = int(user_info.get('income', 0))
        marital_status = user_info.get('marital_status', '').lower()

        # Logic phân nhóm theo 6 phân khúc
        if "có con" in marital_status:
            if income >= 46:
                return {
                    'id': 3,
                    'description': CustomerSegments.get_cluster_description(3)
                }  # Gia đình giàu có
            elif 36 <= income <= 45:
                return {
                    'id': 1,
                    'description': CustomerSegments.get_cluster_description(1)
                }  # Gia đình trung niên khá giả
            else:
                return {
                    'id': 4,
                    'description': CustomerSegments.get_cluster_description(4)
                }  # Gia đình trẻ thu nhập thấp
        elif "độc thân" in marital_status:
            if age <= 25:
                return {
                    'id': 2,
                    'description': CustomerSegments.get_cluster_description(2)
                }  # Độc thân thu nhập thấp
            else:
                return {
                    'id': 5,
                    'description': CustomerSegments.get_cluster_description(5)
                }  # Độc thân trẻ có tích lũy
        else:
            return {
                'id': 0,
                'description': CustomerSegments.get_cluster_description(0)
            }  # Gia đình trẻ ổn định