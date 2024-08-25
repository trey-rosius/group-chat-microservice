import uuid

import grpc
import json

from dapr.clients import DaprClient
from fastapi import FastAPI, HTTPException
import logging
import os
from models.typing_model import TypingModel
from models.cloud_events import CloudEvent

typing_indicator_db = os.getenv('typing-indicator-table', '')
pubsub_name = os.getenv('DAPR_PUB_SUB', '')
group_subscription_topic = os.getenv('DAPR_GROUP_SUBSCRIPTION_TOPIC', '')

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.post('/v1.0/state/typing')
def add_typing_indicator(typing: TypingModel) -> json:
    with DaprClient() as d:
        logging.info(f"Adding Typing Indicator for user: {typing.user_id} and group: {typing.group_id}")

        try:
            d.save_state(store_name=typing_indicator_db,
                         key=f'{typing.user_id}-{typing.groupId}',
                         value=typing.model_dump_json(),
                         state_metadata={"contentType": "application/json"})

            return {
                "status_code": 201,
                "message": "added typing indicator"
            }


        except grpc.RpcError as err:
            logger.error(f"Failed to terminate workflow: {err}")
            raise HTTPException(status_code=500, detail=str(err))


@app.post('/v1.0/subscribe/group/messages')
def update_typing_indicator(cloud_event: CloudEvent) -> json:
    with DaprClient() as d:
        logging.info(f'Received event: %s:' % {cloud_event.model_dump_json()})
        logging.info(f'Received message model event: %s:' % {cloud_event.data['message_model']})

        message_model = json.loads(cloud_event.data['message_model'])

        typing_indicator = TypingModel(
            id=f"{message_model.user - message_model.group_id}",
            user_id=message_model.user_id,
            group_id=message_model.group_id,
            typing=False
        )

        try:
            d.save_state(store_name=typing_indicator_db,
                         key=typing_indicator.id,
                         value=typing_indicator.model_dump_json(),
                         state_metadata={"contentType": "application/json"})

            return {
                "status_code": 201,
                "message": "updated typing indicator"
            }

        except grpc.RpcError as err:
            logger.error(f"Failed to terminate workflow: {err}")
            raise HTTPException(status_code=500, detail=str(err))
