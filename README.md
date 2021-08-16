# Matsubo :flags:
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/makokaz/matsubo/main/LICENSE)

Matsubo parses Japanese 祭り :flags: (Japanese for "festival") and other events from different sources and uses Discord to summarize all event details.

Events are filtered by region and users are reminded at the start of an event. Currently, events are parsed from the following sources:

| Source | URL |
| --- | --- |
| [<img src="https://cdn.cheapoguides.com/wp-content/themes/cheapo_theme/assets/img/logos/tokyocheapo/logo.png" height="30">](https://tokyocheapo.com) | tokyocheapo.com |
| [<img src="https://cdn.cheapoguides.com/wp-content/themes/cheapo_theme/assets/img/logos/japancheapo/logo.png" height="30">](https://japancheapo.com) | japancheapo.com |

**!! Disclaimer** 
```
These websites do not belong to this repository, nor does this repository have a relation with any of these websites.
Matsubo will always direct you to the corresponding source where the event was found, not a direct link to the event website itself. This is to honor the great people working on the mentioned websites.
Matsubo only serves the purpose of summarizing events from different sources, and reminding people when an event has started.
```

# How to use
> Before you follow the steps below, make sure that you have a `Discord Bot Token` by following the guide [how to get a discord bot token](#how-to-get-a-discord-bot-token).

Since Matsubo is a Discord bot that should react to user input anytime, Matsubo should also run at any given time. Below are two options explained to run Matsubo.

## 1. Heroku
Heroku is a hosting website for programs running 24/7 or between specified time intervals. They have a free hobby-dev tier, and more advanced tiers for production.

To host Matsubo on their server, follow these steps:
1. Create an account at heroku.com
2. Deploy by clicking on this button:  
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)  
During Deployment, you will be asked to fill in a few [API Keys](#api-keys).
3. Since Matsubo uses internally a PostgreSQL database to gather all event information, you must add the [Heroku Postgres add-on](https://elements.heroku.com/addons/heroku-postgresql) to your newly created Matsubo application.
4. The postgres-database must now be initialized. At the main page of your Matsubo application, click on `More -> Run Console` and type `python` in the blank field, then Enter.
Copy the following lines into the console that appeared:
    ```python
    from cogs.utils.database import *
    createDatabase(recreate=True)
    ```
5. At the main page of your Matsubo application, next to the Dyno formation, click on `Configure Dynos` and turn it on to run Matsubo!

That's all! :data:


## 2. Local PC (or other services)
If you want to run Matsubo on your local device or another hosting service, first install the necessary software (if you haven't yet):
1. Install [PostgreSQL](https://www.postgresql.org/download/) and a viewer (for example [pgAdmin](https://www.pgadmin.org/download/)).
2. Install `python` and `pip` (in case you haven't yet). Also ensure that you have `pipenv` installed with:  
    ```bash
    pip install pipenv
    ```
3. Open `pgAdmin` (or the other viewer you chose to use) and first do the initial settings (better use the default settings) to create a login access. Then, create a database with the name `matsubo`.

Then, follow these steps:
1. Download this repository and unzip it into a folder you like, or clone it with the following command:
    ```bash
    git clone https://github.com/makokaz/matsubo.git
    ```
2. Copy the file `example.env` from the folder `example/` into the main folder (same folder where `bot.py` is) and rename it to `.env`.
Open it and fill in the [API Keys](#api-keys).
3. Install all necessary package-requirements specified in the `Pipfile` by typing in a console:
    ```bash
    pipenv install
    ```
4. Activate your pipenv shell and initialize the postgres database. To do this, type
    ```bash
    pipenv shell
    pipenv run python
    ```
    then
    ```python
    from cogs.utils.database import *
    createDatabase(recreate=True)
    ```
5. To run Matsubo, simply type:
    ```bash
    pipenv run python bot.py
    ```

That's all! :data:


## API keys
In order to login to your bot account, Matsubo needs a `Discord Bot Token` (refer to [how to get a discord bot token](#how-to-get-a-discord-bot-token)).
- If you chose to host Matsubo on Heroku, you will be asked during deployment to set the API keys. Open the file [example.env](https://github.com/makokaz/matsubo/blob/main/examples/example.env) and simply copy all values you will be asked during deployment. If you will be asked for `BOT_TOKEN`, insert your Discord Bot Token you obtained from [how to get a discord bot token](#how-to-get-a-discord-bot-token).
- If you chose to follow the method on running Matsubo on a [Local PC](#2-local-PC-or-other-services), simply insert the `Discord Bot Token` in the file `.env` where you can find `BOT_TOKEN = XXX` (replace it with `XXX`).

## How to get a discord bot token
To get your Discord `BOT_TOKEN`, follow these steps:
1. Go to https://discord.com/developers/applications and click on `New Application`.
2. Do the initial settings (add a profile picture, ...). This is your Bot Developer page.
3. In the left panel, click on `Bot` and then on `Add Bot`.
4. Below *Token* click on `Copy` to copy your `BOT_TOKEN`.

In order to let the bot join to a Discord Server, on your Bot Developer page:
1. Click on `OAuth2` in the left panel and scroll down until you see the Scopes settings.
2. In Scopes, tick `bot`, and in the new bot permissions settings tick `Administrator`.
3. Copy the URL in Scopes and open it in another tab to proceed to invite Matsubo to your server.

# Matsubo commands
> In the following, substitute `REGION` with one of the following:  
> - Chubu
> - Chugoku
> - Hokkaido
> - Kansai
> - Kanto
> - Kyushu
> - Okinawa
> - Shikoku
> - Tohoku
- To subscribe a channel for where to post events, send a Discord message:
    ```
    .subscribe REGION
    ```
- To unsubscribe a region to a channel, type:
    ```
    .subscribe REGION
    ```
- To see all currently subscribed regions of a channel, type in that channel:
    ```
    .getsubscribedtopics
    ```
- The events will clutter automatically in the channel over the days. If you want to enforce doing it NOW, type:
    ```
    .scrap
    ```

Matsubo also has other commands. Type inside a channel
```
.help
```
to get an overview of all commands, and
```
.help COMMAND
```
to get help for a specific command (substitute `COMMAND` with the command-name, for example `scrap`).

# Structure
```sh
├── cogs/         # the bot functionality goes here
├── example/      # example files to help you set up the bot and how to add functionality
└── bot.py        # the main bot: handles the login process and how to load modules
```

# Contribute

> Due to the module structure when using Discord's "Cogs", additional functionality is easily implemented without changing the base code. (In fact, you just need to insert a file into the `cogs/` folder without touching the base code!).
> For example, you can copy the file [example_cog.py](https://github.com/makokaz/matsubo/blob/main/examples/example_cog.py) from `examples/` into the `cogs` folder to give the bot more functionality.
That's all, really!  
>  
> Refer to the [Discord Docs](https://discordpy.readthedocs.io/en/stable/) to learn the basic functionality of Discord bots.

If you want to contribute, check the current [issues](https://github.com/makokaz/matsubo/issues) and [discussions](https://github.com/makokaz/matsubo/discussions).

Here are a few ideas how you can contribute:
- Increase the number of sources (Facebook-events, university-websites, email-newsletters, ...)
- Fixing a broken source parser
- Adding more discord commands that fit the scheme
- Adding a website frontend to see all events in the database


# History
As an international student coming to Japan, I was very interested in experiencing Japanese Matsuri and other types of events.
Not only locally, but now in the corona pandemic many events are also held online.
However, for the same reason it has become increasingly more difficult to stay up to date with event details and many of them are cancelled last minute.

After missing many events I'd have loved to attend, the idea of Matsubo was born.
The name is a concatenation of the word 祭り ("Matsuri", a Japanese word for "festival" or "event") and "Bot".

Japan had a massive entry ban at the start of the pandemics 2020, prohibiting every student that aimed to study in Japan from entering the country.
Due to the lack of proper information and other mispread details, we international students organized ourselves in a Discord server.
This in the end resulted in using Discord as a front-end to summarize the event-details.

To this date, Matsubo still serves international students in Japan and helping them untie the chaos when it comes to events.

Even though Matsubo was originally designed for international students in Japan, this does not mean that it is exclusive to those, nor that it is only to be used in Japan.
With a few modifications it can serve anyone anywhere. :blush:


# How to support me
If you like my work and want to support me, simply buy me a coffee :coffee: :relieved:
<a href="https://www.buymeacoffee.com/makokaz" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;"></a>