# -*- coding: utf-8 -*-
# Copyright 2018 IBM Corp. All Rights Reserved.

# Licensed under the Apache License, Version 2.0 (the “License”)
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an “AS IS” BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
from dotenv import load_dotenv
from flask import Flask, Response,redirect,url_for
from flask import jsonify
from flask import request
from flask_socketio import SocketIO
from flask_cors import CORS
from ibm_watson import AssistantV1
from ibm_watson import SpeechToTextV1
from ibm_watson import TextToSpeechV1
from ibm_watson import DiscoveryV1
from telnetlib import theNULL
from ibm_watson import LanguageTranslatorV3
from _ast import If
# ======= add login ======= 
from flask_login import login_user, login_required
from flask_login import LoginManager, current_user
from flask_login import logout_user
from user_authorization import User, do_auth
#from flask_wtf.csrf import CsrfProtect

from flask import make_response
import ibm_boto3
from ibm_botocore.client import Config, ClientError
from unittest import case

app = Flask(__name__)
socketio = SocketIO(app)
CORS(app)

language_identify = 'ja'

# ======= add login ======= 
app.secret_key = os.urandom(24)
# use login manager to manage session
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app=app)

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
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
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

@app.route('/')
def Welcome():
#    return app.send_static_file('login.html')
#    return app.send_static_file('login2.html')
    return app.send_static_file('login.html')

@app.route('/api/conversation', methods=['POST', 'GET'])
def getConvResponse():
    # Instantiate Watson Assistant client.
    # only give a url if we have one (don't override the default)
    
    try:
        assistant_kwargs = {
            'version': '2018-09-20',
            'username': assistantUsername,
            'password': assistantPassword,
            'iam_apikey': assistantIAMKey,
            'url': assistantUrl
        }
        
        assistant = AssistantV1(**assistant_kwargs)
        convText = request.form.get('convText')
        convContext = request.form.get('context')
    
        if convContext is None:
            convContext = "{}"
        jsonContext = json.loads(convContext)
    
        if convText != None :
            print('翻訳前：　'+convText)
        
        convText = getTranslatorText(convText)
        
        response = assistant.message(workspace_id=workspace_id,
                                     input={'text': convText},
                                     context=jsonContext)
    except Exception as e:
        print(e)

    response = response.get_result()
   
    json_data = json.dumps(response,indent=2)
    
    moreflg = False;
    if (len(response["output"]["generic"])==1):
        r_type =  response["output"]["generic"][0]["response_type"]
        if r_type == 'text' :
            reponseContent = response["output"]["text"]
        else:
            reponseContent = response["output"]["generic"][0]
    else:
        for item in response["output"]['generic']:
            if item["response_type"] == 'text' :
                reponseContent = item["text"]
            if item["response_type"] == 'option' :
                reponseContent2 = item   
        moreflg =True
    
    r_type =  response["output"]["generic"][0]["response_type"]
    intent = ''
    if len(response["intents"]):
        intent = response["intents"][0]["intent"]
    
    # set reponseContent by response_type
   
        
    print(reponseContent)
    global language_identify
    if language_identify == 'en':
        if r_type == 'text' :
            translation =   getTranslatorToEnlish(reponseContent)
            if(moreflg):
                translation2 =   getTranslatorToEnlish(reponseContent2["title"])
                reponseContent2["title"] = translation2['translations'][0]['translation']
#                 for item in reponseContent2["options"]:
#                     trans_val = getTranslatorToEnlish(item['value']['input']['text'])
#                     print(trans_val['translations'][0]['translation'])
#                     item['value']['input']['text'] = trans_val['translations'][0]['translation']
            print(translation)
            reponseContent = translation['translations'][0]['translation']
        else:
            translation2 =   getTranslatorToEnlish(reponseContent["title"])
            reponseContent["title"] = translation2['translations'][0]['translation']
#             for item in reponseContent["options"]:
#                 
#                 print(item['value']['input']['text'])
#                 item_value = item['value']['input']['text']
#                 item['value']['input']['text'] = getTranslatorToEnlish(item['value']['input']['text'])
           
            
        
    print(intent)
    
    if 'discovery' in intent.lower() :
        if(moreflg):
            responseDetails = {'responseType': 'text',
                       'responseType2': 'option',
                       'reponseContent': reponseContent,
                       'reponseContent2': reponseContent2,
                       'sendToDiscovery': 'send',
                       'context': response["context"]}
        else:
            responseDetails = {'responseType': r_type,
                       'reponseContent': reponseContent,
                       'sendToDiscovery': 'send',
                       'context': response["context"]}       
    else :

        if(moreflg):
            responseDetails = {'responseType': 'text',
                       'responseType2': 'option',
                       'reponseContent': reponseContent,
                       'reponseContent2': reponseContent2,
                       'sendToDiscovery': 'noSend',
                       'context': response["context"]}
        else:
            responseDetails = {'responseType': r_type,
                       'reponseContent': reponseContent,
                       'sendToDiscovery': 'noSend',
                       'context': response["context"]}    
    
    return jsonify(results=responseDetails)


@app.route('/api/text-to-speech', methods=['POST'])
def getSpeechFromText():
    tts_kwargs = {
            'username': textToSpeechUser,
            'password': textToSpeechPassword,
            'iam_apikey': textToSpeechIAMKey,
            'url': textToSpeechUrl
    }

    inputText = request.form.get('text')
    ttsService = TextToSpeechV1(**tts_kwargs)
    
    print(inputText)
    
    global language_identify
    if language_identify == 'en':
        voice_ = 'en-US_AllisonVoice'
    else:
        voice_ = 'ja-JP_EmiVoice'

    def generate():
        audioOut = ttsService.synthesize(
            inputText,
            voice=voice_,
            accept='audio/wav'
#             'en-US_AllisonVoice').get_result()
            ).get_result()
            

        data = audioOut.content

        yield data

    return Response(response=generate(), mimetype="audio/x-wav")


@app.route('/api/speech-to-text', methods=['POST'])
def getTextFromSpeech():
    tts_kwargs = {
            'username': speechToTextUser,
            'password': speechToTextPassword,
            'iam_apikey': speechToTextIAMKey,
            'url': speechToTextUrl
    }

    sttService = SpeechToTextV1(**tts_kwargs)

    response = sttService.recognize(
            audio=request.get_data(cache=False),
            content_type='audio/wav',
            model = 'ja-JP_BroadbandModel',
            timestamps=True,
            word_confidence=True).get_result()

    if len(response['results']):
    
        text_output = response['results'][0]['alternatives'][0]['transcript']
    
    else:
        text_output = '';
        
    return Response(response=text_output, mimetype='plain/text')

def getTranslatorText(convText):
    global language_identify
    laguage_kwargs = {
        'version': '2018-05-01',
        'username': tranlatorUser,
        'password': tranlatorPassword,
        'iam_apikey': tranlatorIAMKey,
        'url': tranlatorUrl
    }
  
    language_translator = LanguageTranslatorV3(**laguage_kwargs)
    if convText!=None and convText != '' :
        language = language_translator.identify(convText).get_result()
        language_identify = language['languages'][0]['language']
        print(language['languages'][0]['language'])

        if language_identify != 'ja' and language_identify !='zh' and language_identify !='zh-TW':
            
            language_identify = 'en'
            translation = language_translator.translate(text=convText,model_id='en'+'-ja').get_result()
#           translation = language_translator.translate(text=convText,model_id=language_identify+'-ja').get_result()  
            convText = translation['translations'][0]['translation']
            print('翻訳後：　　'+convText)
            
    return convText

def getTranslatorToEnlish(text):
    
    laguage_kwargs = {
        'version': '2018-05-01',
        'username': tranlatorUser,
        'password': tranlatorPassword,
        'iam_apikey': tranlatorIAMKey,
        'url': tranlatorUrl
    }
  
    language_translator = LanguageTranslatorV3(**laguage_kwargs)
    translation = language_translator.translate(text=text,model_id='ja-en').get_result()
    return translation

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# csrf protection
#csrf = CSRFProtect()
#csrf.init_app(app)

@app.route('/login', methods=['POST', 'GET'])
def login():
    logout_user()
    user_name = request.args.get('username', None)
    password =  request.args.get('password', None)
    remember_me = request.args.get('rememberme', False)
    if user_name == '' or  password == '':
        return redirect('/')
        
    user = User(user_name)
    
    if do_auth(user_name, password):
        login_user(user, remember=remember_me)
        return app.send_static_file('index.html')
        # return redirect(url_for('/chatbot'))
    else:
        return redirect('/')
    # return app.send_static_file('index.html')
    # return redirect('/index')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/chatbot', methods=['POST', 'GET'])
@login_required
def index():
    return app.send_static_file('index.html')
#     return app.send_static_file('index.html')

@app.route('/api/discoveryChartOne', methods=['POST', 'GET'])
def getDiscoveryChartOne():
    discovery = DiscoveryV1(
    version = discovery_version,
    iam_apikey = discovery_iam_apikey,
    url = discovery_url
    )

#     discovery.set_detailed_response(True)
    response = discovery.query(collection_id=discovery_collection_id,environment_id=discovery_environment_id, filter=None, query="", natural_language_query=None, passages=None, aggregation="timeslice(発生日,1day)", count="2", return_fields=None, offset=None, sort=None, highlight=None, passages_fields=None, passages_count=None, passages_characters=None, deduplicate=None, deduplicate_field=None, similar=None, similar_document_ids=None, similar_fields=None, logging_opt_out=None, collection_ids=None, bias=None);

    json_data = json.dumps(response.get_result(), indent=2,ensure_ascii=False)
    p_obj = json.loads(json_data)
    
    responseDemo = {}
    for resultD in p_obj['aggregations'][0]['results']:
        if resultD['matching_results'] > 0:
            responseDemo[resultD['key_as_string'][5:10].replace('-', ' ')] = resultD['matching_results']

    
    # response = Response(json.dumps(responseDemo))
#     response['Access-Control-Allow-Origin'] = '*'
#     response['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS' 
#     response['Access-Control-Max-Age'] = '1000' 
#     response['Access-Control-Allow-Headers'] = '*'
    return jsonify(results=responseDemo)

@app.route('/api/docs', methods=['POST'])
def download_file(id=None):
    bucket = 'pdf-01'
    
    a_id = request.form.get('id')
    
    file_name = ''
    
    if a_id == 'm001':
        file_name = "ブロー機保守.pdf"
    elif a_id == 'm002':
         file_name = "チャンバー保守.pdf"
    elif a_id == 'm003':
        file_name = "シンクロ保守.pdf"
    elif a_id == 'm004':
         file_name = "フィラー保守.pdf"
    elif a_id == 'k004':
         file_name = "【ﾌｨﾗｰ】点検基準書STⅡ改定.xls"
         
    response = None
    
    # Cosに格納したファイルを読み込む
    try:
         file = cos.Object(bucket, file_name).get()
         response = make_response(file["Body"].read())
    except Exception as e:
        print("Unable to retrieve file contents: {0}".format(e))
    
    if file_name[-3:]=='pdf' :
        response.headers['Content-Type'] = 'application/pdf'
    else:
        response.headers['Content-Type'] = 'application/vnd.ms-excel'

    response.headers['Content-Disposition'] = 'inline; filename='  +file_name.encode('utf-8').decode('latin-1')
#     u'访视频'.encode('utf-8').decode('latin-1')
    
    return response
    
    
port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=int(port), debug=True)
