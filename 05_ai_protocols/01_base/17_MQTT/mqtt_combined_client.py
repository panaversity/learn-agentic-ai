import paho.mqtt.client as mqtt
import time
import logging
import os
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - MQTT_DEMO - %(levelname)s - %(message)s')

# --- Configuration ---
# Use a public broker for ease of testing; for production, use your own secured broker.
MQTT_BROKER_HOST = "test.mosquitto.org"
MQTT_BROKER_PORT = 1883  # Default MQTT port (unencrypted)
# For TLS/SSL, use port 8883 or 8884 typically, and set up client.tls_set()

# Generate a unique client ID to avoid conflicts if multiple instances run
CLIENT_ID = f"daca-mqtt-demo-client-{uuid.uuid4().hex[:6]}"
TOPIC_BASE = "daca/agentic-ai/demo"
TOPIC_TEST = f"{TOPIC_BASE}/{CLIENT_ID}/test" # Unique topic for this client instance

# --- Global variable to signal message reception for the demo ---
message_received_flag = False
received_message_payload = None

# --- Callback functions ---
def on_connect(client, userdata, flags, rc, properties=None):
    """Called when the client connects to the broker."""
    if rc == 0:
        logging.info(f"Successfully connected to MQTT broker {MQTT_BROKER_HOST} with client ID {CLIENT_ID}")
        # Subscribe to the test topic upon successful connection
        # We use QoS 1 for subscription to ensure the subscribe message is acknowledged by the broker.
        (result, mid) = client.subscribe(TOPIC_TEST, qos=1)
        if result == mqtt.MQTT_ERR_SUCCESS:
            logging.info(f"Successfully subscribed to topic '{TOPIC_TEST}' with MID {mid}")
        else:
            logging.error(f"Failed to subscribe to topic '{TOPIC_TEST}'. Result code: {result}")
    else:
        logging.error(f"Failed to connect to MQTT broker. Return code: {rc} ({mqtt.connack_string(rc)})")
        # Handle specific error codes if needed
        if rc == mqtt.MQTT_ERR_CONN_REFUSED:
            logging.error("Connection refused. Check broker address, port, and firewall.")
        elif rc == mqtt.MQTT_ERR_NO_CONN:
            logging.error("No connection to broker. Network issue or broker down?")


def on_disconnect(client, userdata, rc, properties=None):
    """Called when the client disconnects from the broker."""
    logging.info(f"Disconnected from MQTT broker with result code {rc}. Client ID: {CLIENT_ID}")
    if rc != 0:
        logging.warning("Unexpected disconnection.")

def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    """Called when the broker responds to a subscribe request."""
    logging.info(f"Subscription acknowledged by broker. MID: {mid}, Granted QoS: {granted_qos}")

def on_publish(client, userdata, mid, properties=None):
    """Called when a message is successfully published (for QoS > 0)."""
    logging.info(f"Message MID {mid} published successfully.")

def on_message(client, userdata, msg):
    """Called when a message is received from a subscribed topic."""
    global message_received_flag, received_message_payload
    payload_str = msg.payload.decode('utf-8')
    logging.info(f"Received message on topic '{msg.topic}' (QoS {msg.qos}): \"{payload_str}\"")
    message_received_flag = True
    received_message_payload = payload_str
    # In a real application, you would process the message here.

def on_log(client, userdata, level, buf):
    """Paho MQTT internal logging callback."""
    # You can map paho's levels to your logging levels if needed
    # logging.debug(f"PAHO LOG (Level {level}): {buf}")
    pass


# --- Main client logic ---
def run_mqtt_demo():
    global message_received_flag, received_message_payload

    # 1. Create an MQTT client instance
    #    Using MQTTv5 by default if available with paho-mqtt 2.x.
    #    For MQTTv3.1.1 explicitly: client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=CLIENT_ID, protocol=mqtt.MQTTv311)
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID, clean_session=True)
    # Note on clean_session:
    # - True: Broker discards session state (subscriptions, queued messages for QoS 1/2) on disconnect.
    # - False: Broker keeps session state. Client must use same Client ID to resume.

    # 2. Assign callback functions
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe
    client.on_publish = on_publish
    client.on_message = on_message
    client.on_log = on_log # Optional: for detailed Paho logs

    # Optional: Configure Last Will and Testament (LWT)
    # This message is sent by the broker if the client disconnects ungracefully.
    lwt_topic = f"{TOPIC_BASE}/client_status/{CLIENT_ID}"
    lwt_payload = "offline - ungraceful disconnect"
    client.will_set(lwt_topic, payload=lwt_payload, qos=1, retain=True)
    logging.info(f"Configured LWT: Topic='{lwt_topic}', Payload='{lwt_payload}'")

    try:
        # 3. Connect to the broker
        logging.info(f"Attempting to connect to MQTT broker: {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT} as client {CLIENT_ID}")
        # client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, keepalive=60)
        # For paho-mqtt 2.x, connect_async is preferred if you are managing the loop elsewhere
        # but for this simple script, connect() with loop_start() is fine.
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, keepalive=60)
        # Keepalive: Max period in seconds between communications. Broker may disconnect client if exceeded.

        # 4. Start the network loop
        #    loop_start() runs a background thread to handle network traffic, callbacks, and reconnections.
        client.loop_start()
        logging.info("MQTT client network loop started.")

        # Wait a bit for connection and subscription to complete
        time.sleep(3) # Adjust as needed, esp. for slower networks/brokers

        if not client.is_connected():
            logging.error("Client failed to connect after waiting. Exiting.")
            client.loop_stop() # Ensure loop is stopped
            return

        # 5. Publish a test message
        message_to_publish = f"Hello from {CLIENT_ID} at {time.ctime()}!"
        # QoS 0: At most once (fire and forget)
        # QoS 1: At least once (acknowledgement required)
        # QoS 2: Exactly once (two-phase acknowledgement)
        # For this demo, using QoS 1 for publish.
        (result, mid) = client.publish(TOPIC_TEST, payload=message_to_publish, qos=1, retain=False)
        # Retain=False: Broker doesn't store this message for new subscribers.
        # Retain=True: Broker stores it as the "last known good" message for this topic.

        if result == mqtt.MQTT_ERR_SUCCESS:
            logging.info(f"Message \"{message_to_publish}\" published to '{TOPIC_TEST}' with MID {mid}. Waiting for echo...")
        else:
            logging.error(f"Failed to publish message to '{TOPIC_TEST}'. Result code: {result}")

        # 6. Wait for the message to be received by our own subscriber
        wait_time = 10  # seconds
        start_wait_time = time.time()
        while not message_received_flag and (time.time() - start_wait_time) < wait_time:
            time.sleep(0.1)

        if message_received_flag:
            logging.info(f"Successfully received our published message: \"{received_message_payload}\"")
        else:
            logging.warning(f"Did not receive the published message on '{TOPIC_TEST}' within {wait_time} seconds.")

        # 7. Publish a "client online" status message (could be retained)
        status_payload = "online"
        client.publish(lwt_topic, payload=status_payload, qos=1, retain=True) # LWT topic also used for status
        logging.info(f"Published status '{status_payload}' to LWT topic '{lwt_topic}' (retained).")

        # Keep the client running for a bit longer to allow for other interactions or manual testing
        logging.info("Client will remain active for another 10 seconds for observation (e.g. with MQTT Explorer). Press Ctrl+C to exit earlier.")
        time.sleep(10)

    except KeyboardInterrupt:
        logging.info("Keyboard interrupt detected. Shutting down.")
    except ConnectionRefusedError:
        logging.error(f"Connection refused by MQTT broker at {MQTT_BROKER_HOST}. Is it running and accessible?")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        # 8. Disconnect and stop the loop
        if client.is_connected():
            logging.info("Disconnecting from MQTT broker...")
            # Publish a final "offline" status before clean disconnect
            client.publish(lwt_topic, payload="offline - clean disconnect", qos=1, retain=True)
            time.sleep(0.5) # Give a moment for the message to send
            client.disconnect() # This will trigger on_disconnect
        client.loop_stop() # Stop the network loop thread
        logging.info("MQTT client network loop stopped. Exiting demo.")

if __name__ == "__main__":
    run_mqtt_demo() 