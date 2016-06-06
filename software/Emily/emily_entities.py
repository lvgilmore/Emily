#! /usr/bin/python
'''
Created on Apr 26, 2016

@author: geiger
'''
from logging import Logger
import uuid
import logging

class EmilyLogger(Logger):
    def __init__(self, args={}):
        Logger.__init__(self, args['level'])

class Farm:
    
    
    def __init__(self, farm_id, args={}):
        self.farm_id = farm_id
        #set defaults
        self.lb_method = 'round_robin'
        self.port = 80
        self.location = '/'
        self.protocol = 'http'
        self.members = {}
        self.logger = EmilyLogger(args={'level': logging.INFO})
        self.ip = '0.0.0.0'
        self.name = ""
        #so long defaults
        self.upadte_farm(args)
        #name should not be empty
        if self.name == "":
            self.name = str(self.ip) + ":" + str(self.port) + '-' + str(self.location)
            self.name = self.name.replace('/','-')
        
    
    def upadte_farm(self, args):
        if args.has_key('lb_method'): self.lb_method = args.pop('lb_method')
        if args.has_key('port'): self.port = args.pop('port')
        if args.has_key('location'): self.location = args.pop('location')
        if args.has_key('protocol'): self.protocol = args.pop('protocol')
        if args.has_key('members'): self.members = args.pop('members') 
        if args.has_key('ip'): self.ip = args.pop('ip')
        if args.has_key('name'): self.name = args.pop('name')
        
        for key in args.keys():
            self.logger.debug("In Farm.parse_args: received unknown argument %s" % str(key))
                
    
    def get_members(self):
        return self.members
    
    def get_member(self, member_id):
        if self.members.has_key(member_id): return self.members[member_id]
        else: return None
    
    def add_member(self, member):
        member_id = self.genereate_farm_member_id()
        if self.get_member(member_id) is None:
            self.members[member_id] = member
        else:
            self.logger.warning("In Farm.add_member(member_id: %s ): member already exists" % str(member_id))
    
    def delete_member(self, member_id):
        return self.members.pop(member_id)
    
    def genereate_farm_member_id(self):
        uid = uuid.uuid4()
        while  self.get_member(uid) is not None:
            uid = uuid.uuid4()
        return uid
    
    def __str__(self):
        representation = ""
        representation = representation + "name: " + str(self.name) + "\n"
        representation = representation + "protocol: " + str(self.protocol) + "\n"
        representation = representation + "ip: " + str(self.ip) + "\n"
        representation = representation + "port: " + str(self.port) + "\n"
        representation = representation + "location: " + str(self.location) + "\n"
        representation = representation + "lb_method: " + str(self.lb_method) + "\n"
        representation = representation + "logger: " + str(self.logger) + "\n"
        representation = representation + "members: \n"
        for member in self.members.values():
            representation = representation + "\t" + str(member)
        return representation

class Farm_Member:
    def __init__(self, args):
        if isinstance(args, str):
            self.url = args
        else:
            self.url = args['url']
            self.weight = args['weight']
    
    def __str__(self):
        representation = ""
        representation = representation + str(self.url)
        if self.weight is not None and self.weight != "":
            representation = representation + " weight=" + str(self.weight)
        representation = representation + ";"
        return representation
    
    def __repr__(self):
        return str(self)
    
# unit tests
if __name__ == '__main__':
    farm = Farm(farm_id = uuid.uuid4(),
                args = {'lb_method': 'round_robin',
                 'port': 443,
                 'location': '/right/here',
                 'protocol': 'https',
                 'ip': '190.20.18.139'})
    print(str(farm))
    print(" adding member")
    member = Farm_Member({'url': 'lnx-int-yum-1:6793',
                          'weight': 2})
    farm.add_member(member)
    print(member)
    print(str(farm))