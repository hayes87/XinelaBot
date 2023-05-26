# XinelaBot

XinelaBot is a bot built for Discord, which allows users to set up polls and receive reminders for selected events.

The bot uses the discord.py library, APScheduler for managing jobs and scheduling, and ElevenLabs' text-to-speech API for generating audio messages. 

### Features:
- Ability to create polls for selected events
- Option to vote on a poll and display the results
- Scheduled reminders for upcoming events
- Generation of audio messages using text-to-speech

## Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/<username>/xinelaBot.git
    ```

2. Install the requirements:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up your environment variables in a `.env` file. You'll need:

    - `DISCORD_TOKEN`: Your Discord bot token
    - `ELEVENLABS_API`: Your ElevenLabs API key
    - `ROLE_ID`: The role ID of your bot on your Discord server

4. Run the bot:

    ```bash
    python main.py
    ```

## Commands

Here are the commands you can use with XinelaBot:

- `!readycheck`: Starts a new poll
- `!anunciartime`: Announces the winning time slot and the users who voted for it.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
