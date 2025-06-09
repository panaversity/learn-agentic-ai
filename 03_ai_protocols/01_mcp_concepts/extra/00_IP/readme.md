# [Internet Protocol (IP)](https://www.cloudflare.com/learning/network-layer/internet-protocol/)

The IP protocol (Internet Protocol) operates at the network layer (Layer 3) and is responsible for addressing and routing packets. However, raw IP communication is uncommon because IP is typically used with transport protocols like TCP or UDP for reliable or connectionless communication. 

In this step, you’ll create a client that sends a “ClientMessage” packet and a server that responds with “ServerResponse,” using raw IP.

## What is IP?

IP is the internet’s mail system, sending **data packets** (small data chunks, like letters) between devices using IP addresses (e.g., `139.135.36.98`). It’s Layer 3 (network layer of the OSI model) and:
- **Addresses**: Labels packets with source/destination IPs (like sender/recipient).
- **Routes**: Finds network paths (like choosing roads).
- **Delivers**: Sends packets, no delivery guarantee (unlike TCP).

**Raw IP**: Your project skips TCP/UDP (Layer 4, adding reliability/ports) and uses raw IP packets with `proto=253`, like a letter with just an address and message. This is perfect for setting base to start thinking about Future AI protocols.

### What Are Data Packets?
A **data packet** is a unit of data sent over a network, like a letter carrying a message. Packets break data into small chunks for efficient transmission. In your project:
- **Client Packet**: Carries `ClientMessage` (13 bytes).
- **Server Packet**: Carries `ServerResponse` (12 bytes).

**Structure**:
- **Header**: The “envelope” with delivery info (20 bytes for IP):
  - **Version**: `4` (IPv4, your project).
  - **IHL**: Internet Header Length, `5` (20 bytes).
  - **Total Length**: Header + payload (e.g., 38 bytes for `ClientMessage`).
  - **ID**: Packet ID (`1`).
  - **Fragment Offset**: For split packets (`0`).
  - **TTL**: Time to Live, max hops (`64`).
  - **Protocol**: `253` (your custom ID, like a special stamp).
  - **Checksum**: Error check (auto-calculated).
  - **Source/Destination IP**: `139.135.36.98`. (YOUR IP ADDRESS)
- **Payload**: The “letter” content, e.g., `ClientMessage`.

**Example** (your server’s received packet):
```
###[ IP ]###
  version   = 4
  ihl       = 5
  len       = 38
  id        = 1
  frag      = 0
  ttl       = 64
  proto     = 253
  src       = 139.135.36.98
  dst       = 139.135.36.98
###[ Raw ]###
  load      = 'ClientMessage'
```

**Why Packets?**:
- **Efficiency**: Small chunks send faster.
- **Routing**: Packets find independent paths.
- **AI**: Agents send packets for real-time data (e.g., sensor updates).

### Why No Ports?
Ports (e.g., 80 for web) are like apartment numbers, used by TCP/UDP to identify apps. Raw IP uses:
- **IP Addresses**: `139.135.36.98`.
- **Protocol Number**: `253`.
- **Payloads**: `ClientMessage`/`ServerResponse`.

---

## Scapy
**[Scapy](https://scapy.net/)** Crafts packets (e.g., `IP()/Raw()`), sniffs (captures), and parses (e.g., `packet.show()`). It’s beginner-friendly, automating headers, ideal for AI protocol prototyping.

### What is Sniffing?
Sniffing captures packets, like checking your mailbox for specific letters. Scapy’s `sniff()` grabs packets matching a filter (e.g., `ip and proto 253`):
- **Server**: Captures `ClientMessage`.
- **Client**: Captures `ServerResponse`.
- **How**: `sniff(filter="ip and proto 253", prn=handle_packet)` checks packets on `en0`. If matched, `handle_packet` processes them.
- **AI**: Sniffs AI traffic for debugging.
- **Good Practice**: Specific filters (`proto 253`) avoid noise.

### What is Asyncio?
`asyncio` runs tasks concurrently, like juggling requests. It uses:
- **Event Loop**: Schedules tasks.
- **Coroutines**: `async def` functions pause during waits.
- **Why AI?**: Handles multiple agents efficiently.
- **Limit**: No raw IP support, but great for TCP/UDP.

## Setup

### Installation
```bash
uv init ip_hands_on
cd ip_hands_on
uv add scapy
```

## Hands-On: Raw IP Client-Server

Build:
- **Scapy**: Easy, with sniffing.
- **Socket**: Raw, byte-level.
- **Asyncio**: TCP, for AI scalability.

### Prerequisites
- **Python 3.13+**: Check: `python3 --version`.
- **Interface**: `en0` (Wi-Fi) for your ip. [Get your ip](https://whatismyipaddress.com/): i.e: `139.135.36.98`. Verify:
  ```bash
  ifconfig
  ```
  Find `en0` with an IP (not `127.0.0.1`) i.e: 192.168.0.198.
  ```

### Scapy Server (server.py)
Listens for `ClientMessage`.

```python
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
```

**Packet**:
- **Header**: `version=4`, `ihl=5`, `ttl=64`, `proto=253`, `chksum` auto.
- **Payload**: `ClientMessage` (13 bytes).
- **Good Practice**: Tight filter, valid `proto`.

### Scapy Client (client.py)
Sends `ClientMessage`.

```python
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
```


### Running the Code

1. **Start Server**:
   ```bash
   sudo uv run python server.py
   ```
   Expected:
   ```
   Server listening on 139.135.36.98 (interface: en0)...
   Received packet:
   ###[ IP ]###
      version   = 4
      ihl       = 5
      len       = 33
      proto     = 253
      src       = 139.135.36.98
      dst       = 139.135.36.98
   ###[ Raw ]###
      load      = b'ClientMessage'
   Received: ClientMessage from 139.135.36.98
   Sent 1 packets.
   Sent response to 139.135.36.98
   ```

2. **Run Client**:
   ```bash
   sudo uv run python client.py
   ```
   ```
   Sending packet to 139.135.36.98...
   Sent 1 packets.
   Waiting for response...
   Received packet:
   ###[ IP ]###
      version   = 4
      ihl       = 5
      len       = 34
      proto     = 253
      src       = 139.135.36.98
      dst       = 139.135.36.98
   ###[ Raw ]###
      load      = b'ServerResponse'
   Received: ServerResponse from 139.135.36.98
   ```

3. **Stop**:
   - Press `Ctrl+C`.

### Fallback: Loopback
If `139.135.36.98` fails:
- Update Scapy/`socket`:
  ```python
  interface = "lo0"
  server_ip = "127.0.0.1"
  client_ip = "127.0.0.1"
  ```
- Update `asyncio`:
  ```python
  server_ip = "127.0.0.1"
  ```

## Conceptual Overview

### Core Concept
IP delivers packets, like mailing letters. It’s connectionless and unreliable, foundational for AI protocols.

### Key Characteristics
- **Addressing**: IPs (e.g., `139.135.36.98`).
- **Routing**: Packet paths.
- **Connectionless**: Independent packets.
- **Unreliable**: Packet loss.
- **Fragmentation**: Splits packets.

### Strengths
- **Scalability**: Global networks.
- **Flexibility**: Custom protocols.
- **Foundation**: Internet traffic.

### Weaknesses
- **No Reliability**: Packet loss (your issue).
- **No Ports**: Custom logic.
- **Complexity**: Crafting packets.

### AI Protocol Use Cases
- **Custom Protocols**: `proto=253` for agents.
- **Real-Time**: Low latency.
- **Scalability**: `asyncio` for multi-agent systems.

### Protocol Stack
- **Layer**: Network (Layer 3).
- **Above**: TCP, UDP.
- **Below**: Ethernet, Wi-Fi.

## Troubleshooting

If client fails:
1. **Interface**:
   ```bash
   ifconfig
   ```
2. **Firewall**:
   ```bash
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off
   ```
3. **tcpdump**:
   ```bash
   sudo tcpdump -i en0 ip and proto 253
   ```
4. **Wireshark**:
   ```python
   from scapy.all import wireshark
   packets = sniff(iface="en0", filter="ip and proto 253", count=10)
   wireshark(packets)
   ```
5. **Broad Filter (Scapy)**:
   ```python
   sniff(iface=interface, prn=handle_packet, store=0)  # Server
   sniff(iface=interface, stop_filter=handle_response, timeout=15)  # Client
   ```
---

**IP is the invisible backbone of all agentic, multi-modal, and AI-driven communication. Every protocol and data exchange in this directory ultimately depends on IP for delivery.**

## Further Reading

- [Scapy Documentation](https://scapy.readthedocs.io/en/stable/)
- [Python Socket](https://docs.python.org/3/library/socket.html)
- [Python Asyncio](https://docs.python.org/3.15/library/asyncio.html)
- [Cloudflare: IP](https://www.cloudflare.com/learning/network-layer/internet-protocol/)