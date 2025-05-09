import os
import base64
from typing import Dict
import requests
import logging
from jinja2 import Template
from app.config import SENDGRID_API_KEY, EMAIL_SENDER, APP_URL
from app.api.services.helper import coy_profile
from app.api.formatter import formatter

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.api_key = SENDGRID_API_KEY
        self.sender_email = EMAIL_SENDER
        self.app_url = APP_URL
        self.sendgrid_url = "https://api.sendgrid.com/v3/mail/send"
        self.bookingTemplate = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates', 'booking_email.html'))
        self.flightNotification = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates', 'booking_notification.html'))

    def booking_template(self, booking_data, _path):

        try:            
            with open(_path, "r", encoding="utf-8") as file:
                template_content = file.read()

            # Use Jinja2 to inject values
            template = Template(template_content)
            return template.render(data=booking_data)
        
        except Exception as e:
            logger.error(f"❌ Error rendering email template: {str(e)}")

    async def send_email(self, booking_data: dict):
        
        try:
            # office details 
            coy = await coy_profile()
            bookingId = booking_data["data"]["id"]

            booking_data["_id"] = str(booking_data["_id"])            
            emailData =  await formatter.format_flight_booking(booking_data)
            emailData["coy"] = coy
            emailData["booking_url"] = f"{self.app_url}/manage/booking/order/{ base64.b64encode(bookingId.encode('utf-8')).decode('utf-8')  }"
            
            passenger_email = emailData["travelers"][0]["email"]

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # Render the external HTML template with data
            html_content = self.booking_template(emailData, self.bookingTemplate)

            # with open("email_preview.html", "w", encoding="utf-8") as file:
            #     file.write(html_content)

            # print("✅ Email preview saved as 'email_preview.html'. Open in a browser to view.")
            
            payload = {
                "personalizations": [{"to": [{"email": passenger_email}]}],
                "from": {"email": self.sender_email},
                "subject": 'Flight Travel Itinerary',
                "content": [
                    {"type": "text/html", "value": html_content}
                ]
            }

            # Send request to SendGrid API
            response = requests.post(self.sendgrid_url, json=payload, headers=headers)

            if response.status_code == 202:
                logger.info(f"✅ Email sent successfully to {passenger_email}")

                # send team notification
                return await self.booking_notification(emailData)

            else:
                logger.error(f"❌ Failed to send email: {response.text}")
                return {"status": "error", "message": f"Failed to send email: {response.text}"}

        except requests.RequestException as e:
            logger.error(f"❌ Network error while sending email: {str(e)}")
            return {"status": "error", "message": f"Network error: {str(e)}"}

        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}")
            return {"status": "error", "message": f"Unexpected error: {str(e)}"}



    async def booking_notification(self, formattedData: dict):
        
        try:
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # Render the external HTML template with data
            html_content = self.booking_template(formattedData, self.flightNotification)

            # with open("email_preview.html", "w", encoding="utf-8") as file:
            #     file.write(html_content)
            
            payload = {
                "personalizations": [{"to": [{"email": "tech@ocitravels.com"}]}],
                "from": {"email": self.sender_email},
                "subject": 'Flight Travel Itinerary',
                "content": [
                    {"type": "text/html", "value": html_content}
                ]
            }

            # Send request to SendGrid API
            response = requests.post(self.sendgrid_url, json=payload, headers=headers)

            if response.status_code == 202:
                logger.info(f"✅ Email sent successfully to Team")
                return {"status": "success", "message": "Email sent successfully"}
            else:
                logger.error(f"❌ Failed to send email: {response.text}")
                return {"status": "error", "message": f"Failed to send email: {response.text}"}

        except requests.RequestException as e:
            logger.error(f"❌ Network error while sending email: {str(e)}")
            return {"status": "error", "message": f"Network error: {str(e)}"}

        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}")
            return {"status": "error", "message": f"Unexpected error: {str(e)}"}


    async def payment_notification(self, booking_data: dict):
        
        try:
            emailData =  await formatter.format_flight_booking(booking_data)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # Render the external HTML template with data
            html_content = self.booking_template(emailData, self.flightNotification)

            payload = {
                "personalizations": [{"to": [{"email": "tech@ocitravels.com"}]}],
                "from": {"email": self.sender_email},
                "subject": 'Flight Booking Payment Notification',
                "content": [
                    {"type": "text/html", "value": html_content}
                ]
            }

            # Send request to SendGrid API
            response = requests.post(self.sendgrid_url, json=payload, headers=headers)

            if response.status_code == 202:
                logger.info(f"✅ Payment Email sent successfully")
                return {"status": "success", "message": f"Email sent successfully"}

            else:
                logger.error(f"❌ Failed to send email: {response.text}")
                return {"status": "error", "message": f"Failed to send email: {response.text}"}

        except requests.RequestException as e:
            logger.error(f"❌ Network error while sending email: {str(e)}")
            return {"status": "error", "message": f"Network error: {str(e)}"}

        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}")
            return {"status": "error", "message": f"Unexpected error: {str(e)}"}

# Create an instance of the EmailService
email_service = EmailService()
