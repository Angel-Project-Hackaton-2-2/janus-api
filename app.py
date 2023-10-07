from fastapi import FastAPI
from api.user import router as user_router
from api.conversation import router as conversation_router
from api.diary import router as diary_router
from dotenv import load_dotenv
from kafka.errors import NoBrokersAvailable

load_dotenv()

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/test/{fingerprint}")
async def test(fingerprint: str):
    try:
        # producer = KafkaProducer(
        #     bootstrap_servers=[os.getenv("KAFKA_SERVER")],
        #     sasl_mechanism="SCRAM-SHA-256",
        #     security_protocol="SASL_SSL",
        #     sasl_plain_username=os.getenv("KAFKA_USERNAME"),
        #     sasl_plain_password=os.getenv("KAFKA_PASSWORD"),
        # )

        # producer.send("diaries", key=b"foo", value=b"bar")
        # producer.close()

        # initialize consumer based on fingerprint
        

        # consumer = KafkaConsumer(
        #     "angelproject.diaries",
        #     bootstrap_servers=[os.getenv("KAFKA_SERVER")],
        #     sasl_mechanism="SCRAM-SHA-256",
        #     security_protocol="SASL_SSL",
        #     sasl_plain_username=os.getenv("KAFKA_USERNAME"),
        #     sasl_plain_password=os.getenv("KAFKA_PASSWORD"),
        #     auto_offset_reset="earliest",
        # )

        # contents = []
        # for msg in consumer:
        #     msg = json.loads(msg.value.decode("utf-8"))
        #     print(msg)
        #     # document = msg["fullDocument"]
        #     # if document["fingerprint"] == fingerprint:
        #     #     print(document["fingerprint"])
        #     #     print(document["content"])

        # consumer.close()
        return {"message": "test"}
    except NoBrokersAvailable as e:
        print(f"Failed to connect to Kafka brokers: {e}")


app.include_router(user_router)
app.include_router(conversation_router)
app.include_router(diary_router)
