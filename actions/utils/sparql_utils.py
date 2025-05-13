from SPARQLWrapper import SPARQLWrapper, JSON
from typing import Dict, List

def fetch_data(endpoint_url, query):
    sparql = SPARQLWrapper(endpoint_url)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

class RealEstateDataProcessor:
    @staticmethod
    def process_results(results: Dict) -> List[Dict]:
        """Xử lý kết quả từ SPARQL query thành format phù hợp."""
        processed_results = []
        
        for result in results["results"]["bindings"]:
            processed_result = {
                'real_estate_id': result.get('real_estate_id', {}).get('value'),
                'project_name': result.get('project_name', {}).get('value'),
                'type': result.get('category_name', {}).get('value', 'N/A'),
                'location': RealEstateDataProcessor._format_location(result),
                'price': result.get('price', {}).get('value'),
                'rooms': result.get('rooms', {}).get('value'),
                'size': result.get('size', {}).get('value'),
                'toilets': result.get('toilets', {}).get('value'),
                'price_per_m2': result.get('price_million_per_m2', {}).get('value'),
                'thumbnail_image': result.get('thumbnail_image', {}).get('value', ''),
                'support': result.get('support', {}).get('value'),
                'bank_name': result.get('bank_name', {}).get('value'),
                'payment_method': result.get('payment_method', {}).get('value'),
                'interest': result.get('interest', {}).get('value'),
                'discount': result.get('discount', {}).get('value'),
                'profit_commitment': result.get('profit_commitment', {}).get('value'),
                'gifts': result.get('gifts', {}).get('value'),
                'policy_details': result.get('policy_details', {}).get('value')
            }
            processed_results.append(processed_result)
            
        return processed_results

    @staticmethod
    def _format_location(result: Dict) -> str:
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

    @staticmethod
    def process_single_result(result: Dict) -> Dict:
        """Xử lý một kết quả đơn lẻ."""
        return {
            'real_estate_id': result.get('real_estate_id', {}).get('value'),
            'project_name': result.get('project_name', {}).get('value'),
            'type': result.get('category_name', {}).get('value', 'N/A'),
            'location': RealEstateDataProcessor._format_location(result),
            'price': result.get('price', {}).get('value'),
            'rooms': result.get('rooms', {}).get('value'),
            'size': result.get('size', {}).get('value'),
            'toilets': result.get('toilets', {}).get('value'),
            'price_per_m2': result.get('price_million_per_m2', {}).get('value'),
            'thumbnail_image': result.get('thumbnail_image', {}).get('value', ''),
            'total_score': 0,
            'feature_reasons': [],
            'location_reasons': [],
            'financial_reasons': []
        } 