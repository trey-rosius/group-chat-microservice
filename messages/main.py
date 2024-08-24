import grpc
import json

from dapr.clients import DaprClient
from fastapi import FastAPI, HTTPException
import logging
import os
from models.message_model import MessageModel

group_db = os.getenv('DAPR_MESSAGE_TABLE', '')
pubsub_name = os.getenv('DAPR_PUB_SUB', '')
send_message_topic = os.getenv('DAPR_SEND_MESSAGE_TOPIC', '')

app = FastAPI()

logging.basicConfig(level=logging.INFO)


@app.post('/v1.0/state/groups')
def create_group(group_model: GroupModel) -> json:
    with DaprClient() as d:
        logging.info(f"User={group_model.model_dump()}")
        try:
            d.save_state(store_name=group_db,
                         key=str(group_model.id),
                         value=group_model.model_dump_json(),
                         state_metadata={"contentType": "application/json"})

            return {
                "status_code": 201,
                "message": "Group created successfully"
            }

        except grpc.RpcError as err:
            logging.info(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())


@app.get('/v1.0/state/groups/{group_id}')
def get_group(group_id: str):
    with DaprClient() as d:
        try:
            kv = d.get_state(group_db, group_id)
            group = GroupModel(**json.loads(kv.data))

            return group.model_dump()
        except grpc.RpcError as err:
            print(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())
