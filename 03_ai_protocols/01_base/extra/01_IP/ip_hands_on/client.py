from scapy.all import IP, Raw, send, sniff, conf

# Enable pcap for macOS
conf.use_pcap = True

# Configuration
interface = "en0"
server_ip = "139.135.36.98"
client_ip = "139.135.36.98"
protocol = 253

def handle_response(packet):
    if packet.haslayer(IP) and packet.haslayer(Raw) and packet[IP].proto == protocol:
        print("Received packet:")
        packet.show()
        payload = packet[Raw].load.decode('utf-8', errors='ignore')
        if payload == "ServerResponse" and packet[IP].src == server_ip:
            print(f"Received: {payload} from {packet[IP].src}")
            return True
    return False

def main():
    packet = IP(src=client_ip, dst=server_ip, proto=protocol)/Raw(load="ClientMessage")
    print(f"Sending packet to {server_ip}...")
    send(packet, iface=interface, verbose=1)

    print("Waiting for response...")
    sniff(iface=interface, filter=f"ip and proto {protocol} and src host {server_ip}", stop_filter=handle_response, timeout=15)

if __name__ == "__main__":
    main()