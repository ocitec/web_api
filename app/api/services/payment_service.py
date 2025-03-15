import httpx
from fastapi import HTTPException
import requests
from bson import ObjectId
from app.config import PAYSTACK_URL, PAYSTACK_API_KEY, PAYSTACK_SECRET
from app.api.db.collections import payment_collection, amadeus_flight_bookings 
from datetime import datetime

class PaystackPayment:
    def __init__(self):
        self.url = PAYSTACK_URL
        self.secret = PAYSTACK_SECRET 
        self.headers = {
            "Authorization": f"Bearer {self.secret}",
            "Content-Type": "application/json"
        }

    async def initiate_payment(self, payment_params: dict) -> bool:
        """
        Initiates a payment request.
        Returns True if the booking exists and reference is valid, otherwise False.
        """
        try:
            # Check if booking exists in the database
            booking_id = payment_params["booking_id"]

            booking = await amadeus_flight_bookings.find_one({"data.id": booking_id})

            if not booking:
                return False 

            return True
        except Exception as e:
            print(f"Error checking booking: {e}") 
            return False


    async def verify_payment(self, booking_id: str, reference_id: str) -> dict:
        """
        Verifies payment status on Paystack using the reference ID.
        Updates the booking status and saves the payment record if successful.
        """
        try:
            verify_url = f"{self.url}/transaction/verify/{reference_id}"

            async with httpx.AsyncClient() as client:
                response = await client.get(verify_url, headers=self.headers)

            if response.status_code == 200:
                transaction_data = response.json()
                payment_status = transaction_data["data"]["status"]

                if payment_status == "success":
                    # Save payment record after successful verification
                    payment = await self.save_payment_record(transaction_data["data"])

                    # Update booking status in the database
                    update_data = {
                        "$set": {
                            "payment.status": "PAID",
                            "payment.payment_reference_id": reference_id,
                            "payment.payment_id": str(payment.inserted_id),
                            "payment.payment_date": datetime.utcnow().isoformat()
                        }
                    }
                    update_result = await amadeus_flight_bookings.update_one({"_id": ObjectId(booking_id)}, update_data)

                    if update_result.modified_count == 0:
                        raise HTTPException(status_code=404, detail="Booking not found or update failed.")

                    return {"status": "success", "data": transaction_data["data"]}

                else:
                    return {
                        "status": "failed",
                        "message": f"Payment not successful. Status: {payment_status}",
                        "data": transaction_data["data"]
                    }

            else:
                raise HTTPException(status_code=response.status_code, detail="Payment verification failed")

        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Error verifying payment: {str(e)}")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


    def save_payment_record(self, data: dict):
        """
        Saves the verified payment transaction into the database.
        """
        try:
            payment_record = {
                "reference": data.get("reference"),
                "amount": data.get("amount") / 100,  # Convert from kobo to Naira (NGN)
                "currency": data.get("currency"),
                "status": data.get("status"),
                "payment_channel": data.get("channel"),
                "paid_at": data.get("paid_at"),
                "customer": {
                    "email": data["customer"]["email"],
                    "phone": data["customer"].get("phone", "N/A")
                },
                "created_at": datetime.utcnow().isoformat()
            }

            record = payment_collection.insert_one(payment_record) 
            return record


        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving payment record: {str(e)}")

# Create an instance of PaystackPayment
paystack = PaystackPayment()
