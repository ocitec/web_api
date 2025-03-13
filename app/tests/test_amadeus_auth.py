import os
import requests



class AmadeusEnterpriseAPI:
    def __init__(self):
        self.auth_url = 'https://test.api.amadeus.com/v1/security/oauth2/token'
        self.base_url = 'https://test.travel.api.amadeus.com/v1'
        self.token = self.get_access_token()


    def get_access_token(self):
        """Authenticate and retrieve an access token from Amadeus."""
        payload = {
            "grant_type": "client_credentials",
            "client_id": "e0Cc4oltn0GzQSz3uxLDid1GdW0S64sk",
            "client_secret": "cTvZA3KKOU3aNMaj"
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        
        response = requests.post(self.auth_url, data=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            raise Exception(f"Failed to authenticate: {response.json()}")


amadeus_api = AmadeusEnterpriseAPI()
d = amadeus_api.get_access_token()
print(d)