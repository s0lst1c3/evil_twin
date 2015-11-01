# evil_twin

Python script for performing basic Evil Twin attacks on open wifi networks. Developed as part of my series of tutorials on Fake AP attacks, which can be found on [solstice.me](http://solstice.me/python/wireless/scripting/2015/10/04/python-evil-twin/).


##Dependencies

The following packages must be installed in order for evil\_twin.py to run:
- hostapd
- dnsmasq
- iptables

##Running

To run evil\_twin.py, just use the python as shown here:

	python evil_twin.py -c <target ap channel> -u <upstream nic> -i <gateway nic> -s <target essid>
