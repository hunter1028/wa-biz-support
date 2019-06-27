#-*- coding: utf-8 -*-
'''
ibm_dist -- watson assistant biz support

@author:     IBM
@copyright:  2019 IBM distribution. All rights reserved.
@version: 1.0

Created on 2019/06/26
'''
# from flask import Flask
# app = Flask(__name__)

from flask_login import LoginManager, current_user

# use login manager to manage session
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'index'

from ibm_dist.utils.user_authorization import User
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

import json
import os
from dotenv import load_dotenv
import ibm_boto3
from ibm_botocore.client import Config, ClientError
 
language_identify = 'ja'
 
if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    if 'conversation' in vcap:
        conversationCreds = vcap['conversation'][0]['credentials']
        assistantUsername = conversationCreds.get('username')
        assistantPassword = conversationCreds.get('password')
        assistantIAMKey = conversationCreds.get('apikey')
        assistantUrl = conversationCreds.get('url')
         
    print('assistantIAMKey : '+assistantIAMKey)   
 
    if 'text_to_speech' in vcap:
        textToSpeechCreds = vcap['text_to_speech'][0]['credentials']
        textToSpeechUser = textToSpeechCreds.get('username')
        textToSpeechPassword = textToSpeechCreds.get('password')
        textToSpeechUrl = textToSpeechCreds.get('url')
        textToSpeechIAMKey = textToSpeechCreds.get('apikey')
         
    print('textToSpeechIAMKey : '+textToSpeechIAMKey)
         
    if 'speech_to_text' in vcap:
        speechToTextCreds = vcap['speech_to_text'][0]['credentials']
        speechToTextUser = speechToTextCreds.get('username')
        speechToTextPassword = speechToTextCreds.get('password')
        speechToTextUrl = speechToTextCreds.get('url')
        speechToTextIAMKey = speechToTextCreds.get('apikey')
         
    print('speechToTextIAMKey : '+speechToTextIAMKey)
       
    if 'language_translator' in vcap:
        tranlatorCreds = vcap['language_translator'][0]['credentials']
        tranlatorUser = tranlatorCreds.get('username')
        tranlatorPassword = tranlatorCreds.get('password')
        tranlatorUrl = tranlatorCreds.get('url')
        tranlatorIAMKey = tranlatorCreds.get('apikey')
         
    print('tranlatorIAMKey : '+tranlatorIAMKey)
         
    if "WORKSPACE_ID" in os.environ:
        workspace_id = os.getenv('WORKSPACE_ID')
 
    if "ASSISTANT_IAM_APIKEY" in os.environ:
        assistantIAMKey = os.getenv('ASSISTANT_IAM_APIKEY')
         
    discovery_version='2019-02-10'
    discovery_iam_apikey='3UYwda1sKeY8067bhn1QMLqv8ZXhXUMci5GQGwqTwY_f'
    discovery_url='https://gateway-tok.watsonplatform.net/discovery/api'
    discovery_collection_id='5e7a4dba-7dd5-43bf-aae2-6ad71c53f211'
    discovery_environment_id='b38640cb-c019-4e68-9e27-16841796ae92'
 
else:
    print('Found local VCAP_SERVICES')
#    print(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, ".env")))
#     load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
    load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, ".env")))
    assistantUsername = os.environ.get('ASSISTANT_USERNAME')
    assistantPassword = os.environ.get('ASSISTANT_PASSWORD')
    assistantIAMKey = os.environ.get('ASSISTANT_IAM_APIKEY')
    assistantUrl = os.environ.get('ASSISTANT_URL')
 
    textToSpeechUser = os.environ.get('TEXTTOSPEECH_USER')
    textToSpeechPassword = os.environ.get('TEXTTOSPEECH_PASSWORD')
    textToSpeechUrl = os.environ.get('TEXTTOSPEECH_URL')
    textToSpeechIAMKey = os.environ.get('TEXTTOSPEECH_IAM_APIKEY')
 
    speechToTextUser = os.environ.get('SPEECHTOTEXT_USER')
    speechToTextPassword = os.environ.get('SPEECHTOTEXT_PASSWORD')
    workspace_id = os.environ.get('WORKSPACE_ID')
    speechToTextUrl = os.environ.get('SPEECHTOTEXT_URL')
    speechToTextIAMKey = os.environ.get('SPEECHTOTEXT_IAM_APIKEY')
     
    tranlatorUser = os.environ.get('TRANSLATOR_USER')
    tranlatorPassword = os.environ.get('TRANSLATOR_PASSWORD')
    tranlatorUrl = os.environ.get('TRANSLATOR_URL')
    tranlatorIAMKey = os.environ.get('TRANSLATOR_IAM_APIKEY')
     
    discovery_version = os.environ.get('DISCOVERY_VERSION')
    discovery_iam_apikey = os.environ.get('DISCOVERY_IAM_APIKEY')
    discovery_url = os.environ.get('DISCOVERY_URL')
    discovery_collection_id = os.environ.get('DISCOVERY_COLLECTION_ID')
    discovery_environment_id = os.environ.get('DISCOVERY_ENVIRONMENT_ID')
 
# Constants for IBM COS values
COS_ENDPOINT = "https://s3.ams03.cloud-object-storage.appdomain.cloud" # Current list avaiable at https://control.cloud-object-storage.cloud.ibm.com/v2/endpoints
COS_API_KEY_ID = "rr7Gb-oSjjL-OgSrIkdRRQBVSWWuSPvhhhjtM0_pTVG-" # eg "W00YiRnLW4a3fTjMB-oiB-2ySfTrFBIQQWanc--P3byk"
COS_AUTH_ENDPOINT = "https://iam.cloud.ibm.com/identity/token"
COS_RESOURCE_CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/82d7c22519df42d08f81d32010fe9348:32fbf12f-285f-4e22-8b9c-3aedc916405a::" # eg "crn:v1:bluemix:public:cloud-object-storage:global:a/3bf0d9003abfb5d29761c3e97696b71c:d6f04d83-6c4f-4a62-a165-696756d63903::"
COS_BUCKET_LOCATION="ams03-standard"
 
# Create resource
cos = ibm_boto3.resource("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_service_instance_id=COS_RESOURCE_CRN,
    ibm_auth_endpoint=COS_AUTH_ENDPOINT,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT
)