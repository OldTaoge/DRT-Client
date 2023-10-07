import json
import os
import subprocess
import zipfile
from typing import List
import requests

BP = os.path.join(os.path.expanduser("~"), ".DockerRuntimeTool")
if not os.path.exists(BP):
    os.mkdir(BP)
XTLS_BP = os.path.join(BP, "xtls")
FRP_BP = os.path.join(BP, "frp")
config_filename = os.path.join(BP, 'config.json')
FRPC_CONF_TEM = '[common]\nserver_addr = 127.0.0.1\nserver_port = 7001\nauthentication_method = token\ntoken = OTPOrgFrpAuthToken\nuser = %TranportID%\nlogin_fail_exit = false\nlog_file = /tmp/frpc_%TranportID%.log\nnat_hole_stun_server = stun.oldtaoge.space:3478\n\n[stcp-visitor]\nrole = visitor\ntype = stcp\nserver_name = %TranportID%-s\nsk = %ContainerID%\nbind_port = -1\n\n[xtcp-visitor]\nrole = visitor\ntype = xtcp\nserver_name = %TranportID%-x\nsk = %ContainerID%\nbind_addr = 127.0.0.1\nbind_port = %dp%\nfallback_to = %TranportID%.stcp-visitor\nfallback_timeout_ms = 1000'
CFRP: List[dict] = []
FRPM: dict = {}
def save_config(c):
    with open(config_filename, 'w') as file:
        json.dump(c, file)


def install_xtls():
    if not os.path.exists(XTLS_BP):
        os.mkdir(XTLS_BP)
    if not os.path.exists(os.path.join(XTLS_BP, "xray.exe")):
        response = requests.get("https://api.oldtaoge.space/github/Xray-macos-arm64-v8a.zip")
        if response.status_code == 200:
            with open(os.path.join(XTLS_BP, "xtls.zip"), 'wb') as file:
                file.write(response.content)
            with zipfile.ZipFile(os.path.join(XTLS_BP, "xtls.zip"), 'r') as zip_ref:
                zip_ref.extractall(XTLS_BP)
            os.remove(os.path.join(XTLS_BP, "xtls.zip"))
    with open(os.path.join(XTLS_BP, "xray.json"), "w") as xc:
        xc.write('{"log":{"loglevel":"warning", "access": "%s", "error": "%s"},"inbounds":[{"listen":"127.0.0.1","port":7001,"protocol":"dokodemo-door","settings":{"address":"127.0.0.1","port":7001}}],"outbounds":[{"tag":"block","protocol":"blackhole"},{"tag":"proxy","protocol":"vless","settings":{"vnext":[{"address":"hkbgp.node.oldtaoge.space","port":443,"users":[{"id":"drt","encryption":"none","flow":"xtls-rprx-vision"}]}]},"streamSettings":{"network":"tcp","security":"reality","realitySettings":{"serverName":"hkbgp.node.oldtaoge.space","fingerprint":"chrome","show":false,"publicKey":"_zw7JuNMXHXR5NN0M7Tmtmeo6m9-KQpsCKyqf-nKbjk","shortId":"71b027b53d036571","spiderX":"/otporg/drt"}}}],"routing":{"domainStrategy":"AsIs","rules":[{"type":"field","ip":["127.0.0.1"],"port":7001,"outboundTag":"proxy"}]}}' % (os.path.join(XTLS_BP, "xray-frp.log").replace("\\", "\\\\"), os.path.join(XTLS_BP, "xray-frp.log").replace("\\", "\\\\")))
    subprocess.Popen([os.path.join(XTLS_BP, "xray"), "-c", os.path.join(XTLS_BP, "xray.json")])


def install_frp():
    if not os.path.exists(FRP_BP):
        os.mkdir(FRP_BP)
    if not os.path.exists(os.path.join(FRP_BP, "frpc.exe")):
        response = requests.get("https://api.oldtaoge.space/github/frpc_darwin_arm64.zip")
        if response.status_code == 200:
            with open(os.path.join(FRP_BP, "frpc.zip"), 'wb') as file:
                file.write(response.content)
            with zipfile.ZipFile(os.path.join(FRP_BP, "frpc.zip"), 'r') as zip_ref:
                zip_ref.extractall(FRP_BP)
            os.remove(os.path.join(FRP_BP, "frpc.zip"))


def run_frp(t):
    fc = FRPC_CONF_TEM.replace("%TranportID%", str(t["id"]))
    fc = fc.replace("%ContainerID%", t["cuuid"])
    fc = fc.replace("%dp%", str(t["dp"]))
    with open(os.path.join(FRP_BP, "frpc_%d.ini" % t["id"]), "w") as c:
        c.write(fc)
    FRPM[t["id"]] = subprocess.Popen([os.path.join(FRP_BP, "frpc"), "-c", os.path.join(FRP_BP, "frpc_%d.ini" % t["id"])])
    CFRP.append(t)


if __name__ == "__main__":
    if not os.path.exists(config_filename):
        with open(config_filename, 'w') as file:
            json.dump({}, file)
    with open(config_filename, 'r') as file:
        config: dict = json.load(file)
    print("Config loaded")
    print("Installing xray")
    install_xtls()
    print("Installing frp")
    install_frp()
    if config.get("user") is None:
        ui = input("Please open the following url and copy its return into console\nhttps://drt.service.oldtaoge.space/login\n")
        ui = json.loads(ui)
        config["user"] = ui
        save_config(config)
    sshpk = requests.get("https://drt.service.oldtaoge.space/user/sshpk/%d/%s" % (config["user"]["i"], config["user"]["t"])).text
    if sshpk == "":
        sshpk = input("Please paste your ssh public key:")
        requests.put("https://drt.service.oldtaoge.space/user/sshpk/%d/%s" % (config["user"]["i"], config["user"]["t"]), data=sshpk)
    while True:
        try:
            print("="*120)
            print("Use following command to boot your container(Only support Ubuntu/Debian now):")
            print("apt update && apt install libterm-readkey-perl -y && apt install wget -y && wget -O- https://drt.service.oldtaoge.space/container_boot/%d/%s | bash"% (config["user"]["i"], config["user"]["t"]))
            print("Warning: boot script contains key information, please be careful")
            print("Warning: If Windows firewall block transport on frp, please allow it")
            print("Please select container:")
            cs = requests.get("https://drt.service.oldtaoge.space/client/container/%d/%s" % (config["user"]["i"], config["user"]["t"])).json()
            cid = 0
            for c in cs:
                print("%d.'%s': Last seen %s" % (cid, c["cuuid"], c["last_seen"]))
                cid += 1
            print("-"*80)
            try:
                print("Warning: If Windows firewall block transport on frp, please allow it")
                cid = int(input("Please select container(default: 0, -1 to reload):"))
            except ValueError:
                cid = 0
            if cid < 0:
                continue
            c = cs[cid]
            print("1.transport")
            print("2.proxy")
            print("Please select action:")
            s = int(input())
            if s == 1:
                ts = requests.get("https://drt.service.oldtaoge.space/client/container/%s/transport/%d/%s" % (c["cuuid"], config["user"]["i"], config["user"]["t"])).json()
                if len(ts) > 0:
                    ns = set(tuple(sorted(d.items())) for d in ts)
                    oset = set(tuple(sorted(d.items())) for d in CFRP)
                    for nf in [dict(item) for item in (ns - oset)]:
                        run_frp(nf)
                    for of in list(oset - ns):
                        FRPM[of["id"]].kill()
                        CFRP.remove(of)
                print("Current transport list:")
                tid = 1
                for t in ts:
                    print("%d. %d->%d" % (tid, t["sp"], t["dp"]))
                tid = int(input("Select the id to remove, 0 to add a transport, -1 to return: "))
                if tid == 0:
                    sp = int(input("Please input source port:"))
                    dp = int(input("Please input destination port:"))
                    requests.put("https://drt.service.oldtaoge.space/client/container/%s/transport/%d/%s" % (c["cuuid"], config["user"]["i"], config["user"]["t"]), json={"sp": sp, "dp": dp})
                    print("Transport added You need to select the container again to load the transport")
                elif tid > 0:
                    t = ts[tid-1]
                    requests.delete("https://drt.service.oldtaoge.space/client/container/%s/transport/%d/%d/%s" % (c["cuuid"], t["id"], config["user"]["i"], config["user"]["t"]))
            elif s == 2:
                pinf = requests.get("https://drt.service.oldtaoge.space/user/proxy/info/%d/%s" % (config["user"]["i"], config["user"]["t"])).json()
                if not pinf["s"]:
                    print("Please open following url in your browser to load proxy")
                    print("https://drt.service.oldtaoge.space/user/proxy/update/%d/%s" % (config["user"]["i"], config["user"]["t"]))
                    input("And press enter to continue")
                else:
                    s = requests.get("https://drt.service.oldtaoge.space/client/container/%s/proxy/%d/%s" % (c["cuuid"], config["user"]["i"], config["user"]["t"])).json()
                    if s["s"]:
                        print("Proxy enabled, 0 to disable, -1 to return")
                    else:
                        print("Proxy disabled, 1 to enable, -1 to return")
                    a = int(input())
                    if a < 0:
                        continue
                    elif a == 0:
                        requests.delete("https://drt.service.oldtaoge.space/client/container/%s/proxy/%d/%s" % (c["cuuid"], config["user"]["i"], config["user"]["t"]))
                    elif a == 1:
                        requests.put("https://drt.service.oldtaoge.space/client/container/%s/proxy/%d/%s" % (c["cuuid"], config["user"]["i"], config["user"]["t"]))

        except Exception as e:
            print(e)