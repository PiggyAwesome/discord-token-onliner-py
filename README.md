# discord-token-onliner-py

### new update at 20 stars 👀

Makes multiple Discord accounts go online by using their 0Auth token

**Discord Token Onliner** is a Python script that allows you to change your Discord presence status for multiple accounts with various activities. Python rework of [my javascript version](https://github.com/PiggyAwesome/discord-token-onliner)


## Features
- Set custom presence status (Online, Do Not Disturb, Idle, Invisible, or Offline).
- Choose from different activity types (Playing a game, Streaming, Listening, Watching, Custom status, Competing).
- Supports multiple Discord accounts with different presence settings.

## Usage

1. **Setup Your Tokens**:
   - Save your Discord tokens in a `tokens.txt` file, with each token on a new line.

2. **Configure Activities**:
   - Customize your presence activities in the `config.json` file. You can specify online status, activity types, and various options.

3. **Run the Script**:
   - Execute the `main.py` script to start changing the presence for your Discord accounts.

## Configuration
`(keep in mind, to increase the propability of something to be chosen, you can add it to a list multiple times)`

You can configure the following options in `config.json`:

The `config.json` file allows you to customize the behavior of the Discord Presence Changer script. This section provides details on the available configuration options:

- `choose_random_online_status_from`: An array that specifies the online status options you can choose from for your Discord presence. You can pick from the following values:
    - `"online"`: Online
    - `"dnd"`: Do Not Disturb
    - `"idle"`: Idle (Away From Keyboard)
    - `"invisible"`: Invisible (Appears as offline)
    - `"offline"`: Offline

- `choose_random_activity_type_from`: An array that defines the types of activities you can set as your Discord presence. You can choose from the following activity types:
    - `"game"`: Playing a game
    - `"streaming"`: Streaming content
    - `"listening"`: Listening to music or a podcast
    - `"watching"`: Watching a video or stream
    - `"custom"`: Setting a custom status
    - `"competing"`: Competing in an event or tournament

### Game Activity Configuration

For the `game` activity type, you can specify a list of games from which the script will choose randomly for the Discord presence. Customize this section by adding or removing/adding game titles as needed:

```json5
"game": {
    "choose_random_game_from": [
        "Minecraft",
        "Rust",
        "VRChat",
        // Add more game titles here
    ]
}
```

For the `streaming` activity type, you can define the name and URL for streaming. Customize this section with your preferred streaming options:

```json5
"streaming": {
    "choose_random_name_from": [
        "Fortnite",
        "Skibidi Toilet remix live",
        // Add more streaming names here
    ],
    "choose_random_url_from": [
        "https://www.twitch.tv/piggyawesome",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ)",
        // Add more streaming URLs here
    ]
}
```

For the `listening` activity type, specify what the account is listening to. Customize this section with the names of songs, artists, or sources you want to appear in the presence:

```json5
"listening": {
    "choose_random_name_from": [
        "Spotify",
        "Your Favorite Band",
        // Add more listening options here
    ]
}
```

For the `watching` activity type, define what the account should be watching. Customize this section with the names of videos, shows, or streams you want to appear in the presence:

```json5
"watching": {
    "choose_random_name_from": [
        "YouTube Videos",
        "Skibidi toilet",
        // Add more watching options here
    ]
}
```

For the `custom` activity type, you can set your own custom status. Customize this section with the specific custom statuses you want to display:

```json5
"custom": {
    "choose_random_name_from": [
        "Custom Status 1",
        "Custom Status 2",
        // Add more custom status options here
    ]
}
```

For the `competing` activity type, define what the account should be competing in. Customize this section with the names of events, competitions, or tournaments:

```json5
"competing": {
    "choose_random_name_from": [
        "Gaming Tournament",
        "Coding Competition",
        // Add more competing options here
    ]
}
```

## Todo

- [ ] add handler to reconnect if a token disconnects (discord's session thing)

## Dependencies

- The script uses Python and requires the following libraries: `websockets`, `colorama`.

## License

This project is licensed under the GPL-3.0 License. See the [LICENSE](LICENSE) file for details.

## Disclaimer

This script is against Discord's TOS, and made for educational and entertainment purposes only. Please use it responsibly and respect Discord's terms of service.

Feel free to contribute to this project or report any issues!

![GitHub](https://img.shields.io/github/license/PiggyAwesome/discord-token-onliner-py)
