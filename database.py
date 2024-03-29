from typing import Optional, List
import pymysql
from peewee import SqliteDatabase, Model, CharField, DateTimeField, AutoField, ForeignKeyField, BooleanField, \
    IntegerField, BitField, FloatField, MySQLDatabase, InternalError
import datetime
import os
from Util import logger

# This file mostly consists of different, quite identical, calls to the database, and as such functions look quite
# alike. For this reason, the "issues" with duplicates are ignored from this file on Code Climate.

# Initiation of database
if os.getenv('db_type') is not None and os.getenv('db_type').upper() == "MYSQL":
    while True:
        host = "localhost"
        if os.getenv("MARIADB_HOST"):
            host = os.getenv("MARIADB_HOST")
        elif os.getenv('db_host'):
            host = os.getenv('db_host')
        else:
            print("Database host is empty, using " + host + " as host...")

        user = "root"
        if os.getenv("MARIADB_USER"):
            user = os.getenv("MARIADB_USER")
        elif os.getenv('db_user'):
            user = os.getenv('db_user')
        else:
            print("Database user is empty, using " + user + " as user...")

        port = "3306"
        if os.getenv("MARIADB_PORT"):
            port = os.getenv("MARIADB_PORT")
        elif os.getenv('db_port'):
            port = os.getenv('db_port')
        else:
            print("Database port is empty, using " + port + " as port...")

        database_name = "gods"
        if os.getenv('MARIADB_DATABASE'):
            database_name = os.getenv('MARIADB_DATABASE')

        password = None
        if os.getenv("MARIADB_PASSWORD"):
            password = os.getenv("MARIADB_PASSWORD")
        elif os.getenv('db_pword'):
            password = os.getenv('db_pword')

        print("Connecting to database " + database_name + " on " + host + ":" + port + " as " + user + "...")

        db = MySQLDatabase(database_name, user=user, password=password, host=host,
                           port=int(port))

        # Check for possible connection issues to the db
        try:
            db.connection()
            break
        except Exception as e:
            if "Can't connect" in str(e):
                print("An error occured while trying to connect to the MySQL Database: " + str(e) + ". Trying again...")
            elif "Unknown database" in str(e):
                print("An error occured while trying to connect to the MySQL Database: " + str(e) +
                      ". Trying to create database...")
                try:
                    conn = pymysql.connect(host=host, user=user, password=password, port=int(port))
                    conn.cursor().execute('CREATE DATABASE ' + database_name)
                    conn.close()
                    print("Created Database!")
                    break
                except Exception as e:
                    print("An error occured while trying to create the gods Database: " + str(e) + ". Trying again...")
        except InternalError as e:
            print("An error occured while trying to use the MySQL Database: " + str(e) + ". Trying again...")
else:
    print("Database type is not set to MYSQL, using flatfile...")
    db = SqliteDatabase('./Gods.db', pragmas={'foreign_keys': 1})

# Constant variables
snowflake_max_length = 20  # It is currently 18, but max size of uint64 is 20 chars
discordtag_max_length = 37  # Max length of usernames are 32 characters, added # and the discrim gives 37
guildname_max_length = 100  # For some weird reason guild names can be up to 100 chars... whatevs lol
godname_max_length = 16  # Let's just keep godnames at 16 lul
description_max_length = 100  # why not lol


# --------------------------------------------------- GODS ---------------------------------------------------- #


# The Gods Table
class gods(Model):
    ID = AutoField()
    Guild = CharField(max_length=snowflake_max_length)
    Name = CharField(max_length=godname_max_length)
    Gender = CharField(null=True, max_length=19)
    Type = CharField(max_length=10)
    Mood = FloatField(null=True, default=0.0)
    Power = FloatField(default=1.0)
    Priest = IntegerField(null=True)
    InviteOnly = BooleanField(default=False)
    Description = CharField(null=True, max_length=description_max_length)
    CreationDate = DateTimeField(default=datetime.datetime.now())

    class Meta:
        database = db


# Adding new gods to the DB
# Do not typehint godtype, causes circular import
def newGod(guild: int, name: str, godtype: str, gender: Optional[str] = None) -> Optional[gods]:
    try:
        god = gods.create(Guild=guild, Name=name, Type=godtype, Gender=gender)
        return god
    except Exception as error:
        logger.logDebug("Error doing new marriage - " + str(error), "ERROR")
        return None


# See if a god already exists with that name in a guild
def getGodName(name: str, guild: int) -> Optional[gods]:
    query = gods.select().where((gods.Guild == str(guild)) & gods.Name.contains(str(name)))
    if query.exists():
        god = query.execute()
        return god[0]
    return None


# Get a God by ID
def getGod(godid: int) -> Optional[gods]:
    query = gods.select().where(gods.ID == godid)
    if query.exists():
        return query[0]
    return None


# Gets all Gods in a guild
def getGods(guildid: int) -> List[gods]:
    query = gods.select().where(gods.Guild == str(guildid)).order_by(gods.Power.desc())
    return query


# Gets top 50 Gods globally
def getGodsGlobal() -> List[gods]:
    query = gods.select().order_by(gods.Power.desc()).limit(50)
    return query


# Get number of Gods, globally
def getGodsGlobalCount() -> int:
    return gods.select().count()


# Disband a God
def disbandGod(godid: int) -> bool:
    god = gods.select().where(gods.ID == godid)
    query = god[0].delete_instance()
    if query == 1:
        return True
    return False


# Set a priest for a God
def setPriest(godid: int, believerid: Optional[int]) -> None:
    query = gods.update(Priest=believerid).where(gods.ID == godid)
    query.execute()


# Set a description for a God
def setDesc(godid: int, desc: str) -> None:
    query = gods.update(Description=desc).where(gods.ID == godid)
    query.execute()


# Set a type for a God
# Do not typehint godtype, causes circular import
def setType(godid: int, godtype: str) -> None:
    query = gods.update(Type=godtype).where(gods.ID == godid)
    query.execute()


# Set a gender for a God
def setGender(godid: int, gender: str) -> None:
    query = gods.update(Gender=gender).where(gods.ID == godid)
    query.execute()


# Set a mood for a God
def setMood(godid: int, mood: float) -> None:
    query = gods.update(Mood=mood).where(gods.ID == godid)
    query.execute()


# Toggle access (inviteonly)
def toggleAccess(godid: int) -> bool:
    god = getGod(godid)

    access = True
    if god.InviteOnly:
        access = False

    query = gods.update(InviteOnly=access).where(gods.ID == godid)
    query.execute()
    return access


# Subtract mood and power on all Gods
def doGodsFalloff(falloffMood: float, falloffPower: float) -> None:
    query = gods.update(Power=(gods.Power - falloffPower)).where(gods.Power > (0.0 + falloffPower))
    query.execute()

    query = gods.update(Mood=(gods.Mood - falloffMood)).where(gods.Mood > (-100.0 + falloffMood))
    query.execute()


# --------------------------------------------------- BELIEVERS ---------------------------------------------------- #


# The Believers Table
class believers(Model):
    ID = AutoField()
    God = ForeignKeyField(gods, on_delete="CASCADE")
    UserID = CharField(max_length=snowflake_max_length)
    PrayerPower = FloatField(default=1)
    Prayers = CharField(max_length=5, default="0")
    PrayDate = DateTimeField(default=datetime.datetime.now())
    JoinDate = DateTimeField(default=datetime.datetime.now())

    class Meta:
        database = db


# Adding new believers to the DB
def newBeliever(userid: int, god: gods) -> Optional[believers]:
    try:
        believer = believers.create(UserID=userid, God=god)
        return believer
    except Exception as error:
        logger.logDebug("Error doing new believer - " + str(error), "ERROR")
        return None


# Whether a believer already believes in a god on that guild, if yes, returns believer
def getBeliever(userid: int, guild: int) -> Optional[believers]:
    query = believers.select().join(gods).where(gods.Guild == str(guild)).where(believers.UserID == str(userid))
    if query.exists():
        return query[0]
    return None


# Whether a believer already believes in a god on that guild, if yes, returns believer
def getBelieverByID(believerID: int) -> Optional[believers]:
    query = believers.select().where(believers.ID == believerID)
    if query.exists():
        return query[0]
    return None


# Get top 50 believers, globally
def getBelieversGlobal() -> List[believers]:
    query = believers.select().sort(believers.PrayerPower).limit(50)
    if query.exists():
        return query
    return []


# Get number of believers, globally
def getBelieversGlobalCount() -> int:
    return believers.select().count()


# Leave a god
def leaveGod(userid: int, guild: int) -> bool:
    believer = getBeliever(userid, guild)
    query = believer.delete_instance()
    if query == 1:
        return True
    return False


# Leave a god, by ID
def leaveGodID(believerid: int) -> bool:
    believer = getBelieverByID(believerid)
    query = believer.delete_instance()
    if query == 1:
        return True
    return False


# Get a God's believers, using name and guild
def getBelievers(godname: str, guild: int) -> List[believers]:
    query = believers.select().join(gods).where((gods.Guild == str(guild)) & (gods.Name.contains(str(godname))))
    if query.exists():
        return query
    return []


# Get a God's believers, using ID
def getBelieversByID(godid: int) -> List[believers]:
    query = believers.select().join(gods).where(gods.ID == godid)
    if query.exists():
        return query
    return []

# Believer set to another god
def setGod(believerid: int, godid: int) -> None:
    query = believers.update(God=godid).where(believers.ID == believerid)
    query.execute()


# Prays
def pray(believerInput: believers) -> None:
    query = believers.update(PrayDate=datetime.datetime.now(), PrayerPower=(believerInput.PrayerPower + 1),
                             Prayers=str(int(believerInput.Prayers) + 1)).where(believers.ID == believerInput.ID)
    query.execute()

    query = gods.update(Power=(believerInput.God.Power + 1)).where(gods.ID == believerInput.God.ID)
    query.execute()

    moodraise = 10
    query = gods.update(Mood=(believerInput.God.Mood + moodraise)).where((gods.ID == believerInput.God.ID) &
                                                                         (gods.Mood < (100 - moodraise)))
    query.execute()


# Subtract prayerpower on all believers
def doBelieverFalloffs(falloffPrayerPower: float) -> None:
    query = believers.update(PrayerPower=(believers.PrayerPower - falloffPrayerPower)).where(believers.PrayerPower >
                                                                                             (0 + falloffPrayerPower))
    query.execute()


# Subtract prayerpower from a believer
def subtractPrayerPower(believerid: int, power: float) -> None:
    query = believers.update(PrayerPower=(believers.PrayerPower - power)).where(believers.ID == believerid)
    query.execute()


# --------------------------------------------------- MARRIAGES ---------------------------------------------------- #


# The Marriages Table
class marriages(Model):
    ID = AutoField()
    God = ForeignKeyField(gods, on_delete="CASCADE")
    Believer1 = ForeignKeyField(believers, on_delete="CASCADE")
    Believer2 = ForeignKeyField(believers, on_delete="CASCADE")
    LoveDate = DateTimeField(default=datetime.datetime.now())
    MarriageDate = DateTimeField(default=datetime.datetime.now())

    class Meta:
        database = db


# Adding new marriages to the DB
def newMarriage(believer1: believers, believer2: believers, god: gods) -> Optional[marriages]:
    try:
        marriage = marriages.create(God=god, Believer1=believer1, Believer2=believer2)
        return marriage
    except Exception as error:
        logger.logDebug("Error doing new marriage - " + str(error), "ERROR")
        return None


# Gets all Marriages in a guild
def getMarriages(guild: int) -> List[marriages]:
    query = marriages.select().join(gods).where(gods.Guild == str(guild)).order_by(marriages.LoveDate.desc())
    return query


# Gets top 50 Marriages globally
def getMarriagesGlobal() -> List[marriages]:
    query = marriages.select().order_by(marriages.LoveDate.desc()).limit(50)
    return query


# Get someone's marriage
def getMarriage(believerid: int) -> Optional[marriages]:
    query = marriages.select().where((marriages.Believer1 == believerid) | (marriages.Believer2 == believerid))
    if query.exists():
        return query[0]
    return None


# Delete a marriage
def deleteMarriage(marriageid: int) -> bool:
    marriage = marriages.select().where(marriages.ID == marriageid)
    if marriage.exists():
        query = marriage[0].delete_instance()
        if query == 1:
            return True
    return False


# Show someone love
def doLove(marriageid: int) -> None:
    date = datetime.datetime.now()

    query = marriages.update(LoveDate=date).where(marriages.ID == marriageid)
    query.execute()


# --------------------------------------- Offers [Invitations / PriestOffers] --------------------------------------- #


# The Offers Table
class offers(Model):
    ID = AutoField()
    Type = BitField()
    God = ForeignKeyField(gods, on_delete="CASCADE")
    UserID = CharField(max_length=snowflake_max_length)
    CreationDate = DateTimeField(default=datetime.datetime.now())

    class Meta:
        database = db


# Adding new invite to the DB
def newInvite(godid: int, userid: int) -> Optional[offers]:
    try:
        invite = offers.create(God=godid, Type=1, UserID=userid)
        return invite
    except Exception as error:
        logger.logDebug("Error doing new invite - " + str(error), "ERROR")
        return None


# Get someone's invite for a god
def getInvite(userid: int, godid: int) -> Optional[offers]:
    query = offers.select().where((offers.Type == 1) & (offers.UserID == str(userid)) & (offers.God == godid))
    if query.exists():
        return query[0]
    return None


# Clears expired invites
def clearExpiredInvites() -> None:
    today = datetime.datetime.today() - datetime.timedelta(days=1)
    query = offers.delete().where((offers.Type == 1) & (offers.CreationDate < today))
    query.execute()


# Delete an invite // used after an invite has been used
def deleteInvite(offerid: int) -> bool:
    invite = offers.select().where((offers.Type == 1) & (offers.ID == offerid))
    if invite.exists():
        query = invite[0].delete_instance()
        if query == 1:
            return True
    return False


# Adding new priest offer to the DB
def newPriestOffer(godid: int, userid: int) -> Optional[offers]:
    try:
        priestoffer = offers.create(God=godid, Type=2, UserID=userid)
        return priestoffer
    except Exception as error:
        logger.logDebug("Error doing new priestoffer - " + str(error), "ERROR")
        return None


# Get someone's priest offer for a god
def getPriestOffer(godid: int) -> Optional[offers]:
    query = offers.select().where((offers.Type == 2) & (offers.God == godid))
    if query.exists():
        return query[0]
    return None


# Delete a priest offer // used after a priest offer has been used
def deletePriestOffer(offerid: int) -> bool:
    priestoffer = offers.select().where((offers.Type == 2) & (offers.ID == offerid))
    if priestoffer.exists():
        query = priestoffer[0].delete_instance()
        if query == 1:
            return True
    return False


# Get and clear old priest offers
def clearOldPriestOffers() -> List[offers]:
    date = datetime.datetime.today() - datetime.timedelta(days=1)
    priestoffers = offers.select().where((offers.Type == 2) & (offers.CreationDate < date))
    if priestoffers.exists():
        priestoffers = priestoffers.execute()
        query = offers.delete().where((offers.Type == 2) & (offers.CreationDate < date))
        query.execute()
        return priestoffers
    return []


# ------------------------------------------ CUSTOM CONFIGS FOR GUILDS ------------------------------------------ #


# The Guilds Table
class guilds(Model):
    ID = AutoField()
    Guild = CharField(max_length=snowflake_max_length)
    Prefix = CharField(null=True, max_length=6)
    GodRoles = BooleanField(default=False)

    class Meta:
        database = db


# Adding new guild to the DB
def newGuild(guildid: int) -> Optional[guilds]:
    try:
        guild = guilds.create(Guild=guildid)
        return guild
    except Exception as error:
        logger.logDebug("Error doing new guild - " + str(error), "ERROR")
        return None


# Get a guild from the DB
def getGuild(guildid: int) -> Optional[guilds]:
    query = guilds.select().where(guilds.Guild == str(guildid))
    if query.exists():
        return query[0]
    return None


# Set a prefix for a guild
def setPrefix(guildconfigid: int, prefix: str) -> None:
    query = guilds.update(Prefix=prefix).where(guilds.ID == guildconfigid)
    query.execute()


# -------------------------------------------------- SETUP OF TABLES ------------------------------------------------- #


def create_tables():
    with db:
        db.create_tables([gods, believers, marriages, offers, guilds])


create_tables()
