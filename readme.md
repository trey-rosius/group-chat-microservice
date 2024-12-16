# Group Chat Microservice

## Prerequisites
Please ensure you have these dependencies configured and installed before proceeding
- [Diagrid Account](https://catalyst.diagrid.io/)
- [DIAGRID CLI](https://docs.diagrid.io/catalyst/references/cli-reference/intro/)
- [Github Acount](https://docs.diagrid.io/catalyst/references/cli-reference/intro/)
- [AWS Account](https://repost.aws/knowledge-center/create-and-activate-aws-account)
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

## Setup AWS CLI
Retrieve AWS access credentials from the AWS console.

From your CLI run these commands, replacing XXX and YYY with the correct values.
```
export AWS_ACCESS_KEY_ID=XXX
export AWS_SECRET_ACCESS_KEY=YYY
export AWS_DEFAULT_REGION=us-east-1

export GROUP_CHAT_MICROSERVICES=group-chat-microservices 

aws configure
```

## Install Catalyst Project
From the CLI, run the command to install and provision all resources required for your catalyst project

`python run.py`


## Running Github Actions
Fork the github project. Navigate to `settings` -> `secrets and variables` -> `action`.

Click on `new repository secret` button.

Add these secrets

```
Name                           Value
-----
AWS_ACCESS_KEY_ID             -------
AWS_ACCOUNT_ID                -------
AWS_SECRET_ACCESS_KEY         -------
DIAGRID_API_KEY               --------
DIAGRID_PROJECT               --------
```

The Github actions pipeline runs everytime you do a push.

## Create users table

```sql
{
    "database": "group_db",
  "operation": "query",
  "metadata": {

  
"sql": "CREATE TABLE users (id VARCHAR(255) PRIMARY KEY, email VARCHAR(255) NOT NULL UNIQUE, username VARCHAR(255) NOT NULL UNIQUE, profile_pic_url TEXT, created_at BIGINT NOT NULL, updated_at BIGINT);"
  }
 
}


```
## Create messages table

```sql


{
    "database": "group_db",
  "operation": "query",
  "metadata": {

 "sql": "CREATE TABLE messages (id VARCHAR(255) PRIMARY KEY, user_id VARCHAR(255) NOT NULL, group_id VARCHAR(255) NOT NULL, message_type VARCHAR(50) NOT NULL CHECK (message_type IN ('TEXT', 'IMAGE', 'VIDEO')), message_content TEXT, image_url TEXT, video_url TEXT, created_at BIGINT NOT NULL, updated_at BIGINT);"
  }
 
}

```

## Create user group table

```sql


{
    "database": "group_db",
  "operation": "query",
  "metadata": {

"sql": "CREATE TABLE user_group (id VARCHAR(255) PRIMARY KEY, user_id VARCHAR(255) NOT NULL, group_id VARCHAR(255) NOT NULL, role VARCHAR(50) NOT NULL CHECK (role IN ('ADMIN', 'MEMBER')), last_read_msg_id VARCHAR(255), last_read_timestamp BIGINT);"
  }
 
}

```

## Create typing_indicator table

```sql


{
    "database": "group_db",
  "operation": "query",
  "metadata": {

"sql": "CREATE TABLE typing_indicator(id VARCHAR(255) PRIMARY KEY, user_id VARCHAR(255) NOT NULL, group_id VARCHAR(255) NOT NULL, typing BOOLEAN NOT NULL);"
  }
 
}

```

## Create Group Table 

```sql


{
    "database": "group_db",
  "operation": "query",
  "metadata": {

"sql": "CREATE TABLE groups (id VARCHAR(255) PRIMARY KEY, group_name VARCHAR(255) NOT NULL, creator_id VARCHAR(255) NOT NULL, group_description TEXT NOT NULL, group_url VARCHAR(255) NOT NULL, created_at BIGINT NOT NULL, updated_at BIGINT, last_message_id VARCHAR(255), FOREIGN KEY (last_message_id) REFERENCES messages(id));"
  }
 
}

```