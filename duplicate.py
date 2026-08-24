from scapy.all import sniff, sendp, IP, TCP, UDP, Ether, getmacbyip, get_if_hwaddr, ICMP
INTERFACE="eth2"
NEW_DST = "192.168.8.14"
NEW_MAC = "20:7b:d2:e2:a4:39"


def change_packet(packet):
	if IP in packet:

		#IP overwrite
		packet[IP].dst = NEW_DST
		#Checksum delete for changes
		del packet[IP].chksum
		del packet[IP].len
		if packet.haslayer("TCP"):
			del packet["TCP"].chksum
		if packet.haslayer("UDP"):
			del packet["UDP"].chksum
		if packet.haslayer("ICMP"):
			del packet["ICMP"].chksum
		packet[Ether].dst = NEW_MAC
		if packet.haslayer("ICMP"):
			print(f"Neu: {packet[IP].src }..{packet[Ether].src} .... {packet[IP].dst}..{packet[Ether].dst}")

		sendp(packet, iface="br0", verbose=False)
sniff(iface=INTERFACE, prn=change_packet, store=False)
