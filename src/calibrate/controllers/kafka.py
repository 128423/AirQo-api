import os

from confluent_kafka.avro import AvroConsumer, AvroProducer
from confluent_kafka.avro.serializer import SerializerError
from models import regression as rg

# Ref: https://github.com/confluentinc/confluent-kafka-python

BOOTSTRAP_SERVERS = os.getenv("BOOTSTRAP_SERVERS", "34.123.249.54:31000")
SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://127.0.0.1:8081")
INPUT_TOPIC = os.getenv("INPUT_TOPIC")
OUTPUT_TOPIC = os.getenv("OUTPUT_TOPIC")
CONSUMER_GROUP = os.getenv("CONSUMER_GROUP")


def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))


def produce_measurements(measurements, key):

    avr_producer = AvroProducer({
        'bootstrap.servers': BOOTSTRAP_SERVERS,
        'on_delivery': delivery_report,
        'schema.registry.url': SCHEMA_REGISTRY_URL
    })
    avr_producer.produce(topic=OUTPUT_TOPIC, value=measurements, key=key)
    avr_producer.flush()


def consume_measurements():
    consumer = AvroConsumer({
        'bootstrap.servers': BOOTSTRAP_SERVERS,
        'group.id': CONSUMER_GROUP,
        'schema.registry.url': SCHEMA_REGISTRY_URL})

    consumer.subscribe([INPUT_TOPIC])

    rgModel = rg.Regression()
    hourly_combined_dataset = rgModel.hourly_combined_dataset

    while True:
        try:
            msg = consumer.poll(10)

        except SerializerError as e:
            print("Message deserialization failed: {}".format(e))
            break

        if msg is None:
            continue

        if msg.error():
            print("AvroConsumer error: {}".format(msg.error()))
            continue

        calibrated_measurements = []

        print(msg.value())

        try:

            measurements = list(dict(msg.value()))
            for measure in measurements:

                try:
                    measurement = dict(measure)

                    pm25 = measurement.get('pm_2_5').get('value', None)
                    pm10 = measurement.get('pm10').get('value', None)
                    temperature = measurement.get('internalTemperature').get('value', None)
                    humidity = measurement.get('internalHumidity').get('value', None)
                    datetime = measurement.get('time', None)

                    if pm25 and pm10 and temperature and humidity and datetime:
                        calibrated_value = rgModel.random_forest(datetime, pm25, pm10, temperature,
                                                                 humidity, hourly_combined_dataset)
                        measurement["pm_2_5"]["calibratedValue"] = calibrated_value

                    calibrated_measurements.append(measurement)

                except Exception as ex:
                    print(ex)
                    continue

            if calibrated_measurements:
                produce_measurements(calibrated_measurements, "tenant")

        except Exception as e:
            print(e)

    consumer.close()


if __name__ == "__main__":
    consume_measurements()
