from peewee import SqliteDatabase, Model, CharField, DateTimeField, AutoField, ForeignKeyField, BooleanField, \
    IntegerField, BitField, FloatField
import datetime
from Util import logger

db = SqliteDatabase('./Gods.db')

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
def newGod(guild, name, type, gender=None):
    try:
        god = gods.create(Guild=guild, Name=name, Type=type, Gender=gender)
        return god
    except Exception as e:
        logger.logDebug("Error doing new marriage - " + str(e), "ERROR")
        return False


# Get a God's believers, using name and guild
def getBelievers(godname, guild):
    query = believers.select().join(gods).where((gods.Guild == str(guild)) & (gods.Name.contains(str(godname))))
    if query.exists():
        return query
    return False


# Get a God's believers, using ID
def getBelieversByID(godid):
    query = believers.select().join(gods).where(gods.ID == godid)
    if query.exists():
        return query
    return False


# See if a god already exists with that name in a guild
def getGodName(name, guild):
    query = gods.select().where((gods.Guild == str(guild)) & gods.Name.contains(str(name)))
    if query.exists():
        god = query.execute()
        return god[0]
    return False


# Get a God by ID
def getGod(godid):
    query = gods.select().where(gods.ID == godid)
    if query.exists():
        return query[0]
    return False


# Gets all Gods in a guild
def getGods(guild):
    query = gods.select().where(gods.Guild == str(guild)).order_by(gods.Power)
    return query


# Gets top 50 Gods globally
def getGodsGlobal():
    query = gods.select().order_by(gods.Power).limit(50)
    return query


# Disband a God
def disbandGod(godid):
    god = gods.select().where(gods.ID == godid)
    query = god[0].delete_instance()
    if query == 1:
        return True
    return False


# Set a priest for a God
def setPriest(godid, believerid):
    query = gods.update(Priest=believerid).where(gods.ID == godid)
    query.execute()


# Set a description for a God
def setDesc(godid, desc):
    query = gods.update(Description=desc).where(gods.ID == godid)
    query.execute()


# Set a type for a God
def setType(godid, type):
    query = gods.update(Type=type).where(gods.ID == godid)
    query.execute()


# Set a gender for a God
def setGender(godid, gender):
    query = gods.update(Gender=gender).where(gods.ID == godid)
    query.execute()


# Set a mood for a God
def setMood(godid, mood):
    query = gods.update(Mood=mood).where(gods.ID == godid)
    query.execute()


# Toggle access (inviteonly)
def toggleAccess(godid):
    god = getGod(godid)

    access = True
    if god.InviteOnly:
        access = False

    query = gods.update(InviteOnly=access).where(gods.ID == godid)
    query.execute()
    return access


# Subtract mood and power on all Gods
def doGodsFalloff(falloffMood, falloffPower):
    query = gods.update(Power=(gods.Power - falloffPower)).where(gods.Power > (0.0 + falloffPower))
    query.execute()

    query = gods.update(Mood=(gods.Mood - falloffMood)).where(gods.Mood > (-100.0 + falloffMood))
    query.execute()


# --------------------------------------------------- BELIEVERS ---------------------------------------------------- #


# The Believers Table
class believers(Model):
    ID = AutoField()
    God = ForeignKeyField(gods)
    UserID = CharField(max_length=snowflake_max_length)
    PrayerPower = FloatField(default=1)
    Prayers = CharField(max_length=5, default="0")
    PrayDate = DateTimeField(default=datetime.datetime.now())
    JoinDate = DateTimeField(default=datetime.datetime.now())

    class Meta:
        database = db


# Adding new believers to the DB
def newBeliever(userid, god):
    try:
        believer = believers.create(UserID=userid, God=god)
        return believer
    except Exception as e:
        logger.logDebug("Error doing new believer - " + str(e), "ERROR")
        return False


# Whether a believer already believes in a god on that guild, if yes, returns believer
def getBeliever(userid, guild):
    query = believers.select().join(gods).where(gods.Guild == str(guild)).where(believers.UserID == str(userid))
    if query.exists():
        return query[0]
    return False


# Whether a believer already believes in a god on that guild, if yes, returns believer
def getBelieverByID(believerID):
    query = believers.select().where(believers.ID == believerID)
    if query.exists():
        return query[0]
    return False


# Get top 50 believers, globally
def getBelieversGlobal():
    query = believers.select().sort(believers.PrayerPower).limit(50)
    if query.exists():
        return query
    return False


# Get number of believers, globally
def getBelieversGlobalCount():
    return believers.select().count()


# Leave a god
def leaveGod(userid, guild):
    believer = getBeliever(userid, guild)
    query = believer.delete_instance()
    if query == 1:
        return True
    return False


# Believer set to another god
def setGod(believerid, godid):
    query = believers.update(God=godid).where(believers.ID == believerid)
    query.execute()


# Prays
def pray(believerInput):
    query = believers.update(PrayDate=datetime.datetime.now(), PrayerPower=(believerInput.PrayerPower+1),
                             Prayers=str(int(believerInput.Prayers)+1)).where(believers.ID == believerInput.ID)
    query.execute()

    query = gods.update(Power=(believerInput.God.Power+1)).where(gods.ID == believerInput.God.ID)
    query.execute()

    moodRaise = 10
    query = gods.update(Mood=(believerInput.God.Mood+moodRaise)).where((gods.ID == believerInput.God.ID) &
                                                                       (gods.Mood < (100 - moodRaise)))
    query.execute()


# Subtract prayerpower on all believers
def doBelieverFalloffs(falloffPrayerPower):
    query = believers.update(PrayerPower=(believers.PrayerPower - falloffPrayerPower)).where(believers.PrayerPower > (0 + falloffPrayerPower))
    query.execute()


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
        return False


# Gets all Marriages in a guild
def getMarriages(guild):
    query = marriages.select().join(gods).where(gods.Guild == str(guild)).order_by(marriages.LoveDate)
    return query


# Gets top 50 Marriages globally
def getMarriagesGlobal():
    query = marriages.select().order_by(marriages.LoveDate).limit(50)
    return query


# Get someone's marriage
def getMarriage(believerid):
    query = marriages.select().where((marriages.Believer1 == believerid) | (marriages.Believer2 == believerid))
    if query.exists():
        return query[0]
    return False


# Delete a marriage
def deleteMarriage(marriageid):
    marriage = marriages.select().where(marriages.ID == marriageid)
    if marriage.exists():
        query = marriage[0].delete_instance()
        if query == 1:
            return True
    return False


# Show someone love
def doLove(marriageid):
    date = datetime.datetime.now()

    query = marriages.update(LoveDate=date).where(marriages.ID == marriageid)
    query.execute()


# --------------------------------------- Offers [Invitations / PriestOffers] --------------------------------------- #


# The Offers Table
class offers(Model):
    ID = AutoField()
    Type = BitField()
    God = ForeignKeyField(gods)
    UserID = CharField(max_length=snowflake_max_length)
    CreationDate = DateTimeField(default=datetime.datetime.now())

    class Meta:
        database = db


# Adding new invite to the DB
def newInvite(godid, userid):
    try:
        invite = offers.create(God=godid, Type=1, UserID=userid)
        return invite
    except Exception as e:
        logger.logDebug("Error doing new invite - " + str(e), "ERROR")
        return False


# Get someone's invite for a god
def getInvite(userid, godid):
    query = offers.select().where((offers.Type == 1) & (offers.UserID == str(userid)) & (offers.God == godid))
    if query.exists():
        return query[0]
    return False


# Clears expired invites
def clearExpiredInvites():
    today = datetime.datetime.today() - datetime.timedelta(days=1)
    query = offers.delete().where((offers.Type == 1) & (offers.CreationDate < today))
    query.execute()


# Delete an invite // used after an invite has been used
def deleteInvite(offerid):
    invite = offers.select().where((offers.Type == 1) & (offers.ID == offerid))
    if invite.exists():
        query = invite[0].delete_instance()
        if query == 1:
            return True
    return False


# Adding new priest offer to the DB
def newPriestOffer(godid, userid):
    try:
        priestoffer = offers.create(God=godid, Type=2, UserID=userid)
        return priestoffer
    except Exception as e:
        logger.logDebug("Error doing new priestoffer - " + str(e), "ERROR")
        return False


# Get someone's priest offer for a god
def getPriestOffer(godid):
    query = offers.select().where((offers.Type == 2) & (offers.God == godid))
    if query.exists():
        return query[0]
    return False


# Delete a priest offer // used after a priest offer has been used
def deletePriestOffer(offerid):
    priestoffer = offers.select().where((offers.Type == 2) & (offers.ID == offerid))
    if priestoffer.exists():
        query = priestoffer[0].delete_instance()
        if query == 1:
            return True
    return False


# Get and clear old priest offers
def clearOldPriestOffers():
    date = datetime.datetime.today() - datetime.timedelta(days=1)
    priestOffers = offers.select().where((offers.Type == 2) & (offers.CreationDate < date))
    if priestOffers.exists():
        priestOffers = priestOffers.execute()
        query = offers.delete().where((offers.Type == 2) & (offers.CreationDate < date))
        query.execute()
        return priestOffers
    return False


# -------------------------------------------------- SETUP OF TABLES ------------------------------------------------- #


def create_tables():
    with db:
        db.create_tables([gods, believers, marriages, offers])


create_tables()
