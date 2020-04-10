from __future__ import print_function  # Python 2/3 compatibility
from py2neo import Graph, Node, Relationship
import decimal
import urllib.request, json
from neo4j import GraphDatabase
from lib2to3.tests.support import driver
from ctypes.test.test_pickling import name
import boto3
import botocore
import paramiko
from Tools.scripts.parse_html5_entities import get_json
from sys import stderr
import threading
import time
import logging


# neo4j
uri = "bolt://localhost:7687"
#auth=(username,password)
graph_ = Graph(uri, auth=("neo4j",passwd))

instance = ""
user_ = ""





#ssh key
key = paramiko.RSAKey.from_private_key_file(r"/keylocation")


client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

#creates log from servers it logs into
def set_log(info):
    File_log = open(r"C:\Users\scar1\eclipse-workspace\seniorP\src\logfiles\log.txt","a")
    
    temp = str(info).replace('\\n','\n')
    
    
    File_log.write(temp)
    
    File_log.close
    
#tells you what server its working on 
#also due to threading this is inaccurate need to change something
def set_log_name(name):
    File_log = open(r"C:\Users\scar1\eclipse-workspace\seniorP\src\logfiles\log.txt","a")
    
    File_log.write("\n-------"+ name+"----------\n")
    
    File_log.close

#lets you know in log if script is not found   
def get_log_err(name):
    File_log = open(r"C:\Users\scar1\eclipse-workspace\seniorP\src\logfiles\log.txt","a")
    
    File_log.write("\nScript can not be found:"+ name+"\n")
    
    File_log.close
    
    
#reads json thats stored on S3
def url_json(name):      
    with urllib.request.urlopen(name) as url:
        data = json.loads(url.read().decode())
        
        print("loading json...")
        print("getting server info...")
        
        instance = data['ip']
        user_ = data['user']
        
        
        for scripts in data['scripts']:
            for key, comm in scripts.items():

                exe_comms(instance,user_,comm)
                
        print("closing json...")
        url.close()
        

#get the servers name from the neo4j database
def get_neo4j_single(name_server):
    print("getting server script info...")
    return graph_.run("MATCH (a:Server) WHERE a.name=$x RETURN a.script",x=name_server).evaluate()

#current the servers are broken up into group to do multiple server at once with no down time
#i have to review this to work solely of queries instead of groups of servers
#this update the first set of servers
#problem: this will update all servers so i was planning to take total number/2 then this method will take ceilling number
#and the second method will take the floor of the int
def get_neo4j_group(name_group):
    

    even_server= 0
    
    print("getting " +name_group+" of server list...")
    
    list_ = graph_.run("MATCH (a:Group1) WHERE a.name=$x RETURN a.list",x=name_group).evaluate()
    
    
    
    while(even_server < len(list_)):
        
        temp = list_.pop(even_server)
        
        print("starting "+ temp + " ssh....")
        
        
        set_log_name(temp)
          
        
        url_json(get_neo4j_single(temp))
        
        print("finished "+ temp + " ssh....")
        
        even_server = even_server + 2
        


#second set of servers go through update        
def get_neo4j_group_odd(name_group):
    
    
    #time.sleep(25)
    #sleep is here to make sure the commands both reach the console because i believe the way the methods currently are
    #the commands butt heads so i believe revising the exe_comms will fix this
    logging.info("Thread odd: starting")
    
    odd_server= 1
    
    print("getting " +name_group+" of server list...")
    
    list_ = graph_.run("MATCH (a:Group1) WHERE a.name=$x RETURN a.list",x=name_group).evaluate()
    
    
    
    while(odd_server < len(list_)):
        
        temp = list_.pop(odd_server)
        
        print("starting "+ temp + " ssh....")
        
        set_log_name(temp)

        
        url_json(get_neo4j_single(temp))
        
        print("finished "+ temp + " ssh....")
        
        odd_server = odd_server + 2
        

#ssh into servers and excute commands
def exe_comms(ip,user,comm):
    try:
        
        print("attempting  ssh....")
        
        #Here 'ec2-user' is user name and 'instance' is public IP of EC2
        client.connect(hostname=ip, username=user, pkey=key)
        
        print("ssh complete....")
        print("attempting to exe command...")
        
        # Execute a command(....) after connecting/ssh to an instance
        stdin, stdout, stderr = client.exec_command(comm)
        
        
        if(str(comm).find("log")) > -1:
            
            set_log(str(stdout.read()))
        
        
        if (str(stderr.read()).find("No such file or directory")) >= 0  :

            get_log_err(comm)
            
            print("script not found")
            
        else:
            
            print(comm + " successful!")
        
        # close the client connection once the job is done
        print("closing  ssh....")
        client.close()

    except Exception:
        print("Connection failed")


if __name__ == "__main__":
    #sets the methods get_neo4j_group and get_neo4j_group_odd up for threading 
    t1 = threading.Thread(name = "even",target=get_neo4j_group, args=("group1",))
    t2 = threading.Thread(name = "odd",target=get_neo4j_group_odd, args=("group1",))
    
    #start threading
    t1.start()
    t2.start()
    
    










