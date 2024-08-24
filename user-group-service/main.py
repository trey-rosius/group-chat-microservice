import json
import logging
import os
from models.cloud_events import CloudEvent
from dapr.clients import DaprClient
from fastapi import FastAPI, HTTPException

user_group_table = os.getenv('DAPR_USER_GROUP_TABLE', '')
pubsub_name = os.getenv('DAPR_PUB_SUB', '')
send_message_topic = os.getenv('DAPR_SEND_MESSAGE_TOPIC', '')

app = FastAPI()

logging.basicConfig(level=logging.INFO)


# subscribe to add group participant event
@app.post('/v1.0/subscribe/group/add-user')
def add_group_participant(event: CloudEvent):
    return
