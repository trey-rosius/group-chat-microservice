import json
import logging
import os

import grpc
from dapr.clients import DaprClient
from fastapi import FastAPI, HTTPException

from models.group_model import GroupModel, MessageModel,Member
from models.cloud_events import CloudEvent

group_db = os.getenv('DAPR_GROUPS_TABLE', '')
pubsub_name = os.getenv('DAPR_PUB_SUB', '')
group_subscription_topic = os.getenv('DAPR_GROUP_SUBSCRIPTION_TOPIC', '')

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


@app.post('/v1.0/publish/groups/{group_id}/messages')
def send_group_message(group_id: str, message: MessageModel):
    with DaprClient() as d:
        logging.info(f"message={message.model_dump()}")
        try:
            group_message_details = {
                "message_model": message.model_dump_json(),
                "event_type": "send-message"
            }

            # save message as last message to group DS
            # first, we get the group

            group_data = d.get_state(group_db, group_id)
            group_model = GroupModel(**json.loads(group_data.data))
            group_model.last_message = message

            d.save_state(store_name=group_db,
                         key=str(group_model.id),
                         value=group_model.model_dump_json(),
                         state_metadata={"contentType": "application/json"})

            # public send-message event
            d.publish_event(
                pubsub_name=pubsub_name,
                topic_name=group_subscription_topic,
                data=json.dumps(group_message_details),
                data_content_type='application/json',
            )
            return {"message": "successful"}

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


@app.post('/v1.0/state/groups/{group_id}/users/{user_id}')
def add_user_to_group(group_id: str, user_id: str, role: str):
    with DaprClient() as d:
        try:
            user_group_details = {
                "user_group_model": {
                    "id": f'{user_id}-{group_id}',
                    "group_id": group_id,
                    "user_id": user_id,
                    "role": role
                },
                "event_type": "add_group_participant"
            }

            #get group
            group_data = d.get_state(group_db, group_id)

            group_model = GroupModel(**json.loads(group_data.data))
            member_data = {"user_id": user_id, "role": role}

            member = Member(**member_data)

            #update group
            group_model.members.append(member)

            d.save_state(store_name=group_db,
                         key=str(group_model.id),
                         value=group_model.model_dump_json(),
                         state_metadata={"contentType": "application/json"})


            # publish add_group_participant
            d.publish_event(
                pubsub_name=pubsub_name,
                topic_name=group_subscription_topic,
                data=json.dumps(user_group_details),
                data_content_type='application/json',
            )
            return {"message": "successful"}

        except grpc.RpcError as err:
            logging.error(f"Failed to terminate workflow: {err}")
            raise HTTPException(status_code=500, detail=str(err))
