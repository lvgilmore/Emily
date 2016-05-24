#! /usr/bin/python
'''
Created on Apr 24, 2016

@author: geiger
'''
#from api_router import api_router
from emily_model import Emily_Model
from flask import request
import json
from flask.helpers import make_response

class Emily_view:
    
    def __init__(self, model=None):
        if model is None:
            self.model = Emily_Model()
        else:
            self.model = model
    
    def farms_api(self):
        if request.method == 'GET':
            return json.dumps(self.model.get_farms())
        elif request.method == 'POST':
            args = self.request_data(request)
            make_response(self.model.create_farm(args))
        else:
            raise "in Emily_View.farms_api, unknown method: %s" % request.method.to_string()
    
    def farm_api(self, farm_id):
        if request.method == 'GET':
            return json.dumps(self.model.get_farm(farm_id))
        elif request.method == 'PUT':
            args = self.request_data(request)
            make_response(self.model.update_farm(farm_id, args))
        elif request.method == 'DELETE':
            make_response(self.model.delete_farm(farm_id))
        else:
            raise "in Emily_View.farm_api, unknown method: %s" % request.method.to_string()
    
    def farm_members_api(self, farm_id):
        if request.method == 'GET':
            return json.dumps(self.model.get_farm_members(farm_id))
        elif request.method == 'POST':
            args = self.request_data(request)
            return json.dumps(self.model.create_farm_member(farm_id, args))
        else:
            raise "in Emily_View.farm_members_api, unknown method: %s" % request.method.to_string()
        
    def farm_member_api(self, farm_id, member_id):
        if request.method == 'GET':
            return json.dumps(self.model.get_farm_member(farm_id, member_id))
        elif request.method == 'DELETE':
            return json.dumps(self.model.delete_farm_member(farm_id, member_id))
        else:
            raise "in Emily_View.farm_member_api, unknown method: %s" % request.method.to_string()
        
    def request_data(self, request):
        if request.headers['Content-Type'] == 'application/json':
            return request.json
        elif request.headers['Content-Type'] == 'text/plain':
            try:
                return  json.loads(request.data)
            except:
                raise "couldn't parse request %s as json" % str(request)
        else:
            raise "unknown content type: %s" % request.headers['Content-Type']
        
    def view_api(self):
        routes = [
                {'rule': '/Emily/farms',
                 'view_func': self.farms_api,
                 'methods': ['GET', 'POST']},
                {'rule': '/Emily/farms/<string:farm_id>',
                 'view_func': self.farm_api,
                 'methods': ['GET', 'PUT', 'DELETE']},
                {'rule': '/Emily/farms/<string:farm_id>/members',
                 'view_func': self.farm_members_api,
                 'methods': ['GET', 'POST']},
                {'rule': '/Emily/farms/<string:farm_id>/members/<string:member_id>',
                 'view_func': self.farm_member_api,
                 'methods': ['GET', 'DELETE']}
                ]
        return routes
    