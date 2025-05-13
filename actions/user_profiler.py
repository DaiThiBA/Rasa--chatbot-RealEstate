class UserProfiler:
    @staticmethod
    def get_age_group(age):
        """Phân nhóm tuổi
        0: <25 (Rất trẻ)
        1: 26-35 (Trẻ)
        2: 36-45 (Trung niên)
        3: 46-55 (Cao tuổi)
        4: >55 (Rất cao tuổi)
        """
        age = int(age)
        if age < 25:
            return 0
        elif 26 <= age <= 35:
            return 1
        elif 36 <= age <= 45:
            return 2
        elif 46 <= age <= 55:
            return 3
        else:
            return 4

    @staticmethod
    def get_marital_status_code(status):
        """Mã hóa tình trạng hôn nhân
        0: Độc thân
        1: Đã có gia đình (chưa có con)
        2: Đã kết hôn và có con
        """
        status = status.lower()
        if "độc thân" in status:
            return 0
        elif "có con" in status:
            return 2
        elif "gia đình" in status or "kết hôn" in status:
            return 1
        return 0

    @staticmethod
    def get_income_group(income):
        """Phân nhóm thu nhập (triệu/tháng)
        1: 5-15 (Thấp)
        2: 16-25 (Trung bình thấp)
        3: 26-35 (Trung bình)
        4: 36-45 (Khá)
        5: 46-70 (Cao)
        6: >70 (Rất cao)
        """
        # Xử lý chuỗi thu nhập, lấy số
        if isinstance(income, str):
            income = float(''.join(filter(str.isdigit, income)))
        else:
            income = float(income)

        if income <= 15:
            return 1
        elif 16 <= income <= 25:
            return 2
        elif 26 <= income <= 35:
            return 3
        elif 36 <= income <= 45:
            return 4
        elif 46 <= income <= 70:
            return 5
        else:
            return 6

    @staticmethod
    def determine_cluster(age_group, marital_status, income_group):
        """Xác định nhóm khách hàng dựa trên các đặc điểm
        0: Gia đình trẻ ổn định (26-35, đã có gia đình, thu nhập cao)
        1: Gia đình trung niên khá giả (46-55, có con, thu nhập khá)
        2: Độc thân thu nhập thấp (<25, độc thân, thu nhập thấp)
        3: Gia đình giàu có (36-45, có con, thu nhập rất cao)
        4: Gia đình trẻ thu nhập thấp (46-55, có con, thu nhập thấp)
        5: Độc thân trẻ có tích lũy (26-35, độc thân, thu nhập khá)
        """
        # Cluster 0: Gia đình trẻ ổn định
        if age_group == 1 and marital_status == 1 and income_group >= 4:
            return 0
            
        # Cluster 1: Gia đình trung niên khá giả
        if age_group == 3 and marital_status == 2 and income_group == 4:
            return 1
            
        # Cluster 2: Độc thân thu nhập thấp
        if age_group == 0 and marital_status == 0 and income_group == 1:
            return 2
            
        # Cluster 3: Gia đình giàu có
        if age_group == 2 and marital_status == 2 and income_group >= 5:
            return 3
            
        # Cluster 4: Gia đình trẻ thu nhập thấp
        if age_group == 3 and marital_status == 2 and income_group == 1:
            return 4
            
        # Cluster 5: Độc thân trẻ có tích lũy
        if age_group == 1 and marital_status == 0 and income_group == 3:
            return 5

        # Mặc định về cluster phổ biến nhất nếu không khớp điều kiện nào
        return 0 