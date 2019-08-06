import json, smooch, os, requests
from smooch.rest import ApiException
from pprint import pprint

origin_string = "smoochBYOC-sample"

def userMessage(event, context):
    #print(locals())                                            # dev
    #print("Headers: %s" % event['headers'])                     # dev
    #print("QueryStrings: %s" % event['queryStringParameters'])  # dev
    print("Body: %s" % event['body'])                           # dev

    # Validation of request signature/authenticity/etc. is left as an excercise for the reader

    request_body = json.loads(event["body"])

    # Respond to Slack challenges (to validate the webhook URL)
    if 'challenge' in request_body.keys():
        response = {
            "statusCode": 200,
            "body": json.loads(event["body"])['challenge']
        }
        print("Sending response: %s" % response)
        return response
    elif 'bot_id' in request_body['event'].keys():
        response = {
            'statusCode': 200,
            'body': json.dumps({'message': "Skipping message from bot_id: %s" % request_body['event']['bot_id']})
        }
        print(response)
        return response

    response = {}
    response['body'] = {}

    # Configure HTTP basic authorization: basicAuth
    smooch.configuration.username = os.environ['smoochAppKeyId']
    smooch.configuration.password = os.environ['smoochAppSecret']
    # OR
    # Configure JWT authorization (alternative method): jwt
    #smooch.configuration.api_key['Authorization'] = 'YOUR_JWT'
    #smooch.configuration.api_key_prefix['Authorization'] = 'Bearer'

    # Create an instance of the Smooch API class
    conversation_api_instance = smooch.ConversationApi()
    app_id = os.environ['smoochAppId'] # str | Identifies the app.
    message_post_body = smooch.MessagePost() # MessagePost | Body for a postMessage request. Additional arguments are necessary based on message type ([text](https://docs.smooch.io/rest/#text), [image](https://docs.smooch.io/rest/#image), [carousel](https://docs.smooch.io/rest/#carousel), [list](https://docs.smooch.io/rest/#list), [form](https://docs.smooch.io/rest/#form)) 

    message_post_body.role = 'appUser'
    message_post_body.metadata = {
        "origin": origin_string,
        "slack_team": request_body['team_id'],
        "slack_api_app_id": request_body['api_app_id'],
        "slack_channel": request_body['event']['channel'],
    }
    if 'user' in request_body['event'].keys():
        slackUserId = request_body['event']['user']
        message_post_body.metadata['slack_user'] = slackUserId
    else:
        slackUserId = ""

    # rebuild message content from received webhook
    user_id = "%s:%s" % (request_body['event']['channel'], slackUserId)
    message_post_body.text = request_body['event']['text']
    #role	str	The role of the individual posting the message. See RoleEnum for available values.	
    message_post_body.type = 'text'

    # Adding support for images, etc. is left as an excercise for the reader
    #message_post_body.type = 'image'   # str	The message type. See MessageTypeEnum for available values.	https://github.com/smooch/smooch-python/blob/master/docs/Enums.md#MessageTypeEnum
    #message_post_body.media_url = "?"  # str	The mediaUrl for the message. Required for image/file messages.	[optional]
    #message_post_body.media_type = "?" # str	The mediaType for the message. Required for image/file messages.	[optional]

    retry_send = True
    create_user_result = ""
    while (retry_send):
        try:
            print("Sending message to Smooch...")
            postmessage_api_response = conversation_api_instance.post_message(app_id, user_id, message_post_body)
            #pprint(postmessage_api_response)
            #pprint("Post Message Response: %s" % str(postmessage_api_response))
        except ApiException as e:
            e_body = json.loads(e.body)
            if 'error' in e_body.keys() and \
                'code' in e_body['error'].keys() and \
                e_body['error']['code'] == 'user_not_found':
                    # create an instance of the API class
                    user_api_instance = smooch.AppUserApi()
                    app_user_pre_create_body = smooch.AppUserPreCreate() # AppUserPreCreate | Body for a preCreateAppUser request.
                    
                    app_user_pre_create_body.user_id = user_id  # str	The app user's userId. This ID is specified by the appMaker.
                    app_user_pre_create_body.properties = { "origin": origin_string } # object	Custom properties for the app user.	[optional]
                    
                    # Including additional user data in the appUser profile is left as an excercise for the reader
                    #given_name	str	The app user's given name.	[optional]
                    #surname	str	The app user's surname.	[optional]
                    #email	str	The app user's email.	[optional]
                    #signed_up_at	str	A datetime string with the format yyyy-mm-ddThh:mm:ssZ representing the moment an appUser was created.	[optional]
                    try:
                        createuser_api_response = user_api_instance.pre_create_app_user(app_id, app_user_pre_create_body)
                        #pprint(createuser_api_response)
                    except ApiException as e:
                        print("Exception when calling AppUserApi->pre_create_app_user: %s\n" % e)
                        response = {
                            'statusCode': int(createuser_api_response),
                            'body': json.dumps({'create_user_result': createuser_api_response})
                        }
                        print(response)
                        return response
                    else:
                        print("Created new appUser: %s" % app_user_pre_create_body.user_id)
                        create_user_result = "User %s created!\n" % app_user_pre_create_body.user_id
                        continue
            else:
                print("Exception when calling ConversationApi->post_message: %s\n" % e)
                response = {
                    'statusCode': int(postmessage_api_response),
                    'body': json.dumps({'message': "Message sent!"})
                }
                print(response)
                return response
        else:
            #print(dir(postmessage_api_response))
            '''for att in dir(postmessage_api_response):
                if att.startswith('_'):
                   continue
                print("> postmessage_api_response attribute %s: %s" % (att, getattr(postmessage_api_response, att)))
            '''
            response = {
                'statusCode': 200,
                'body': json.dumps( {'message': create_user_result+"Message sent!"} )
            }
            print(response)
            return response

    #return response
    
    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """

def businessMessage(event, context):
    #print(locals())                                            # dev
    #print("Headers: %s" % event['headers'])                    # dev

    # Validation of request signature/authenticity/etc. is left as an excercise for the reader

    request_body = json.loads(event["body"])
    print("Received webhook with %s messages" % len(request_body['messages']))
    print("Request body: %s" % request_body)
    userId = request_body['appUser']['userId']
    slackChannel = userId[:userId.find(':')]
    #slackUserId = userId[userId.find(':')+1:]

    slackMsg = {
        "url": "https://slack.com/api/chat.postMessage",
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "Bearer %s" % os.environ['slackBotAccessToken']
        },
        "payload": {
            "token": os.environ['slackBotAccessToken'],
            "channel": slackChannel,
            "text": request_body['messages'][0]['text']
        }
    }

    # De-duplication of messages (in case of webhook retries) is left as an excercise for the reader

    slackPostResp = requests.post(slackMsg['url'], headers=slackMsg['headers'], json=slackMsg['payload'])
    slackRespText = json.loads(slackPostResp.text)
    print("Slack said: %s %s" % (type(slackRespText), slackRespText))

    '''for att in dir(slackPostResp):
        if att.startswith("_"):
            continue
        print("%s: %s" % (att, getattr(slackPostResp, att)))
    '''

    if not slackRespText['ok']:
        response = {
            'statusCode': 400,
            'body': json.dumps({'error': slackRespText})
        }
    else:
        response = {
            'statusCode': 200,
            'body': json.dumps({'response': slackRespText})
        }
    
    print(response)
    return response