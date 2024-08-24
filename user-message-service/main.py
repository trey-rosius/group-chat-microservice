import grpc
import json

from dapr.clients import DaprClient
from fastapi import FastAPI, HTTPException
import logging
import os
from models.cloud_events import  CloudEvent

user_messages_db = os.getenv('DAPR_USER_MESSAGES_TABLE', '')
pubsub_name = os.getenv('DAPR_PUB_SUB', '')
send_message_topic = os.getenv('DAPR_SEND_MESSAGE_TOPIC', '')

app = FastAPI()

logging.basicConfig(level=logging.INFO)


@app.post('/v1.0/subscribe/group/messages')
def save_user_message(cloud_event:CloudEvent) -> json:
    with DaprClient() as d:
        logging.info(f'Received event: %s:' % {cloud_event.model_dump_json()})
        logging.info(f'Received message model event: %s:' % {cloud_event.data['message_model']})

        message_model = json.loads(cloud_event.data['message_model'])
        try:
            d.save_state(store_name=user_messages_db,
                         key=str(message_model.id),
                         value=message_model.model_dump_json(),
                         state_metadata={"contentType": "application/json"})

            return {
                "status_code": 201,
                "message": "user message saved successfully"
            }

        except grpc.RpcError as err:
            logging.info(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())


