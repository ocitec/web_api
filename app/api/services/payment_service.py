import httpx
from fastapi import HTTPException
import requests
from bson import ObjectId
from app.config import PAYSTACK_URL, PAYSTACK_API_KEY, PAYSTACK_SECRET
from app.api.db.collections import payment_collection, amadeus_flight_bookings 
from datetime import datetime
from app.api.services.amadeus_service import amadeus_api
from app.api.services.email_service import email_service


class PaystackPayment:
    def __init__(self):
        self.url = PAYSTACK_URL
        self.secret = PAYSTACK_SECRET 
        self.headers = {
            "Authorization": f"Bearer {self.secret}",
            "Content-Type": "application/json"
        }

    async def initiate_payment(self, payment_params: dict):
       
        try:
            # Check if booking exists in the database
            booking_id = payment_params["booking_id"]

            booking = await amadeus_flight_bookings.find_one({"_id": ObjectId(booking_id)})

            if not booking:
                return False 

            return str(booking["_id"])

        except Exception as e:
            print(f"Error checking booking: {e}") 
            return False


    async def verify_payment(self, verify_params:dict):
        
        try:

            verify_url = f"{self.url}/transaction/verify/{verify_params['reference_id']}"

            async with httpx.AsyncClient() as client:
                response = await client.get(verify_url, headers=self.headers)
                response_data = response.json()

            if response_data["status"] == True:
                transaction_data = response_data
                payment_status = transaction_data["data"]["status"]
                booking_id = verify_params["booking_id"]
                reference_id = verify_params["reference_id"]
                payment_method = verify_params["payment_method"]

                if payment_status == "success":
                    # Save payment record after successful verification
                    payment = await self.save_payment_record(transaction_data["data"])

                    # Update booking status in the database
                    update_data = {
                        "$set": {
                            "payment.status": "PAID",
                            "payment.payment_reference_id": reference_id,
                            "payment.payment_id": str(payment.inserted_id),
                            "payment.payment_date": datetime.utcnow().isoformat(),
                            "payment.method": payment_method
                        }
                    }

                    update_result = await amadeus_flight_bookings.update_one({"_id": ObjectId(booking_id)}, update_data)

                    if update_result.modified_count == 0:
                        raise HTTPException(status_code=404, detail="Booking not found or update failed.")


                    # send email notification to team
                    bookingDetails = await amadeus_flight_bookings.find_one({"_id": ObjectId(booking_id)})
                    c = await email_service.payment_notification(bookingDetails)


                    return {
                        "status": "Verified",
                        "booking_id": booking_id,
                        "reference_id": reference_id,
                        "message": "Payment Verified" 
                    }

                else:
                    return {
                        "status": "failed",
                        "booking_id": booking_id,
                        "reference_id": reference_id,
                        "message": f"Payment not successful. Status: {payment_status}",
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
                "reference": data.get("reference_id"),
                "amount": data.get("amount") / 100,  # Convert from kobo to Naira (NGN)
                "currency": data.get("currency"),
                "status": data.get("status"),
                "payment_channel": data.get("payment_channel"),
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



    def save_visa_record(self, data: dict):
        """
        Saves the verified payment transaction into the database.
        """
        try:
            payment_record = {
                "status": data["status"],
                "visa_type": data["visa_type"],
                "visa_for": data["visa_for"],
                "booking_id": data["booking_id"],
                "reference": data["reference"],
                "amount": data["amount"] / 100,  # Convert from kobo to Naira (NGN)
                "currency": data["currency"],
                "payment_channel": data["channel"],
                "paid_at": data.get("paid_at"),
                "customer": {
                    "email": data["customer"]["email"],
                    "phone": data["customer"].get("phone", "N/A"),
                    "name": f'{data["customer"].get("title", "")} {data["customer"].get("first_name", "")} {data["customer"].get("last_name", "")}'
                },
                "message": data["customer"].get("message", ""),
                "created_at": datetime.utcnow().isoformat()
            }

            record = payment_collection.insert_one(payment_record) 
            return record


        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving payment record: {str(e)}")


    async def verify_visa_payment(self, verify_params:dict):
        
        try:

            verify_url = f"{self.url}/transaction/verify/{verify_params['reference_id']}"

            async with httpx.AsyncClient() as client:
                response = await client.get(verify_url, headers=self.headers)
                response_data = response.json()

            if response_data["status"] == True:
                transaction_data = response_data
                payment_status = transaction_data["data"]["status"]
                transaction_data["data"]["visa_type"] = verify_params["visa_type"],
                transaction_data["data"]["visa_for"] = verify_params["visa_for"],
                transaction_data["data"]["booking_id"] = verify_params["booking_id"]
                transaction_data["data"]["customer"]["phone"] = verify_params["phone"]
                transaction_data["data"]["customer"]["title"] = verify_params["title"]
                transaction_data["data"]["customer"]["first_name"] = verify_params["first_name"]
                transaction_data["data"]["customer"]["last_name"] = verify_params["last_name"]
                transaction_data["data"]["customer"]["nationality"] = verify_params["nationality"]
                transaction_data["data"]["customer"]["message"] = verify_params["message"]

                if payment_status == "success":
                    payment = await self.save_visa_record(transaction_data["data"])

                    # send email notification
                    info = await payment_collection.find_one({"_id": ObjectId(payment.inserted_id)})
                    # c = await email_service.visa_notification(info)

                    return {
                        "status": "Verified",
                        "booking_id": verify_params["booking_id"],
                        "reference_id": verify_params["reference_id"],
                        "message": "Payment Verified" 
                    }

                else:
                    return {
                        "status": "failed",
                        "booking_id": booking_id,
                        "reference_id": reference_id,
                        "message": f"Payment not successful. Status: {payment_status}",
                    }

            else:
                raise HTTPException(status_code=response.status_code, detail="Payment verification failed")

        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Error verifying payment: {str(e)}")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Create an instance of PaystackPayment
paystack = PaystackPayment()
