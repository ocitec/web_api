from app.api.pricing import pricing

class FlightRules:
    @staticmethod
    def exchange_rule(maxPenaltyAmount):
        rule_message = f"If you need to change your flight, a penalty fee of up to ₦{maxPenaltyAmount:,} will apply. \
                            The fee is determined based on the airline's fare conditions and how far \
                            in advance the change is made."

        return rule_message

    @staticmethod
    def revalidation_rule():
        rule_message = "Revalidating your ticket is not applicable to this fare. If you need to make any changes to your flight, \
                you will need to reissue your ticket, which may involve additional costs or penalties."

        return rule_message

    @staticmethod
    def refund_rule(maxPenaltyAmount):
        rule_message = f"Refunds are available for this fare, subject to airline policies. " \
               f"A refund penalty may apply depending on when the cancellation occurs. " \
               f"Please note that some fares are non-refundable. " \
               f"{f'A penalty fee of up to ₦{maxPenaltyAmount:,} may apply.' if maxPenaltyAmount != 0 else ''}"

        return rule_message

    @staticmethod
    def reissue(maxPenaltyAmount):
        rule_message = f"To make significant changes to your booking, your ticket may need to be reissued. " \
               f"{f'A fee of up to ₦{maxPenaltyAmount:,} may apply, depending on the fare conditions and the type of change requested.' if maxPenaltyAmount != 0 else ''}"

        return rule_message

    @staticmethod
    def cancellation(maxPenaltyAmount):
        rule_message = f"You may cancel your booking, but a cancellation fee of up to ₦{maxPenaltyAmount:,} may apply. " \
               f"The penalty amount depends on how far in advance the cancellation is made. Some tickets may be non-refundable. " \
               f"{f'A cancellation fee of up to ₦{maxPenaltyAmount:,} may apply.' if maxPenaltyAmount != 0 else ''}"

        return rule_message


    def flight_rule(self, fareRules):
        rule_list = {}
        rule_list["rules"] = []
        
        if fareRules and "rules" in fareRules:  # Ensure fareRules and "rules" are present
            for rule in fareRules["rules"]:
                # Extract max penalty if present
                max_penalty = pricing.convert_usd_to_ngn(rule.get("maxPenaltyAmount", 0))

                # Handle each category type
                if rule["category"] == "EXCHANGE":
                    msg = self.exchange_rule(maxPenaltyAmount=max_penalty)
                    rule_list["rules"].append({
                        "category": "EXCHANGE",
                        "message": msg
                    })

                elif rule["category"] == "REVALIDATION":
                    msg = self.revalidation_rule()
                    rule_list["rules"].append({
                        "category": "REVALIDATION",
                        "message": msg
                    })

                elif rule["category"] == "REFUND":
                    msg = self.refund_rule(maxPenaltyAmount=max_penalty)
                    rule_list["rules"].append({
                        "category": "REFUND",
                        "message": msg
                    })

                elif rule["category"] == "REISSUE":
                    msg = self.reissue(maxPenaltyAmount=max_penalty)
                    rule_list["rules"].append({
                        "category": "REISSUE",
                        "message": msg
                    })

                elif rule["category"] == "CANCELLATION":
                    msg = self.cancellation(maxPenaltyAmount=max_penalty)
                    rule_list["rules"].append({
                        "category": "CANCELLATION",
                        "message": msg
                    })

        return rule_list

flightrules = FlightRules()