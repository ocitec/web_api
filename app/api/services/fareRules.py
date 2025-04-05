
class FlightRules:
	def __init__(self):
		pass	

	def exchange_rule(self, maxPenaltyAmount):
		rule_message = f"If you need to change your flight, a penalty fee of up to ₦{maxPenaltyAmount:,} will apply. \
							The fee is determined based on the airline's fare conditions and how far \
							in advance the change is made."

		return rule_message


	def revalidation_rule(self):
		rule_message = f"Revalidating your ticket is not applicable to this fare. If you need to make any changes to your flight, \
						you will need to reissue your ticket, which may involve additional costs or penalties."

		return rule_message

	def refund_rule(self, maxPenaltyAmount):
		rule_message = f"Refunds are available for this fare, subject to airline policies. " \
               f"A refund penalty may apply depending on when the cancellation occurs. " \
               f"Please note that some fares are non-refundable. " \
               f"{f'A penalty fee of up to ₦{maxPenaltyAmount:,} may apply.' if maxPenaltyAmount != 0 else ''}"


		return rule_message

	def reissue(self, maxPenaltyAmount):
		rule_message = f"To make significant changes to your booking, your ticket may need to be reissued. " \
               f"{f'A fee of up to ₦{maxPenaltyAmount:,} may apply, depending on the fare conditions and the type of change requested.' if maxPenaltyAmount != 0 else ''}"


		return rule_message


	def cancellation(maxPenaltyAmount):
		rule_message = f"You may cancel your booking, but a cancellation fee of up to ₦{maxPenaltyAmount:,} may apply. " \
               f"The penalty amount depends on how far in advance the cancellation is made. Some tickets may be non-refundable. " \
               f"{f'A cancellation fee of up to ₦{maxPenaltyAmount:,} may apply.' if maxPenaltyAmount != 0 else ''}"


		return rule_message



flightRules = FlightRules()