MAC Changer

A simple and efficient MAC address changer written in Python. This script allows users to:

Change their MAC address manually or generate a random one.

Restore the original MAC address from a backup.

Ensure network anonymity and security testing.

Features

Change MAC address of a network interface
Generate a random MAC address
Restore the original MAC from backup
Works with modern Linux distributions (using ip command)

Installation

Clone the repository:

git clone https://github.com/stephenson218/mac-changer.git
cd mac-changer

Usage

Run the script with root privileges:

sudo python3 mac_changer.py -i eth0 -r   # Generate random MAC
sudo python3 mac_changer.py -i wlan0 -m 00:1A:2B:3C:4D:5E  # Set specific MAC
sudo python3 mac_changer.py -i eth0 --restore  # Restore original MAC

Requirements

Python 3

Linux OS (Tested on Ubuntu, Kali, Debian)
