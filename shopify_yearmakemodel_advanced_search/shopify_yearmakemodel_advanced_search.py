"""Main module."""
import requests
from enum import Enum  


class SearchConditionsEnum(Enum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    BEGINS_WITH = "begins_with"
    ENDS_WITH = "ends_with"
    CONTAINS = "contains"
    DOES_NOT_CONTAINS = "does_not_contains"
    GREATER_THAN = "greater_than"
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"
    LESS_THAN = "less_than"
    LESS_THAN_OR_EQUAL = "less_than_or_equal"


class Shopify_YMM_AS:

    DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36"

    ROUTES = {
        "GET_YMM": "/ajax/manage_ymm.php",
        "POST_YMM": "/ajax/manage_ymm.php",
        "ASSIGN_YMM": "/ajax/bulk_ymm.php",
        "GET_PROD_YMM": "/ajax/manage_ymm.php"
    }

    def __init__(
        self, domain,
        service_domain="https://www.ymmshopify.capacitywebservices.com"
    ):
        self.domain = domain
        self.service_domain = service_domain
        self.headers = {}
        
    def build_default_headers(self):
        headers = self.headers
        if not "user-agent" in headers:
            headers["user-agent"] = self.DEFAULT_USER_AGENT
        return headers
        

    def build_post_fields(self, fields):
        """ Given an array of values, 
        build the array with the data expected by the payload
        for each entry.
        """
        return [
            {
                "field_val": value,
                "tag_val": value,
                "field":"field_{}".format(i),
                "tag_field":"field_{}_tag".format(i)
            }
            for i, value in enumerate(fields, start=1) 
        ]

    def get_ymms(self):
        """ Performs a GET request to obtain all YMM entries 
        for the domain object's target domain.
        Given the correct parameters, 
        Returns an HTTP response with the JSON YMM data
        example: {"all_count":"3","total":3,"list":[{"id":"1","field_1":"1999","field_2":"Make ","field_3":"Nano"}]}
        """
        headers = self.build_default_headers()
        response = requests.get(
            f"{self.service_domain}{self.ROUTES['GET_YMM']}",
            params={
                "action": "get",
                "domain": self.domain
            },
            headers=headers
        )
        return response
    
    def search_ymms(
        self, 
        text_search,
        filter_year=True,
        filter_make=True,
        filter_model=True,
        page=1,
        search_type=SearchConditionsEnum.EQUALS
    ):
        """ Performs a POST request to obtain all YMM entries 
        for the domain object's target domain, that match a certain search criteria.
        """
        headers = self.build_default_headers()
        payload = {}
        payload["txt"] = text_search
        filter_fields = []
        if filter_year:
            filter_fields.append("field_1")
        if filter_make:
            filter_fields.append("field_2")
        if filter_model:
            filter_fields.append("field_3")
        payload["search_cond"] = search_type.value if type(search_type) == SearchConditionsEnum else search_type
        payload["page"] = page
        payload["filter_fields"] = filter_fields

        response = requests.post(
            f"{self.service_domain}{self.ROUTES['GET_YMM']}",
            params={
                "action": "get",
                "domain": self.domain
            },
            json=payload,
            headers=headers
        )
        return response

    def search_ymm(self, *args, **kwargs):
        """
        Performs a search_ymms, returns None if no results were found
        returns the id if only 1 result was found , or return the list of results
        if many are found.
        """
        response_data = self.search_ymms(*args, **kwargs).json()
        if response_data["total"] == 1:
            return response_data["list"][0]["id"]
        if response_data["total"] > 0:
            return response_data["list"]
        return None

    def get_single_ymm(self, ymm_id):
        """ Performs a GET request to obtain a single YMM entry 
        for the domain object's target domain.
        Given the correct parameters, 
        Returns an HTTP response with the JSON YMM data
        example: {"id":"18","shop_id":"49639227552",
        "product_ids":"6074816233632,6071459348640,6071459610784","field_1":"2020","field_1_tag":"yr_2020",
        "field_2":"model2","field_2_tag":"mk_model2","field_3":"make2","field_3_tag":"md_make2"}
        """
        headers = self.build_default_headers()
        response = requests.get(
            f"{self.service_domain}{self.ROUTES['GET_YMM']}",
            params={
                "action": "edit",
                "data_id": ymm_id,
                "domain": self.domain
            },
            headers=headers
        )
        return response
    
    def add_ymm(self, fields, prod_ids=[]):
        """
        Given an array of YMM field values, 
        and an optional array of product ids.
        build the fields expected payload
        and perform a POST request to create a new 
        YMM entry, if product_ids where given, 
        the new entry will be related to the given product_ids.
        """
        payload = {
            "ymm_fields": self.build_post_fields(fields),
            "product_ids": prod_ids
        }
        headers = self.build_default_headers()
        return requests.post(
            f"{self.service_domain}{self.ROUTES['POST_YMM']}",
            json = payload,
            params = {
                "domain": self.domain,
                "action": "save"
            },
            headers = headers
        )

    def update_ymm(self, fields, ymm_id, prod_ids=[]):
        """
        Given an array of YMM field values, 
        and an optional array of product ids.
        build the fields expected payload
        and perform a POST request to update a 
        YMM entry, if product_ids where given, 
        the new entry will be related to the given product_ids.
        """
        payload = {
            "ymm_fields": self.build_post_fields(fields),
            "product_ids": prod_ids
        }
        headers = self.build_default_headers()
        return requests.post(
            f"{self.service_domain}{self.ROUTES['POST_YMM']}",
            json = payload,
            params = {
                "domain": self.domain,
                "data_id": ymm_id,
                "action": "save"
            },
            headers = headers
        )

    def assign_prods_ymms(self, prods, ymms):
        """
        Given a list of shopify product ids
        and a list of YMM ids.
        Perform a POST request to create a relation between them.
        Returns the response object from the performed request.
        """
        payload = {
            "product_ids": prods,
            "ymm_row_ids": ymms,
        }
        headers = self.build_default_headers()
        return requests.post(
            f"{self.service_domain}{self.ROUTES['ASSIGN_YMM']}",
            json = payload,
            params = {
                "domain": self.domain,
                "action": "bulk_assign"
            },
            headers=headers
        )
    
    def get_prod_ymms(self, prod_ymms_id):
        """
        Given a YMM id, Perform a GET request to 
        obtain the given YMM id information and all the Product-YMMs relations
        Returns the response object from the performed request.
        """
        headers = self.build_default_headers()

        return requests.get(
            f"{self.service_domain}{self.ROUTES['GET_PROD_YMM']}",
            params = {
                "domain": self.domain,
                "action": "edit",
                "data_id": prod_ymms_id
            },
            headers=headers
        )

    def delete_ymm(self, ymm_id):
        """
        Given an array of a single or multiple YMM ids as string, 
        perform a POST request to delete existent YMM entries.
        """
        payload = {
            "delete_id": ymm_id
        }
        headers = self.build_default_headers()
        return requests.post(
            f"{self.service_domain}{self.ROUTES['POST_YMM']}",
            json = payload,
            params = {
                "domain": self.domain,
                "action": "delete"
            },
            headers = headers
        )

    def delete_all_ymms(self):
        """ Performs a GET request to delate all YMM entries 
        for the domain object's target domain.
        Given the correct parameters, 
        Returns an HTTP response with code 200
        """
        headers = self.build_default_headers()
        response = requests.get(
            f"{self.service_domain}{self.ROUTES['GET_YMM']}",
            params={
                "action": "delete_all",
                "domain": self.domain
            },
            headers=headers
        )
        return response
