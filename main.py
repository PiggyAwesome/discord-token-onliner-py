import json
import random
import time
from enum import Enum, IntEnum
from threading import Thread
from typing import Dict, List, Optional, Tuple, Union

import websockets.typing
from colorama import Back, Fore, Style
from websockets.exceptions import ConnectionClosedError
from websockets.sync.client import connect
from websockets.sync.connection import Connection


class Status(Enum):
    "More information at https://discord.com/developers/docs/topics/gateway-events#activity-object-activity-types"
    ONLINE = "online"  # Online
    DND = "dnd"  # Do Not Disturb
    IDLE = "idle"  # AFK
    INVISIBLE = "invisible"  # Invisible and shown as offline
    OFFLINE = "offline"  # Offline


class Activity(Enum):
    "More information at https://discord.com/developers/docs/topics/gateway-events#activity-object"
    GAME = 0  #   Playing {name}
    STREAMING = 1  #   Streaming {details}
    LISTENING = 2  #   Listening to {name}
    WATCHING = 3  #   Watching {name}
    CUSTOM = 4  #   {emoji} {state} am cool
    COMPETING = 5  #   Competing in {name} World Champions


class OPCodes(Enum):
    "More information at https://discord.com/developers/docs/topics/opcodes-and-status-codes#opcodes-and-status-codes"
    Dispatch = 0  # An event was dispatched.
    Heartbeat = 1  # Fired periodically by the client to keep the connection alive.
    Identify = 2  # Starts a new session during the initial handshake.
    PresenceUpdate = 3  # Update the client's presence.
    VoiceStateUpdate = 4  # Used to join/leave or move between voice channels.
    Resume = 6  # Resume a previous session that was disconnected.
    Reconnect = 7  # You should attempt to reconnect and resume immediately.
    RequestGuildMembers = (
        8  # Request information about offline guild members in a large guild.
    )
    InvalidSession = 9  # The session has been invalidated. You should reconnect and identify/resume accordingly.
    Hello = (
        10  # Sent immediately after connecting, contains the heartbeat_interval to use.
    )
    HeartbeatACK = 11  # Sent in response to receiving a heartbeat to acknowledge that it has been received.


class DiscordIntents(IntEnum):
    "More information at https://discord.com/developers/docs/topics/gateway#gateway-intents"
    GUILDS = 1 << 0
    GUILD_MEMBERS = 1 << 1
    GUILD_MODERATION = 1 << 2
    GUILD_EMOJIS_AND_STICKERS = 1 << 3
    GUILD_INTEGRATIONS = 1 << 4
    GUILD_WEBHOOKS = 1 << 5
    GUILD_INVITES = 1 << 6
    GUILD_VOICE_STATES = 1 << 7
    GUILD_PRESENCES = 1 << 8
    GUILD_MESSAGES = 1 << 9
    GUILD_MESSAGE_REACTIONS = 1 << 10
    GUILD_MESSAGE_TYPING = 1 << 11
    DIRECT_MESSAGES = 1 << 12
    DIRECT_MESSAGE_REACTIONS = 1 << 13
    DIRECT_MESSAGE_TYPING = 1 << 14
    MESSAGE_CONTENT = 1 << 15
    GUILD_SCHEDULED_EVENTS = 1 << 16
    AUTO_MODERATION_CONFIGURATION = 1 << 20
    AUTO_MODERATION_EXECUTION = 1 << 21


class Presence:
    """
    This class is used to manage the presence of a user on Discord.
    It allows you to set the user's online status and activities,
    which are displayed on the user's profile.

    Parameters:
    -----------
    online_status: Status
        An enum value representing the user's online status. This can be one of the predefined Status types, such as Online, Do Not Disturb, Away, Invisible, or Offline.

    Attributes:
    -----------
    online_status: Status
        The current online status of the user.
    activities: List[Activity]
        A list of activities that the user is currently engaged in. Each activity is represented by an Activity object, which contains information such as the name of the activity, its type, and any relevant URLs.

    Methods:
    --------
    addActivity(name: str, activity_type: Activity, url: Optional[str]) -> int
        Adds a new activity to the user's presence. Returns the index of the newly added activity.
    removeActivity(index: int) -> bool
        Removes an activity from the user's presence. Returns True if the activity was removed, False if the index was out of range.
    """

    def __init__(self, online_status: Status) -> None:
        self.online_status: Status = online_status
        self.activities: List[Activity] = []

    def addActivity(
        self, name: str, activity_type: Activity, url: Optional[str]
    ) -> int:
        """
        Adds a new activity to the user's current presence in Discord.

        Parameters:
        ----------
        name : str
            The displayed name of the activity. This could also be the name of a game
        activity_type : Activity
            An enum value representing the type of activity. This should be one of the predefined Activity types, such as Playing, Streaming, Listening, etc.
        url : Optional[str]
            The URL associated with the activity. This is particularly relevant if the activity_type is Streaming, in which case this URL should be the link to the stream.

        Returns:
        -------
        int
            The index of the newly added activity in the activities list, which can be used to reference or modify the activity later.

        Example:
        -------
        >>> addActivity("Playing Chess", Activity.Playing)
        >>> addActivity("Streaming Art", Activity.Streaming, "http://twitch.tv/example_stream")

        Note:
        ----
        The URL parameter is only used if the activity_type is Streaming; for other activity types, the URL is ignored and can be omitted.

        """

        self.activities.append(
            {
                "name": name,
                "type": activity_type.value,  # The enum value of the activity type
                "url": url if activity_type == Activity.STREAMING else None,
            }
        )
        return len(self.activities) - 1

    def removeActivity(self, index: int) -> bool:
        """
        Removes an activity to the user's current presence in Discord.

        Parameters
        ----------
        index : int
            The index of the activity to remove.

        Returns
        -------
        bool
            ``True`` if the activity was removed, ``False`` if the index was out of range.

        Example
        -------
        >>> removeActivity(0)
        >>> removeActivity(2)

        """

        if index < 0 or index >= len(self.activities):
            return False
        self.activities.pop(index)
        return True


class DiscordWebSocket:
    """
    This class is used to manage the connection to the Discord WebSocket.

    Parameters:
    -----------
    None

    Attributes:
    -----------
    websocket_instance: websocket.WebSocketClientProtocol
        The WebSocket connection to the Discord server.
    heartbeat_counter: int
        The number of heartbeats sent since connecting.
    username: str
        The username of the authenticated user.
    required_action: int
        The required action to take after attempting to authenticate.
    heartbeat_interval: int
        The interval between heartbeats, in milliseconds.
    last_heartbeat: float
        The time of the last received heartbeat.

    Methods:
    --------
    get_heatbeat_interval(self) -> None
        This function is used to get the heartbeat interval from the Discord WebSocket.

    authenticate(self, token: str, rich: Presence) -> Optional[Dict]
        Authenticates the user with the Discord API using the given token.

    send_heartbeat(self) -> websockets.typing.Data
        Send a heartbeat to keep the connection alive.

    """

    def __init__(self) -> None:
        self.websocket_instance = connect(
            "wss://gateway.discord.gg/?v=10&encoding=json"
        )
        self.heartbeat_counter = 0

        self.username: str = None
        self.required_action: str = None
        self.heartbeat_interval: int = None
        self.last_heartbeat: float = None

    def get_heatbeat_interval(self) -> None:
        """
        This function is used to get the heartbeat interval from the Discord WebSocket.

        The heartbeat interval ensures that the connection to the Discord server is maintained
        and not closed due to inactivity. It must be called periodically, as specified
        by the heartbeat interval.
        """

        resp: Dict = json.loads(self.websocket_instance.recv())
        self.heartbeat_interval = resp["d"]["heartbeat_interval"]

    def authenticate(self, token: str, rich: Presence) -> Union[Dict, bool]:
        """
        Authenticates the user with the Discord API using the given token.
        This is an [IDENTIFY payload](https://discord.com/developers/docs/topics/gateway-events#identify-identify-structure) containing a [Presence update](https://discord.com/developers/docs/topics/gateway-events#update-presence)

        Parameters:
        -----------
        token: str
            The user's Discord authentication token.
        rich: Presence
            The user's presence information, including their online status and activities.

        Returns:
        --------
        Optional[Dict]
            The response from the Discord API, or None if the authentication failed.
        """
        self.websocket_instance.send(
            json.dumps(
                {
                    "op": OPCodes.Identify.value,  # Operation code for Identify, used to authenticate the client to the server.
                    "d": {
                        "token": token,  # OAuth token used for verifying the client's identity with Discord.
                        "intents": DiscordIntents.GUILD_MESSAGES
                        | DiscordIntents.GUILDS,  # Bitwise combination of intents specifying the types of events the client wants to receive.
                        "properties": {
                            "os": "linux",  # The operating system of the client
                            "browser": "Brave",  # The browser in which the client is running
                            "device": "Desktop",  # Type of device being used
                        },
                        "presence": {
                            "activities": [
                                activity for activity in rich.activities
                            ],  # List of activities for rich presence.
                            "status": rich.online_status.value,  # The client's online status (e.g., online, idle).
                            "since": time.time(),  # UNIX timestamp indicating when the client's status was last set.
                            "afk": False,  # Boolean flag indicating whether the client is marked as "away from keyboard" (AFK).
                        },
                    },
                }
            )
        )
        try:
            resp = json.loads(self.websocket_instance.recv())
            self.username: str = resp["d"]["user"]["username"]
            self.required_action = resp["d"].get("required_action")
            self.heartbeat_counter += 1
            self.last_heartbeat = time.time()

            return resp
        except ConnectionClosedError:
            return False

    def send_heartbeat(self) -> websockets.typing.Data:
        """
        Send a heartbeat to keep the connection alive.

        Returns:
            The response from the server.
        """
        self.websocket_instance.send(
            json.dumps(
                {"op": OPCodes.Heartbeat.value, "d": None}
            )  # Operation code for sending a heartbeat, used to keep the connection alive.
        )

        self.heartbeat_counter += 1
        self.last_heartbeat = time.time()

        resp = self.websocket_instance.recv()
        return resp


def intro(tokens) -> None:
    print(
        Fore.GREEN
        + "Piggy's Onliner "
        + Fore.MAGENTA
        + "Epic "
        + Fore.CYAN
        + "[Multiple Accounts] "
        + Fore.RED
        + f"Total Accounts: {len(tokens)}"
        + Style.RESET_ALL
    )
    print(
        """
██████╗ ██╗ ██████╗  ██████╗██╗   ██╗ ██╗███████╗     ██████╗ ███╗   ██╗██╗     ██╗███╗   ██╗███████╗██████╗ 
██╔══██╗██║██╔════╝ ██╔════╝╚██╗ ██╔╝██╔╝██╔════╝    ██╔═══██╗████╗  ██║██║     ██║████╗  ██║██╔════╝██╔══██╗
██████╔╝██║██║  ███╗██║  ███╗╚████╔╝ ╚═╝ ███████╗    ██║   ██║██╔██╗ ██║██║     ██║██╔██╗ ██║█████╗  ██████╔╝
██╔═══╝ ██║██║   ██║██║   ██║ ╚██╔╝      ╚════██║    ██║   ██║██║╚██╗██║██║     ██║██║╚██╗██║██╔══╝  ██╔══██╗
██║     ██║╚██████╔╝╚██████╔╝  ██║       ███████║    ╚██████╔╝██║ ╚████║███████╗██║██║ ╚████║███████╗██║  ██║
╚═╝     ╚═╝ ╚═════╝  ╚═════╝   ╚═╝       ╚══════╝     ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝
    """
        + Fore.GREEN
        + "                         Created By PiggyAwesome"
        + Style.RESET_ALL
    )


def plog(symbol, text, username, extra):
    print(f"[{symbol}] {f'{text} |':>25} {username + ' |':>32} {extra}")


def main(token: str, activity: Presence):
    socket = DiscordWebSocket()
    socket.get_heatbeat_interval()

    auth_resp = socket.authenticate(token, activity)
    if not auth_resp:
        plog("🔐", "Failed to Authenticate", "-", "TOKEN INVALID")
        return

    plog("🔑", "Authenticated", socket.username, socket.required_action)

    while True:
        try:
            if (
                time.time() - socket.last_heartbeat
                >= (socket.heartbeat_interval / 1000) - 5
            ):  # convert to seconds as a common unit and minus 5 to make room for error
                plog(
                    f"💓 Sending Heartbeat", f"{socket.heartbeat_counter:04}", socket.username, f"{socket.heartbeat_interval}ms",
                )
                resp = socket.send_heartbeat()
            time.sleep(0.5)
        except IndentationError:
            print(resp)


if __name__ == "__main__":
    # get tokens from token file
    try:
        with open("tokens.txt", "r") as token_file:
            tokens: List[str] = token_file.read().splitlines()
            
        with open("config.json", "r") as config_file:
            config: Dict[str, Union[List[str], Dict[str, List[str]]]] = json.loads(config_file.read())

        activity_types: List[Activity] = [
            Activity[x.upper()] for x in config["choose_random_activity_type_from"]
        ]
        online_statuses: List[Status] = [
            Status[x.upper()] for x in config["choose_random_online_status_from"]
        ]
    except KeyError:
        print("Invalid config! Exiting...")
        exit()
    
    thrds = []
    intro(tokens)
    
    for token in tokens:
        online_status = random.choice(online_statuses)
        chosen_activity_type = random.choice(activity_types)
        url = None

        match chosen_activity_type:
            case Activity.GAME:
                name = random.choice(config["game"]["choose_random_game_from"])

            case Activity.STREAMING:
                name = random.choice(config["streaming"]["choose_random_name_from"])
                url = random.choice(config["streaming"]["choose_random_url_from"])

            case Activity.LISTENING:
                name = random.choice(config["listening"]["choose_random_name_from"])

            case Activity.WATCHING:
                name = random.choice(config["watching"]["choose_random_name_from"])

            case Activity.CUSTOM:
                name = random.choice(config["custom"]["choose_random_name_from"])

            case Activity.COMPETING:
                name = random.choice(config["competing"]["choose_random_name_from"])

        activity = Presence(online_status)
        activity.addActivity(activity_type=chosen_activity_type, name=name, url=url)
        
        x = Thread(target=main, args=(token, activity))
        thrds.append(x)
        x.start()

    for thr in thrds:
        thr.join()