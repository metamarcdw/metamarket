# METAmarket - Trustless Federated Marketplaces
http://metamarket.biz

* * *

*REQUIREMENTS:*
```
Install Bitcoin Core - http://bitcoin.org
sudo apt-add-repository ppa:bitcoin/bitcoin
sudo apt-get update
sudo apt-get install bitcoin-qt
bitcoin-qt
```
*Install Bitmessage* - http://bitmessage.org
```
sudo apt-get install python openssl git python-qt4
git clone https://github.com/Bitmessage/PyBitmessage ~/PyBitmessage 
~/PyBitmessage/src/bitmessagemain.py

Edit ~/.config/PyBitmessage/keys.dat
Or   %APPDATA%\PyBitmessage\keys.dat on Windows
Add:
apienabled = True
apiport = 8442
apiinterface = 127.0.0.1
apiusername = username
apipassword = password

Edit ~/.bitcoin/bitcoin.conf
Or   %APPDATA%\Bitcoin\bitcoin.conf on Windows
Add:
server=1
testnet=1
rpcuser=user
rpcpassword=password
```

*INSTALL ON UBUNTU GNU/LINUX:*

**DEPENDENCIES:**
```
sudo apt-get install python-dev libssl-dev python-pip
sudo pip install simplejson
sudo pip install scrypt
sudo pip install pycrypto
sudo pip install simple-crypt
sudo pip install pycoin
export install_dir=~
cd $install_dir
git clone https://github.com/petertodd/python-bitcoinlib.git
python python-bitcoinlib/setup.py install
```

**INSTALL METAmarket:**
```
wget https://github.com/metamarcdw/metamarket/archive/v0.1.0-alpha.tar.gz
tar -x -f v0.1.0-alpha.tar.gz
cd metamarket-0.1.0-alpha
./mmcli.py --help
```

**INSTALL REGTEST SUITE (Linux):**
```
cd ~/.bitcoin
wget http://metamarket.biz/test_suite/regtest_conf.tar.gz
tar -x -f regtest_conf.tar.gz

cd $install_dir
wget http://metamarket.biz/test_suite/test_suite_scripts.tar.gz
tar -x -f test_suite_scripts.tar.gz
./copyscripts
```

*INSTALL ON WINDOWS:*
```
Download ZIP from https://github.com/metamarcdw/metamarket/releases/download/v0.1.0-alpha/metamarket-win32-0.1.0-alpha.zip
Extract metamarket-win32-0.1.0-alpha
Open Command Prompt
cd %HOMEPATH%\Downloads\metamarket-win32-0.1.0-alpha
mmcli.exe --help
```

* * *
*Usage:*
```
usage: mmcli.py [-h] [-e ENTITY] [-c CHAIN] [-p BTC_PORT]
                {checkinbox,processinbox,modbanuser,modbantag,modremoveoffer,showchan,showchanmsg,showmsglist,showmsg,createmsg,sendmsg,sendmarketoffer}
                ...

METAMARKET Command Line Interface

positional arguments:
  {checkinbox,processinbox,modbanuser,modbantag,modremoveoffer,showchan,showchanmsg,showmsglist,showmsg,createmsg,sendmsg,sendmarketoffer}
                        Program mode:
    checkinbox          Check your BM inbox for new MM Messages.
    processinbox        Parse your BM inbox for MM Messages.
    modbanuser          Moderator: Ban a User.
    modbantag           Moderator: Ban a Tag. (and all Offers bearing said
                        Tag)
    modremoveoffer      Moderator: Remove an Offer.
    showchan            Show a list of available chan messages.
    showchanmsg         Show a specific chan message.
    showmsglist         Show your current list of some type of MM Messages.
    showmsg             Show a specific MM Message in detail.
    createmsg           Create any new MM Message.
    sendmsg             Send any MM Message over BM.
    sendmarketoffer     As a Moderator, send your Market offer to the chan.

optional arguments:
  -h, --help            show this help message and exit
  -e ENTITY, --entity ENTITY
                        Choose which entity to act as: buyer, vendor, or mod.
  -c CHAIN, --chain CHAIN
                        Choose which blockchain to use: testnet or mainnet.
  -p BTC_PORT, --btcport BTC_PORT
                        Use a specific RPC port to connect to Bitcoin Core.
```
