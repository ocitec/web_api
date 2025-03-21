from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class FlightSearchRequest(BaseModel):
    trip_type: str  
    origins: List[str]  
    destinations: List[str]  
    departure_dates: List[str]  
    return_date: Optional[str] = None  
    cabin: List[str]  
    adults: int = 1  
    children: int = 0  
    infants: int = 0  

    class Config:
        json_schema_extra = {
            "example": {
              "trip_type": "round-trip",
              "origins": ["LOS"],
              "destinations": ["LHR"],
              "departure_dates": ["2025-06-17"],
              "return_date": "2025-06-29",
              "cabin": ["ECONOMY"],
              "adults": 1,
              "children": 1,
              "infants": 0
            }
        }


# Define request body schema for flight pricing
class FlightPricingRequest(BaseModel):
    data_id: str
    flight_offer: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "data_id": "67d3f7c8bf2500d32ad0054e",
                "flight_offer": {
                    "type": "flight-offer",
                    "id": "1",
                    "source": "GDS"
                }
            }
        }



# Define request body schema for flight booking
class FlightBookingRequest(BaseModel):
    data_id: str  
    travelers: List[Dict[str, Any]]  

    class Config:
        json_schema_extra = {
            "example": {
                "data_id": "67d3f7dfbf2500d32ad0054f",
                "travelers": [
                    {
                        "id": "1",
                        "dateOfBirth": "2000-01-16",
                        "name": {
                            "firstName": "OLANREWAJU",
                            "lastName": "SAMUEL"
                        },
                        "gender": "MALE",
                        "contact": {
                            "emailAddress": "sample.email@email.com",
                            "phones": [
                                {
                                    "deviceType": "MOBILE",
                                    "countryCallingCode": "234",
                                    "number": "1234567890"
                                }
                            ]
                        },
                        "documents": [
                            {
                                "documentType": "PASSPORT",
                                "birthPlace": "Madrid",
                                "issuanceLocation": "Madrid",
                                "issuanceDate": "2023-04-14",
                                "number": "00000000",
                                "expiryDate": "2027-04-14",
                                "issuanceCountry": "NG",
                                "validityCountry": "NG",
                                "nationality": "NG",
                                "holder": True
                            }
                        ]
                    },
                    {
                        "id": "2",
                        "dateOfBirth": "2016-08-16",
                        "name": {
                            "firstName": "OLANREWAJU",
                            "lastName": "ATANDA"
                        },
                        "gender": "MALE",
                        "contact": {
                            "emailAddress": "sample.email@email.com",
                            "phones": [
                                {
                                    "deviceType": "MOBILE",
                                    "countryCallingCode": "234",
                                    "number": "1234567890"
                                }
                            ]
                        },
                        "documents": [
                            {
                                "documentType": "PASSPORT",
                                "birthPlace": "Madrid",
                                "issuanceLocation": "Madrid",
                                "issuanceDate": "2024-04-14",
                                "number": "111112222",
                                "expiryDate": "2027-04-14",
                                "issuanceCountry": "NG",
                                "validityCountry": "NG",
                                "nationality": "NG",
                                "holder": True
                            }
                        ]
                    }         
                ]
            }
        }


# Define request body schema for booking Order
class FlightBookingOrder(BaseModel):
    booking_id: str
    reference: str

    class Config:
        json_schema_extra = {
            "example": {
                "booking_id": "eJzTd9cPd3J3CgwGAAtcAmw%3D",
                "reference": "WBGBQS"
            }
        }


# Define flight order issuance
class FlightOrderIssuarance(BaseModel):
    order_id: str
    formOfPayment: Dict[str, Any]


    class Config:
        json_schema_extra = {
            "example": {
                "order_id": "67d3f7c8bf2500d32ad0054e",
                "formOfPayment": [
                    {
                        "other":
                        {
                            "method" : "CASH"
                        }
                    } 
                ]
            }
        }