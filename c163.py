#test game server control moudle _ c.163 api

__version__ = '0.0.3'
__all__=["c163"]
__author__ = 'dixyes <dixyes@gmail.com>'

_app_key="xxxxxx" #not recomended
_app_secret="yyyyyy"
_api_doamin="https://open.c.163.com"
#_api_doamin="http://localhost:2334"

_default_charge_type=1
_default_spec_id=1
_default_image_type=1
_default_image_id=2
_default_name="new container "
_default_bandwidth=100

import json,time,sys
if sys.version_info < (3,0):
    import urllib2 #  HTTPError
    from urllib2 import HTTPError
else:
    import urllib.request as urllib2 #  HTTPError
    #urllib2.Request=urllib2.request
    from urllib.error import HTTPError
    

class c163:
    def __init__(self,**opts):
        self.err=None
        self.code=None
        self.token=opts.get("token")
    def __setattr__(self, name, value):
        self.__dict__[name] = value
    def __getattr__(self, name):
        try:
            if not self.__dict__.get(name):
                if name in ["token","image_list","ssh_key_list","repo_list","container_list"]:
                    return self._hget(name)
            return self.__dict__[name]
        except KeyError:
            raise AttributeError(name)
    def _hget(self,name):
        if name == "token":
            return self.get_token()
        if name == "image_list":
            return self.get_image_list()
        if name == "ssh_key_list":
            return self.get_ssh_key_list()
        if name == "repo_list":
            return self.get_repo_list()
        if name == "container_list":
            return self.get_container_list()
        raise KeyError
# get part
    def get_token(self):
        payload={
        'app_key':_app_key,
        'app_secret':_app_secret
        }
        token=self.post(_api_doamin+'/api/v1/tokne',json.dumps(payload))
        if token :
            self.token=token.get("token","")
            return self.token
        return None
    def get_image_list(self):
        self.image_list=self.get_uri(_api_doamin+'/api/v1/containers/images')
        return self.image_list
    def get_container_list(self,offset=None,limit=None):
        uri=_api_doamin+'/api/v1/containers?'
        if limit:
            uri+="limit="+str(limit)+"&"
        if offset:
            uri+="offset="+str(offset)
        if uri[-1:]=="?" or uri[-1:]=="&":
            uri=uri[:-1]
        if not (limit or offset):
            self.image_list=self.get_uri(uri)
            return self.image_list
        else:
            return self.get_uri(uri)
    def get_ssh_key_list(self):
        self.ssh_key_list=self.get_uri(_api_doamin+'/api/v1/secret-keys',)
        return self.ssh_key_list
    def get_repo_list(self):
        self.repo_list=self.get_uri(_api_doamin+'/api/v1/repositories')
        return self.repo_list
    def get_repo(self,rid):
        return self.get_uri(_api_doamin+'/api/v1/repositories/'+str(rid))
    def get_flow(self,cid=0,from_time=None,to_time=None):
        if from_time or to_time:
            uri=_api_doamin+'/api/v1/containers/'+str(rid)+'/flow?from_time='+(from_time or "0")+'&to_time='+(to_time or str(int(time.time())))
        else:
            uri=_api_doamin+'/api/v1/containers/'+str(rid)+'/flow'
        return self.get_uri(uri)
    def get_uri(self,uri=""):
        try:
            req=urllib2.Request(uri,None,{'Content-Type':'application/json','Authorization':'Token '+self.token})
            rep=urllib2.urlopen(req)
            repstr=rep.read()
        except HTTPError as e :
            self.err=str(e)
            self.code=e.code
            return None
        except:
            self.err="unknow err"
            return None
        try:
            #print(repstr.decode("utf8"))
            if sys.version_info < (3,0):
                ret=json.loads(repstr)
            else:
                ret=json.loads(repstr.decode("utf8"))
            self.err=None
            self.code=rep.code
            return ret
        except TypeError or ValueError:
            self.err="cant parse respond:"+str(repstr)
            return None
        except:
            self.err="unknow err"
            return None

# post part
    def create_container(self,**opts):
        payload={
        "charge_type": opts.get("charge_type",_default_charge_type),
        "spec_id": opts.get("spec_id",_default_spec_id),
        "image_type": opts.get("image_type",_default_image_type),
        "image_id": opts.get("image_id",_default_image_id),
        "name": opts.get("name",_default_name+str(int(time.time())))
        }
        if payload["charge_type"]==2:
            payload["use_public_network"]=opts.get("use_public_network",1)
        if opts.get("desc"):
            payload["desc"]=opts.get("desc")
        if opts.get("ssh_key_ids"):
            payload["ssh_key_ids"]=opts.get("ssh_key_ids")
        if opts.get("env_var"):
            payload["env_var"]=opts.get("env_var")
        if payload.get("use_public_network") and payload["use_public_network"]==1:
            payload["network_charge_type"]=opts.get("network_charge_type",1)
        if payload.get("network_charge_type") and payload["network_charge_type"]==1:
            payload["bandwidth"]=opts.get("bandwidth",_default_bandwidth)
        print("payload="+json.dumps(payload))
        for char in payload["name"]:
            if not char in "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890":
                raise NameError("illegal char \""+char+"\"in name option")
        ret=self.post_uri(_api_doamin+"/api/v1/containers",json.dumps(payload))
        self.get_container_list()
        #print(json.dumps(ret))
        return ret
    def save_container(self,cid,**opts):
        payload={
        'repo_name':opts.get('repo_name'),
        'tag':opts.get('tag')
        }
        ret=self.post_uri(_api_doamin+"/api/v1/containers/"+str(cid)+"/tag",json.dumps(payload))
        self.get_image_list()
        return ret
    def create_ssh_key(self,**opts):
        payload={opts.get("key_name")}
        ret=self.post_uri(_api_doamin+"/api/v1/secret-keys",json.dumps(payload))
        self.get_ssh_key_list()
        return ret
    def post_uri(self,uri="",payload=""):
        try:
            if sys.version_info < (3,0):
                if self.token:
                    req=urllib2.Request(uri,payload,{'Content-Type':'application/json','Authorization':'Token '+self.token})
                else:
                    req=urllib2.Request(uri,payload,{'Content-Type':'application/json'})
                
            else:
                if self.token:
                    req=urllib2.Request(uri,data=payload.encode("utf8"),headers={'Content-Type':'application/json','Authorization':'Token '+self.token})
                else:
                    req=urllib2.Request(uri,data=payload.encode("utf8"),headers={'Content-Type':'application/json'})
                #repstr=req.read()
            rep=urllib2.urlopen(req)
            repstr=rep.read()
            #print(str(urllib2.urlopen(req).code))#todo: another code get way
        except HTTPError as e :
            self.code=e.code
            self.err=str(e)
            return None
        except:
            self.code=None
            self.err="unknow err"
            return None
        try:
            if sys.version_info < (3,0):
                ret=json.loads(repstr)
            else:
                ret=json.loads(repstr.decode("utf8"))
            self.code=rep.code
            self.err=None
            return ret
        except TypeError:
            self.err="cant parse respond:"+str(repstr)
            return None

#other method
    def modify_container(self,**opts):
        payload={}
        if opts.get("charge_type"):
            payload["charge_type"]=opts.get("charge_type")
        if opts.get("desc"):
            payload["desc"]=opts.get("desc")
        if opts.get("network_charge_type"):
            payload["network_charge_type"]=opts.get("network_charge_type")
        if opts.get("bandwidth"):
            payload["bandwidth"]=opts.get("bandwidth")
        ret=self.method_uri(_api_doamin+'/api/v1/containers/'+opts.get("id","impossibleid"),json.dumps(payload),"PUT")
        self.get_container_list()
        return ret
    def delete_container(self,cid):
        ret=self.method_uri(_api_doamin+'/api/v1/containers/'+str(cid),None,"DELETE")
        self.get_container_list()
        return ret
    def restart_container(self,cid):
        ret=self.method_uri(_api_doamin+'/api/v1/containers/'+str(cid)+'/actions/restart',None,"PUT")
        self.get_container_list()
        return ret
    def delete_image(self,repo_name="",tag=""):
        ret=self.method_uri(_api_doamin+'/api/v1/repositories/'+repo_name+'/tags/'+tag,None,"DELETE")
        self.get_image_list()
        return ret
    def method_uri(self,uri="",payload="",method="PUT"):
        try:
            if sys.version_info < (3,0):
                req=urllib2.Request(uri,payload,{'Content-Type':'application/json','Authorization':'Token '+self.token})
                req.get_method = lambda:method
            else:
                if(payload==None):
                    req=urllib2.Request(uri,headers={'Content-Type':'application/json','Authorization':'Token '+self.token},method=method)
                else:
                    req=urllib2.Request(uri,data=payload.encode("utf8"),headers={'Content-Type':'application/json','Authorization':'Token '+self.token},method=method)
            rep=urllib2.urlopen(req)
            repstr=rep.read()
        except HTTPError as e :
            self.code=e.code
            self.err=str(e)
            return None
        except:
            self.err="unknow err"
            return None
        try:
            if repstr and str(repstr)!="":
                if sys.version_info < (3,0):
                    ret=json.loads(repstr)
                else:
                    ret=json.loads(repstr.decode("utf8"))
                self.code=rep.code
                self.err=None
                return ret
            else: 
                self.code=rep.code
                return None
        except TypeError:
            self.err="cant parse respond:"+str(repstr)
            return None
        except:
            self.err="unknown err:"+str(repstr)
            return None
        
        
        
        
        
