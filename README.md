<h1 align="center">Gods - Religion on Discord</h1>
<div align="center">

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/19876a2da2964fa9b118274838d9e274)](https://www.codacy.com/manual/Fido2603/DiscordGods?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Fido2603/DiscordGods&amp;utm_campaign=Badge_Grade)
[![Maintainability](https://api.codeclimate.com/v1/badges/fd768438ad9d66b23cfb/maintainability)](https://codeclimate.com/github/Fido2603/DiscordGods/maintainability)
[![Build Status](https://travis-ci.com/Fido2603/DiscordGods.svg?branch=master)](https://travis-ci.com/Fido2603/DiscordGods)
[![Made With Python 3.6.6](https://img.shields.io/badge/Python-3.6.6-blue.svg)](https://www.python.org/downloads/release/python-366/)
[![Made With discord.py 1.2.2](https://img.shields.io/badge/discord.py-1.3.3-blue.svg)](https://github.com/Rapptz/discord.py)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://raw.githubusercontent.com/Fido2603/DiscordGods/master/LICENSE)
</div>

The legendary [Minecraft Plugin by DogOnFire](https://github.com/DogOnFire/Gods), ported into Discord. Gods bring religion to your Discord Server. Members can now get married, become a priest and pray to their favorite God. Can your God climb the ranks and become the most powerful religion?
> A God is an entity that exist because someone has chosen to believe in it.

___

<div align="center">

[![Gods Banner](https://raw.githubusercontent.com/Fido2603/DiscordGods/master/docs/indexfiles/img/Gods-banner.png)](https://discordapp.com/oauth2/authorize?scope=bot&client_id=180405652605239296)
</div>

## Adding Gods to your server
You can invite Gods to your servers, and thus enable your members to create their very own religions, get married and more, using this invite link:

<div align="center">
<h3>Invite Gods</h3>

[![Invite Gods](https://img.shields.io/static/v1.svg?label=Invite%20Gods&message=No%20Permissions&color=7289DA&stile=flat&logo=discord&logoColor=7289DA&labelColor=2C2F33)](https://discordapp.com/oauth2/authorize?scope=bot&client_id=180405652605239296)
</div>

## Commands & Features
### Key Features
-   [x] Create Gods
-   [x] Get married with that special someone
-   [x] Miscellaneous commands with GIF's, like hugging
-   [x] Global Leaderboards - become the most powerful religion globally!

### Commands
| Category                 | Command             | Aliases                               | Description                                          | Who can use                                              | Usage                                            |
|--------------------------|---------------------|---------------------------------------|------------------------------------------------------|----------------------------------------------------------|--------------------------------------------------|
| Administrator Management | /g forcedeletegod   | deletegod, removegod, forcedisbandgod | Removes a religion from the server.                  | Server Administrator                                     | /g forcedeletegod 'GodName'                      |
| Administrator Management | /g forcedescription | forcedesc, admindesc                  | Forces a description for a religion.                 | Server Administrator                                     | /g forcedescription 'GodName' 'Description'      |
| Administrator Management | /g forcesetgender   | forcegenderset, forcegender           | Set the gender of a God to something else.           | Server Administrator                                     | /g forcesetgender 'GodName' 'Gender'             |
| Administrator Management | /g forcesetpriest   | forcepriest, adminpriest              | Set the priest of a God.                             | Server Administrator                                     | /g forcesetpriest 'GodName' 'User ID or Mention' |
| Administrator Management | /g forcesettype     | forcetypeset, forcetype               | Set the type of a God to something else.             | Server Administrator                                     | /g forcesettype 'GodName' 'Type'                 |
| Administrator Management | /g setprefix        | prefix                                | Sets a custom prefix for the bot on the server.      | Server Administrator                                     | /g setprefix 'Prefix'                            |
| Believer                 | /g divorce          | leave_with_the_kids                   | Generates a new captcha for a user                   | Everyone who is married                                  | /g divorce                                       |
| Believer                 | /g join             | enter                                 | Generates a new captcha for a user                   | Everyone who is not believing in a God                   | /g join 'GodName'                                |
| Believer                 | /g leave            | yeet                                  | Generates a new captcha for a user                   | Everyone who is believing in a God                       | /g leave                                         |
| Believer                 | /g marry            | propose                               | Marry that special someone.                          | Everyone who is believing in a God, and isn't married    | /g marry 'User ID or Mention'                    |
| Believer                 | /g no               | deny, decline, reject                 | Reject a proposal from your God.                     | Everyone who has an Offer from their God                 | /g no                                            |
| Believer                 | /g pray             | p                                     | Pray to your God.                                    | Everyone who is believing in a God                       | /g pray                                          |
| Believer                 | /g yes              | accept                                | Accept a proposal from your God.                     | Everyone who has an Offer from their God                 | /g yes                                           |
| Bot Commands             | /g botinfo          | bot                                   | Gets information about the bot                       | Everyone                                                 | /g botinfo                                       |
| Bot Commands             | /g botinvite        | invitebot, addbot                     | Sends an OAuth2 link to add the bot                  | Everyone                                                 | /g botinvite                                     |
| Bot Commands             | /g listcogs         | cogs                                  | Lists all the cogs.                                  | Bot Owner                                                | /g listcogs                                      |
| Bot Commands             | /g loadcog          | loadextension                         | Loads a cog.                                         | Bot Owner                                                | /g loadcog                                       |
| Bot Commands             | /g source           | code, sourcecode                      | View and/or help with the source code of Gods.       | Everyone                                                 | /g source                                        |
| Bot Commands             | /g support          |                                       | Get help and support regarding the bot.              | Everyone                                                 | /g support                                       |
| Bot Commands             | /g unloadcog        | unloadextension                       | Unloads a cog.                                       | Bot Owner                                                | /g unloadcog                                     |
| Information              | /g globallist       | globalgods, glist, ggods              | Lists the top Gods globally.                         | Everyone                                                 | /g globallist                                    |
| Information              | /g globalmarriages  | gmarriages, globalmarrylist           | Lists the most loving married couples globally.      | Everyone                                                 | /g globalmarriages                               |
| Information              | /g info             | godinfo, i                            | Gets information about a God.                        | Everyone                                                 | /g info 'GodName'                                |
| Information              | /g list             | gods                                  | Lists the top Gods on the server.                    | Everyone                                                 | /g list                                          |
| Information              | /g marriages        | not_singles_like_you, marrylist       | Lists the most loving married couples on the server. | Everyone                                                 | /g marriages                                     |
| Miscellaneous            | /g getcolor         | getColor, getcolour, getColour        | Gets information about a color from its HEX code.    | Everyone                                                 | /g getcolor 'HEX Code'                           |
| Miscellaneous            | /g hug              |                                       | Hugs someone, awhh.                                  | Everyone who believes in a God, and has 0.5 Prayer Power | /g hug 'User ID or Mention'                      |
| Miscellaneous            | /g love             | kiss                                  | Shows your special someone that you love them.       | Everyone who is married                                  | /g love                                          |
| Religion Management      | /g access           | lock, open                            | Set your religion as open or invite only.            | Everyone who is a Priest for their God                   | /g access                                        |
| Religion Management      | /g create           | newgod                                | Creates a new God.                                   | Everyone who is not believing in a God                   | /g create 'GodName'                              |
| Religion Management      | /g description      | desc                                  | Sets a description for your religion.                | Everyone who is a Priest for their God                   | /g description 'Description'                     |
| Religion Management      | /g invite           | inv                                   | Invite someone to your religion.                     | Everyone who is a Priest for their God                   | /g invite 'User ID or Mention'                   |
| Religion Management      | /g setgender        | genderset, gender                     | Set the gender of your God to something else.        | Everyone who is a Priest for their God                   | /g gender 'Gender'                               |
| Religion Management      | /g settype          | typeset, type                         | Set the type of your God to something else.          | Everyone who is a Priest for their God                   | /g type 'Type'                                   |
| No Category              | /gods help          |                                       | Sends a help message, listing all the commands.      | Everyone                                                 | /g help                                          |

### Leaving Feedback // Getting Support
I would be very happy if you could give some feedback on the bot, after you have tried it out. If there're issues with the bot, then you can also reach out to me on my server, [Treeland](https://discord.gg/PvFPEfd).

## Running Gods locally
1.  Extract the code
2.  Install the requirements (requirements.txt)
3.  Copy the configexample.py and rename it to config.py
4.  Fill out the config
5.  Run bot.py, and enjoy

___
<div align="center">

[![Treeland Discord Server](https://discordapp.com/api/guilds/221996778092888065/widget.png?style=banner3)](https://discord.gg/PvFPEfd)
</div>
