# etcctracker

Setup instructions:
```
sudo pip3 install -r requirements.txt 
```

Allow inbound HTTP traffic to the server:
```
iptables -A INPUT -i eth0 -p tcp --dport 80 -m state --state NEW,ESTABLISHED -j ACCEPT
iptables -A OUTPUT -o eth0 -p tcp --sport 80 -m state --state ESTABLISHED -j ACCEPT
```

To start the server
```
screen -S server
sudo python3 server.py
```

To start the watcher
```
screen -S watcher
sudo python3 watcher.py
```

To send emails for alerts, please update watcher.py's variables:
```
gmail_user = '[gmail address]'
gmail_password = '[gmail password]'
```
