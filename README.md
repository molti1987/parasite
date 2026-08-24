# Network Difference Measurement Tool

This repository contains the source code developed for the master's thesis
"How can a Raspberry Pi be configured to transparently forward network traffic
for 802.1X and remain undetected by network scanners".

The program is intended for use only in a controlled laboratory setup or for testing purposes.

This tool uses a CLI Interface to set up the Bridge Mode and Parasite Mode.

The measurement process consists of the following steps:

1. Create the first and second bridge interfaces.
2. Start the measurement.
3. Stop the measurement.
4. Analyze the collected data.

# Example
- Start the CLI with: 
sudo python3 parasyte.py
- Create Bridge Interface
cb "int1" "int2"
=> This mode only enables the device do sniffer the network traffic

- Create two bridge interfaces
cp "int1" "int2" "Client MAC" "Client IP" "IP Bridge Interface"
=> This mode sets an IP address to the Network Bridge Interface to access the network. Inside a second terminal window, the duplycate.py script needs to be started within the parasite network namespace
Inside the script, the interface close to the client need to be adopted and also the IP and MAC of the Bridge interface
sudo ip netns exec parasite python3 duplicate.py

