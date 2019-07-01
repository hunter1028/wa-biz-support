#-*- coding: utf-8 -*-
'''
ibm_dist.api.speechFromText -- watson assistant biz support

@author:     IBM
@copyright:  2019 IBM distribution. All rights reserved.
@version: 1.0

Created on 2019/06/26
'''

from flask import Response
from flask import Blueprint, request
from ibm_dist import textToSpeechUser, textToSpeechPassword, textToSpeechIAMKey, textToSpeechUrl, language_identify
from ibm_watson import TextToSpeechV1
 
url = Blueprint('textToSpeech', __name__)

@url.route('/api/text-to-speech', methods=['POST'])
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
    
#     global language_identify
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