from pydantic import BaseModel
from typing import Optional


# Payment Request Model
class PaymentRequest(BaseModel):
    payment_type: str
    booking_id: str
    amount: float
    currency: str
    payment_method: str
    customer_id: str
    order_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "payment_type": "paystack", # paystack, flutterwave etc
                "booking_id": "eJzTd9cPd3J3CgwGAAtcAmw%3D", 
                "amount": 150.75,
                "currency": "USD",
                "payment_method": "credit_card",
                "customer_id": "CUST12345",
                "order_id": "ORD98765"
            }
        }

# Payment Response Model
class PaymentResponse(BaseModel):
    status: str
    booking_id: Optional[str]
    transaction_id: Optional[str]
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "booking_id": "eJzTd9cPd3J3CgwGAAtcAmw%3D",
                "transaction_id": "TXN567890",
                "message": "Payment processed successfully"
            }
        }

# Payment Verification Model
class PaymentVerificationRequest(BaseModel):
    booking_id: str
    transaction_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "booking_id": "eJzTd9cPd3J3CgwGAAtcAmw%3D",
                "transaction_id": "TXN567890"
            }
        }

class PaymentVerificationResponse(BaseModel):
    booking_id: str
    transaction_id: str
    status: str
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "booking_id": "eJzTd9cPd3J3CgwGAAtcAmw%3D",
                "transaction_id": "TXN567890",
                "status": "verified",
                "message": "Payment successfully verified"
            }
        }
