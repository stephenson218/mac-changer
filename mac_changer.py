#! /usr/bin/env python3

import subprocess
import argparse
import re
import random
import shutil
import netifaces
import json
import os
import sys

def check_root():
    if os.getuid() != 0:
        print(f"[-] You need to run under root. Try : sudo python3 mac_changer_pro.py")
        sys.exit(1)

def get_arguments():
    parser = argparse.ArgumentParser(description="MAC Address Changer")
    parser.add_argument("-i", "--interface", required=True, help="Enter interface (ex: eth0, wlan0, docker0")
    parser.add_argument("-m", "--mac", help="Enter new MAC address.")
    parser.add_argument("-r", "--random", action="store_true", help="Create random MAC address.")
    parser.add_argument("--restore", action="store", help="Restore original MAC address from bcakup")
    return parser.parse_args()

def get_current_mac(interface):
    if shutil.which("ip"):
        result = subprocess.run(["ip", "link", "show", interface], capture_output=True, text=True)
        mac_line = re.search(r"link/ether\s+([0-9a-fA-F:]+)", result.stdout)
        if mac_line:
            return mac_line.group(1).upper()
    if shutil.which("ifconfig"):
        result = subprocess.run(["ifconfig", interface], capture_output=True, text=True)
        mac_address = re.search(r"([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:"
                                r"[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})", result.stdout)
        if mac_address:
            return mac_address.group(0).upper()
    return None

def generate_random_mac():
    first_byte = random.randint(0x00, 0xFF)
    first_byte = (first_byte | 0x02) & 0xFE
    mac_bytes = [first_byte]
    for _ in range(5):
        mac_bytes.append(random.randint(0x00, 0xFF))
    return ":".join(f"{byte:02x}" for byte in mac_bytes).upper()

def run_command(command):
    subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def change_mac(interface, new_mac):
    commands = []
    if shutil.which("ip"):
        commands = [
            f"ip link set dev {interface} down",
            f"ip link set dev {interface} address {new_mac}",
            f"ip link set dev {interface} up"
        ]
    elif shutil.which("ifconfig"):
        commands = [
            f"ifconfig {interface} down",
            f"ifconfig {interface} hw ether {new_mac}",
            f"ifconfig {interface} up"
        ]
    else:
        print("[-] Unsupported system: neither 'ip' nor 'ifconfig' found.")
        sys.exit(1)
    print(f"[*] Changing MAC address for {interface} to {new_mac}")
    for cmd in commands:
        run_command(cmd)

    final_mac = get_current_mac(interface)
    if final_mac == new_mac:
        print(f"[+] MAC successfully changed to {final_mac}")
    else:
        print("[-] Failed to change MAC address.")

def save_original_mac(interface, mac):
    backup_file = "mac_backup.json"
    try:
        data = {}
        if os.path.exists(backup_file):
            with open(backup_file, "r") as file:
                data = json.load(file)
        data[interface] = mac
        with open(backup_file, "w") as file:
            json.dump(data, file, indent=4)
        print(f"[+] Original MAC {mac} saved for {interface}")
    except Exception as e:
        sys.exit(f"[-] Error saving backup: {e}")

def load_original_mac(interface):
    try:
        with open("mac_backup.json", "r") as file:
            data = json.load(file)
            return data.get(interface)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def main():
    check_root()
    args = get_arguments()

    if args.restore:
        original_mac = load_original_mac(args.interface)
        if not original_mac:
            print(f"[-] No backup MAC found for {args.interface}")
            sys.exit(1)
        change_mac(args.interface, original_mac)
        print(f"[+] Restore original MAC: {original_mac}")
        sys.exit(0)

    if args.interface not in netifaces.interfaces():
        print(f"[-] Interface {args.interface} does not exist.")
        sys.exit(1)

    current_mac = get_current_mac(args.interface)
    if not current_mac:
        print(f"[-] Could not retrieve MAC for {args.interface}. Check interface status.")
        sys.exit(1)

    save_original_mac(args.interface, current_mac)

    if args.random:
        new_mac = generate_random_mac()
    else:
        new_mac = args.mac
        if not re.match(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$", new_mac):
            print("[-] Invalid MAC format. Use format like 00:1a:2b:3c:4d:5e")
            sys.exit(1)

    change_mac(args.interface, new_mac)

if __name__ == "__main__":
    main()