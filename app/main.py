from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import ALLOWED_ORIGINS
from app.api.routes.flights.flights import router as flights_router
from app.api.routes.flights.flight_booking import router as flight_booking_router
from app.api.routes.flights.destinations import router as destinations_router
from app.api.routes.flights.flight_deals import router as flight_deals_router
from app.api.routes.payments.payments import router as payments_router
from app.api.routes.coy.about import router as about_router
from app.api.routes.coy.agencymgt import router as agencymgt_router
from app.api.routes.tours.tour_packages import router as tour_packages_router
from app.api.routes.tours.tour_package_reservation import router as reservation_router
from app.api.routes.visa.visa import router as visa_router
from app.api.routes.currency.currency import router as currency_router
from app.api.routes.airport.airports import router as airports_router
from app.api.db.collections import create_ttl_index

app = FastAPI(title="Flight Booking API")

@app.on_event("startup")
async def startup_db():
    await create_ttl_index()

# ✅ Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Restrict to allowed domains
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Register flight routes
app.include_router(flights_router, prefix="/api/flights", tags=["Flights"])
app.include_router(flight_booking_router, prefix="/api/flights/booking", tags=["Flights"])

# register payment routes
app.include_router(payments_router, prefix="/api/payments", tags=["Payments"])

app.include_router(about_router, prefix="/api/about")
app.include_router(agencymgt_router, prefix="/api/about")

app.include_router(tour_packages_router, prefix="/api/tour")
app.include_router(reservation_router, prefix="/api/tour")
app.include_router(visa_router, prefix="/api/visa")
app.include_router(destinations_router, prefix="/api/destinations")
app.include_router(flight_deals_router, prefix="/api/flight-deals")
app.include_router(currency_router, prefix="/api/currency", tags=["Currency"])
app.include_router(airports_router, prefix="/api/airport", tags=["Airport"])

@app.get("/")
def home():
    return {"message": "Welcome to the Flight Booking API"}


if __name__ == "__main__":
    import uvicorn
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=HOST, port=PORT)