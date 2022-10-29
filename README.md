Kiss My Parts
=======

Decentralized escrow. 

Choose a seller, create a payment file, and exchange chia for any product or service.

Exchange anything. No middle man. No KYC. Open source. 

Built for [Chia](https://www.chia.net/) in [Chialisp](https://chialisp.com/).

[How it works](https://github.com/sometwit/kissmp#how-it-works)

[Get started](https://github.com/sometwit/kissmp/blob/main/GETSTARTED.md)

[FAQ](https://github.com/sometwit/kissmp/blob/main/FAQ.md)

Install
-------

**Ubuntu/Debian/MacOSs**
```
git clone https://github.com/sometwit/kissmp.git
cd kissmp
python3 -m venv venv
. ./venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install .
deactivate
```
(If you're on an M1 Mac, make sure you are running an ARM64 native python virtual environment)

troubleshooting, ubuntu/debian might need:
```
sudo apt-get install build-essential python3-dev git
```

**Windows Powershell**
```
git clone https://github.com/sometwit/kissmp.git
cd kissmp
py -m venv venv
./venv/Scripts/activate
python -m pip install --upgrade pip setuptools wheel
pip install .
deactivate
```

Run
-------
Requires synced, running light wallet.

**Ubuntu/Debian/MacOSs**
```
. ./venv/bin/activate
kissmp
```

**Windows Powershell**
```
./venv/Scripts/activate
kissmp
```


How it works
-------

There are just one buyer and one seller, interacting with chia smart coins, no arbitrage or middle-man involved.

Buyer will deposit 125% of price into a smart coin of his control, for a specific seller, and a payment file will be created to locate that coin. That could be recover by buyer at any time while seller has not locked that payment yet.

Seller has power enough to lock buyer’s amount if he is willing to deposit on top 30% of price.
Seller could decide to cancel after locked, buyer will have back 130% of the price. and seller 25% or price.

Once Seller has locked the amount, trade off-chain can begin by seller. And trade will not be over until buyer confirm received. Once confirmed by buyer, seller will received his 30% deposit plus 100% payment, and buyer will have back his 25% deposit. 


