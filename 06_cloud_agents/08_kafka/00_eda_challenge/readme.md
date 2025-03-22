# A Challenge: FastAPI Event Driven Microservices Development With Kafka, KRaft, Docker Compose, and Poetry 

Event-driven architecture (EDA) is a popular design pattern for building applications that react to events.  

[Kafka Visualization](https://softwaremill.com/kafka-visualisation/)

[official Documentation](https://kafka.apache.org/documentation/)

[Textbook: Kafka: The Definitive Guide: Real-Time Data and Stream Processing at Scale 2nd Edition](https://www.amazon.com/Kafka-Definitive-Real-Time-Stream-Processing/dp/1492043087/ref=sr_1_2)

Here's a breakdown of why it's used and its pros and cons:

**Why use EDA?**

* **Loose coupling:**  Components are independent and communicate through events,  making them easier to develop, maintain, and update. 
* **Scalability:**  EDA can handle increased load by adding more consumers to process events.
* **Real-time processing:**  Events can trigger actions as they happen, enabling real-time applications.

**Advantages of EDA**

* **Flexibility:**  EDA can accommodate changing business needs by adding new event types.
* **Resilience:**  If one part of the system fails, others can continue processing events.
* **Concurrency:**  Multiple consumers can process events simultaneously.

**Disadvantages of EDA**

* **Complexity:**  Designing and debugging EDA systems can be more complex than traditional architectures.
* **Monitoring:**  Troubleshooting issues can be challenging due to asynchronous communication.
* **Testing:**  Testing event-driven systems can require specialized tools and techniques.

Overall, EDA is a powerful approach for building scalable and responsive applications.  However, it's important to consider the trade-offs before implementing it.

## Gemini Chat:

https://g.co/gemini/share/fca64d9f215c

https://g.co/gemini/share/e386f9de6d20


## How To Learn Apache Kafka By Watching and Doing in 2024

[Kafka 101 Video Tutorial](https://developer.confluent.io/courses/apache-kafka/events/)

https://www.projectpro.io/article/learn-kafka/970

Upcoming Online Talks: Building Event-Driven Microservices with Apache Kafka

https://www.confluent.io/resources/online-talk/microservices-and-apache-kafka/


## Kafka 3.7 Docker Image

Follow this Quick Start with Docker and KRaft: 

https://kafka.apache.org/quickstart


**Using Kafka from Console with KRaft Using Docker Image**

Get the docker image

    docker pull apache/kafka:3.7.0

Start the kafka docker container

    docker run -p 9092:9092 apache/kafka:3.7.0

Open another console and check to see if container running:

    docker ps

Copy the container name, and give the following command to attach:

    docker exec -it <container-name> /bin/bash

Note: Kafka commands are in this directory in the container 

    /opt/kafka/bin

CREATE A TOPIC TO STORE YOUR EVENTS

Kafka is a distributed event streaming platform that lets you read, write, store, and process events (also called records or messages in the documentation) across many machines.

Example events are payment transactions, geolocation updates from mobile phones, shipping orders, sensor measurements from IoT devices or medical equipment, and much more. These events are organized and stored in topics. Very simplified, a topic is similar to a folder in a filesystem, and the events are the files in that folder.

So before you can write your first events, you must create a topic. Open another terminal session and run:

    /opt/kafka/bin/kafka-topics.sh --create --topic quickstart-events --bootstrap-server localhost:9092


All of Kafka's command line tools have additional options: 

Note: run the kafka-topics.sh command without any arguments to display usage information. For example, it can also show you details such as the partition count of the new topic:

    /opt/kafka/bin/kafka-topics.sh --describe --topic quickstart-events --bootstrap-server localhost:9092

Topic: quickstart-events        TopicId: NPmZHyhbR9y00wMglMH2sg PartitionCount: 1       ReplicationFactor: 1	Configs:
    Topic: quickstart-events Partition: 0    Leader: 0   Replicas: 0 Isr: 0


WRITE SOME EVENTS INTO THE TOPIC

A Kafka client communicates with the Kafka brokers via the network for writing (or reading) events. Once received, the brokers will store the events in a durable and fault-tolerant manner for as long as you need—even forever.

Run the console producer client to write a few events into your topic. By default, each line you enter will result in a separate event being written to the topic.

    /opt/kafka/bin/kafka-console-producer.sh --topic quickstart-events --bootstrap-server localhost:9092

This is my first event

This is my second event

You can stop the producer client with Ctrl-C at any time.

READ THE EVENTS

Open another terminal session and run the console consumer client to read the events you just created:

    /opt/kafka/bin/kafka-console-consumer.sh --topic quickstart-events --from-beginning --bootstrap-server localhost:9092

This is my first event

This is my second event

You can stop the consumer client with Ctrl-C at any time.

Feel free to experiment: for example, switch back to your producer terminal (previous step) to write additional events, and see how the events immediately show up in your consumer terminal.

Because events are durably stored in Kafka, they can be read as many times and by as many consumers as you want. You can easily verify this by opening yet another terminal session and re-running the previous command again.

# Kafka UI 

This is a popular open-source web UI specifically designed for viewing Kafka topics, messages, brokers, consumer groups, and even lets you create new topics. It's known for being lightweight, easy to set up, and supports secure connections. You can find the project on Github here:

https://github.com/provectus/kafka-ui

https://github.com/provectus/kafka-ui?tab=readme-ov-file#getting-started

    docker network create -d bridge kafka-net

    docker network ls

    docker run -p 9092:9092 --network kafka-net --name mykafka apache/kafka:3.7.0

    docker run -it -p 8080:8080 --network kafka-net -e DYNAMIC_CONFIG_ENABLED=true provectuslabs/kafka-ui

*Note: We will learn docker compose later, how to use docker compose to configure kafka, right now after a minutes it will go offline.

Then access the web UI at http://localhost:8080

In order to integrate kafka broker with kafkaUI use container name in the host

## Kafka with KRaft setup using Docker Compose | Kafka tutorial for beginners

https://www.youtube.com/watch?v=aTl2iSCynVc

https://medium.com/@tetianaokhotnik/setting-up-a-local-kafka-environment-in-kraft-mode-with-docker-compose-and-bitnami-image-enhanced-29a2dcabf2a9


## The Evolution of Kafka Architecture: From ZooKeeper to KRaft

https://romanglushach.medium.com/the-evolution-of-kafka-architecture-from-zookeeper-to-kraft-f42d511ba242

As of Kafka 3.5, the ZooKeeper mode is being deprecated, and it will be completely removed from Kafka with the release of Kafka 4.0.



## FastAPI and Apache Kafka

https://docs.google.com/document/d/15usu1hkrrRLRjcq_3nCTT-0ljEcgiC44iSdvdqrCprk/edit?usp=sharing


## Tutorial Part 1:

https://ahmed-nafies.medium.com/fastapi-event-driven-development-with-kafka-zookeeper-and-docker-compose-a-step-by-step-guide-3e07151c3e4d


## Tutorial Part 2:

https://ahmed-nafies.medium.com/fastapi-event-driven-development-with-kafka-zookeeper-and-docker-compose-a-step-by-step-guide-417f88a0fb23


## Tutorial Part 3:

https://ahmed-nafies.medium.com/fastapi-event-driven-development-with-kafka-zookeeper-and-docker-compose-a-step-by-step-guide-53fd739b1310



## Event-Driven Architectures with Kafka and Python

https://itnext.io/event-driven-architectures-with-kafka-and-python-41114de4938b

## Understanding Docker & Deploying Apache Kafka on docker in a few simple steps

https://www.linkedin.com/pulse/understanding-docker-deploying-apache-kafka-few-simple-jatin-rajpal/

## You will develop a template like this once you are an expert:

https://stackoverflow.com/questions/75839415/kafka-fastapi-docker-template

