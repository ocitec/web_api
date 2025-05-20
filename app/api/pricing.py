class Pricing:

    def __init__(self):
        self.exchange_rate = 1603 # dynamically generate from back office or API

    def exchange_rate(self):
        pass

    def convert_usd_to_ngn(self, usd_amount):
        return round(float(usd_amount) * self.exchange_rate, 2)

    def apply_markup(self, price, markup_percentage=0):
        price = float(price)
        if markup_percentage == 0:
            return round(price, 2)
        return round(price * (1 + markup_percentage / 100), 2)


    def convert_currency(self, amount, from_currency, to_currency):
        if not amount:
            return None
        return round(currency_rates.convert(from_currency, to_currency, amount), 2)



pricing = Pricing()