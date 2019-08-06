# Deploying to AWS Lambda via Serverless

## Serverless quickstart
https://medium.com/devopslinks/aws-lambda-serverless-framework-python-part-1-a-step-by-step-hello-world-4182202aba4a

## Pre-Requisites
1. Serverless (& Python-requirement package): `npm install -g serverless serverless-python-requirements`
2. Authorised/configured AWS IAM user (e.g.:)
    * keyId/secret under [serverless] in ~/.aws/credentials, or
    * `serverless config credentials --provider aws --key xxxxxxxxxxx --secret xxxxxxxxxxx`
3. Python3 (+ pip3)
    1. Python3 dependencies: `pip3 install smooch`
4. External system to send webhooks

## Push environment variables to AWS (SSM)
Use the command `aws ssm put-parameter --name supermanToken --type String --value mySupermanToken`
* connectCampaignIds
NOTE: Serverless will raise a warning if keys are specified (serverless.yml) but not found in the AWS SSM/environment
NOTE: _connectCampaignIds_ can contain a comma-separated list of authorised CampaignIds

## Clone code
Clone this project

## Deploy to AWS Lambda with Serverless
`serverless deploy` (or `sls deploy`)

## Monitoring logs with Serverless
`serverless logs -f connect -t`
* `-f` specifies the Serverless function name
* `-t` to display/update logs in [near] real-time

# Slack App Config
## Slack App Features & Functionality
Based on:
With resources:
* Bots              _(Name the bot users will DM)_
* Event Subscriptions:
 * Enable Events    _(add `inbounnd`/`userMessage` endpoint URL from `sls info`)_
 * Subscribe to Bot Events: [ im_created, message.im ]
* Permissions       _(Note the `Bot User OAuth Access Token` and add to AWS SSM, as below)_
## SSM Credentials
* `aws ssm put-parameter --name slackBotAccessToken --type String --value <<Bot User OAuth Access Token>>`

# Smooch App Config
* Create an app and note the `appId` _(and add to AWS SSM, as below)_
* In the app's settings, create a Key/secret pair _(and add to AWS SSM, as below)_
* create a `webhook` integration (via UI or API)
 * _The webhook should be set to `includeFullAppUser` by default_
## SSM Credentials
* `aws ssm put-parameter --name smoochAppId --type String --value <<appId>>`
* `aws ssm put-parameter --name smoochAppKeyId --type String --value <<KeyId>>`
* `aws ssm put-parameter --name smoochAppSecret --type String --value <<secret>>`

# Serverless tools used (Cheatsheet)
## Init new project
 * ~initialize project: `serverless create --template aws-python3 --name smoochConnect`~

## Injecting python packages from venv
https://serverless.com/blog/serverless-python-packaging/
```
virtualenv venv --python=python3
source venv/bin/activate
pip3 install smooch
pip3 freeze > requirements.txt
npm install --save serverless-python-requirements
```

### serverless.yml
```
plugins:
    - serverless-python-requirements
```

## Advanced: key management
https://serverless.com/blog/serverless-secrets-api-keys/
 * store keys as Env variables: `aws ssm put-parameter --name supermanToken --type String --value mySupermanToken`

### serverless.yml
```
environment:
    MY_API_SECRET: ${ssm:nameOfKey}
```

### handler.py
```
import os
access_token = os.environ['TWITTER_ACCESS_TOKEN']
```

## Postman testing
`POST @ https://<<ID>>.execute-api.us-east-1.amazonaws.com/dev/<<endpoint>>`
Body: raw > JSON (application/json)

# Iteration prep/cleanup:
* supportkit.Zendesk: delete old tickets
* API(postman)
 * delete appUsers
 * prep notification-send call (text = HSM shorthand)
 * prep webhook event
* WA: Delete chat (conversation history)

## Deployment
* Deploy: `sls deploy`
* [Repeat] info on deployed function(s): `sls info`
note the URL and function name (before the ':')

## Live monitoring
Last few lines of log: `sls -f connect logs`

# Relevant links
## Supportkit's Zendesk Connect
https://supportkit.zendesk.com/connect/dashboard/dashboard/campaign/5c5b45b8fc46e37b29e15cf6/edit
## Supportkit's Zendesk Support
https://supportkit.zendesk.com/agent/tickets/2375
## Notify API docs
https://docs.google.com/document/d/1vvcJuMPVkQKc0Rd0ip6AVnqFWWoLyyTYs1Hk2Atz-eM/edit#
## Error: "distutils.errors.DistutilsOptionError: must supply either home or prefix/exec-prefix -- not both"
https://github.com/edmunds/shadowreader/blob/master/docs/setup.md