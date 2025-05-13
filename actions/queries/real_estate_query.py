import logging
logger = logging.getLogger(__name__)

class RealEstateQueries:
    @staticmethod
    def get_real_estate_query(price_range=None, desired_size=None, location=None):
        base_query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX : <https://raw.githubusercontent.com/DaiThiBA/dataOWL/refs/heads/main/updated_real_estate_ontology_V3.rdf#>

        SELECT DISTINCT ?project_id ?project_name ?short_introduction ?process ?type_name ?web_url ?geo 
                ?region_name ?area_name ?ward_name ?street_name
                ?investor_name
                ?facilities ?surroundings
                ?real_estate_id ?category_name ?subject ?body ?price ?size ?rooms ?toilets ?price_million_per_m2
                ?seller_name ?seller_avatar
                ?images ?thumbnail_image
                ?support ?payment_method ?interest ?discount ?profit_commitment ?gifts ?policy_details
        WHERE {
            # Project details
            ?project rdf:type :Project ;
                     :projectid ?project_id ;
                     :project_name ?project_name ;
                     :short_introduction ?short_introduction ;
                     :process ?process ;
                     :type_name ?type_name ;
                     :web_url ?web_url ;
                     :geo ?geo ;
                     :located_at ?location ;
                     :has_investor ?investor ;
                     :has_amenities ?amenities .

            # Location details
            ?location rdf:type :Location ;
                      :region_name ?region_name ;
                      :area_name ?area_name ;
                      :ward_name ?ward_name ;
                      :street_name ?street_name .

            # Investor details  
            ?investor rdf:type :Investor ;
                      :investor_name ?investor_name .

            # Amenities details
            ?amenities rdf:type :Amenities .
            OPTIONAL { ?amenities :facilities ?facilities }
            OPTIONAL { ?amenities :surroundings ?surroundings }

            # Real estate details
            OPTIONAL {
                ?real_estate rdf:type :RealEstate ;
                             :belongs_to_project ?project ;
                             :real_estate_id ?real_estate_id ;
                             :category_name ?category_name ;
                             :subject ?subject ;
                             :body ?body ;
                             :price ?price ;
                             :size ?size ;
                             :rooms ?rooms ;
                             :toilets ?toilets ;
                             :price_million_per_m2 ?price_million_per_m2 ;
                             :has_seller ?seller ;
                             :has_media ?media .

                # Seller details
                ?seller rdf:type :Seller ;
                        :account_name ?seller_name ;
                        :avatar ?seller_avatar .

                # Media details
                ?media rdf:type :Media ;
                       :images ?images ;
                       :thumbnail_image ?thumbnail_image .
            }

            # Financial policy details
            OPTIONAL {
                ?project :has_financial_policy ?financial_policy .
                OPTIONAL { ?financial_policy :support ?support }
                OPTIONAL { ?financial_policy :payment_method ?payment_method }
                OPTIONAL { ?financial_policy :interest ?interest }
                OPTIONAL { ?financial_policy :discount ?discount }
                OPTIONAL { ?financial_policy :profit_commitment ?profit_commitment }
                OPTIONAL { ?financial_policy :gifts ?gifts }
                OPTIONAL { ?financial_policy :policy_details ?policy_details }
            }

            # Filters
            %s

            FILTER(
                !BOUND(?size) 
                || (ABS(?size - %f) <= 20)
            )
        }
        ORDER BY ?size
        """
        
        # Build location filters
        filters = []
        if location:
            if location.get('region_name'):
                filters.append(f'FILTER(CONTAINS(LCASE(STR(?region_name)), "{location["region_name"].lower()}"))')
            if location.get('area_name'):
                filters.append(f'FILTER(CONTAINS(LCASE(STR(?area_name)), "{location["area_name"].lower()}"))')
            if location.get('ward_name'):
                filters.append(f'FILTER(CONTAINS(LCASE(STR(?ward_name)), "{location["ward_name"].lower()}"))')
        
        location_filter = "\n            ".join(filters)
        
        # Điền giá trị vào query
        min_price = price_range[0] if price_range else 0
        max_price = price_range[1] if price_range else 1000
        target_size = desired_size if desired_size else 80
        
        # Build query with parameters
        final_query = base_query % (location_filter, target_size)
        
        # Log the final query
        logger.info("\n=== SPARQL QUERY ===")
        logger.info(final_query)
        
        return final_query

def build_location_query(location_info):
    location_filters = []
    
    if location_info.get('region_name'):
        region = location_info['region_name'].lower()
        location_filters.append(f'FILTER(CONTAINS(LCASE(STR(?region_name)), "{region}"))')
    
    if location_info.get('area_name'):
        area = location_info['area_name'].lower()
        location_filters.append(f'FILTER(CONTAINS(LCASE(STR(?area_name)), "{area}"))')
    
    return "\n            ".join(location_filters) 