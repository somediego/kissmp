
from kissmp.amounts import (
    amounts_buyer_create,
    amounts_seller_confirm,
    amounts_buyer_finish,
    amounts_buyer_cancel,
    amounts_seller_cancel,
    amounts_submit_review,
)
DEFAULT_FEE= 1000
BILLION= 1000000000
TRILLION= 1000000000000

PAYMENT= 1000
DEPOSIT= 250	# buyer's and seller's deposit size
EXTRA= 50	# seller's penalty size if cancelled.


class TestClassAmounts:
    price= 0.000000001
    fee  = DEFAULT_FEE
    fee_xch = 0.000000001
    file = {
        'price_kmojos': 1,
    }
    verbosity = 1

    def test_amounts(self):
        amount=  amounts_buyer_create(self.price, self.fee, self.verbosity)
        assert (self.price == float(amount['price_kmojos'])/BILLION)
        assert (self.fee_xch == float(amount['fee'])/TRILLION)
        assert (amount['buyer_amount'] == amount['price_kmojos'] * (PAYMENT + DEPOSIT))
        assert (amount['seller_amount']== amount['price_kmojos'] * (DEPOSIT + EXTRA))

        assert (amount['fee'] == self.fee)
        assert (amount['price']== self.price)
        assert (amount['price_kmojos'] == 1)
        assert (amount['buyer_amount'] == 1250)
        assert (amount['seller_amount']== 300)

        amount=  amounts_seller_confirm(self.file, self.fee, self.verbosity)
        assert (amount['fee'] == self.fee)
        assert (amount['old']== 1250)
        assert (amount['deposit'] == 250)
        assert (amount['penalty']== 50)
        assert (amount['contribution'] == 300)
        assert (amount['new']== 1550)

        amount=  amounts_buyer_finish(self.file, self.fee, self.verbosity)
        assert (amount['fee'] == self.fee)
        assert (amount['old']== 1550)
        assert (amount['buyer_deposit'] == 250)
        assert (amount['seller_deposit']== 300)
        assert (amount['new']== 0)

        amount=  amounts_buyer_cancel(self.file, self.fee, self.verbosity)
        assert (amount['fee'] == self.fee)
        assert (amount['old']== 1250)
        assert (amount['deposit'] == 250)
        assert (amount['new']== 0)

        amount=  amounts_seller_cancel(self.file, self.fee, self.verbosity)
        assert (amount['fee'] == self.fee)
        assert (amount['old']== 1550)
        assert (amount['deposit'] == 250)
        assert (amount['penalty']== 50)
        assert (amount['new']== 0)

        amount=  amounts_submit_review(self.fee, self.verbosity)
        assert (amount['fee'] == self.fee)
        assert (amount['treasury']== 2000000000)



