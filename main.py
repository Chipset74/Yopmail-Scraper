import requests
import re
from datetime import *
import time

class yopMail:
    def __init__(self, inbox) -> None:
        self.Session = requests.Session()
        self.inbox = inbox
        #self.proxy = 'ROTATING_PROXY_HERE' - Optional Proxies
        #self.Session.proxies = {'http': 'http://' + self.proxy, 'https': 'http://' + self.proxy}
        #self.Session.verify = False - Debugging Line
        if self.getInitCookies(): # If we get the initial cookies, we can continue
            self.getYPValue()
            self.getYTime()

    def getCaptcha(self): # This is an XEvil call, not 2captcha
        req = requests.get("http://www.2captcha.com/in.php?key=b7b7cc9e4c063eb60b88afd45495635f&method=userrecaptcha&googlekey=6LcG5v8SAAAAAOdAn2iqMEQTdVyX8t0w9T3cpdN2&pageurl=https://yopmail.com").text
        captcha = req.split("|")[1]
        notFound = True
        while notFound:
            x = requests.get("http://www.2captcha.com/res.php?key=b7b7cc9e4c063eb60b88afd45495635f&action=get&id=" + captcha)
            if x.text == "CAPCHA_NOT_READY":
                time.sleep(1)
                continue
            else:
                notFound = False
                captchaSolved = x.text.split("|")[1]
                break
        return captchaSolved

    def getInitCookies(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US;q=0.8',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Sec-GPC': '1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36',
        }

        response = self.Session.get('https://yopmail.com/en/', headers=headers)
        self.yp = re.findall('id=\"yp\" value=\"(.*)\"/><div', response.text)[0]

        if response.status_code == 200:
            return True

    def getInboxEmailIDs(self, captcha=""):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://yopmail.com/en/wm',
            'Sec-Fetch-Dest': 'iframe',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-GPC': '1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36',
        }

        params = {
            'login': self.inbox,
            'p': '1',
            'd': '',
            'ctrl': '',
            'yp': self.yp,
            'yj': self.yj,
            'v': '5.6',
            'r_c': captcha,
            'id': '',
        }

        response = self.Session.get('https://yopmail.com/en/inbox', params=params, headers=headers)
        if "GoogleAnalyticsObject" not in response.text:
            self.getInboxEmailIDs(self.getCaptcha())

        email_ids = re.findall('class="m" id="(.*)" >', response.text)
        if len(email_ids) > 0:
            return ["m" + x for x in email_ids]
        return []
    
    def retrieveEmail(self, email_id, captcha=None):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://yopmail.com/en/wm',
            'Sec-Fetch-Dest': 'iframe',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-GPC': '1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36',
        }
        params = {
            'b':self.inbox,
            'id':email_id,
        }
        if captcha is not None:
            params['r_c'] = captcha

        response = self.Session.get('https://yopmail.com/en/mail', headers=headers, params=params)
        if "Complete the CAPTCHA to continue" in response.text:
            return self.retrieveEmail(email_id, self.getCaptcha())

        return response.text

    def getYTime(self):
        time = datetime.now()
        self.Session.cookies['ytime'] = str(time.hour) + ":" + str(time.minute)

    def getYPValue(self):
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Referer': 'https://yopmail.com/en/',
            'Sec-Fetch-Dest': 'script',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-GPC': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36',
        }

        response = self.Session.get('https://yopmail.com/ver/5.6/webmail.js', headers=headers)
        self.yj = re.findall('yj=(.*)&v=\'', response.text)[0]

x = yopMail("test") 
emailIDs = x.getInboxEmailIDs() # get all email IDs in inbox
email = x.retrieveEmail(emailIDs[0]) # get email with specific email ID
