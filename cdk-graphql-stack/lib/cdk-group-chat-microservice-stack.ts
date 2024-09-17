import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as appsync from "aws-cdk-lib/aws-appsync";
import * as cognito from "aws-cdk-lib/aws-cognito";
import path = require("path");

import { readFileSync } from "fs";
import { Service } from "./services";

const SEVEN_DAYS = 7 * 24 * 60 * 60 * 1000; // 7 days in milliseconds
const CURRENT_DATE = new Date();
const KEY_EXPIRATION_DATE = new Date(CURRENT_DATE.getTime() + SEVEN_DAYS);

export class CdkGroupChatMicroserviceStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Get file name from context and parse JSON
    const inputFile = this.node.tryGetContext("configfile");
    const services: [Service] = JSON.parse(readFileSync(inputFile).toString());

    //create our API
    const api = new appsync.GraphqlApi(this, "group-chat-api-microservice", {
      name: "groupChatApiMicroservice",
      definition: appsync.Definition.fromFile("./schema/schema.graphql"),
      authorizationConfig: {
        defaultAuthorization: {
          authorizationType: appsync.AuthorizationType.API_KEY,
          apiKeyConfig: {
            name: "default",
            description: "default auth mode",
            expires: cdk.Expiration.atDate(KEY_EXPIRATION_DATE),
          },
        },
      },
      logConfig: {
        fieldLogLevel: appsync.FieldLogLevel.ALL,
      },
      xrayEnabled: true,
    });

    const dataSources: { [key: string]: appsync.HttpDataSource } = {};

    // Loop through services and create a data source for each
    for (let index = 0; index < services.length; index++) {
      const service = services[index];

      // Dynamically add each service as an HTTP Data Source
      dataSources[service.service] = api.addHttpDataSource(
        service.service,
        `http://${service.url}`
      );
    }

    // You can now reference any datasource from the `dataSources` object
    // For example, userService, groupService, etc.
    const userServiceAPIDatasource = dataSources["user-service"];
    const groupServiceAPIDatasource = dataSources["group-service"];
    const messageServiceAPIDatasource = dataSources["message-service"];
    const typingAPIDatasource = dataSources["typing-indicator-service"];

    const nonDataSource = api.addNoneDataSource("none");

    // Create a function that will add user account
    const createUserAccountFunction = new appsync.AppsyncFunction(
      this,
      "createUserAccountFunction",
      {
        api,
        dataSource: userServiceAPIDatasource,
        name: "createUserAccountFunction",
        code: appsync.Code.fromAsset(
          "./resolvers/users-service/createUserAccount.js"
        ),
        runtime: appsync.FunctionRuntime.JS_1_0_0,
      }
    );

    const formatUserAccountInputFunction = new appsync.AppsyncFunction(
      this,
      "formatUserAccountInputFunction",
      {
        api,
        dataSource: nonDataSource,
        name: "formatUserAccountInputFunction",
        code: appsync.Code.fromAsset(
          "./resolvers/users-service/formatUserAccountInput.js"
        ),
        runtime: appsync.FunctionRuntime.JS_1_0_0,
      }
    );

    new appsync.Resolver(this, "createUserAccountPipelineResolver", {
      api,
      typeName: "Mutation",
      fieldName: "createUserAccount",
      runtime: appsync.FunctionRuntime.JS_1_0_0,
      code: appsync.Code.fromAsset("./resolvers/pipeline/default.js"),
      pipelineConfig: [
        formatUserAccountInputFunction,
        createUserAccountFunction,
      ],
    });

    new appsync.Resolver(this, "getUserAccountResolver", {
      api,
      typeName: "Query",
      fieldName: "getUserAccount",
      dataSource: userServiceAPIDatasource,
      runtime: appsync.FunctionRuntime.JS_1_0_0,
      code: appsync.Code.fromAsset(
        "./resolvers/users-service/getUserAccount.js"
      ),
    });

    new appsync.Resolver(this, "getMessagesPerGroupResolver", {
      api,
      typeName: "Query",
      fieldName: "getGroupMessages",
      dataSource: groupServiceAPIDatasource,
      runtime: appsync.FunctionRuntime.JS_1_0_0,
      code: appsync.Code.fromAsset(
        "./resolvers/messages-service/getMessagesPerGroup.js"
      ),
    });

    new appsync.Resolver(this, "getUsersResolver", {
      api,
      typeName: "Query",
      fieldName: "getUsers",
      dataSource: userServiceAPIDatasource,
      runtime: appsync.FunctionRuntime.JS_1_0_0,
      code: appsync.Code.fromAsset("./resolvers/users-service/getUsers.js"),
    });

    new appsync.Resolver(this, "createGroupResolver", {
      api,
      typeName: "Mutation",
      fieldName: "createGroup",
      dataSource: groupServiceAPIDatasource,
      runtime: appsync.FunctionRuntime.JS_1_0_0,
      code: appsync.Code.fromAsset("./resolvers/groups-service/createGroup.js"),
    });
    new appsync.Resolver(this, "sendGroupMessageResolver", {
      api,
      typeName: "Mutation",
      fieldName: "sendGroupMessage",
      dataSource: messageServiceAPIDatasource,
      runtime: appsync.FunctionRuntime.JS_1_0_0,
      code: appsync.Code.fromAsset(
        "./resolvers/messages-service/sendGroupMessage.js"
      ),
    });

    new appsync.Resolver(this, "addGroupParticipantResolver", {
      api,
      typeName: "Mutation",
      fieldName: "addGroupParticipant",
      dataSource: groupServiceAPIDatasource,
      runtime: appsync.FunctionRuntime.JS_1_0_0,
      code: appsync.Code.fromAsset(
        "./resolvers/groups-service/addGroupParticipant.js"
      ),
    });

    new appsync.Resolver(this, "getGroupResolver", {
      api,
      typeName: "Query",
      fieldName: "getGroup",
      dataSource: groupServiceAPIDatasource,
      runtime: appsync.FunctionRuntime.JS_1_0_0,
      code: appsync.Code.fromAsset("./resolvers/groups-service/getGroup.js"),
    });

    new appsync.Resolver(this, "addTypingIndicatorResolver", {
      api,
      typeName: "Mutation",
      fieldName: "addTypingIndicator",
      dataSource: typingAPIDatasource,
      runtime: appsync.FunctionRuntime.JS_1_0_0,
      code: appsync.Code.fromAsset(
        "./resolvers/typing-indicator-service/addTypingIndicator.js"
      ),
    });

    //////////////////////////
    new cdk.CfnOutput(this, "appsync api key", {
      value: api.apiKey!,
    });

    new cdk.CfnOutput(this, "appsync endpoint", {
      value: api.graphqlUrl,
    });

    new cdk.CfnOutput(this, "appsync apiId", {
      value: api.apiId,
    });
  }
}
