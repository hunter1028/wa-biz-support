#!/usr/local/bin/python2.7
# encoding: utf-8
'''
ibm_dist.api.api_utils -- shortdesc

ibm_dist.api.api_utils is a description

It defines classes_and_methods

@author:     user_name

@copyright:  2019 organization_name. All rights reserved.

@license:    license

@contact:    user_email
@deffield    updated: Updated
'''
from ibm_watson import LanguageTranslatorV3
from ibm_dist.api import tranlatorUser, tranlatorPassword, tranlatorIAMKey, tranlatorUrl

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