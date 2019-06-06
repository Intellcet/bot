import sqlite3


# Класс для работы с базой данных.
# Все запросы прописываются здесь
class DB:

    conn = None

    def __init__(self, settings):
        self.conn = sqlite3.connect(settings['PATH'])
        self.conn.row_factory = self.dictFactory
        self.c = self.conn.cursor()
        self.__initDB()

    def __del__(self):
        self.conn.close()

    @staticmethod
    def dictFactory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def __dropDB(self):
        query = "DROP TABLE IF EXISTS hash"
        self.c.execute(query)
        query = "DROP TABLE IF EXISTS song"
        self.c.execute(query)

    def __initDB(self):
        self.__dropDB()
        query = "CREATE TABLE song ( id INTEGER NOT NULL CONSTRAINT song_pk PRIMARY KEY AUTOINCREMENT , name TEXT NOT NULL)"
        self.c.execute(query)
        query = "CREATE TABLE hash ( id INTEGER NOT NULL CONSTRAINT hash_pk PRIMARY KEY AUTOINCREMENT , id_song INTEGER NOT NULL , hash_str INTEGER NOT NULL)"
        self.c.execute(query)
        self.conn.commit()

    def getSongId(self, songName):
        query = "SELECT id FROM song WHERE name = :name"
        self.c.execute(query, {'name': songName})
        return self.c.fetchone()['id']

    def addSong(self, songName):
        query = "INSERT INTO song (name) VALUES (:name)"
        self.c.execute(query, {'name': songName})
        self.conn.commit()
        return self.getSongId(songName)

    def addHashes(self, songId, hashes):
        for hash in hashes:
            query = "INSERT INTO hash (id_song, hash_str)  VALUES (:songId, :hash)"
            self.c.execute(query, {'songId': songId, 'hash': hash})
        self.conn.commit()

    def getSongByHashes(self, hashes):
        query = "SELECT song.name FROM hash JOIN song ON (song.id = hash.id_song) WHERE "
        for hash in hashes:
            query += "hash_str = " + str(hash) + " OR "
        query = query[:-3]
        query += "GROUP BY song.name ORDER BY count(song.name) DESC LIMIT 1"
        self.c.execute(query)
        return self.c.fetchone()
