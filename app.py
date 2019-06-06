from SETTINGS import SETTINGS
from application.db.db import DB
from application.managers.songManager import SongManager
from application.managers.botManager import BotManager

db = DB(SETTINGS['DB'])
songManager = SongManager({'db': db})

songManager.fillDB()
BotManager({ 'findSong': songManager.findSong })


