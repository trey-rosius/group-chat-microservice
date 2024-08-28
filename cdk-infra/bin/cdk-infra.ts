#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import {CdkInfraStack, RepositoryStack} from '../lib/cdk-infra-stack';

const app = new cdk.App();

const repoStack = new RepositoryStack(app, "repoStackName", {})
new CdkInfraStack(app, 'CdkInfraStack', {

});