from fastapi import APIRouter, HTTPException, Body
from app.api.models.payments import PaymentRequest, PaymentResponse, PaymentVerificationRequest, PaymentVerificationResponse
from app.api.services.payment_service import paystack

router = APIRouter()

# Payment Initiation Endpoint
@router.post("/initiate_payment", response_model=PaymentResponse,
    summary="initiate payment",
    description="")
async def initiate_payment(request: PaymentRequest):
    try:
        if request.payment_type.casefold() != "paystack":
            raise HTTPException(status_code=400, detail="Unsupported payment type")

        # Process Paystack payment
        payment_success = paystack.initiate_payment(request)

        if payment_success:
            return PaymentResponse(
                status="success",
                booking_id="eJzTd9cPd3J3CgwGAAtcAmw%3D",
                transaction_id="TXN567890",
                message="Payment processed successfully"
            )
        return PaymentResponse(
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
    """
    Simulates verifying a payment.
    """
    # Simulated verification logic
    if request.transaction_id == "TXN567890":
        return PaymentVerificationResponse(
            transaction_id=request.transaction_id,
            status="verified",
            message="Payment successfully verified"
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid transaction ID")


# Payment Status Check Endpoint
@router.get("/payment_status/{transaction_id}", response_model=PaymentVerificationResponse)
async def payment_status(transaction_id: str):
    """
    Retrieves the payment status.
    """
    # Simulated payment status check
    if transaction_id == "TXN567890":
        return PaymentVerificationResponse(
            transaction_id=transaction_id,
            status="completed",
            message="Payment has been completed"
        )
    else:
        raise HTTPException(status_code=404, detail="Transaction not found")
