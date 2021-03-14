"""Main module."""
import requests

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
