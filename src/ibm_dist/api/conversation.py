# #!/usr/local/bin/python2.7
# # encoding: utf-8
# '''
# ibm_dist.api.conversation -- shortdesc
# 
# ibm_dist.api.conversation is a description
# 
# It defines classes_and_methods
# 
# @author:     user_name
# 
# @copyright:  2019 organization_name. All rights reserved.
# 
# @license:    license
# 
# @contact:    user_email
# @deffield    updated: Updated
# '''
# import json
# from flask import jsonify
# from flask import Blueprint, request
# from ibm_dist import assistantUsername, assistantPassword, assistantIAMKey, assistantUrl, workspace_id
# from ibm_dist.api.api_utils import getTranslatorText, getTranslatorToEnlish
# from ibm_watson import AssistantV1
# 
# url = Blueprint('conversation', __name__)
# 
# # @url.route('/api/conversation', methods=['POST', 'GET'])
# def getConvResponse():
#     # Instantiate Watson Assistant client.
#     # only give a url if we have one (don't override the default)
#     try:
#         assistant_kwargs = {
#             'version': '2018-09-20',
#             'username': assistantUsername,
#             'password': assistantPassword,
#             'iam_apikey': assistantIAMKey,
#             'url': assistantUrl
#         }
#         
#         assistant = AssistantV1(**assistant_kwargs)
#         convText = request.form.get('convText')
#         convContext = request.form.get('context')
#     
#         if convContext is None:
#             convContext = "{}"
#         jsonContext = json.loads(convContext)
#     
#         if convText != None :
#             print('翻訳前：　'+convText)
#         
#         convText = getTranslatorText(convText)
#         
#         response = assistant.message(workspace_id=workspace_id,
#                                      input={'text': convText},
#                                      context=jsonContext)
#     except Exception as e:
#         print(e)
# 
#     response = response.get_result()
#    
#     json_data = json.dumps(response,indent=2)
#     
#     moreflg = False;
#     if (len(response["output"]["generic"])==1):
#         r_type =  response["output"]["generic"][0]["response_type"]
#         if r_type == 'text' :
#             reponseContent = response["output"]["text"]
#         else:
#             reponseContent = response["output"]["generic"][0]
#     else:
#         for item in response["output"]['generic']:
#             if item["response_type"] == 'text' :
#                 reponseContent = item["text"]
#             if item["response_type"] == 'option' :
#                 reponseContent2 = item   
#         moreflg =True
#     
#     r_type =  response["output"]["generic"][0]["response_type"]
#     intent = ''
#     if len(response["intents"]):
#         intent = response["intents"][0]["intent"]
#     
#     # set reponseContent by response_type
#    
#         
#     print(reponseContent)
#     global language_identify
#     if language_identify == 'en':
#         if r_type == 'text' :
#             translation =   getTranslatorToEnlish(reponseContent)
#             if(moreflg):
#                 translation2 =   getTranslatorToEnlish(reponseContent2["title"])
#                 reponseContent2["title"] = translation2['translations'][0]['translation']
# #                 for item in reponseContent2["options"]:
# #                     trans_val = getTranslatorToEnlish(item['value']['input']['text'])
# #                     print(trans_val['translations'][0]['translation'])
# #                     item['value']['input']['text'] = trans_val['translations'][0]['translation']
#             print(translation)
#             reponseContent = translation['translations'][0]['translation']
#         else:
#             translation2 =   getTranslatorToEnlish(reponseContent["title"])
#             reponseContent["title"] = translation2['translations'][0]['translation']
# #             for item in reponseContent["options"]:
# #                 
# #                 print(item['value']['input']['text'])
# #                 item_value = item['value']['input']['text']
# #                 item['value']['input']['text'] = getTranslatorToEnlish(item['value']['input']['text'])
#            
#     print(intent)
#     
#     if 'discovery' in intent.lower() :
#         if(moreflg):
#             responseDetails = {'responseType': 'text',
#                        'responseType2': 'option',
#                        'reponseContent': reponseContent,
#                        'reponseContent2': reponseContent2,
#                        'sendToDiscovery': 'send',
#                        'context': response["context"]}
#         else:
#             responseDetails = {'responseType': r_type,
#                        'reponseContent': reponseContent,
#                        'sendToDiscovery': 'send',
#                        'context': response["context"]}       
#     else :
# 
#         if(moreflg):
#             responseDetails = {'responseType': 'text',
#                        'responseType2': 'option',
#                        'reponseContent': reponseContent,
#                        'reponseContent2': reponseContent2,
#                        'sendToDiscovery': 'noSend',
#                        'context': response["context"]}
#         else:
#             responseDetails = {'responseType': r_type,
#                        'reponseContent': reponseContent,
#                        'sendToDiscovery': 'noSend',
#                        'context': response["context"]}    
#     
#     return jsonify(results=responseDetails)