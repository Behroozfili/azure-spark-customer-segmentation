FROM openjdk:11

RUN apt-get update && \
    apt-get install -y python3 python3-pip curl wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip

ENV SPARK_VERSION=3.5.5
ENV SPARK_HOME=/opt/spark
ENV PATH=${SPARK_HOME}/bin:${SPARK_HOME}/sbin:${PATH}
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

RUN curl -fL https://dlcdn.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz -o /opt/spark.tgz && \
    tar -xzf /opt/spark.tgz -C /opt/ && \
    mv /opt/spark-${SPARK_VERSION}-bin-hadoop3 ${SPARK_HOME} && \
    rm /opt/spark.tgz && \
    chmod +x ${SPARK_HOME}/bin/* && \
    chmod +x ${SPARK_HOME}/sbin/*

RUN pip3 install --no-cache-dir pyspark==${SPARK_VERSION} python-dotenv numpy  pytest

WORKDIR /app
COPY ./src /app/src
COPY .env /app/.env
COPY ./tests /app/tests
ENV PYTHONPATH=/app/src

CMD ["python3", "src/main.py"]