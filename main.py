import asyncio, time, json, random
from websockets.sync.client import connect
from websockets.sync.connection import Connection
from websockets.exceptions import ConnectionClosedError
from threading import Thread



class Status:
    "Some enum-like variables to easily choose a status"
    ONLINE = "online"	        # Online
    DND = "dnd"	                # Do Not Disturb
    IDLE = "idle"	            # AFK
    INVISIBLE = "invisible"	    # Invisible and shown as offline
    OFFLINE = "offline"	        # Offline
    all_types = [ONLINE, DND, IDLE, INVISIBLE, OFFLINE]
    all_online_types = [ONLINE, DND, IDLE]
    class Activity:
        Game = 0	                #   Playing {name}
        Streaming = 1	            #   Streaming {details}
        Listening = 2	            #   Listening to {name}
        Watching = 3	            #   Watching {name}
        Custom = 4	                #   {emoji} {state} am cool
        Competing = 5	            #   Competing in {name} World Champions
        all_types = [Game, Streaming, Listening, Watching, Custom, Competing]
        class Games:
            all_games =  ['Minecraft', 'Rust', 'VRChat', 'reeeee', 'MORDHAU', 'Fortnite', 'Apex Legends', 'Escape from Tarkov', 'Rainbow Six Siege', 'Counter-Strike: Global Offense', 'Sinner: Sacrifice for Redemption', 'Minion Masters', 'King of the Hat', 'Bad North', 'Moonlighter', 'Frostpunk', 'Starbound', 'Masters of Anima', 'Celeste', 'Dead Cells', 'CrossCode', 'Omensight', 'Into the Breach', 'Battle Chasers: Nightwar', 'Red Faction Guerrilla Re-Mars-tered Edition', 'Spellforce 3', 'This is the Police 2', 'Hollow Knight', 'Subnautica', 'The Banner Saga 3', 'Pillars of Eternity II: Deadfire', 'This War of Mine', 'Last Day of June', 'Ticket to Ride', 'RollerCoaster Tycoon 2: Triple Thrill Pack', '140', 'Shadow Tactics: Blades of the Shogun', 'Pony Island', 'Lost Horizon', 'Metro: Last Light Redux', 'Unleash', 'Guacamelee! Super Turbo Championship Edition', 'Brutal Legend', 'Psychonauts', 'The End Is Nigh', 'Seasons After Fall', 'SOMA', 'Trine 2: Complete Story', 'Trine 3: The Artifacts of Power', 'Trine Enchanted Edition', 'Slime-San', 'The Inner World', 'Bridge Constructor', 'Bridge Constructor Medieval', 'Dead Age', 'Risk of Rain', "Wasteland 2: Director's Cut", 'The Metronomicon: Slay The Dance Floor', 'TowerFall Ascension + Expansion', 'Nidhogg', 'System Shock: Enhanced Edition', 'System Shock 2', "Oddworld:New 'n' Tasty!", 'Out of the Park Baseball 18', 'Hob', 'Destiny 2', 'Torchlight', 'Torchlight 2', 'INSIDE', 'LIMBO', "Monaco: What's Yours Is Mine", 'Tooth and Tail', 'Dandara', 'GoNNER', 'Kathy Rain', 'Kingdom: Classic', 'Kingdom: New Lands', 'Tormentor X Punisher', 'Chaos Reborn', 'Ashes of the Singularity: Escalation', 'Galactic Civilizations III', 'Super Meat Boy', 'Super Hexagon', 'de Blob 2', 'Darksiders II Deathinitive Edition', 'Darksiders Warmastered Edition', 'de Blob', 'Red Faction 1', 'Dungeon Defenders']


class Presence:
    # Precence class for better token management 
    def __init__(self, online_status) -> None:
        self.online_status = online_status
        self.activities = []

    def addActivity(self, name, activity_type, url=None):
        self.activities.append({
            "name": name,                                   # activity name (can be game name)
            "type": activity_type,                          # activity type (https://discord.com/developers/docs/topics/gateway-events#activity-object)
            "url":  url if activity_type == \
                    Status.Activity.Streaming else None     # url if you are streaming
        })
        return len(self.activities) - 1

    def removeActivity(self, index):
        self.activities.pop(index)
        return True




class DiscordWebSocket:
    def __init__(self) -> None:
        self.websocket_instance = connect("wss://gateway.discord.gg/?v=10&encoding=json")
        self.heartbeat_counter = 0

    def get_heatbeat_interval(self):
        resp = json.loads(self.websocket_instance.recv())
        self.heartbeat_interval = resp["d"]["heartbeat_interval"]

    def authenticate(self, token, rich:Presence):
        """
        We send the websocket some authentication info once we have connected to verify our identity.

        This is an [IDENTIFY payload](https://discord.com/developers/docs/topics/gateway-events#identify-identify-structure)
        containing a [Presence update](https://discord.com/developers/docs/topics/gateway-events#update-presence)
        """
        self.websocket_instance.send(json.dumps({
                    "op": 2,                                        # 2 means authenticating
                    "d": {
                        "token": f"{token}",                        # oauth token goes here for verifying identity
                        "intents": 513,                             # parameters for what to recieve from ws
                        "properties": {
                            "os": "linux",                          # operating system
                            "browser": "Brave",                     # browser
                            "device": "Desktop"                     # device
                        },
                    "presence": {
                        "activities": [activity for activity in rich.activities],
                        "status": rich.online_status,               # online status
                        "since": time.time(),                       # epoch time for when your status started
                        "afk": False                                # whether or not you appear to be afk
                        }
                    }
                })
            )
        try:
            resp = json.loads(self.websocket_instance.recv())
            self.username = resp['d']['user']['username']
            self.required_action = resp['d'].get('required_action', None) #NEW changes
            self.heartbeat_counter += 1
            self.last_heartbeat = time.time()

            return resp
        except ConnectionClosedError:
            return False


    def send_heartbeat(self):
        """You need to send a heartbeat at least once in an interval to stay connected to Discord's websocket"""
        self.websocket_instance.send(json.dumps({
            "op": 1,                                    # code 1 is to send a heartbeat
            "d": None
        }))

        self.heartbeat_counter += 1
        self.last_heartbeat = time.time()

        resp = self.websocket_instance.recv()
        return resp


def intro(tokens):
    from colorama import Fore, Back, Style
    print(Fore.GREEN + "Piggy's Onliner "
        + Fore.MAGENTA + "Epic " 
        + Fore.CYAN + "[Multiple Accounts] "
        + Fore.RED + f"Total Accounts: {len(tokens)}"
        + Style.RESET_ALL)

    print("██████╗ ██╗ ██████╗  ██████╗██╗   ██╗███████╗     ██████╗ ███╗   ██╗██╗     ██╗███╗   ██╗███████╗██████╗ ")
    print("██╔══██╗██║██╔════╝ ██╔════╝╚██╗ ██╔╝██╔════╝    ██╔═══██╗████╗  ██║██║     ██║████╗  ██║██╔════╝██╔══██╗")
    print("██████╔╝██║██║  ███╗██║  ███╗╚████╔╝ ███████╗    ██║   ██║██╔██╗ ██║██║     ██║██╔██╗ ██║█████╗  ██████╔╝")
    print("██╔═══╝ ██║██║   ██║██║   ██║ ╚██╔╝  ╚════██║    ██║   ██║██║╚██╗██║██║     ██║██║╚██╗██║██╔══╝  ██╔══██╗")
    print("██║     ██║╚██████╔╝╚██████╔╝  ██║   ███████║    ╚██████╔╝██║ ╚████║███████╗██║██║ ╚████║███████╗██║  ██║")
    print("╚═╝     ╚═╝ ╚═════╝  ╚═════╝   ╚═╝   ╚══════╝     ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝")
    print(Fore.GREEN + "                         Created By PiggyAwesome" + Style.RESET_ALL)                                                                                                    


def plog(symbol, text, username, extra):
    print(f"[{symbol}] {f'{text} |':>25} {username + ' |':>32} {extra}")


def main(token, activity:Presence):
    socket = DiscordWebSocket()
    socket.get_heatbeat_interval()

    auth_resp = socket.authenticate(token, activity)
    if not auth_resp: plog("🔐", "Failed to Authenticate", "-", "TOKEN INVALID"); return

    plog("🔑", "Authenticated", socket.username, socket.required_action)

    while True:
        try:
            if time.time()-socket.last_heartbeat >= (socket.heartbeat_interval/1000)-5: # convert to seconds as a common unit and minus 5 to make room for error
                plog("💓", f"Sending Heartbeat {socket.heartbeat_counter:04}", socket.username, f"{socket.heartbeat_interval}ms")
                resp = socket.send_heartbeat()
            time.sleep(0.5)
        except TypeError:
            print(resp)


if __name__ == "__main__":
    # get tokens from token file
    with open("tokens.txt", "r") as token_file: 
        tokens = token_file.read().splitlines()
    
    
    with open("config.json", "r") as config_file:
        config = json.loads(config_file.read())
    
    activity_types:list = config["choose_random_activity_type_from"]
    activity_lookup_table:dict = {"game": 0, "streaming": 1, "listening": 2, "watching": 3, "custom": 4, "competing": 5}
    

    intro(tokens)
    for token in tokens:
        online_status = random.choice(config["choose_random_online_status_from"])
        chosen_activity_type = activity_lookup_table[random.choice(config["choose_random_activity_type_from"])]
        url = None

        match chosen_activity_type:
            case Status.Activity.Game:
                name = random.choice(config["game"]["choose_random_game_from"])

            case Status.Activity.Streaming:
                name = random.choice(config["streaming"]["choose_random_name_from"])
                url = random.choice(config["streaming"]["choose_random_url_from"])

            case Status.Activity.Listening:
                name = random.choice(config["listening"]["choose_random_name_from"])

            case Status.Activity.Watching:
                name = random.choice(config["watching"]["choose_random_name_from"])

            case Status.Activity.Custom:
                name = random.choice(config["custom"]["choose_random_name_from"])

            case Status.Activity.Competing:
                name = random.choice(config["competing"]["choose_random_name_from"])



        activity = Presence(online_status)
        activity.addActivity(
            activity_type=chosen_activity_type,
            name=name,
            url=url
        )

        Thread(target=main, args=(token, activity)).start()
