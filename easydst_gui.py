
# -*- coding: utf-8 -*-

#easier  gssvr.py - c163 x dst 
#easydst_gui.py
import sys,threading,locale
if sys.version_info < (3,0):
    from Tkinter import *
    import tkSimpleDialog
else:
    from tkinter import *
    import tkinter.simpledialog
    tkSimpleDialog=tkinter.simpledialog
#,sys,pywin32
import easydst

_translation={}
_translation["C"]={
"input a token":"input a token",
"creating":"creating",
"create_succ":"create_succ",
"deleting":"deleting",
"create_fail":"create_fail",
"known":"known",
"Done starting ":"Done starting ",
" is already started":" is already started",
" start fail":" start fail",
"Working":"Working",
"Done saving ":"Done saving ",
" save fail":" save fail",
"save token":"save token",
"sv list":"sv list",
"getting":"getting"
}
_translation["en_us"]=_translation["en_gb"]={
"input a token":"input a token(32-digit hex)",#todo：balabala
"creating":"creating",
"create_succ":"running",
"deleting":"deleting",
"create_fail":"create fail",
"known":"not running",
"Done starting ":"Done starting ",
" is already started":" is already started",
" start fail":" start fail",
"Working":"Working",
"Done saving ":"Done saving ",
" save fail":" save fail",
"Done stoping ":"Done stoping ",
" stop fail":" stop fail",
"save token":"save token",
"sv list":"server list",
"getting":"gathering info...",
"refresh":"refresh",
"start":"start",
"stop":"stop",
"save":"save",
"QUIT":"QUIT"
}
_translation["zh_cn"]={
"input a token":"输入token（32个字母或数字）",#todo：balabala
"creating":"创建中",
"create_succ":"运行中",
"deleting":"删除中",
"create_fail":"创建失败",
"known":"未运行",
"Done starting ":"完成启动 ",
" is already started":" 已在运行",
" start fail":" 启动失败",
"Working":"工作中",
"Done saving ":"完成保存 ",
" save fail":" 保存失败",
"Done stoping ":"完成停止 ",
" stop fail":" 停止失败",
"save token":"保存 token",
"sv list":"服务器列表",
"getting":"获取信息中",
"refresh":"刷新",
"start":"开始",
"stop":"停止",
"save":"保存",
"QUIT":"退出"
}
_translation["zh_tw"]=_translation["zh_hk"]={
"input a token":"键入token（32個字母或數字）",#todo：balabala
"creating":"構建中",
"create_succ":"運行中",
"deleting":"移除中",
"create_fail":"構建失敗",
"known":"未運行",
"Done starting ":"完成啓動 ",
" is already started":" 已在運行",
" start fail":" 啓動失敗",
"Working":"工作中",
"Done saving ":"完成儲存 ",
" save fail":" 儲存失敗",
"Done stoping ":"完成停止 ",
" stop fail":" 停止失敗",
"save token":"儲存token",
"sv list":"伺服器列表",
"getting":"獲取信息中",
"refresh":"刷新",
"start":"開始",
"stop":"停止",
"save":"存檔",
"QUIT":"退出"
}
def _translate(key):
    print("[debug] lang set to: "+locale.getdefaultlocale()[0])
    return _translation.get(locale.getdefaultlocale()[0].lower(),_translation["C"]).get(key,_translation.get("C").get(key,"No such translation"))
    

class easydst_gui(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.showdata=[]
        self.selected=0
        try:
            self._edst=easydst.easydst()
        except ValueError :
            token=tkSimpleDialog.askstring("input a token", "token:" ,parent=self)
            if token!=None and len(token)==32:
                self._edst=easydst.easydst(token=token)
                self._edst.save_cfg()
            else :
                raise ValueError("invalid token")
        self.pack(fill=BOTH)
        self.createWidgets()
    def limited(self,sv):
        c = sv.get()[0:31]
        #print "c=" , c
        sv.set(c)
    def refresh_token(self):
        if not self.tok.get() == "********************************":
            self._edst.set_token(self.tok.get())
        else:
            pass
            #print("notchange")
    def refresh_list(self):
        self._edst.get_list()
        all_sv=dict(self._edst.known_sv,**self._edst.unknown_sv)
        data=[]
        i=0
        for svk in sorted(all_sv.keys()):
            data.append({"name":svk})
            sv=all_sv[svk]
            if sv.get("status") in ("creating","create_succ","deleting","create_fail"):
                data[i]["status"]=sv.get("status")
            else:
                data[i]["status"]="known"
            if sv.get("pubip")!=None:
                data[i]["pubip"]=sv.get("pubip")
            i+=1
            
        self.sv_list.delete(0, END)
        for i in range(0,len(data)):
            self.sv_list.insert(END,_translate(data[i]["status"])+" "+data[i]["name"])
        self.showdata=data
        import json
        print("[debug] on write "+json.dumps(data)+" to self.showdata:"+json.dumps(self.showdata))
    def refresh_list_async(self):
            refresher=threading.Thread(target=self.refresh_list)
            refresher.start()
    def start_sv(self):
        self._edst.get_list()
        ret=self._edst.start_svr(self.showdata[self.selected]["name"])
        if ret==0 :
            self.info_notation["text"]=_translate("Done starting ")+self.showdata[self.selected]["name"]
            self.info_notation["fg"]="green"
        elif ret==-1 :
            self.info_notation["text"]=self.showdata[self.selected]["name"]+_translate(" is already started")
            self.info_notation["fg"]="yellow"
        else:
            self.info_notation["text"]=self.showdata[self.selected]["name"]+_translate(" start fail")
            self.info_notation["fg"]="red"
        self.refresh_list_async()
    def start_sv_async(self):
        self.info_notation["text"]=_translate("Working")
        self.info_notation["fg"]="yellow"
        st=threading.Thread(target=self.start_sv)
        st.start()
    def save_sv(self):
        self._edst.get_list()
        ret=self._edst.save_svr(self.showdata[self.selected]["name"])
        if ret==0 :
            self.info_notation["text"]=_translate("Done saving ")+self.showdata[self.selected]["name"]
            self.info_notation["fg"]="green"
        else:
            self.info_notation["text"]=self.showdata[self.selected]["name"]+_translate(" save fail")
            self.info_notation["fg"]="red"
    def save_sv_async(self):
        self.info_notation["text"]=_translate("Working")
        self.info_notation["fg"]="yellow"
        st=threading.Thread(target=self.save_sv)
        st.start()
    def stop_sv(self):
        self._edst.get_list()
        ret=self._edst.stop_svr(self.showdata[self.selected]["name"])
        if ret==0 :
            self.info_notation["text"]=_translate("Done stoping ")+self.showdata[self.selected]["name"]
            self.info_notation["fg"]="green"
        else:
            self.info_notation["text"]=self.showdata[self.selected]["name"]+_translate(" stop fail")
            self.info_notation["fg"]="red"
        self.showdata[self.selected]["status"]="known"
        self.refresh_list_async()
    def stop_sv_async(self):
        self.info_notation["text"]=_translate("Working")
        self.info_notation["fg"]="yellow"
        st=threading.Thread(target=self.stop_sv)
        st.start()
    def onselect(self,evt):
        #todo: use normal way
        w = evt.widget
        #index = =index
        #value = w.get(index)
        import json
        print("[debug] on select:self.showdata:"+json.dumps(self.showdata))
        self.start_button["state"]=NORMAL
        self.save_button["state"]=NORMAL
        self.stop_button["state"]=NORMAL
        self.selected=int(w.curselection()[0])
        if self.showdata[self.selected]["status"] in ("creating","create_fail","create_succ"):
            self.start_button["state"]=DISABLED
        if self.showdata[self.selected]["status"] in ("creating","create_fail","known"):
            self.save_button["state"]=DISABLED
        if self.showdata[self.selected]["status"] in ("creating","known"):
            self.stop_button["state"]=DISABLED
        #print 'You selected item %d: "%s"' % (index, value)
    def createWidgets(self):
    #
        self.token_frame=Frame(self)
        
        self.token_label=Label(self.token_frame,text="token:")
        self.token_label.pack(side=LEFT,fill=X)
        
        self.tok = StringVar()
        self.tok.set("********************************")
        self.tok.trace("w", lambda name, index, mode, tok=self.tok: self.limited(tok))
        
        self.token_input=Entry(self.token_frame, textvariable=self.tok,show="*",width=32,font=("Monospace"))# 
        self.token_input.pack(side=LEFT,fill=X)
        
        self.save_token = Button(self.token_frame)
        self.save_token["text"] = _translate("save token")
        self.save_token["command"] = self.refresh_token
        self.save_token.pack(side=LEFT,fill=X)
        
        self.token_frame.pack(side=TOP,fill=X)
    # 
    #
        self.sv_frame=Frame(self)
        #
        self.sv_label=Label(self.sv_frame,text=_translate("sv list"))
        self.sv_label.pack(side=TOP,fill=X)
        
        self.sv_list=Listbox(self.sv_frame)
        self.sv_list.insert(END, _translate("getting"))
        
        self.sv_list.bind('<<ListboxSelect>>', self.onselect)
        
        self.refresh_list_async()
        
        self.sv_list.pack(side=TOP,fill=X)
        
        self.action_frame=Frame(self.sv_frame)
            #
        self.refresh_button=Button(self.action_frame)
        self.refresh_button["text"] = _translate("refresh")
        self.refresh_button["command"] = self.refresh_list_async
        self.refresh_button.pack(side=LEFT,fill=X)
        self.start_button=Button(self.action_frame)
        self.start_button["text"] = _translate("start")
        self.start_button["command"] = self.start_sv_async
        self.start_button["state"]=DISABLED
        self.start_button.pack(side=LEFT,fill=X)
        self.save_button=Button(self.action_frame)
        self.save_button["text"] = _translate("save")
        self.save_button["command"] = self.save_sv_async
        self.start_button["state"]=DISABLED
        self.save_button.pack(side=LEFT,fill=X)
        self.stop_button=Button(self.action_frame)
        self.stop_button["text"] = _translate("stop")
        self.stop_button["command"] = self.stop_sv_async
        self.start_button["state"]=DISABLED
        self.stop_button.pack(side=LEFT,fill=X)
        self.info_notation=Label(self.action_frame)
        self.info_notation.pack(side=LEFT,fill=X)
            #
        self.action_frame.pack(side=TOP,fill=X)
        #
        self.sv_frame.pack(side=TOP,fill=X)
    #
    #
        self.QUIT = Button(self)
        self.QUIT["text"] = _translate("QUIT")
        #self.QUIT["fg"]   = "red"
        self.QUIT["command"] =  self.quit
        self.QUIT.pack(side=TOP,fill=X)
    #
        # self.hi_there = Button(self)
        # self.hi_there["text"] = "Hello",
        # self.hi_there["command"] = self.say_hi
        # self.hi_there.pack(side=TOP,fill=X)
    

def main():
    root = Tk()
    
    #root.tk.call('tk', 'scaling', 2.0)
    app = easydst_gui(master=root)
    app.master.title("EaSyDStGuI ver "+easydst.str_ver)
    app.mainloop()
    try:
        root.destroy()
    except:
       pass
    
if __name__ == "__main__": 
    main()