from pydantic import BaseModel
from typing import Optional


# Payment Request Model
class PaymentRequest(BaseModel):
    payment_type: str
    booking_id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "payment_type": "paystack", # paystack, flutterwave etc
                "booking_id": "eJzTd9cPd3J3CgwGAAtcAmw%3D"             
            }
        }

# Payment Response Model
class PaymentRequestResponse(BaseModel):
    status: str
    booking_id: Optional[str]
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "booking_id": "eJzTd9cPd3J3CgwGAAtcAmw%3D",
                "message": "Booking valid"
            }
        }

# Payment Verification Model
class PaymentVerificationRequest(BaseModel):
    booking_id: str
    reference_id: str # payment reference ID
    payment_method: str

    class Config:
        json_schema_extra = {
            "example": {
                "booking_id": "eJzTd9cPd3J3CgwGAAtcAmw%3D",
                "reference_id": "TXN567890",
                "payment_method": "CARD"
            }
        }

class PaymentVerificationResponse(BaseModel):
    booking_id: str
    reference_id: str
    status: str
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "booking_id": "eJzTd9cPd3J3CgwGAAtcAmw%3D",
                "reference_id": "TXN567890",
                "status": "verified",
                "message": "Payment successfully verified"
            }
        }
