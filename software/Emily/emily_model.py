#! /usr/bin/python
'''
Created on Apr 24, 2016

@author: geiger
'''

import json
from emily_controller import Emily_Controller
from emily_entities import Farm, Farm_Member
import uuid

class Emily_Model(object):

    def __init__(self, controller=None):
        '''
        Constructor
        '''
        if controller is None:
            self.controller = Emily_Controller()
        else:
            self.controller = controller
        self.farms = {}
        self.indexes = {}
        self.load_farms()
    
    def load_farms(self):
        self.farms = self.controller.load_farms()
        for farm_id, farm in self.farms.items():
            self.create_indexes(farm_id, farm)
    
    def get_farms(self):
        return self.farms
    
    def get_farm(self, farm_id):
        if self.indexes.has_key(farm_id):
            farm_id = self.indexes[farm_id]
        if self.farms.has_key(farm_id):
            self.farms[farm_id] = self.controller.load_farm(farm_id)
        else:
            self.controller.load_farms()
            
        if self.farms.has_key(farm_id): return self.farms[farm_id]
        else: return None
    
    def create_farm(self, args):
        farm_id = self.generate_farm_id()
        new_farm = Farm(farm_id, args)
        self.farms[farm_id] = new_farm
        self.create_indexes(farm_id, new_farm)
        self.controller.commit_farm(new_farm)
        return json.dumps({"farm": new_farm}), 201
        
    def update_farm(self, farm_id, args):
        farm = self.get_farm(farm_id)
        farm.update_farm(args)
        self.create_indexes(farm_id, farm)
        self.controller.commit_farm(farm)
        return json.dumps({"farm": farm}), 201
    
    def delete_farm(self, farm_id):
        if self.indexes.has_key(farm_id):
            farm_id = self.indexes[farm_id]
        if self.get_farm(farm_id) is None:
            return json.dumps({"error": "farm not found"}), 404
        else:
            self.farms[farm_id] = None
            self.controller.delete_farm(farm_id)
            for key, value in self.indexes.items():
                if value == farm_id: self.indexes.pop(key)
            return json.dumps({"farm_id": farm_id}), 201
        
    def get_farm_members(self, farm_id):
        if self.get_farm(farm_id) is None:
            return json.dumps({"error": "farm not found"}), 404
        return self.get_farm(farm_id).get_members()
    
    def get_farm_member(self, farm_id, member_id):
        if self.get_farm(farm_id) is None:
            return json.dumps({"error": "farm not found"}), 404
        return self.get_farm(farm_id).get_member(member_id)
    
    def create_farm_member(self, farm_id, args):
        if self.get_farm(farm_id) is None:
            return json.dumps({"error": "farm not found"}), 404
        farm = self.get_farm(farm_id)
        return json.dumps(farm.add_member(args))
    
    def delete_farm_member(self, farm_id, member_id):
        if self.get_farm(farm_id) is None:
            return json.dumps({"error": "farm not found"}), 404
        farm = self.get_farm(farm_id)
        if farm.get_member(member_id) is None:
            return json.dumps({"error": "member not found"}), 404
        else:
            farm.delete_member(member_id)
            self.controller.commit_farm(farm)
            return json.dumps({"member_id": member_id, "farm_id": farm_id}), 201
    
    def generate_farm_id(self):
        uid = uuid.uuid4() 
        while self.get_farm(uuid) is not None:
            uid = uuid.uuid4()
        return uid

    def create_indexes(self, farm_id, farm):
        id_string = str(farm.ip) + ":" + str(farm.port) + "/" + str(farm.location) 
        self.indexes[id_string] = farm_id
    
# unit tests
if __name__ == '__main__':
    model = Emily_Model()
    print(str(model))
    for farm in model.get_farms().values():
        print str(farm)
    