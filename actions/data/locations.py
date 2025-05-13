import json
import os
from typing import Dict, List, Optional

class Locations:
    def __init__(self):
        # Load locations data from JSON file
        json_path = os.path.join(os.path.dirname(__file__), 'locations.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def validate_region(self, region_name: str) -> Optional[str]:
        """Validate và chuẩn hóa tên region"""
        if not region_name:
            return None
            
        # Chuẩn hóa input
        region_name = region_name.lower().strip()
        
        # Check exact match first
        for region in self.data:
            if region.lower() == region_name:
                return region
                
        # Check partial match
        for region in self.data:
            if region_name in region.lower():
                return region
                
        return None

    def get_areas(self, region_name: str) -> List[str]:
        """Lấy danh sách area của region"""
        if region_name in self.data:
            return list(self.data[region_name].keys())
        return []

    def get_wards(self, region_name: str, area_name: str) -> List[str]:
        """Lấy danh sách ward của area"""
        if region_name in self.data and area_name in self.data[region_name]:
            return self.data[region_name][area_name]
        return []

class LocationManager:
    """
    Quản lý dữ liệu địa điểm với cấu trúc phân cấp hành chính:
    
    region_name (Tỉnh/Thành phố trực thuộc trung ương):
    - Tp Hồ Chí Minh
    - Hà Nội
    - Đà Nẵng
    - Bình Dương
    - Đồng Nai
    ...
    
    area_name (Quận/Huyện/Thành phố/Thị xã thuộc tỉnh):
    - Quận 1, Quận 2, ..., Quận 12
    - Thành phố Thủ Đức
    - Huyện Nhơn Trạch
    - Thành phố Biên Hòa
    ...
    
    ward_name (Phường/Xã/Thị trấn):
    - Phường Bến Nghé
    - Phường Tân Định
    - Xã Long Thọ
    - Thị trấn Long Thành
    ...
    
    Ví dụ cấu trúc đầy đủ:
    - Tp Hồ Chí Minh (region_name) > Quận 7 (area_name) > Phường Tân Thuận Đông (ward_name)
    - Đồng Nai (region_name) > Huyện Long Thành (area_name) > Xã Long An (ward_name)
    """
    
    def __init__(self):
        self.locations_data = self._load_location_data()
        self.formatted_locations = self._format_locations()

    def _load_location_data(self) -> Dict:
        """Load dữ liệu từ file JSON."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'locations.json')
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _format_locations(self) -> List[Dict]:
        """Format dữ liệu địa điểm thành cấu trúc phân cấp."""
        locations = {}
        
        # Xử lý từng bản ghi trong dữ liệu JSON
        for result in self.locations_data["results"]["bindings"]:
            region = result.get('region_name', {}).get('value')
            area = result.get('area_name', {}).get('value')
            ward = result.get('ward_name', {}).get('value')

            if region:
                if region not in locations:
                    locations[region] = {'areas': {}}
                
                if area:
                    if area not in locations[region]['areas']:
                        locations[region]['areas'][area] = {'wards': []}
                    
                    if ward and ward not in locations[region]['areas'][area]['wards']:
                        locations[region]['areas'][area]['wards'].append(ward)

        # Chuyển đổi thành danh sách có cấu trúc
        formatted_list = []
        for region, region_data in locations.items():
            region_item = {
                'id': f'region_{self._normalize_id(region)}',
                'type': 'region',
                'name': region,
                'areas': []
            }

            for area, area_data in region_data['areas'].items():
                area_item = {
                    'id': f'area_{self._normalize_id(area)}',
                    'type': 'area',
                    'name': area,
                    'wards': []
                }

                for ward in sorted(area_data['wards']):
                    ward_item = {
                        'id': f'ward_{self._normalize_id(ward)}',
                        'type': 'ward',
                        'name': ward
                    }
                    area_item['wards'].append(ward_item)

                region_item['areas'].append(area_item)

            formatted_list.append(region_item)

        return sorted(formatted_list, key=lambda x: x['name'])

    def _normalize_id(self, text: str) -> str:
        """Chuẩn hóa text thành id."""
        return text.lower().replace(' ', '_').replace('đ', 'd').replace('/', '_')

    def get_locations(self) -> List[Dict]:
        """Trả về danh sách địa điểm đã được format."""
        return self.formatted_locations

    def search_locations(self, query: str) -> List[Dict]:
        """Tìm kiếm địa điểm theo từ khóa."""
        query = query.lower()
        results = []
        
        for region in self.formatted_locations:
            # Tìm trong tên region
            if query in region['name'].lower():
                results.append(region)
                continue
                
            # Tìm trong areas
            matching_areas = []
            for area in region['areas']:
                if query in area['name'].lower():
                    matching_areas.append(area)
                    continue
                    
                # Tìm trong wards
                matching_wards = [
                    ward for ward in area['wards']
                    if query in ward['name'].lower()
                ]
                
                if matching_wards:
                    area_copy = area.copy()
                    area_copy['wards'] = matching_wards
                    matching_areas.append(area_copy)
            
            if matching_areas:
                region_copy = region.copy()
                region_copy['areas'] = matching_areas
                results.append(region_copy)
                
        return results 

    def get_location_examples(self) -> Dict[str, List[str]]:
        """Trả về ví dụ cho mỗi cấp hành chính."""
        return {
            'region_examples': [
                'Tp Hồ Chí Minh',
                'Hà Nội',
                'Bình Dương',
                'Đồng Nai'
            ],
            'area_examples': [
                'Quận 1',
                'Thành phố Thủ Đức',
                'Huyện Nhơn Trạch',
                'Thành phố Biên Hòa'
            ],
            'ward_examples': [
                'Phường Bến Nghé',
                'Phường Tân Định',
                'Xã Long Thọ',
                'Thị trấn Long Thành'
            ],
            'full_examples': [
                'Tp Hồ Chí Minh > Quận 7 > Phường Tân Thuận Đông',
                'Đồng Nai > Huyện Long Thành > Xã Long An',
                'Bình Dương > Thành phố Thủ Dầu Một > Phường Phú Cường'
            ]
        } 