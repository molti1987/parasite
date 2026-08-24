# Network Parasite for 802.1X protected Networks

This repository contains the source code developed for the master's thesis:
"How can a Raspberry Pi be configured to transparently forward network traffic
for 802.1X and remain undetected by network scanners".

The program is intended for use only in a controlled laboratory setup or for testing purposes.
TCP traffic ist currentl not supported in Parasite Mode.

This tool provides a command line interface (CLI) to configure Bridge- and Parasite-Mode

# Script
parasite.py  => main CLI application
duplicate.py => packet duplication

# Example
- Start the CLI with: 
sudo python3 parasyte.py

- Create Bridge Interface

cb "int1" "int2"

=> This mode only enables the device to transparently forward and capture network traffic

- Create two bridge interfaces
 
cp "int1" "int2" "Client MAC" "Client IP" "IP Bridge Interface"

=> This mode assigns an IP address to the network bridge interface. In a second terminal, the duplicate.py script must be started within the "parasite" network namespace"
Inside the script, the interface close to the client need to be adopted and also the IP and MAC of the Bridge interface
sudo ip netns exec parasite python3 duplicate.py

