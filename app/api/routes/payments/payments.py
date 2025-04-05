from fastapi import APIRouter, HTTPException, Body
from app.api.models.payments import PaymentRequest, PaymentRequestResponse, PaymentVerificationRequest, PaymentVerificationResponse
from app.api.services.payment_service import paystack

router = APIRouter()

# Payment Initiation Endpoint
@router.post("/initiate_payment", response_model=PaymentRequestResponse,
    summary="initiate payment",
    description="")
async def initiate_payment(request: PaymentRequest):
    try:
        if request.payment_type.casefold() != "paystack":
            raise HTTPException(status_code=400, detail="Unsupported payment type")

        # Process Paystack payment
        payment_success = await paystack.initiate_payment(request.dict())

        if payment_success:
            return PaymentRequestResponse(
                status="success",
                booking_id=payment_success,
                message="valid booking"
            )
        return PaymentRequestResponse(
            status="error",
            transaction_id=None,
            message="Booking record not found"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Payment Verification Endpoint
@router.post("/verify_payment", response_model=PaymentVerificationResponse,
    summary="verify payment",
    description="")
async def verify_payment(request: PaymentVerificationRequest):
    validate_payment = await paystack.verify_payment(request.dict())

    if validate_payment:
        return PaymentVerificationResponse(
            booking_id=validate_payment["booking_id"],
            reference_id=validate_payment["reference_id"],
            status=validate_payment["status"],
            message=validate_payment["message"]
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid transaction ID")


# Payment Status Check Endpoint
@router.get("/payment_status/{reference_id}", response_model=PaymentVerificationResponse)
async def payment_status(reference_id: str):
    """
    Retrieves the payment status.
    """
    # Simulated payment status check
    if reference_id == "TXN567890":
        return PaymentVerificationResponse(
            reference_id=reference_id,
            status="completed",
            message="Payment has been completed"
        )
    else:
        raise HTTPException(status_code=404, detail="Transaction not found")
