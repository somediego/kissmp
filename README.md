Kiss My Parts
=======

Decentralized escrow. 

Exchange anything. No middle man. No KYC. Open source. 

Built for [Chia](https://www.chia.net/) in [Chialisp](https://chialisp.com/).

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
[introdution](https://kissmy.parts/?page_id=2)
[deep dive](https://kissmy.parts/?page_id=110)


Where to buy or sell
-------
Anywhere that accepts XCH.
You can start here:
https://kissmy.parts


Others
-------
Thanks to Quexington and Kronus91, I have learnt most of the chia stuff reading through their open code.
