#-*- coding: utf-8 -*-
'''
ibm_dist.api.downloadFile -- watson assistant biz support

@author:     IBM
@copyright:  2019 IBM distribution. All rights reserved.
@version: 1.0

Created on 2019/06/26
'''

from flask import request, make_response
from flask import Blueprint
from ibm_dist import cos

url = Blueprint('downloadFile', __name__)

@url.route('/api/docs', methods=['POST'])
def download_file(id= None):
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