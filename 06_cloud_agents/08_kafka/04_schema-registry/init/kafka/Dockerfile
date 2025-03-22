FROM openjdk:8-jre-slim
# ARG kafka_version
# ARG kafka_package
WORKDIR /app

ENV KAFKA_HOME=/app/3.7.0 PATH=$PATH:.

RUN apt update \
	&& apt install -y bash \
	&& apt install -y wget \
	&& wget http://www.apache.org/dist/kafka/3.7.0/$kafka-3.7.0-src.tgz \
	&& tar xzf kafka-3.7.0-src.tgz \
	&& chmod +x /app \
	&& rm -rf /var/cache/apk/*

COPY create-topics.sh /app/

ENTRYPOINT ["create-topics.sh"]