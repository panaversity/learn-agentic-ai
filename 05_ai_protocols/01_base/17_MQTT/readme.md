# MQTT

MQTT is a lightweight, publish-subscribe messaging protocol designed for low-bandwidth, high-latency, or unreliable networks. It is widely used in IoT, sensor networks, and distributed agentic systems for efficient event-driven communication.

---

## Working with MQTT in Python: paho-mqtt

- [`paho-mqtt`](https://pypi.org/project/paho-mqtt/) is the most popular Python library for MQTT clients (publishers and subscribers).

### Installation

```bash
pip install paho-mqtt
```

### Note: MQTT Broker

To test locally, you need an MQTT broker. You can use [Mosquitto](https://mosquitto.org/) or a public broker like `test.mosquitto.org`.

### Example 1: MQTT Publisher

```python
import paho.mqtt.client as mqtt

broker = 'test.mosquitto.org'
topic = 'agentic-ai/demo'

client = mqtt.Client()
client.connect(broker, 1883, 60)
client.publish(topic, payload="Hello, MQTT!", qos=0, retain=False)
client.disconnect()
print("Message published.")
```

### Example 2: MQTT Subscriber

```python
import paho.mqtt.client as mqtt

broker = 'test.mosquitto.org'
topic = 'agentic-ai/demo'

def on_message(client, userdata, msg):
    print(f"Received: {msg.payload.decode()} on topic {msg.topic}")

client = mqtt.Client()
client.connect(broker, 1883, 60)
client.subscribe(topic)
client.on_message = on_message
print("Subscribed. Waiting for messages...")
client.loop_forever()
```

---

## Conceptual Overview

### What is MQTT?

MQTT (Message Queuing Telemetry Transport) is a lightweight, publish-subscribe network protocol that transports messages between devices. It is designed for connections with remote locations where a small code footprint is required or network bandwidth is limited.

### Key Characteristics

- **Publish-Subscribe:** Decouples message senders (publishers) and receivers (subscribers).
- **Lightweight:** Minimal protocol overhead, ideal for IoT and embedded systems.
- **QoS Levels:** Supports different levels of message delivery assurance.
- **Retained Messages:** Optionally retain last message on a topic.

### Strengths

- **Efficiency:** Low bandwidth and power usage.
- **Scalability:** Supports thousands of clients.
- **Reliability:** QoS and retained messages for robust delivery.

### Weaknesses

- **No Built-In Security:** Relies on TLS and broker configuration.
- **Simple Topic Model:** No advanced routing or filtering.

### Use Cases in Agentic and Multi-Modal AI Systems

- **IoT Devices:** Sensor data collection and control.
- **Event-Driven Agents:** Real-time notifications and coordination.
- **Edge AI:** Lightweight messaging for distributed intelligence.

### Place in the Protocol Stack

- **Layer:** Application Layer (OSI Layer 7)
- **Above:** IoT apps, agent frameworks
- **Below:** TCP/IP

### Further Reading

- [paho-mqtt Documentation](https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php)
- [MQTT.org](https://mqtt.org/)
- [Mosquitto Broker](https://mosquitto.org/)
