# TelegramCompanion

 ![](https://img.shields.io/github/forks/nitanmarcel/TelegramCompanion.svg?style=social) ![](https://img.shields.io/github/stars/nitanmarcel/TelegramCompanion.svg?style=social) ![](https://img.shields.io/github/watchers/nitanmarcel/TelegramCompanion.svg?style=social)

> TelegramCompanion is simple userbot for Telegram to make your time spent on telegram more enjoyable. It runs in the background of your PC or server and gives you some new and usefull features

## Table of Contents

-   [Installation](#Installation)
-   [Setup](#Setup)
-   [Features](#Features)
-   [Plugins](#Plugins)
-   [Contributing](#Contributing)
-   [Support](#Support)
-   [Thanks](#Thanks)
-   [Donate](#Donate)
-   [License](#License)

## Installation

-   Install python3.7 and python3.7-dev. python3.6 and python3-dev will work too:

```
sudo apt install python3.7 python3.7-dev
```

![Python Installation](/src/python.gif?raw=true)


-   Clone this repo by running:

```shell
git clone https://github.com/nitanmarcel/TelegramCompanion
```

-   Install all the requirements using pip3

```shell
pip3 install -r requirements.txt
```

![Requirements Installation](/src/requirements.gif?raw=true)

---

# Setup

#### First you need to create a Postgres database. You can create one following the instructions below.

* Install Postgres.

`sudo apt-get update && sudo apt-get install postgresql`

* Change to a Postgres user.

`sudo su - Postgres`

* Create a new user for your database. Replace YOUR_USER with the desired user name.

`createuser -P -s -e YOUR_USER`

* Create a new database table. Change YOUR_USER with the user you used above and YOUR_DB_NAME the desired database name.

`createdb -O YOUR_USER YOUR_DB_NAME`

* Change YOUR_USER and YOUR_DB_NAME with the user and database name you used above.

`psql YOUR_DB_NAME -h YOUR_HOST YOUR_USER`

This will create a database and you can connect to it using the terminal. But we will use it to create a URL that you'll use in the config.env file. By default, your hostname should be 0.0.0.0 and the port should be 5432.

Now build your database URL:

`postgres://username:password@hostname:port/db_name`


#### Now before starting the companion you have to configure it as per your requirements.
> -   Create a config.env file. Follow the example from sample.config.env.
> -   Write the config values explained below in the created file.

#### The available config values are:

> -   `APP_ID` = (required) Your telegram app id from <https://my.telegram.org/apps>
>
> -   `APP_HASH` = (required) Your telegram app hash from <https://my.telegram.org/apps>
>
> -   `DB_URI` = (required) Your postgress database url. Leave empty to disable the modules that use it
>
> -   `CMD_HANDLER` = (optional) You can set it to a custom symbol that will trigger any commands. For example: if you want to use /ping instead of .ping set it to /
>
>
> -   `SESSION_NAME` = (optional) Custom session name. Leave empty to use the default session name
>
> -   `STATS_TIMER` = (optional) Set the stats update time in seconds. Set it to 0 to completly disable stats.
>     - **WARNING** : If enabled the companion will not respond to your commands for 5 seconds when starting the bot for the first time
>
> -   `SUBPROCESS_ANIM` = (optional) (optional) Set to True if you want to enable animations when using a terminal command.
>     -   **WARNING** : When executing commands with long outputs it might trigger a flood wait that will restrict you from editing any send messages for a given time. Usualy just 250 seconds."
>
> -   `BLOCK_PM` = (optional) Set to True if you want to block new PMs. New PMs will be deleted and user blocked
>
> -   `NOPM_SPAM` = (optional) Set to True if you want to block users that are spamming your PMs.
>
> -   `PROXY_TYPE` = (optional) Your proxy type HTTP/SOCKS4/SOCKS5. Leave empty to disable proxy.
>
> -   `HOST` = (optional) The host of the used proxy.
>
> -   `PORT` = (optional) The port of the used proxy.
>
> -   `USERNAME` = (optional) The username of the used proxy. (If any)
>
> -   `PASSWORD` = (optional) The password of the used proxy. (If any)
>
> -   `ENABLE_SSH` = (optional) Set True if you want to execute or upload from a ssh server"
>
> -   `SSH_HOSTNAME` = (optional)  (optional) The hostname or address to connect to.
>
> -   `SSH_PORT` = (optional)  (optional) The port number to connect to.
>
> -   `SSH_USERNAME` = (optional)  (optional) Username to authenticate as on the server.
>
> -   `SSH_PASSWORD` = (optional)  (optional) The password to use for client password authentication
>
> -   `SSH_PASSPHRASE` = (optional)  (optional) The passphrase for your ssh connection.
>
> -   `SSH_KEY` = (optional)   (optional) The private key which will be used to authenticate this client"


---
# Features

Telegram Companion brings some small improvements and new features to any Telegram Client

You can some features using a command. Others are enabled from the config file and they work in the background.
Every command follows tgbot's syntax but instead of `/<command>` we use `.<command>` (This can be changed from the config.env file)

You can use .help to get all the available commands and what they can do


## Plugins

Plugins allow users to create their own plugins in a official [repo](https://github.com/nitanmarcel/TgCompanionPlugins) or on their own repo, so the user can install them using `python3 -m tg_companion.pluginmanager --install` `<pluginname>` or `python3 -m tg_companion.pluginmanager` `<githubusername>` `<reponame>` `pluginname`.

To uninstall a plugin run `python3 -m tg_companion.pluginmanager --remove` `<pluginname>`

Check [TgCompanionPlugins](https://github.com/nitanmarcel/TgCompanionPlugins) repo for more informations.
## Contributing

Feel free to open an issue (or even better, send a **Pull Request**) for improving the bot's code. **Contributions** are very welcome !! :smiley:

Note that the PR needs to reach a certain level of engagement before it gets merged. This way we keep the quality of the bot intact. Also, we won't accept any PR that uses an external API key to work. PR to [TgCompanionPlugins](https://github.com/nitanmarcel/TgCompanionPlugins) instead

When making a new pull request that brings a new feature make sure you use @client.CommandHandler(..) instead of the default @client.on(event)

For example:

```
@client.CommandHandler(outgoing=True, command="your_command")
def my_function(event):
```



This method is an alternative for `client.on()` which uses the same arguments but with some exceptions
```
  Optional Args:
      command (str):
          If set to any str instance the decorated function will only work if
                  the message matches the command handler symbol ( default "." ) + the word/regex in the command argument
                  if the command is not set or None it will execute the decorated function when a message event is triggered

    allow_edited (bool):
          If set True the command will also work when the message is edited.
```

You can add an help text for a command by adding a docstring:


```
@client.CommandHandler(outgoing=True, command="example")
async def example(event):
    """
    **What the function does**
        __Args, Usage or Example:__
            `<arg>` - **(optional/required)** argument description
    """
```
## Support

You can ask for support or report a bug in our telegram [group](https://t.me/tgcompanion)


## Thanks
Thanks to everyone who helped me with ideas and with the project. Including @Yash-Garg for letting me host this project on his private repo, @baalajimaestro for the idea that gave birth to this user-bot. (Also check his [userbot](https://github.com/baalajimaestro/Telegram-UserBot)). And not last @sicrs for all the support he gave me.

## Donate
It took a lot of work and white nights for me to do this user-bot and make it look less like another Bot that you control and more a part of your telegram client.
I know is not perfect but I'm trying my best and if you enjoy this UserBot and you want to help me you can buy me a beer using [PayPal](https://www.paypal.me/marcelalexandrunitan). Any donation will help. Thanks and I hope you enjoy my UserBot


## License
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

This code is licensed under [GPL v3](LICENSE).
