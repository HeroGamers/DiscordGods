from peewee import SqliteDatabase, Model, CharField, DateTimeField, AutoField, ForeignKeyField
import datetime
from Util import logger

db = SqliteDatabase('./Gods.db')

snowflake_max_length = 20  # It is currently 18, but max size of uint64 is 20 chars
discordtag_max_length = 37  # Max length of usernames are 32 characters, added # and the discrim gives 37
guildname_max_length = 100  # For some weird reason guild names can be up to 100 chars... whatevs lol
godname_max_length = 16 # Let's just keep godnames at 16 lul
description_max_length = 100 # why not lol


# --------------------------------------------------- GODS ---------------------------------------------------- #


# The Gods Table
class gods(Model):
    ID = AutoField()
    Guild = CharField(max_length=snowflake_max_length)
    Name = CharField(max_length=godname_max_length)
    Gender = CharField(null=True, max_length=15)
    Type = CharField(max_length=10)
    Verbosity = CharField(null=True, max_length=3)
    Priest = CharField(null=True, max_length=snowflake_max_length)
    Description = CharField(null=True, max_length=description_max_length)
    CreationDate = DateTimeField(default=datetime.datetime.now())

    class Meta:
        database = db


# Adding new gods to the DB
def newGod(guild, name, type, gender=None):
    try:
        god = gods.create(Guild=guild, Name=name, Type=type, Gender=gender, Verbosity=50)
        return god
    except Exception as e:
        logger.logDebug("Error doing new marriage - " + str(e), "ERROR")


# Get a God's believers, using name and guild
def getBelievers(godname, guild):
    query = believers.select().join(gods).where(gods.Guild.contains(str(guild)) & gods.Name.contains(str(godname)))
    if query.exists():
        return True
    return False


# Get a God's believers, using ID
def getBelieversByID(god):
    query = believers.select().join(gods).where(gods.ID.contains(str(god)))
    if query.exists():
        return query
    return False


# See if a god already exists with that name in a guild
def godExists(name, guild):
    query = gods.select().where((gods.Guild.contains(str(guild)) & gods.Name.contains(str(name))))
    if query.exists():
        god = query.execute()
        return god[0]
    return False


# --------------------------------------------------- BELIEVERS ---------------------------------------------------- #


# The Believers Table
class believers(Model):
    ID = AutoField()
    God = ForeignKeyField(gods)
    UserID = CharField(max_length=snowflake_max_length)
    PrayDate = DateTimeField(default=datetime.datetime.now())
    JoinDate = DateTimeField(default=datetime.datetime.now())

    class Meta:
        database = db


# Adding new gods to the DB
def newBeliever(userid, god):
    try:
        believer = believers.create(UserID=userid, God=god)
        return believer
    except Exception as e:
        logger.logDebug("Error doing new marriage - " + str(e), "ERROR")


# Whether a believer already believes in a god on that guild
def isBeliever(userid, guild):
    query = believers.select().join(gods).where(gods.Guild.contains(str(guild))).where(believers.UserID.contains(str(userid)))
    if query.exists():
        return True
    return False


# Leave a god
def leaveGod(userid, guild):
    believer = believers.select().join(gods).where(gods.Guild.contains(str(guild))).where(believers.UserID.contains(str(userid)))
    query = believer[0].delete_instance()
    if query == 1:
        return True
    return False


# --------------------------------------------------- MARRIAGES ---------------------------------------------------- #


# The Marriages Table
class marriages(Model):
    ID = AutoField()
    God = ForeignKeyField(gods)
    Believer1 = ForeignKeyField(believers)
    Believer2 = ForeignKeyField(believers)
    LoveDate = DateTimeField(default=datetime.datetime.now())
    MarriageDate = DateTimeField(default=datetime.datetime.now())

    class Meta:
        database = db


# Adding new marriages to the DB
def newMarriage(believer1, believer2, god):
    try:
        marriage = marriages.create(God=god, Believer1=believer1, Believer2=believer2)
        return marriage
    except Exception as e:
        logger.logDebug("Error doing new marriage - " + str(e), "ERROR")


# -------------------------------------------------- SETUP OF TABLES ------------------------------------------------- #


def create_tables():
    with db:
        db.create_tables([gods, believers, marriages])


create_tables()
