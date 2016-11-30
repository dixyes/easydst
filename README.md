# easydst
a simple docker container controller for manage DST gameserver
## usage
1. you need a [网易蜂巢](https://c.163.com/) account and an avaliable accesskey
2. create your own image named &lt;somename&gt;
3. use that key to generate a token:  

    curl https://open.c.163.com/api/v1/token -H"Content-Type: application/json" -d'{"app_key":"your key","app_secret":"your secret"}'

4. modify easydst.json:

    {
    "ver": 0,                         //no use yet, but you can set it to anything interesting
    "token": "a token",               //put your token here
    "svrlist": {
        "slot_a": {
            "repo_name":"dstsuite",   //your image repo name, this prog will find "<prefix>latest" tag in this repo to create container
            "status":"known"          //if that tag does not exist, it will use "lastest" instead
            },
        "slot_b": {
            "repo_name":"mcsuite",
            "status":"known"          //for some fxxking reason ,this is necessary
            }
        }
    }
    
and easydst.py:

    ctr_prefix="EDST"#神tm连连字符都不支持，仅限字母数字 #all prefix for this prog created containers
    img_prefix=ctr_prefix   #all prefix for this prog created images
    str_ver=__version__     #__version__ is a good choice, yep?
    int_ver=0               #no use yet, but you can set it to anything interesting
    cfg_path="easydst.json" #conf file path
5. use easydst.py or easydst_gui.py to manage containers:

    python easydst.py token <sometoken>
    python easydst.py list
    python easydst.py start <someslot>
    python easydst.py save <someslot>
    python easydst.py stop <someslot>
    
    python easydst_gui.py

6. if you like, you can use pyinstaller to pack that prog and share with you friends

    pyinstaller sgeasydst_gui.spec

## something is wrong?
no troubleshooting yet, fell free to tell me via issue 
## license
all parts wrote by myself use [WTFPL](//www.wtfpl.org)