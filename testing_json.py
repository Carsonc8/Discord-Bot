
import requests

r = requests.get(url="https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid=2073850")
d = r.json()
print(d) 
index = d['response']['player_count']
print(index)