from peewee import SqliteDatabase, Model, CharField, DateTimeField, AutoField, ForeignKeyField, SmallIntegerField, \
    BooleanField, IntegerField, BitField
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
    Gender = CharField(null=True, max_length=19)
    Type = CharField(max_length=10)
    Mood = SmallIntegerField(null=True, default=0)
    Power = CharField(max_length=5, default="1")
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
    query = believers.select().join(gods).where(gods.Guild.contains(str(guild)) & gods.Name.contains(str(godname)))
    if query.exists():
        return query
    return False


# Get a God's believers, using ID
def getBelieversByID(god):
    query = believers.select().join(gods).where(gods.ID.contains(str(god)))
    if query.exists():
        return query
    return False


# Get believers, globally
def getBelieversGlobal():
    query = believers.select()
    if query.exists():
        return query
    return False


# See if a god already exists with that name in a guild
def getGodName(name, guild):
    query = gods.select().where((gods.Guild.contains(str(guild)) & gods.Name.contains(str(name))))
    if query.exists():
        god = query.execute()
        return god[0]
    return False


# Get a God by ID
def getGod(godid):
    query = gods.select().where(gods.ID.contains(str(godid)))
    if query.exists():
        return query[0]
    return False


# Gets all Gods in a guild
def getGods(guild):
    query = gods.select().where(gods.Guild.contains(str(guild))).order_by(gods.Power)
    return query


# Disband a God
def disbandGod(godid):
    god = gods.select().where(gods.ID.contains(str(godid)))
    query = god[0].delete_instance()
    if query == 1:
        return True
    return False


# Set a priest for a God
def setPriest(godid, believerid):
    query = gods.update(Priest=believerid).where(gods.ID.contains(godid))
    query.execute()


# Set a description for a God
def setDesc(godid, desc):
    query = gods.update(Description=desc).where(gods.ID.contains(godid))
    query.execute()


# Toggle access (inviteonly)
def toggleAccess(godid):
    god = getGod(godid)

    access = True
    if god.InviteOnly:
        access = False

    query = gods.update(InviteOnly=access).where(gods.ID.contains(godid))
    query.execute()
    return access


# --------------------------------------------------- BELIEVERS ---------------------------------------------------- #


# The Believers Table
class believers(Model):
    ID = AutoField()
    God = ForeignKeyField(gods)
    UserID = CharField(max_length=snowflake_max_length)
    PrayerPower = CharField(max_length=5, default="1")
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
        logger.logDebug("Error doing new marriage - " + str(e), "ERROR")
        return False


# Whether a believer already believes in a god on that guild, if yes, returns believer
def getBeliever(userid, guild):
    query = believers.select().join(gods).where(gods.Guild.contains(str(guild))).where(believers.UserID.contains(str(userid)))
    if query.exists():
        return query[0]
    return False


# Whether a believer already believes in a god on that guild, if yes, returns believer
def getBelieverByID(believerID):
    query = believers.select().where(believers.ID.contains(believerID))
    if query.exists():
        return query[0]
    return False


# Leave a god
def leaveGod(userid, guild):
    believer = getBeliever(userid, guild)
    query = believer.delete_instance()
    if query == 1:
        return True
    return False


# Prays
def pray(believerid):
    believer = getBelieverByID(believerid)
    god = getGod(believer.God)
    date = datetime.datetime.now()

    query = believers.update(PrayDate=date, PrayerPower=str(int(believer.PrayerPower)+1), Prayers=str(int(believer.Prayers)+1)).where(believers.ID.contains(believer.ID))
    query.execute()

    query = gods.update(Power=str(int(god.Power)+1)).where(gods.ID.contains(god.ID))
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
    query = marriages.select().join(gods).where(gods.Guild.contains(str(guild))).order_by(marriages.LoveDate)
    return query


# Get someone's marriage
def getMarriage(believerid):
    query = marriages.select().where(marriages.Believer1.contains(believerid) | marriages.Believer2.contains(believerid))
    if query.exists():
        return query[0]
    return False


# Delete a marriage
def deleteMarriage(marriageid):
    marriage = marriages.select().where(marriages.ID.contains(marriageid))
    if marriage.exists():
        query = marriage[0].delete_instance()
        if query == 1:
            return True
    return False


# Show someone love
def doLove(marriageid):
    date = datetime.datetime.now()

    query = marriages.update(LoveDate=date).where(marriages.ID.contains(marriageid))
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
    query = offers.select().where(offers.Type == 1 & offers.UserID.contains(userid) & offers.God.contains(godid))
    if query.exists():
        return query[0]
    return False


# Clears expired invites
def clearExpiredInvites():
    today = datetime.datetime.today()
    query = offers.delete().where(offers.Type == 1 & offers.CreationDate < today)
    query.execute()


# Delete an invite // used after an invite has been used
def deleteInvite(offerid):
    invite = offers.select().where(offers.Type == 1 & offers.ID.contains(offerid))
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
def getPriestOffer(userid, godid):
    query = offers.select().where(offers.Type == 2 & offers.UserID.contains(userid) & offers.God.contains(godid))
    if query.exists():
        return query[0]
    return False


# Delete a priest offer // used after a priest offer has been used
def deletePriestOffer(offerid):
    priestoffer = offers.select().where(offers.Type == 2 & offers.ID.contains(offerid))
    if priestoffer.exists():
        query = priestoffer[0].delete_instance()
        if query == 1:
            return True
    return False


# Get and clear old priest offers
def clearOldPriestOffers(date):
    priestOffers = offers.select().where(offers.Type == 2 & offers.CreationDate < date)
    if priestOffers.exists():
        query = offers.delete().where(offers.Type == 2 & offers.CreationDate < date)
        query.execute()
        return priestOffers
    return False


# -------------------------------------------------- SETUP OF TABLES ------------------------------------------------- #


def create_tables():
    with db:
        db.create_tables([gods, believers, marriages, offers])


create_tables()
