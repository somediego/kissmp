Kiss My Parts
=======

Decentralized escrow. 

Exchange anything. No middle man. No KYC. Open source. 

Built for [Chia](https://www.chia.net/) in [Chialisp](https://chialisp.com/).


How it works
-------

[Chia](https://www.chia.net/) created a new world thanks to [Offers](https://www.chia.net/offers/), this project try to focus on an off-chain side of the coin.

Choose a seller, create a payment file, and exchange chia for any off-chain product or service.

[Introdution](https://kissmy.parts/?page_id=2)

[Deep dive FAQ](https://kissmy.parts/?page_id=110)


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


Where to buy or sell
-------
Anywhere or anybody that accepts XCH.
You can start here:
https://kissmy.parts


Others
-------
Thanks to Quexington and Kronus91, I have learnt most of the chia stuff reading through their open code.
