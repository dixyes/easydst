
# -*- coding: utf-8 -*-

#easier  gssvr.py - c163 x dst 
#easydst.py

__version__ = '0.0.2'
__all__=["easydst"]
__author__ = 'dixyes <dixyes@gmail.com>'

import json,time,sys,os,locale
from c163 import c163

ctr_prefix="EDST"#神tm连连字符都不支持，仅限字母数字
img_prefix=ctr_prefix
str_ver=__version__
int_ver=0
cfg_path="easydst.json"

def _resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
cfg_path=_resource_path(cfg_path)

_translation={}
_translation["C"]={
"help_text":"help_text"
}
_translation["en_us"]=_translation["en_gb"]=_translation["en_au"]={
"help_text":"help text here"#todo：balabala
}
_translation["zh_cn"]={
"help_text":"记得写个帮助提示"#todo：balabala
}
_translation["zh_tw"]=_translation["zh_hk"]={
"help_text":"记得写个帮助提示"#todo：balabala
}
def _translate(key):
    if verbose>4:
        print("[debug] lang set to: "+locale.getdefaultlocale()[0])
    return _translation.get(locale.getdefaultlocale()[0].lower(),_translation["C"])[key]


verbose=4 #debug5 verbose4 info3 warn2 error1 none0

class easydst :
    def __init__(self,token=None):
        if verbose >3 :
            print("[verbose] __init__ of easydst class")
        self.cfg=None
        try:
            with open(cfg_path,"r") as cfgfile:
                try:
                    self.cfg=json.loads(cfgfile.read())
                except:
                    raise Exception("bad cfg file")
        except IOError:
            self.cfg={"ver":int_ver,"token":None,"svrlist":{}}
            self.save_cfg()
        #print(json.dumps(cfg))
        if token == None:
            token=self.get_token()
        if len(str(token)) != 32:
            raise  ValueError("no token got")
        self.cfg["token"]=token
        self.known_sv=self.cfg.get("svrlist")
        self.unknown_sv={}
        self._c163=c163(token=token)
    def save_cfg(self):
        if verbose >3 :
            print("[verbose] saving config")
        with open(cfg_path,"w") as cfgfile:
            try:
                cfgfile.write(json.dumps(self.cfg))
            except IOError as e:
                raise Exception("save cfg file fail : IOError"+str(e))
            except:
                raise Exception("save cfg file fail :"+str(sys.exc_info()[1]))
    def set_token(self,token):
        #todo input here
        self.cfg["token"]=token
        self.save_cfg()
        return self.cfg.get("token",None)
    def get_token(self):
        #todo input here
        return self.cfg.get("token",None)
    def get_list(self):
        #get json save list
        resp=self._c163.get_container_list()
        if verbose >4 :
            print("[debug] response:"+json.dumps(resp)+"   "+str(self._c163.code)+"   "+str(self._c163.err))
        if verbose >4:
            print("[debug] known: "+json.dumps(self.known_sv)+" uknown:"+json.dumps(self.known_sv))
        for sv in self.known_sv:
            self.known_sv[sv]["status"]="known"
            self.known_sv[sv]["pubip"]=None
            self.known_sv[sv]["id"]=None
        for container in resp["containers"]:
            if container["name"].startswith(ctr_prefix):
                if container["name"][len(ctr_prefix):] in self.known_sv.keys():
                    self.known_sv[container["name"][len(ctr_prefix):]].update({"id":container["id"],"pubip":container["public_ip"],"status":container["status"]})
                else:
                    self.unknown_sv.update({container["name"][len(ctr_prefix):]:{"id":container["id"],"pubip":container["public_ip"],"status":container["status"]}})
    def start_svr(self,svrname):
        if verbose >4 :
            print("[debug] start_svr:"+json.dumps(self.known_sv.get(svrname,None)))
        if svrname in self.known_sv.keys():
            if self.known_sv[svrname].get("id")!=None:
                if verbose >2 :
                    print("[info] already started")
                return -1
            else:
                resp=self._c163.get_image_list()
                imgid=None
                if verbose >4 :
                    print("[debug] get_image_list resp:"+json.dumps(resp)+" ,err:"+json.dumps(self._c163.err))
                for img in resp["custom_images"]:
                    if img["name"] == self.known_sv.get(svrname,{}).get("repo_name","dstsuite") and img["tag"] == self.known_sv.get(svrname,{}).get("tag",img_prefix+"latest") :
                        imgid=img["id"]
                if imgid==None:
                    if verbose >1 :
                        print("[warn] no default tag \""+self.known_sv.get(svrname,{}).get("tag",img_prefix+"latest")+"\" found, use \"lastest\" instead")
                    for img in resp["custom_images"]:
                        if img["name"] == self.known_sv.get(svrname,{}).get("repo_name","dstsuite") and img["tag"] =="latest":
                            #use default instead
                            imgid=img["id"]
                if imgid==None:
                    raise Exception("no imgid got")
                #for dst, use these options
                resp=self._c163.create_container(
                charge_type=2,
                image_type=2,
                image_id=self.known_sv.get(svrname,{}).get("image_id",imgid),
                name=ctr_prefix+svrname,
                use_public_network=1,
                network_charge_type=2,
                bandwidth=100,
                spec_id=20
                )#20
                if verbose >4 :
                    print("[debug] create_container resp:"+json.dumps(resp)+" ,err:"+json.dumps(self._c163.err)+" ,code:"+json.dumps(self._c163.code))
                if self._c163.code==200 and resp!=None and resp.get("id")!=None:
                    if verbose >2 :
                        print("[info] start \""+svrname+"\" success!")
                    return 0
                else:
                    if verbose >2 :
                        print("[info] start \""+svrname+"\" fail with status code "+str(self._c163.code))
                    return -2
    def stop_svr(self,svrname):
        ret=self.save_svr(svrname)
        if ret != 0:
            return ret
        if verbose >4 :
            print("[debug] stop_svr:"+json.dumps(self.known_sv.get(svrname,None)))
        all_sv=dict(self.known_sv,**self.unknown_sv)
        resp=self._c163.delete_container(all_sv[svrname]["id"])
        if verbose >4 :
            print("[debug] delete_container resp:"+json.dumps(resp)+" ,err:"+json.dumps(self._c163.err))
        if self._c163.code == 200:
            if verbose >2 :
                print("[info] stop_svr success")
            return 0
        return -1
    def save_svr(self,svrname):
        if verbose >4 :
            print("[debug] save_svr:"+json.dumps(self.known_sv.get(svrname,None)))
        all_sv=dict(self.known_sv,**self.unknown_sv)
        #print(json.dumps(self.known_sv))
        sv=all_sv.get(svrname)
        if sv==None or not sv.get("status")=="create_succ":
            if verbose >0 :
                if sv==None:
                    print("[error] unknown slot \""+svrname+"\"")
                elif sv.get("status")=="create_fail":
                    print("[error] slot \""+svrname+"\" create fail, delete it instantly")
                elif sv.get("status")=="creating":
                    print("[error] slot \""+svrname+"\" is still creating")
                else:
                    print("[error] unknown slot \""+svrname+"\" status")
            return -1
        resp=self._c163.save_container(sv["id"],repo_name=sv.get(svrname,{"repo_name":"dstsuite"})["repo_name"],tag=img_prefix+"latest")
        if verbose >4 :
            print("[debug] save_container resp:"+json.dumps(resp)+" ,err:"+json.dumps(self._c163.err))
        if resp==None or resp.get("image_id")==None:
            if verbose >0 :
                print("[error] save fail")
            return -1
        resp=self._c163.save_container(sv["id"],repo_name=sv.get(svrname,{"repo_name":"dstsuite"})["repo_name"],tag=img_prefix+str(int(time.time())))
        if verbose >4 :
            print("[debug] save_container resp:"+json.dumps(resp)+" ,err:"+json.dumps(self._c163.err))
        if resp==None or resp.get("image_id")==None:
            if verbose >0 :
                print("[error] save fail")
            return -1
        return 0

def _main():
    import sys
    print("easydst ver "+str_ver+" by dixyes")
    for help in sys.argv[1:]:
        if help in ["help","-h","--help"]:
            print(_translate("help_text"))
            return 0
    action=(sys.argv[1:2]+[""])[0]
    parm=sys.argv[2:]
    if action in ["token","start","stop","list"]:
        if action == "token":
            easydst(token=parm[0]).save_cfg()
            return 0
        if action == "start":
            ed=easydst()
            ed.get_list()
            if ed.start_svr(parm[0]) ==0 :
                return 0
            else :
                return -1
        if action == "save":
            ed=easydst()
            ed.get_list()
            if ed.save_svr(parm[0]) ==0 :
                if verbose > 0:
                    print("[info] save slot \""+parm[0]+"\" done")
                return 0
            else :
                return -1
        if action == "stop":
            ed=easydst()
            ed.get_list()
            if ed.stop_svr(parm[0]) == 0 :
                ed.get_list()
                print("known_sv:\n"+json.dumps(ed.known_sv,indent=2))
                print("unknown_sv:\n"+json.dumps(ed.unknown_sv,indent=2))
                return 0
            else:
                return -1
        if action == "list":
            ed=easydst()
            ed.get_list()
            print("known_sv:\n"+json.dumps(ed.known_sv,indent=2))
            print("unknown_sv:\n"+json.dumps(ed.unknown_sv,indent=2))
            return 0
    
    
        
if __name__ == "__main__":  
    _main()