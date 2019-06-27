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
from flask import Response,redirect,url_for
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
from ibm_dist.user_authorization import User, do_auth
#from flask_wtf.csrf import CsrfProtect

from flask import make_response
import ibm_boto3
from ibm_botocore.client import Config, ClientError
from unittest import case

from ibm_dist import app
socketio = SocketIO(app)
CORS(app)

# ======= add login ======= 
from ibm_dist.view import login
app.register_blueprint(login.url)
app.secret_key = os.urandom(24)
from ibm_dist import login_manager
login_manager.init_app(app=app)

# ======= api ======= 
# from ibm_dist.api import assistantUsername, assistantPassword, assistantIAMKey, assistantUrl, workspace_id
from ibm_dist.api import conversation
app.register_blueprint(conversation.url)

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
