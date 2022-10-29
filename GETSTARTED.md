

Download app from https://github.com/sometwit/kissmp and choose an item to buy from any website, as long seller accepts chia.


Buyer
=======

```
kissmp buyer
```
Command to see different buyer options.


Create a payment file:
-------

```
kissmp buyer create
```
To create payment file. You will need seller’s “cupkey”, that he will provide to you. Send a copy of the file to the seller, plus any extra info he could need to deliver.


Cancel payment file:
-------

```
kissmp buyer calcel <payment_file>
```
If seller has not accepted the payment yet, you can get back your money at any time. If seller has already accepted the payment, money is locked and seller has already started to send the product.


Confirm everything went alright:
-------

```
kissmp buyer finish <payment_file>
```
You and seller will have your deposit amounts back, and payment will be delivered to the seller.


Seller
=======

```
kissmp seller
```
Command to see different seller options.


Preparation:
-------

```
kissmp seller cupkey
```
Will show you a key you will need, to sell anything. Create a listing, and wait for a buyer to send you a payment file.


Confirm payment file:
-------

```
kissmp seller confirm <payment_file>
```
If you are happy with place to deliver, and you have product on stock. Money will be locked. You can start the trade, and wait for buyer to confirm received that.


Cancel sell:
-------

```
kissmp seller cancel <payment_file>
```
Command to cancel, if you can not deliver after locking the payment. A penalty will be taken from your deposit and give it to buyer in exchange for locking his money.

