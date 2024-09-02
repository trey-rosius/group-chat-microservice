from typing import Optional

import grpc
import json

from dapr.clients import DaprClient
from fastapi import FastAPI, HTTPException
import logging
import os
from models.user_model import UserModel

user_db = os.getenv('DAPR_USERS_TABLE', '')
pubsub_name = os.getenv('DAPR_AWS_PUB_SUB_BROKER', '')
group_subscription_topic = os.getenv('DAPR_GROUP_SUBSCRIPTION_TOPIC', '')

app = FastAPI()

logging.basicConfig(level=logging.INFO)


@app.get('/')
def health_check():
    return {"Health Ok"}


@app.post('/users')
def create_user_account(user_model: UserModel):
    with DaprClient() as d:
        logging.info(f"User={user_model.model_dump()}")
        try:
            d.save_state(store_name=user_db,
                         key=str(user_model.id),
                         value=user_model.model_dump_json(),
                         state_metadata={"contentType": "application/json"})

            return user_model

        except grpc.RpcError as err:
            logging.info(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())


@app.get('/users/{user_id}')
def get_user_account(user_id: str):
    with DaprClient() as d:
        try:
            kv = d.get_state(user_db, user_id)
            user_account = UserModel(**json.loads(kv.data))

            return user_account
        except grpc.RpcError as err:
            logging.info(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())

@app.get('/users')
def get_groups( token: Optional[str] = None, limit: int = 10):
    with DaprClient() as d:
        try:
            users = []
            query_filter = {

                "sort": [
                    {
                        "key": "created_at",
                        "order": "DESC"
                    }
                ],
                "page": {
                    "limit": limit

                }
            }
            # Add the token only if it is not None
            if token:
                query_filter["page"]["token"] = token

            query_filter_json = json.dumps(query_filter)
            logging.info(f'query filter: {query_filter_json}')

            user_kv = d.query_state(
                store_name=user_db,
                query=query_filter_json
            )
            for item in user_kv.results:
                user_model = UserModel(**json.loads(item.value))
                users.append(user_model)
                logging.info(f"message{user_model.model_dump()}")

            return users
        except grpc.RpcError as err:
            print(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())
