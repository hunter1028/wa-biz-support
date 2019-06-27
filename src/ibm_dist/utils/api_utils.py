#-*- coding: utf-8 -*-
'''
ibm_dist.utils.api_utils -- watson assistant biz support

@author:     IBM
@copyright:  2019 IBM distribution. All rights reserved.
@version: 1.0

Created on 2019/06/26
'''

from ibm_watson import LanguageTranslatorV3
from ibm_dist import tranlatorUser, tranlatorPassword, tranlatorIAMKey, tranlatorUrl

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