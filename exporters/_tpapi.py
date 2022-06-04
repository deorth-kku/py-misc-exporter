#!/bin/python3
import requests
import logging
from requests.utils import quote, unquote


class TPapi:
    error_names={
    0:'ENONE' ,
    -1:'ERR_PERCENT' ,
    -40101:'ESYSTEM' ,
    -40102:'EEXPT' ,
    -40103:'ENOMEMORY' ,
    -40104:'EINVEVT' ,
    -40105:'ECODE' ,
    -40106:'EINVINSTRUCT' ,
    -40107:'EFORBID' ,
    -40108:'ENOECHO' ,
    -40109:'ESYSBUSY' ,
    -40110:'ENODEVICE' ,
    -40201:'EOVERFLOW' ,
    -40202:'ETOOLONG' ,
    -40203:'EENTRYEXIST' ,
    -40204:'EREFERED' ,
    -40205:'EENTRYNOTEXIST' ,
    -40206:'EENTRYCONFLIC' ,
    -40207:'ETABLEFULL' ,
    -40208:'ETABLEEMPTY' ,
    -40209:'EINVARG' ,
    -40210:'EINVFMT' ,
    -40211:'ELACKARG' ,
    -40212:'EINVBOOL' ,
    -40213:'ESTRINGLEN' ,
    -40301:'EINVIP' ,
    -40302:'EINVGROUPIP' ,
    -40303:'EINVIPFMT' ,
    -40304:'EINVLOOPIP' ,
    -40305:'EINVMASK' ,
    -40306:'EINVGTW' ,
    -40307:'EGTWUNREACH' ,
    -40308:'ECOMFLICTNET' ,
    -40309:'EINVNET' ,
    -40310:'EINVMACFMT' ,
    -40311:'EINVMACGROUP' ,
    -40312:'EINVMACZERO' ,
    -40313:'EINVMACBROAD' ,
    -40314:'EINVNETID' ,
    -40315:'EINVHOSTID' ,
    -40316:'EINDOMAIN' ,
    -40317:'EINVIPMASKPAIR' ,
    -40318:'EMACEMPTY' ,
    -40319:'ECONFLICTFDNS' ,
    -40320:'ECONFLICTSDNS' ,
    -40321:'ECONFLICTGATEWAY' ,
    -40322:'ECONFLICTDUALWAN' ,
    -40323:'ECONFLICTLANMAC' ,
    -40324:'ECONFLICTWANMAC' ,
    -40325:'ECONFLICTWANGATEWAY' ,
    -40326:'ECONFLICTIPWANDNS' ,
    -40327:'ECONFLICTGATEWAYWANIP' ,
    -40328:'ECONFLICTDNSWANIP' ,
    -90421:'EMULTIWANENABLE' ,
    -90422:'EWDSENABLE' ,
    -90423:'EDHCPSOFF' ,
    -90431:'ELAGDIFFERR' ,
    -40401:'EUNAUTH' ,
    -40402:'ECODEUNAUTH' ,
    -40403:'ESESSIONTIMEOUT' ,
    -40404:'ESYSLOCKED' ,
    -40405:'ESYSRESET' ,
    -40406:'ESYSCLIENTFULL' ,
    -40407:'ESYSCLIENTNORMAL' ,
    -40408:'ESYSLOCKEDFOREVER' ,
    -50101:'EINVMTU' ,
    -50102:'EINVFDNSVR' ,
    -50103:'EINVSDNSVR' ,
    -50104:'EDNSMODE' ,
    -50105:'ENOLINK' ,
    -50106:'ENETMASKNOTMATCH' ,
    -50107:'ENETLANSAME' ,
    -50108:'ENETWANSAME' ,
    -50109:'EWANSPEED' ,
    -50110:'EISPMODE' ,
    -50111:'EDIAGMODE' ,
    -50112:'ECONNECTMODE' ,
    -50113:'ELANIPMODE' ,
    -50114:'EHOSTNAME' ,
    -50115:'EPPPOEUSER' ,
    -50116:'EPPPOEPWD' ,
    -50117:'EINVTIME' ,
    -50118:'EPPPOEAC' ,
    -50119:'EPPPOESVR' ,
    -50120:'EINVPTC' ,
    -50121:'EWANTYPE' ,
    -50122:'EMACCLONECONFLICT' ,
    -50123:'EMANUALLANMODE' ,
    -50124:'EMANUALAPMODE' ,
    -50143:'EINVLANMASK' ,
    -50144:'ELANIPCONFLICT' ,
    -50145:'EINVDHCPSLANMODE' ,
    -50201:'EWLANPWDBLANK' ,
    -50202:'EINVSSIDLEN' ,
    -50203:'EINVSECAUTH' ,
    -50204:'EINVWEPAUTH' ,
    -50205:'EINVRADIUSAUTH' ,
    -50206:'EINVPSKAUTH' ,
    -50207:'EINVCIPHER' ,
    -50208:'EINVRADIUSLEN' ,
    -50209:'EINVPSKLEN' ,
    -50210:'EINVGKUPINTVAL' ,
    -50211:'EINVWEPKEYTYPE' ,
    -50212:'EINVWEPKEYIDX' ,
    -50213:'EINVWEPKEYLEN' ,
    -50214:'EINVACLDESCLEN' ,
    -50215:'EINVWPSPINLEN' ,
    -50216:'EINVAPMODE' ,
    -50217:'EINVWLSMODE' ,
    -50218:'EINVREGIONIDX' ,
    -50219:'EINVCHANWIDTH' ,
    -50220:'EINVRTSTHRSHLD' ,
    -50221:'EINVFRAGTHRSHLD' ,
    -50222:'EINVBCNINTVL' ,
    -50223:'EINVTXPWR' ,
    -50224:'EINVDTIMINTVL' ,
    -50225:'EINVWLANPWD' ,
    -50226:'ESSIDBROAD' ,
    -50227:'EAPISOLATE' ,
    -50228:'EWIFISWITCH' ,
    -50229:'EMODEBANDWIDTHNOTMATCH' ,
    -50230:'EINVCHANNEL2G' ,
    -50231:'EINVCHANNEL5G' ,
    -50232:'EPSKNOTHEX' ,
    -50233:'EINVWDSAUTH' ,
    -50234:'EINVA34DETECT' ,
    -50235:'EINVTURBO' ,
    -50236:'EINVSECCHECK' ,
    -50237:'EINVSSIDEMPTY' ,
    -50238:'EINVCHNAMODEBAND' ,
    -50239:'EINVSSIDBLANK' ,
    -50246:'EINVWPSPINFORMAT' ,
    -50247:'EINVWPSPINEMPTY' ,
    -50301:'EINVLEASETIME' ,
    -50302:'EINVSTARTADDRPOOL' ,
    -50303:'EINVENDADDRPOOL' ,
    -50304:'EDHCPDGTW' ,
    -50305:'EGTWNOTLANSUBNET' ,
    -50306:'EDHCPDPRIDNS' ,
    -50307:'EDHCPDSNDDNS' ,
    -50308:'EDHCPDAUTO' ,
    -50309:'EINVCAPABILITYSMALL' ,
    -50317:'EWDSMODEOPEN' ,
    -50318:'EAPMODEOPEN' ,
    -50319:'EWDSMODECLOSE' ,
    -50320:'EAPMODECLOSE' ,
    -50401:'EHOSTNAMEEMP' ,
    -50402:'EOBJNAMEEMP' ,
    -50403:'EPLANNAMEEMP' ,
    -50404:'ERULENAMEEMP' ,
    -50405:'EOBJDOMAINALLEMP' ,
    -50406:'EHOSTALLEMPTY' ,
    -50407:'EOBJALLEMPTY' ,
    -50408:'ENOTLANSUBNET' ,
    -50409:'ELANSUBNET' ,
    -50410:'ELANIPCONFLIC' ,
    -50411:'EILLEGALPORT' ,
    -50412:'EPORTRESERVED' ,
    -50413:'EINVPORT' ,
    -50414:'EINVPORTFMT' ,
    -50501:'EINVNASUSER' ,
    -50502:'EINVNASUSERLEN' ,
    -50503:'EINVNASPWD' ,
    -50504:'EINVNASPWDLEN' ,
    -50505:'EDELADMIN' ,
    -50506:'EEDITADMIN' ,
    -50507:'EINVPATHNULL' ,
    -50508:'EINVPATH' ,
    -50509:'EINVPATHLEN' ,
    -50510:'EPATHCONFLICT' ,
    -51001:'EFTPNAMENULL' ,
    -51002:'EFTPNAME' ,
    -51003:'EFTPNAMELEN' ,
    -51004:'EFTPNAMECONFLICT' ,
    -50701:'ESCANVAL' ,
    -50702:'EMSNAMENULL' ,
    -50703:'EMSNAME' ,
    -50704:'EMSNAMELEN' ,
    -50705:'EMSNAMECONFLICT' ,
    -50801:'ENAMEBLANK' ,
    -50802:'EINVNAME' ,
    -50803:'EINVNAMELEN' ,
    -50804:'EDDNSPWDLEN' ,
    -50805:'EDDNSPWD' ,
    -50806:'EDDNSPWDBLANK' ,
    -50901:'EINVDATE' ,
    -50902:'EINVTIMEZONE' ,
    -50903:'EFWERRNONE' ,
    -50904:'EFWEXCEPTION' ,
    -50905:'EFWRSAFAIL' ,
    -50906:'EFWHWIDNOTMATCH' ,
    -50907:'EFWZONECODENOTMATCH' ,
    -50908:'EFWVENDORIDNOTMATCH' ,
    -50909:'EFWNOTINFLANDBL' ,
    -50910:'EFWNEWEST' ,
    -50911:'EFWNOTSUPPORTED' ,
    -50914:'EMD5' ,
    -50915:'EDESENCODE' ,
    -50916:'EDESDECODE' ,
    -50917:'ECHIPID' ,
    -50918:'EFLASHID' ,
    -50919:'EPRODID' ,
    -50920:'ELANGID' ,
    -50921:'ESUBVER' ,
    -50922:'EOEMID' ,
    -50923:'ECOUNTRYID' ,
    -50924:'EFILETOOBIG' ,
    -50925:'EPWDERROR' ,
    -50926:'EPWDBLANK' ,
    -50927:'EINVPWDLEN' ,
    -50928:'EINVKEY' ,
    -50929:'EINVLGPWDLEN' ,
    -50930:'EINLGVALCHAR' ,
    -50931:'EINLGVALOLDSAME' ,
    -50932:'EHASINITPWD' ,
    -50933:'ECHPWDDIF' ,
    -50934:'EUSRERROR' ,
    -50935:'EUSRBLANK' ,
    -50936:'EINVUSRLEN' ,
    -50937:'EINVNEWUSR' ,
    -50938:'EINVLGUSRLEN' ,
    -50939:'EINLGUSRVALCHAR' ,
    -50940:'EINLGUSRVALOLDSAME' ,
    -50941:'EHASINITUSR' ,
    -50942:'ECHUSRDIF' ,
    -50943:'EINVUSR' ,
    -50944:'ECMCCUSRERROR' ,
    -50201:'EINVMAILFMT' ,
    -50202:'EINVMAILLEN' ,
    -50203:'EINVMAILPWDLEN' ,
    -51204:'EINVCLIENTINTERNAL' ,
    -51205:'EINVREQUESTIDNOTFOUND' ,
    -51206:'EINVMETHODNOTFOUND' ,
    -51207:'EINVPARAMETER' ,
    -51208:'EINVGETDATAFAILED' ,
    -51209:'EINVURLINVALID' ,
    -51210:'EINVPASSWORDFMT' ,
    -51211:'EINVDOWNLOADFWFAILED' ,
    -51212:'EINVUPGRADEFWFAILED' ,
    -51213:'EINVCONFIGURATEFAILED' ,
    -51214:'EINVPERMISSIONDENIED' ,
    -51215:'EINVREQUESTTIMEOUT' ,
    -51216:'EINVMEMORYOUT' ,
    -51217:'EINVSENDREQMSGFAILED' ,
    -51218:'EINVCONNECTTINGCLOUDSERVER' ,
    -51219:'EINVLASTOPTIONISNOTFINISHED' ,
    -51220:'EINVCLOUDUSRCOUNTFORMAT' ,
    -51221:'EINVVERICODEFORMAT' ,
    -51222:'EINVNEWPASSWORD' ,
    -51223:'EINVCLOUDACCOUNT' ,
    -51224:'EINDEVICEIDERROR' ,
    -51225:'EINDEVICENOTBIND' ,
    -51226:'EINACCOUNTEMPTY' ,
    -51227:'EINPASSWORDEMPTY' ,
    -51228:'EINVERICODEEMPTY' ,
    -51229:'EINVILLEGALDEVICE' ,
    -51230:'EINDEVICEALREADYBOUND' ,
    -51231:'EINDEVICEALREADYUNBOUND' ,
    -9E4:'EINVCLOUDCLIENTGENERIC' ,
    -90100:'EINVCLOUDDNSQUERYERR' ,
    -90101:'EINVCLOUDTCPCONTERR' ,
    -90102:'EINVCLOUDSSLSIGNERR' ,
    -90103:'EINVCLOUDDOMAINERR' ,
    -90104:'EINVCLOUDSSLTIMEERR' ,
    -90105:'EINVCLOUDSSLENCRYPTIONERR' ,
    -90106:'EINVCLOUDDEVICEILLEGAL' ,
    -90200:'EINVCLOUDCLIENTHEARTREQUESTTIMEOUT' ,
    -90201:'EINVCLOUDSTOPCONCT' ,
    -90202:'EINVCLOUDCLIENTWANIPCHANGE' ,
    -90203:'EINVCLOUDCLIENTDISCONNECTFIN' ,
    -90204:'EINVCLOUDCLIENTDISCONNECTRST' ,
    -90205:'EINVCLOUDCLIENTDISCONNECT' ,
    -90206:'EINVCLOUDCLIENTDISCONNECTSOCKETERRNUM' ,
    -90207:'EINVCLOUDCLIENTWANPHYPORTLINKDOWN' ,
    -90300:'EINVCLOUDCLIENTHELLOCLOUD' ,
    -90301:'EINVCLOUDCLIENTPUSHPLUGININFO' ,
    -90302:'EINVCLOUDCLIENTGETFWLIST' ,
    -90303:'EINVCLOUDCLIENTGETINITFWLIST' ,
    -90400:'EINVCLOUDCLIENTDOWNLOADPARSEDNSREQUEST' ,
    -90401:'EINVCLOUDCLIENTDOWNLOADESTABLISHTCP' ,
    -90402:'EINVCLOUDCLIENTDOWNLOADHTTPNOTOK' ,
    -90403:'EINVCLOUDCLIENTDOWNLOADTIMEOUT' ,
    -56301:'EIPV6CONFIGTYPE' ,
    -56302:'EIPV6PDMODE' ,
    -56303:'EIPV6INVIPFMT' ,
    -56304:'EIPV6LINKLOCAL' ,
    -56305:'EIPV6LOOP' ,
    -56306:'EIPV6INVIP' ,
    -56307:'EIPV6INVGROUPIP' ,
    -56308:'EIPV6INVGTW' ,
    -56309:'EIPV6INVFDNSVR' ,
    -56310:'EIPV6INVSDNSVR' ,
    -56311:'EIPV6INVPREFIX' ,
    -56313:'EIPV6NOTLANSUBNET' ,
    -1E4:'EINVCLOUDERRORGENERIC' ,
    -10100:'EINVCLOUDERRORPARSEJSON' ,
    -10101:'EINVCLOUDERRORPARSEJSONNULL' ,
    -2E4:'EINVCLOUDERRORSERVERINTERNALERROR' ,
    -20001:'EINVERRORPERMISSIONDENIED' ,
    -20002:'EINVCLOUDERRORPERMISSIONDENIED' ,
    -20003:'EINVCLOUDERRDENYPASSEDDEV' ,
    -20100:'EINVCLOUDERRORPARSEJSONID' ,
    -20103:'EINVCLOUDERRORMETHODNOTFOUND' ,
    -20104:'EINVCLOUDERRORPARAMSNOTFOUND' ,
    -20105:'EINVCLOUDERRORPARAMSWRONGTYPE' ,
    -20106:'EINVCLOUDERRORPARAMSWRONGRANGE' ,
    -20107:'EINVCLOUDERRORINVALIDPARAMS' ,
    -20200:'EINVACCOUNTEMAILFMT' ,
    -20201:'EINVACCOUNTPHONENUMFMT' ,
    -20500:'EINVERRORDEVICEIDFORMATERROR' ,
    -20501:'EINVDEVICEIDNOTEXIST' ,
    -20502:'EINVCLOUDERRORBINDDEVICEERROR' ,
    -20503:'EINVCLOUDERRORUNBINDDEVICEERROR' ,
    -20504:'EINVCLOUDERRORHWIDNOTFOUND' ,
    -20505:'EINVNOTFOUNTNEWFW' ,
    -20506:'EINVACCOUNTBINDED' ,
    -20507:'EINVACCOUNTUNBINDED' ,
    -20571:'EINVCLOUDERRORDEVICEOFFLINE' ,
    -20572:'EINVCLOUDERRORDEVICEALIASFORMATERROR' ,
    -20600:'EINVACCOUNTNOTEXIST' ,
    -20601:'EINVACCOUNTPWDERR' ,
    -20603:'EINVACCOUNTREGISTED' ,
    -20604:'EINVCLOUDERRORACCOUNTUSERNAMEFORMATERROR' ,
    -20606:'EINVCLOUDERRORACCOUNTACTIVEMAILSENDFAIL' ,
    -20607:'EINVACCOUNTRESETPWDCAPTCHAERR' ,
    -20608:'EINVACCOUNTLENGTH' ,
    -20609:'EINVCLOUDERRORRESETMAILSENDFAIL' ,
    -20610:'EINVACCOUNTTYPEERR' ,
    -20615:'EINVACCOUNTPWDFMT' ,
    -20616:'EINVACCOUNTNEWPWDERR' ,
    -20651:'EINVCLOUDERRORTOKENEXPRIED' ,
    -20652:'EINVCLOUDERRORTOKENINCORRECT' ,
    -20661:'EINVACCOUNTLOCKED' ,
    -20662:'EINVDEVICELOCKED' ,
    -20671:'EINVCLOUDERRORACCOUNTACTIVEFAIL' ,
    -20672:'EINVCLOUDERRORACCOUNTACTIVETIMEOUT' ,
    -20673:'EINVCLOUDERRORRESETPWDTIMEOUT' ,
    -20674:'EINVCLOUDERRORRESETPWDFAIL' ,
    -20676:'EINVCLOUDERRORCAPTCHAINVAL' ,
    -20703:'EINVCLOUDERRORFWIDNOTSUPPORTDEVICE' ,
    -51301:'EINVSPEEDCFG' ,
    -51302:'EINVTIMEOUTCFG' ,
    -51303:'EINVLIMITTYPE' ,
    -51304:'EINVMON' ,
    -51305:'EINVTUE' ,
    -51306:'EINVWED' ,
    -51307:'EINVTHU' ,
    -51308:'EINVFRI' ,
    -51309:'EINVSAT' ,
    -51310:'EINVSUN' ,
    -51311:'EINVPERIODBLANK' ,
    -51312:'EINVPERIODTOOLONG' ,
    -51313:'EINVBEGINTIME' ,
    -51314:'EINVENDTIME' ,
    -51315:'EINVBEGINENDTIME' ,
    -51316:'EINVREPEATBLANK' ,
    -51317:'EINVLIMITTIMEREPEAT' ,
    -51401:'ENOTLANWANNET' ,
    -51402:'EBINDIPUSED' ,
    -51501:'ETIMEPERIODBLANK' ,
    -51502:'ETIMEPERIODTOOLONG' ,
    -51503:'EINVTLBEGINTIME' ,
    -51504:'EINVTLEENDTIME' ,
    -51505:'EINVTLBEGINENDTIME' ,
    -51506:'ETLREPEATBLANK' ,
    -51507:'ELIMITTIMEREPEAT' ,
    1E4:'SYNC_GET_SUCCESS' ,
    10001:'SYNC_GETTING' ,
    -1E4:'SYNC_GET_SYSTEM_ERROR' ,
    -10001:'SYNC_GET_TIMEOUT' ,
    -10002:'SYNC_GET_TOPO_ERROR' ,
    5:'EINVCODE' ,
    43:'EINVTYPE' ,
    44:'EINVMODE' ,
    48:'EINVDATA' ,
    55:'EINVNUM' ,
    56:'EINVSIZE' ,
    57:'EINVTIMEOUT' ,
    58:'EINVMETRIC' ,
    59:'EINVINTERVAL' ,
    69:'EINVBOOL' ,
    96:'EINVHOSTNAMELEN' ,
    109:'EDELPARTIAL' ,
    110:'EDELNOTHING' ,
    111:'ERSACHECK' ,
    117:'EOUTOFRANGE' ,
    119:'ELACKCFGINFO' ,
    121:'EINVRMTPORT' ,
    1001:'ECFGSAVEFAIL' ,
    1002:'ECFGAPPLYFAIL' ,
    1037:'ESTRINGLEN' ,
    2E3:'ENOUCI' ,
    2001:'ENOSEC' ,
    2002:'EREPEATSEC' ,
    2004:'EAPPNONE' ,
    2005:'EAPPHAS' ,
    2006:'EAPPNOT' ,
    2007:'EINSFAIL' ,
    2008:'EUNINSFAIL' ,
    -90401:'EPORTCUSTOMCONFLIC' ,
    -90501:'EIPTVTABLEFULL' ,
    -90502:'EIPTVENTRYCONFLIC' ,
    -90503:'EIPTVENTRYNOTEXIST' ,
    -90504:'EIPTVLINKMODEERROR' ,
    -90505:'EIPTVWORKMODEERROR' ,
    -90506:'EIPTVVLANIDERROR' ,
    -90507:'EIPTVWANINDEXERROR' ,
    -55900:'ECHANGETUNNELNAME' ,
    -55901:'ETUNNELNAMECONFLICT' ,
    -55902:'EBINDIFCONFLICT' ,
    -55904:'EREADTUNNELINFOFAIL' ,
    -55903:'EOUTIFANDSERVERIPEXIST' ,
    -55905:'EADDOREDITMULTI1' ,
    -55906:'EDELCONNECTEDCLIENT1' ,
    -55907:'EQQSADDFAIL1' ,
    -55908:'EQQSDELFAIL1' ,
    -55910:'ELACKCONFIGARG' ,
    -55911:'EIPSECNAMEREPEAT' ,
    -55912:'ESUBNETOVERLAP' ,
    -55913:'EBINDIFNOTEXIST' ,
    -55914:'ELOCALIDTYPEERRORIDNULL' ,
    -55915:'EREMOTEIDTYPEERRORIDNULL' ,
    -55916:'ELACKIKEPROPOSAL' ,
    -55917:'ELACKPH2PROPOSAL' ,
    -55918:'ESAMEIPNEEDSAMEIKEARG' ,
    -55919:'ESAMEIPNEEDSAMEPSK' ,
    -55920:'ECONFIGOVERFLOW1' ,
    -55921:'ECONFIGOVERFLOW2' ,
    -55922:'ELOCALIDINCLUDEINVCHARORSPACE' ,
    -55923:'EREMOTEIDINCLUDEINVCHARORSPACE' ,
    -55924:'EPH2SELESPANDAH' ,
    -55925:'EIPSECNAMEINCLUDEINVCHAR' ,
    -55926:'ECHANGEUSERNAME' ,
    -55927:'EADDOREDITMULTI2' ,
    -55928:'EREADTUNNELINFOFAIL' ,
    -55929:'EADDOREDITMULTI3' ,
    -55930:'EDELCONNECTEDCLIENT2' ,
    -55931:'EQQSADDFAIL2' ,
    -55932:'EQQSDELFAIL2' 
}
    @staticmethod
    def passwdEncryption(PassWd):
        Secret_key = "RDpbLfCPsJZ7fiv"
        Encrypted_string = "yLwVl0zKqws7LgKPRQ84Mdt708T1qQ3Ha7xv3H7NyU84p21BriUWBU43odz3iP4rBL3cD02KZciXTysVXiV8ngg6vL48rPJyAUw0HurW20xqxv9aYb4M9wK1Ae0wlro510qXeU07kV57fQMc8L6aLgMLwygtc0F10a0Dg70TOoouyFhdysuRMO51yY5ZlOZZLEal1h0t9YQW0Ko7oBwmCAHoic4HYbUyVeU3sfQ1xtXcPcf1aT303wAQhv66qzW"

        L_PassWd = len(PassWd)
        L_Secret_Ket = len(Secret_key)
        L_Encrypted_string = len(Encrypted_string)
        e = max(L_PassWd, L_Secret_Ket)

        result = []
        for l in range(e):
            m = chr(187)
            k = chr(187)
            if l >= L_PassWd:
                m = Secret_key[l]
            else:
                if l >= L_Secret_Ket:
                    k = PassWd[l]
                else:
                    k = PassWd[l]
                    m = Secret_key[l]
            k = ord(k)
            m = ord(m)
            result.append(Encrypted_string[(k ^ m) % L_Encrypted_string])

        return "".join(result)

    @staticmethod
    def ruleConvert(rule):
        name = list(rule.keys())[0]
        attr = list(rule.values())[0]
        return name, attr

    def __init__(self, url: str, passwd: str = None, encrypted: str = False, stok: str = None) -> None:
        self.url = url
        if stok == None:
            if not encrypted:
                passwd = TPapi.passwdEncryption(passwd)
            data = {"method": "do", "login": {"password": passwd}}
            req = requests.post(url=self.url, json=data)
            try:
                stok = req.json()["stok"]
            except KeyError:
                raise ValueError("Incorrect password")
        self.stok = stok
        self.apiurl = self.url+"stok=%s/ds" % stok

    def apipost(self, data: dict):
        req = requests.post(url=self.apiurl, json=data)
        ret = req.json()
        if ret["error_code"] != 0:
            raise RuntimeError(self.error_names[ret["error_code"]])
        return ret

    def __getattr__(self, name):
        if name.startswith("get"):
            self.methodname = name.lstrip("get")
            return self.__defaultMethod

    def __defaultMethod(self, *args):
        data = {"network": {"name": self.methodname}, "method": "get"}
        return self.apipost(data)

    def getsyslog(self, page: int = 1, num_per_page: int = 20):
        data = {
            "system": {
                "read_logs": {
                    "page": page,
                    "num_per_page": num_per_page
                }
            },
            "method": "do"}
        syslog = self.apipost(data)["syslog"]
        out = []
        log_levels = ["", "DEBUG", "INFO", "NOTICE",
                      "WARNING", "ERROR", "CRITICAL"]
        for line in syslog:
            name = list(line.keys())[0]

            text = unquote(line[name])
            level = log_levels[int(text[1])]
            text = text[3:]
            text = text.split(",")
            days_str = text[0]
            hour_str, min_str, sec_str = text[1].split(":")
            text = ",".join(text[2:])
            days: int = int(days_str.rstrip("days"))
            hour: int = int(hour_str.lstrip(" "))
            minute: int = int(min_str)
            second: int = int(sec_str)
            uptime = days*86400+hour*3600+minute*60+second
            out.append({
                "name": name,
                "text": text,
                "level": level,
                "uptime": uptime
            })
        return out

    def reconnectv6(self):
        logging.info("reconnet ipv6 now")
        data = {"network": {"change_wanv6_status": {
            "proto": "pppoev6", "operate": "connect"}}, "method": "do"}
        return self.apipost(data)

    def reconnectv4(self):
        logging.info("reconnet ipv4 now")
        data = {"network": {"change_wan_status": {
            "proto": "pppoe", "operate": "connect"}}, "method": "do"}
        return self.apipost(data)

    def setv6dns(self, dns1, dns2="::1"):
        logging.info("set ipv6 dns %s" % dns1)
        dns1 = quote(dns1)
        dns2 = quote(dns2)
        data = {
            "protocol": {
                "pppoev6": {"pri_dns": dns1, "snd_dns": dns2}
            },
            "method": "set"
        }
        return self.apipost(data)

    def getfwrules(self):
        data = {"firewall": {"table": "redirect"}, "method": "get"}
        return self.apipost(data)["firewall"]["redirect"]

    def gethostinfo(self):
        data = {"hosts_info": {"table": "host_info",
                               "name": "cap_host_num"}, "method": "get"}
        return self.apipost(data)

    def getcurhostinfo(self):
        hosts = self.gethostinfo()["hosts_info"]["host_info"]
        for host in hosts:
            info = list(host.values())[0]
            if info["is_cur_host"] == "1":
                return info

    def gethostinfobymac(self, mac):
        mac = mac.lower()
        mac = mac.replace(":", "-")
        hosts = self.gethostinfo()["hosts_info"]["host_info"]
        for host in hosts:
            info = list(host.values())[0]
            if info["mac"] == mac:
                return info
        logging.warning("cannot find host by mac %s" % mac)

    def delfwrule(self, rule_name):
        data = {"firewall": {"name": [rule_name]}, "method": "delete"}
        return self.apipost(data)

    def addfwrule(self, port, ipv4="", ipv6="", proto="all", name=None):
        logging.debug("add rule %s %s %s %s" % (ipv4, ipv6, port, proto))
        if name == None:
            num = 0
            for rule in self.getfwrules():
                rulename, _ = TPapi.ruleConvert(rule)
                if rulename.startswith("redirect"):
                    num = int(rulename.split("_")[1])
            name = "redirect_%d" % (num+1)

        if ipv4 == "" and ipv6 == "":
            raise ValueError("you must input at lease one ip")

        ipv6 = quote(ipv6)
        port = str(port)
        data0 = {
            "firewall": {
                "table": "redirect",
                "name": name,
                "para": {
                    "proto": proto,
                    "src_dport_start": port,
                    "src_dport_end": port,
                    "dest_port": port,
                    "wan_port": 0,
                    "dest_ip": ipv4,
                    "dest_ip6": ipv6
                }
            },
            "method": "add"}
        return self.apipost(data0)

    def reboot(self):
        logging.warning("reboot router now")
        data = {"system": {"reboot": None}, "method": "do"}
        return self.apipost(data)


if __name__ == "__main__":
    pass
