
FAQ
=======

Where and how?
-------

Everything runs on chia blockchain, buyer and seller, peer to peer, no arbitrage, no third party and no need for a website.


Difference with “Offer Files”?
-------

So Offer files will not create a transaction, until a counter party take the other side of an offer.
With a payment file, the transaction has already been done to a smart coin, and it is sitting there waiting for you to take your money back, or for a seller to lock that money.
Plus these payment files are oriented to trade chia with off-chain stuff.


What is a payment file?
-------

It is just info about a smart coin, into a text file, so buyer and seller can locate that coin and use it.
If you loose that file, you can ask seller or buyer to send you again a copy, it is in his interest to make sure you can find that coin.
If you both loose the file, it still could be found by looking at your wallet transactions, of course, that it is not a comfortable way.


How to create a Payment file?
-------

Buyer will create a file, with the help of https://github.com/sometwit/kissmp .


I am the buyer or the seller?
-------

The one that offers chia is always the buyer, the one that offers a product that is not chia, it is always the seller.


Can anyone lock that money?
-------

No. If you send a file to 3 or 4 sellers, just the one that you specified when creating that payment file will be the only one with power to do so.


How does a buyer specify a seller?
-------

Seller will publicly publish, or send to buyer, his “cupkey”, that it will get with https://github.com/sometwit/kissmp .


What is a cupkey?
-------

It is just a “synthetic wallet public key on index 84”, way too long, so just “cupkey” for short. Used to identify sellers and give them some control over the coin.


What kind of control has a seller over the new created smart coin?
-------

To lock that smart coin or cancel locking that smart coin. That is all the control a seller will have.


What kind of control has a buyer over the new created smart coin?
-------

If not locked by seller yet, It will be able to have his money back at any time.

if it is locked by seller, it will be the only one with power to confirm that a trade has finished happily as it supposed to. So everyone can get back their extra deposits and payment delivered to seller.


Can seller lock and disappear?
-------

Yes, but it will need nearly 1/3 of price to lock it, no really edge for misbehaving sellers to do any kind of profitable business doing so.


Can buyer receive a product and not finishing the trade, so seller will not receive his payment?
-------

Yes, but same thing here, buyer will have 1/4 of price as deposit, it is in his interest to get his deposit back, no edge for misbehaving buyers to get any king of economic benefit from doing that, just the opposite.


What if both behave and trade get lost?
-------

That can happen with big middle-man companies too. Here you do not pay extra to a middle-man for taking care of everything. But you might need to pay extra for a tracking number. So buyer can see why it is taking so long, and see if seller really send it to the right address, or somewhere else. Tracking numbers will be more important in these environments, where seller has to prove to a buyer that a product is not lost yet.


How does a seller confirm or deliver trade?
-------

It is buyer and seller own duty, decide what are the conditions before a trade begins. If a packet will be delivered with a tracking number, or for a cryptocurrency will have some specific exchange rate to use, or spread, or for fiat what will be the channel of exchange and how long it will take.

Buyer and seller must have a medium of contact, for sensible information to happen like real world address, or some paypal info, or a specific place to meet, or just a bitcoin wallet address.

You two will be writing your own rules on the fly.

Eventually some will get experience, share it, and they will teach us all.


If this is free, how this project earn money?
-------

It does not, however, I added a command to review cupkeys on blockchain, so anyone can give negative or positive stars to any cupkey, those reviews stay there forever, and they are not necessary for any trade to happen, just an extra silly utility. Cost 0.002 XCH, plus some day might be enough for this project to maintain itself.


How to see a cupkey reviews?
-------

```
kissmp review info
```

One command.


How to deal with really small prices?
-------

Minimum required price is 1000 mojos and multiples, so 1500 mojos will not work, but 1000, 2000, 3000, etc. will.


Other things to know?
-------

You do not need a full node, just a light wallet.

use “–verbosity” flag with any command if you want to print spendbundles, or some extra detail.

All commands will ask you for confirmation before pushing any transaction to the network.



