'''
Created on Apr 26, 2016

@author: geiger
'''
from os import remove, system, listdir
from emily_entities import EmilyLogger, Farm_Member, Farm
from logging import INFO
from io import open

DEFAULT_CONF_DIR="../../tmp/conf.d/"

class Emily_Controller(object):
    '''
    classdocs
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        self.conf_dir = DEFAULT_CONF_DIR
        self.logger = EmilyLogger({'level': INFO})
    
    def load_farms(self):
        farms={}
        conf_files = listdir(self.conf_dir)
        for conf in conf_files:
            if conf.endswith('.conf'):
                farm_id=conf[:-5]
                farms[farm_id] = self.load_farm(farm_id)
        return farms
    
    def load_farm(self, farm_id):
        filename = str(self.conf_dir) + str(farm_id) +".conf"
        conf_file = open(filename, 'r')
        file_content = str(conf_file.read()).split()
        conf_file.close() 
        farm_args, members_args = self.parse_configuration(file_content)
        members={}
        while members_args.__len__() > 0:
            item = members_args.popitem()
            members[item[0]] = Farm_Member({'url': item[0], 'weight': item[1]})
        farm_args['members'] = members
        return Farm(farm_id, farm_args)
    
    def commit_farm(self, farm):
        file_content = self.configuration_string(farm)
        destination = open(self.conf_dir + str(farm.farm_id) +".conf", 'w')
        destination.write(unicode(file_content))
        destination.close()
        # infrom nginx about the changes
        system("nginx -s reload")
    
    def delete_farm(self, farm_id):
        filename = str(self.conf_dir) + str(farm_id) +".conf"
        try: 
            remove(filename)
        except OSError as e:
            if e.errno == 2: # file not found error
                self.logger.info("In Emily_Controller.delete_farm(farm_id: %s ): file not found" % farm_id)
            else: raise e
        # infrom nginx about the changes
        system("nginx -s reload")
        
    
    def configuration_string(self, farm):
        file_content = ""
        # build the farm members configuration section
        file_content = file_content + 'upstream ' + str(farm.farm_id) + ' {\n'
        if farm.lb_method != "": file_content = file_content + '\t' + farm.lb_method + ';\n'
        for member in farm.members:
            file_content = file_content + '\tserver ' + str(member) + ';\n'
        file_content = file_content + '}\n'
        # build the farm configuration section
        file_content = file_content + 'server {\n'
        file_content = file_content + '\tlisten ' + str(farm.ip) + ':' + str(farm.port) + ';\n'
        file_content = file_content + '\tlocation ' + str(farm.location) + ' {\n'
        file_content = file_content + '\t\tproxy_pass ' + str(farm.protocol) + '://' + farm.farm_id + ';\n'
        file_content = file_content + '\t}\n'
        file_content = file_content + '}\n'
        
        return file_content
    
    # I chose to parse using an automate, sorry if its too big a hustle
    def parse_configuration(self, content):
        farm_args = {}
        members_args = {}
        # Reversing the order of the array, because working with pop is so much easier
        content.reverse()
        self.parsing_begin(content, farm_args, members_args)
        return farm_args, members_args
    
    def parsing_begin(self, content, farm_args, members_args):
        try:
            while True:
                head = str(content.pop())
                if head == 'upstream':
                    farm_args['name'] = content.pop()
                    if str(content.pop()) == '{':
                        self.parsing_upstream(content, farm_args, members_args)
                    else:
                        raise "In Emily_Controller.parsing_begin: after upstream expected {, instead got %s " % head
                elif head == 'server':
                    if str(content.pop()) == '{':
                        self.parsing_server(content, farm_args, members_args)
                    else:
                        raise "In Emily_Controller.parsing_begin: after server expected {, instead got %s " % head
                else:
                    raise "In Emily_Controller.parsing_begin: unknown word %s " % head
        except IndexError: # indcates that the array is empty, which means we're done
            return True
        
    def parsing_upstream(self, content, farm_args, members_args):
        try:
            while True:
                head = str(content.pop())
                if head in ['round_robin;', 'ip_hash;', 'least_conn;']:
                    farm_args['lb_method'] = head[:-1]
                elif head == "server":
                    self.parsing_member(content, farm_args, members_args)
                elif head == "}":
                    return True
                else:
                    raise("In Emily_Controller.parsing_upstream: unknown word %s " % head)
        except IndexError:
            raise "In Emily_Controller.parsing_upstream: ended unexpectedly"
    
    def parsing_member(self, content, farm_args, members_args):
        head = str(content.pop())
        if head[head.__len__()-1] == ';':
            members_args[head[:-1]] = 1
            return True
        else:
            weight = str(content.pop()) 
            if weight.startswith('weight='):
                members_args[head] = weight.split('=')[1]
            else:
                raise("In Emily_Controller.parsing_member: unknown word %s , expected ; or weight" % weight)
    
    def parsing_server(self, content, farm_args, members_args):
        try:
            while True:
                head = str(content.pop())
                if head == 'listen':
                    listen = str(content.pop())
                    if listen.endswith(';'): listen = listen[:-1]
                    if ':' in listen:
                        listen = listen.split(':')
                        farm_args['ip'] = listen[0]
                        farm_args['port'] = listen[1]
                    else:
                        farm_args['port'] = listen
                elif head == 'location':
                    farm_args['location'] = str(content.pop())
                    if str(content.pop()) == '{':
                        self.parsing_location(content, farm_args, members_args)
                    else:
                        raise "In Emily_Controller.parsing_server: after location expected {, instead got %s " % head
                elif head == '}':
                    return True
                else:
                    raise "In Emily_Controller.parsing_server: unknown word %s " % head
        except IndexError:
            raise "In Emily_Controller.parsing_server: ended unexpectedly"
    
    def parsing_location(self, content, farm_args, members_args):
        try:
            while True:
                head = str(content.pop())
                if head == 'proxy_pass':
                    head = str(content.pop())
                    if "://" in head:
                        farm_args['protocol'] = head.split("://")[0]
                elif head == '}':
                    return True
                else:
                    raise "In Emily_Controller.parsing_location: expected proxy_pass, instead got %s " % head
        except IndexError:
            raise "In Emily_Controller.parsing_location: ended unexpectedly"

# unit tests
if __name__ == '__main__':
    controller = Emily_Controller()
    farms = controller.load_farms()
    print(str(farms))
    for farm in farms.values():
        print("\t" + str(farm))
    farms['me'].location="/over/there"
    controller.commit_farm(farms['me'])
