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
from flask import Flask, Response
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

app = Flask(__name__)
socketio = SocketIO(app)
CORS(app)

language_identify = 'ja'
  
if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    print('Found VCAP_SERVICES')
    if 'conversation' in vcap:
        conversationCreds = vcap['conversation'][0]['credentials']
        assistantUsername = conversationCreds.get('username')
        assistantPassword = conversationCreds.get('password')
        assistantIAMKey = conversationCreds.get('apikey')
        assistantUrl = conversationCreds.get('url')

    if 'text_to_speech' in vcap:
        textToSpeechCreds = vcap['text_to_speech'][0]['credentials']
        textToSpeechUser = textToSpeechCreds.get('username')
        textToSpeechPassword = textToSpeechCreds.get('password')
        textToSpeechUrl = textToSpeechCreds.get('url')
        textToSpeechIAMKey = textToSpeechCreds.get('apikey')
    if 'speech_to_text' in vcap:
        speechToTextCreds = vcap['speech_to_text'][0]['credentials']
        speechToTextUser = speechToTextCreds.get('username')
        speechToTextPassword = speechToTextCreds.get('password')
        speechToTextUrl = speechToTextCreds.get('url')
        speechToTextIAMKey = speechToTextCreds.get('apikey')

    if "WORKSPACE_ID" in os.environ:
        workspace_id = os.getenv('WORKSPACE_ID')

    if "ASSISTANT_IAM_APIKEY" in os.environ:
        assistantIAMKey = os.getenv('ASSISTANT_IAM_APIKEY')

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

@app.route('/')
def Welcome():
    return app.send_static_file('index.html')


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
    if r_type == 'text' and language_identify == 'en':
        translation =   getTranslatorToEnlish(reponseContent)
        if(moreflg):
            translation2 =   getTranslatorToEnlish(reponseContent)
            reponseContent2 = translation2['translations'][0]['translation']
        print(translation)
        reponseContent = translation['translations'][0]['translation']
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

    def generate():
        audioOut = ttsService.synthesize(
            inputText,
            'audio/wav',
#             'en-US_AllisonVoice').get_result()
            'ja-JP_EmiVoice').get_result()
            

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

        if language_identify != 'ja' and language_identify !='zh':
            
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
    
port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=int(port))
