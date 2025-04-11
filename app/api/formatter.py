from app.api.pricing import pricing
from app.api.services.flightRules import flightrules
from app.api.util import flightutils
from app.api.services.helper import convertDateTime, iataCarrier, airportName

class FlightFormatter:

    def format_flight_search_data(self, response_data):
        formatted_results = {}

        # Extract dictionaries and _id from response_data
        dictionaries = response_data.get("dictionaries", {})
        _id = response_data.get("inserted_id", {})

        # Initialize the 'data' key as a list to handle multiple offers
        formatted_results["data"] = []

        # Process each offer in the response data
        for offer in response_data.get("data", []):
            # Format the individual offer data
            formatted_offer = {
                "type": offer["type"],
                "id": offer["id"],
                "source": offer["source"],
                "instantTicketingRequired": offer["instantTicketingRequired"],
                "one_way": offer["oneWay"],
                "is_up_sell_offer": offer["isUpsellOffer"],
                "last_ticketing_date": offer["lastTicketingDate"],
                "last_ticketing_time": offer["lastTicketingDateTime"],
                "available_seats": offer["numberOfBookableSeats"],
                "price": {
                    "currency": "NGN", 
                    "grand_total": pricing.convert_usd_to_ngn(pricing.apply_markup(offer["price"]["grandTotal"])),
                    "base_price": pricing.convert_usd_to_ngn(pricing.apply_markup(offer["price"]["base"]))
                },
                "pricing_options": {
                    "fare_type": [offer["pricingOptions"]["fareType"]],
                    "included_checked_BagOnly": offer["pricingOptions"]["includedCheckedBagsOnly"]
                },
                "validating_airline": offer["validatingAirlineCodes"],
                "itineraries": [],
                "fare_rules": []
            }

            # fare rule
            fare_rule = flightrules.flight_rule(offer["fareRules"])
            formatted_offer["fare_rules"].append(fare_rule)

            # Process each itinerary for the current offer
            for itinerary in offer["itineraries"]:
                formatted_itinerary = {
                    "duration": flightutils.convert_duration(itinerary["duration"]),
                    "segments": []
                }

                prev_arrival_time = None  # Track the previous arrival time for layover calculation

                # Process each segment in the itinerary
                for segment in itinerary["segments"]:
                    departure_airport_code = segment["departure"]["iataCode"]
                    arrival_airport_code = segment["arrival"]["iataCode"]
                    airline_code = segment["carrierCode"]

                    fare_details = flightutils.get_fare_details(offer, segment["id"])
                    
                    formatted_segment = {
                        "departure": {
                            "airport": {
                                "code": departure_airport_code,
                                "name": dictionaries["locations"].get(departure_airport_code, {}).get("countryCode", "Unknown Airport")
                            },
                            "terminal": segment["departure"].get("terminal", "N/A"),
                            "date": flightutils.convert_date(segment["departure"]["at"]),
                            "time": flightutils.convert_date_to_time(segment["departure"]["at"])
                        },
                        "arrival": {
                            "airport": {
                                "code": arrival_airport_code,
                                "name": dictionaries["locations"].get(arrival_airport_code, {}).get("countryCode", "Unknown Airport")
                            },
                            "terminal": segment["arrival"].get("terminal", "N/A"),
                            "date": flightutils.convert_date(segment["arrival"]["at"]),
                            "time": flightutils.convert_date_to_time(segment["arrival"]["at"])
                        },
                        "flight_number": f"{airline_code}{segment['number']}",
                        "airline": {
                            "code": airline_code,
                            "name": dictionaries["carriers"].get(airline_code, "Unknown Airline"),
                            "logo": f"https://www.gstatic.com/flights/airline_logos/70px/{airline_code}.png"
                        },
                        "aircraft": dictionaries["aircraft"].get(segment["aircraft"]["code"], "Unknown Aircraft"),
                        "operating_airline": segment.get("operating", {}).get("carrierCode", ""),
                        "stops": segment["numberOfStops"],
                        "segment_class": fare_details.get("class", "Unknown"),
                        "travel_class": fare_details.get("cabin", "Unknown"),
                        "baggage": fare_details.get("baggage", "No baggage info"),
                        "fare_basis": fare_details.get("fare_basis", "Unknown"),
                        "is_refundable": fare_details.get("is_refundable", "Unknown")
                    }

                    # Calculate layover duration if previous arrival time exists
                    if prev_arrival_time:
                        layover_duration = flightutils.calculate_layover(prev_arrival_time, segment["departure"]["at"])
                        formatted_segment["layover_duration"] = layover_duration

                    prev_arrival_time = segment["arrival"]["at"]  # Update the previous arrival time

                    formatted_itinerary["segments"].append(formatted_segment)

                formatted_offer["itineraries"].append(formatted_itinerary) 

            # Append each formatted offer to the 'data' list
            formatted_results["data"].append(formatted_offer)

        # Add 'dictionaries' and 'data_id' to the formatted results
        formatted_results["dictionaries"] = dictionaries
        formatted_results["data_id"] = str(_id)

        return formatted_results



    async def format_flight_pricing_data(self, response_data):
        formatted_pricing = []
        dictionaries = response_data.get("dictionaries", {})
        _id = response_data.get("inserted_id", {})

        def get_aircraft_name(aircraft_code):
            return dictionaries.get("aircraft", {}).get(aircraft_code, "Unknown Aircraft")

        for offer in response_data.get("data", {}).get("flightOffers", []):
            # Simplified pricing conversion and markup application
            price_data = offer.get("price", {})
            formatted_offer = {
                "flight_id": offer.get("id"),
                "source": offer.get("source"),
                "instant_Ticketing_Required": offer.get("instantTicketingRequired"),
                "last_ticketing_date": offer.get("lastTicketingDate"),
                "itineraries": [],
                "price": {
                    "currency": "NGN",
                    "total": pricing.convert_usd_to_ngn(pricing.apply_markup(price_data.get("grandTotal", 0))),
                    "base": pricing.convert_usd_to_ngn(pricing.apply_markup(price_data.get("base", 0)))
                },
                "validating_airline": offer.get("validatingAirlineCodes", []),
                "traveler_pricing": []
            }

            for itinerary in offer.get("itineraries", []):
                formatted_itinerary = {
                    "segments": []
                }

                prev_arrival_time = None  # Track previous arrival time for layovers

                for segment in itinerary.get("segments", []):
                    departure_airport_code = segment.get("departure", {}).get("iataCode", "")
                    arrival_airport_code = segment.get("arrival", {}).get("iataCode", "")
                    airline_code = segment.get("carrierCode", "")

                    fare_details = flightutils.get_fare_details(offer, segment.get("id"))
                    departure_airport = await airportName(departure_airport_code)
                    arrival_airport = await airportName(arrival_airport_code)
                    
                    formatted_segment = {
                        "departure": {
                            "airport": {
                                "code": departure_airport_code,
                                "name": departure_airport.get("name", "N/A"),
                                "city": departure_airport.get("city", "N/A"),
                                "country": departure_airport.get("country", "N/A")
                            },
                            "terminal": segment.get("departure", {}).get("terminal", "N/A"),
                            "date": flightutils.convert_date(segment.get("departure", {}).get("at")),
                            "time": flightutils.convert_date_to_time(segment.get("departure", {}).get("at"))
                        },
                        "arrival": {
                            "airport": {
                                "code": arrival_airport_code,
                                "name": arrival_airport.get("name", "N/A"),
                                "city": arrival_airport.get("city", "N/A"),
                                "country": arrival_airport.get("country", "N/A")
                            },
                            "terminal": segment.get("arrival", {}).get("terminal", "N/A"),
                            "date": flightutils.convert_date(segment.get("arrival", {}).get("at")),
                            "time": flightutils.convert_date_to_time(segment.get("arrival", {}).get("at"))
                        },
                        "flight_number": f"{airline_code}{segment.get('number', '')}",
                        "airline": {
                            "code": airline_code,
                            "name": await iataCarrier(airline_code),
                            "logo": f"https://www.gstatic.com/flights/airline_logos/70px/{airline_code}.png"
                        },
                        "aircraft": get_aircraft_name(segment.get("aircraft", {}).get("code", "")),
                        "operating_airline": segment.get("operating", {}).get("carrierCode", ""),
                        "stops": segment.get("numberOfStops", 0),
                        "duration": flightutils.convert_duration(segment.get("duration"))
                    }

                    # Calculate layover duration if previous arrival time exists
                    if prev_arrival_time:
                        layover_duration = flightutils.calculate_layover(prev_arrival_time, segment.get("departure", {}).get("at"))
                        formatted_segment["layover_duration"] = layover_duration

                    prev_arrival_time = segment.get("arrival", {}).get("at")  # Update previous arrival time
                    formatted_itinerary["segments"].append(formatted_segment)

                formatted_offer["itineraries"].append(formatted_itinerary)

            for traveler in offer.get("travelerPricings", []):
                traveler_details = {
                    "traveler_id": traveler.get("travelerId"),
                    "fare_option": traveler.get("fareOption"),
                    "traveler_type": traveler.get("travelerType"),
                    "base_price": pricing.convert_usd_to_ngn(pricing.apply_markup(traveler.get("price", {}).get("base", 0))),
                    "total_price": pricing.convert_usd_to_ngn(pricing.apply_markup(traveler.get("price", {}).get("total", 0))),
                    "segments": []
                }

                for segment in traveler.get("fareDetailsBySegment", []):
                    segment_details = {
                        "segment_id": segment.get("segmentId"),
                        "cabin": segment.get("cabin"),
                        "class": segment.get("class"),
                        "fare_basis": segment.get("fareBasis"),
                        "baggage": segment.get("includedCheckedBags", {}).get("quantity", "Unknown"),
                        "is_refundable": "Yes" if "REFUNDABLE" in segment.get("fareBasis", "").upper() else "No"
                    }
                    traveler_details["segments"].append(segment_details)

                formatted_offer["traveler_pricing"].append(traveler_details)

            formatted_pricing.append(formatted_offer)

        # Append dictionaries and data_id at the end
        formatted_pricing.append(dictionaries)
        formatted_pricing.append({"data_id": str(_id)})

        return formatted_pricing



    async def format_flight_booking(self, response_data):
        booking_id = response_data.get("bookingId", "")
        booking_data = response_data.get("data", {})
        payment_data = response_data.get("payment", {})
        status = response_data.get("status")
        dictionaries = response_data.get("dictionaries", {}) 

        formatted_booking = {
            "booking_id": booking_id,
            "booking_reference": booking_data.get("id"),
            "status": status,
            "date": response_data.get("date"),
            "associated_records": booking_data.get("associatedRecords", []),
            "flight_offers": [],
            "travelers": [],
            "itineraries": []
        }

        # Extract flight offers
        for offer in booking_data.get("flightOffers", []):
            formatted_booking["flight_offers"].append({
                "flight_id": offer["id"],
                "source": offer["source"],
                "validating_airline": offer["validatingAirlineCodes"],
                "included_checked_BagOnly": offer["pricingOptions"]["includedCheckedBagsOnly"],
                "pricing": {
                    "total": pricing.convert_usd_to_ngn(pricing.apply_markup(offer["price"]["total"])),
                    "base": pricing.convert_usd_to_ngn(pricing.apply_markup(offer["price"]["base"])),
                    "grand_total": pricing.convert_usd_to_ngn(pricing.apply_markup(offer["price"]["grandTotal"])),
                },
                "traveler_pricings": offer["travelerPricings"],

            })


        # Extract travelers
        for traveler in booking_data.get("travelers", []):
            formatted_booking["travelers"].append({
                "traveler_id": traveler["id"],
                "name": f"{traveler['name']['firstName']} {traveler['name']['lastName']}",
                "date_of_birth": traveler["dateOfBirth"],
                "gender": traveler["gender"],
                "email": traveler["contact"]["emailAddress"],
                "phone": f"{traveler['contact']['phones'][0]['countryCallingCode']}{traveler['contact']['phones'][0]['number']}" if "phones" in traveler["contact"] and traveler["contact"]["phones"] else "N/A",
                "documents": traveler.get("documents", [])
            })

        # Extract itineraries
        for offer in booking_data.get("flightOffers", []):
            for itinerary in offer.get("itineraries", []):
                formatted_itinerary = {
                    "segments": []
                }

                prev_arrival_time = None

                for segment in itinerary.get("segments", []):
                    airline_code = segment["carrierCode"]
                    flightDet = await flightutils.aita_code_det(airline_code)
                    depart_loc = await flightutils.aita_code_det(segment["departure"]["iataCode"])
                    arrive_loc = await flightutils.aita_code_det(segment["arrival"]["iataCode"])

                    segment_split = {
                        "departure": {
                            "iata_code": segment["departure"]["iataCode"],
                            "location": depart_loc.get("name", ""),
                            "terminal": segment["departure"].get("terminal", "N/A"),
                            "time": convertDateTime(segment["departure"]["at"])
                        },
                        "arrival": {
                            "iata_code": segment["arrival"]["iataCode"],
                            "location": arrive_loc.get("name", ""),
                            "terminal": segment["arrival"].get("terminal", "N/A"),
                            "time": convertDateTime(segment["arrival"]["at"])
                        },
                        "carrier_code": airline_code,
                        "flight_number": segment["number"],
                        "flight_logo": f"https://www.gstatic.com/flights/airline_logos/70px/{airline_code}.png",
                        "flight_duration": flightutils.convert_duration(segment["duration"]),
                        "aircraft_code": segment["aircraft"]["code"],
                        "number_of_stops": segment.get("numberOfStops", 0),
                        "cabin_class": "ECONOMY - V"
                    }
                    
                    if prev_arrival_time:
                        layover_duration = flightutils.calculate_layover(prev_arrival_time, segment["departure"]["at"])
                        segment_split["layover_duration"] = layover_duration
                    
                    prev_arrival_time = segment["arrival"]["at"]

                    formatted_itinerary["segments"].append(segment_split)



                formatted_booking["itineraries"].append(formatted_itinerary)


        # Extract payment details
        payment_details = {
            "payment_id": payment_data.get("payment_id", ""),
            "payment_status": payment_data.get("status", ""),
            "payment_reference_id": payment_data.get("payment_reference_id", "")
        }
        formatted_booking["payment"] = payment_details


        return formatted_booking



formatter = FlightFormatter()