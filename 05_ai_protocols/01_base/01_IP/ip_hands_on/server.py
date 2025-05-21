from scapy.all import IP, Raw, sniff, send, conf

# Enable pcap for macOS
conf.use_pcap = True

# Configuration
interface = "en0"
server_ip = "139.135.36.98"
client_ip = "139.135.36.98"
protocol = 253

def handle_packet(packet):
    if packet.haslayer(IP) and packet.haslayer(Raw) and packet[IP].proto == protocol:
        print("Received packet:")
        packet.show()
        payload = packet[Raw].load.decode('utf-8', errors='ignore')
        # Only process ClientMessage, ignore ServerResponse to avoid loopback
        if payload == "ClientMessage" and packet[IP].src == client_ip:
            print(f"Received: {payload} from {packet[IP].src}")
            response = IP(src=server_ip, dst=client_ip, proto=protocol)/Raw(load="ServerResponse")
            send(response, iface=interface, verbose=1)
            print(f"Sent response to {client_ip}")

def main():
    print(f"Server listening on {server_ip} (interface: {interface})...")
    # Simplified filter: capture IP packets with proto 253
    sniff(iface=interface, filter=f"ip and proto {protocol}", prn=handle_packet, store=0)

if __name__ == "__main__":
    main()