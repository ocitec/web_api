from fastapi import HTTPException
import os
import requests
import httpx

def coy_profile():
    agencymgt_data = {
                "coy_name": "Company's name",
                "contact_firstname": "Atanda",
                "contact_lastname": "Hilary",
                "address_1": "21 sample street, lagos",
                "address_2": "22 sample street, lagos",
                "city": "Lagos",
                "state": "Lagos",
                "postal_code": "100001",
                "country_code": "234",
                "agency_country_code": "0001",
                "agency_phone_number": "09876542342",
                "agency_email": "sample@email.com",
                "base_currency": "NGN"
            }

    return agencymgt_data


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


    def book_flight_order(self, flight_offer: dict, travelers: list):
        
        try:
            if "data" not in flight_offer or "flightOffers" not in flight_offer["data"]:
                raise HTTPException(status_code=400, detail="Invalid flight offer format.")


            token = self.get_access_token()
            url = f"{self.base_url}/v1/booking/flight-orders"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }            

            # get coy information
            coy = coy_profile()
            print(f'Company profile: {coy.get("coy_named", "x")}\n\n')

            payload = {
                "data": {
                    "type": "flight-order",
                    "flightOffers": flight_offer["data"]["flightOffers"], 
                    "travelers": travelers, 
                    "remark": {
                        "general": [
                            {
                                "subType": "SOAS",
                                "text": "ONLINE BOOKING FROM SOAS" 
                            }
                        ]
                    },
                    "ticketingAgreement": {
                        "option": "DELAY_TO_CANCEL",
                        "delay": "1D" 
                    },
                    
                      "contacts": [
                        {
                          "addresseeName": {
                            "firstName": "SOYEMI",
                            "lastName": "OLANREWAJU"
                          },
                          "companyName": "SOAS",
                          "purpose": "STANDARD",
                          "phones": [
                            {
                              "deviceType": "LANDLINE",
                              "countryCallingCode": "234",
                              "number": "1234567890"
                            },
                            {
                              "deviceType": "MOBILE",
                              "countryCallingCode": "234",
                              "number": "1234567890"
                            }
                          ],
                          "emailAddress": "info@ocitravels.com",
                          "address": {
                            "lines": [
                              "37B Fola Sibo Street"
                            ],
                            "postalCode": "100001",
                            "cityName": "Lagos",
                            "countryCode": "NG"
                          }
                        }
                      ]                  

                }
            }

            return payload

            # async with httpx.AsyncClient() as client:
            #     response = await client.post(url, json=payload, headers=headers, timeout=60)

            # # Handle response
            # if response.status_code == 201:
            #     booking_data = response.json()

            #     # add info
            #     additional_info = {
            #         "status": "booked",
            #         "payment_status": "pending",
            #         "payment_reference_no": None,
            #         "date": get_booking_date()
            #     }

            #     booking_data["additional"] = additional_info

            #     # save booking data
            #     insert_result = await amadeus_flight_bookings.insert_one(booking_data)

            #     return self.format_flight_booking(booking_data)  # Format booking response
            # else:
            #     raise HTTPException(status_code=response.status_code, detail=f"Failed to book flight: {response.json()}")

        except HTTPException:
            raise  
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error booking flight: {str(e)}")

amadeus_api = AmadeusEnterpriseAPI()

flight_offer = {
    "data": {
        "flightOffers" : None
    }
}

travelers = [
    {
        "id": "1"
    },
    {
        "id": "2"
    }
]


d = amadeus_api.book_flight_order(flight_offer, travelers)
print(d)