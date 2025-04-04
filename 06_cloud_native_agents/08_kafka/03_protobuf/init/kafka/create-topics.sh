#!/bin/bash

# This script assumes that Kafka bin utilities are available in the PATH.
# If they are not, you might need to specify the full path to kafka-topics.sh.

# Check if KAFKA_CREATE_TOPICS is set and not empty
if [[ -z "$KAFKA_CREATE_TOPICS" ]]; then
    echo "No topics to create."
    exit 0
fi

# Wait for Kafka to be ready
while ! nc -z $KAFKA_HOST $KAFKA_PORT; do
    echo "Waiting for Kafka to be available on $KAFKA_HOST:$KAFKA_PORT..."
    sleep 3
done
echo "Kafka is now reachable. Proceeding with topic creation."

# Loop over comma-separated topic definitions and create them
# Expected format: "topicname:partitions:replicationfactor:cleanup.policy"
IFS=','; for topicToCreate in $KAFKA_CREATE_TOPICS; do
    IFS=':' read -ra topicConfig <<< "$topicToCreate"
    if [ -z "${topicConfig[0]}" ] || [ -z "${topicConfig[1]}" ] || [ -z "${topicConfig[2]}" ]; then
        echo "Invalid topic configuration: $topicToCreate"
        continue
    fi
    topicName=${topicConfig[0]}
    partitions=${topicConfig[1]}
    replicationFactor=${topicConfig[2]}
    configEntries=""

    if [ ! -z "${topicConfig[3]}" ]; then
        configEntries="--config cleanup.policy=${topicConfig[3]}"
    fi

    # Create the topic
    kafka-topics.sh --create --bootstrap-server $KAFKA_HOST:$KAFKA_PORT \
                    --topic $topicName --partitions $partitions \
                    --replication-factor $replicationFactor $configEntries \
                    --if-not-exists
    echo "Created topic $topicName with $partitions partitions and replication factor of $replicationFactor."
done
