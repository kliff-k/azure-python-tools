from rtcclient import RTCClient
import requests

requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'ALL:@SECLEVEL=1'


url = ""
username = ""
password = ""

myclient = RTCClient(url, username, password, form_login=True, ends_with_jazz=False)

myquery = myclient.query
myquerystr = 'rtc_cm:ID_mudanca_prd="**" and rtc_cm:archived=false'
wk_list = myquery.queryWorkitems(myquerystr, projectarea_id="_kz1AN5gJEeSpMKZUvO3lOw")

# wk = myclient.getWorkitem(19629536)

# Entrypoint
if __name__ == '__main__':

    for wk in wk_list:
        print(wk.getattr("title"))
