# D621

## Installation

To use this bot, you'll need to have Python and the required dependencies installed. You can install the dependencies by running the following command:

`pip install discord py621`

## Usage

Once you have the dependencies installed, you can run the bot by executing the bot.py file. 

Before running the bot, you'll need to provide your Discord bot token in the client.run() method at the end of the file. You can obtain a token by creating a bot on the Discord developer portal.

## Commands

The bot has the following commands:

./e621 search [tag]: Browse through posts with your selected tag(s).
./e621 pool [pool ID]: Browse a Pool with a Pool ID.
./e621 status: Fetch the status of the e621 API.
./e621 about: Get information about the bot and its commands.

## Thread Usage

To prevent spamming the e621 API, the bot uses a thread system. Each user is allowed a single thread to interact with the API. This helps prevent clutter and spam. The bot will automatically close a thread after 90 seconds of inactivity.
