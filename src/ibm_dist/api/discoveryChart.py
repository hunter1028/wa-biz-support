#-*- coding: utf-8 -*-
'''
ibm_dist.api.discoveryChart -- watson assistant biz support

@author:     IBM
@copyright:  2019 IBM distribution. All rights reserved.
@version: 1.0

Created on 2019/06/26
'''

from flask import json, jsonify
from flask import Blueprint
from ibm_dist import discovery_version, discovery_iam_apikey, discovery_url,discovery_collection_id,discovery_environment_id
from ibm_watson import DiscoveryV1

url = Blueprint('discoveryChart', __name__)

@url.route('/api/discoveryChartOne', methods=['POST', 'GET'])
def getDiscoveryChartOne():
    discovery = DiscoveryV1(
    version = discovery_version,
    iam_apikey = discovery_iam_apikey,
    url = discovery_url
    )

#   discovery.set_detailed_response(True)
    response = discovery.query(collection_id=discovery_collection_id,environment_id=discovery_environment_id, filter=None, query="", natural_language_query=None, passages=None, aggregation="timeslice(発生日,1day)", count="2", return_fields=None, offset=None, sort=None, highlight=None, passages_fields=None, passages_count=None, passages_characters=None, deduplicate=None, deduplicate_field=None, similar=None, similar_document_ids=None, similar_fields=None, logging_opt_out=None, collection_ids=None, bias=None);

    json_data = json.dumps(response.get_result(), indent=2,ensure_ascii=False)
    p_obj = json.loads(json_data)
    
    responseDemo = {}
    for resultD in p_obj['aggregations'][0]['results']:
        if resultD['matching_results'] > 0:
            responseDemo[resultD['key_as_string'][5:10].replace('-', ' ')] = resultD['matching_results']

    
#     response = Response(json.dumps(responseDemo))
#     response['Access-Control-Allow-Origin'] = '*'
#     response['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS' 
#     response['Access-Control-Max-Age'] = '1000' 
#     response['Access-Control-Allow-Headers'] = '*'
    return jsonify(results=responseDemo)