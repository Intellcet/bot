import os
import math
from numpy.fft import fft


class SongManager:

    # получить бинарное представление песни
    # @param songURI - путь к песне, бинарник которой нужно получить
    # @return бинарное представление песни
    @staticmethod
    def __getBinary(songURI):
        # открываем файл расположенный по пути songURI и устанавливаем флаг чтения - 'rb'
        with open(songURI, 'rb') as file:
            data = bytearray(file.read())  # кодируем в бинарник
            return data

    # чтобы не добавлять дупликаты, написана функция для сравнения
    @staticmethod
    def __isListsEquals(list1, list2):
        flag = False
        for i in range(0, len(list1)):
            if list1[i] == list2[i]:
                flag = True
            else:
                flag = False
                break
        return flag

    # Получить список всех песен в папке samples
    @staticmethod
    def __getListOfFiles():
        files = []
        for root, dir, file in os.walk('samples/'):
            for f in file:
                if '.mp3' in f:
                    files.append(os.path.join(root, f))
        return files

    chunkSize = 4096  # размер одной "части"(?) песни
    size = 0  # размер массива байтов песни
    sampledChunkSize = 0  # размер массива частей песни

    dftRes = []  # матрица с набором данных после преобразования Фурье

    RANGE = [40, 80, 120, 180, 300]  # диапазоны поиска важных точек в песне
    FUZ_FACTOR = 2  # коэффициент учёта шумов и пр...

    points = []  # важные точки песни
    p = []  # вспомогательный массив для поиска высших точек
    highScores = []  # массив с самыми высокими значениями точек

    def __init__(self, options):
        self.db = options['db']

    # инициализируем матрицу
    def __initMatrix(self):
        self.dftRes = []
        for i in range(0, self.sampledChunkSize):
            self.dftRes.append(None)

    # инициализируем минимальными значениями
    def __initHighScores(self):
        self.highScores = []
        for i in range(0, 5):
            self.highScores.append(-1)

    def __initP(self):
        self.p = []
        for i in range(0, len(self.RANGE)):
            self.p.append(None)

    # Преобразование Фурье
    def __discreteFourierTrans(self, songBytes):
        for i in range(0, self.sampledChunkSize):
            arr = []
            for j in range(0, self.chunkSize):
                arr.append(complex(songBytes[(i * self.chunkSize) + j], 0))
            self.dftRes[i] = (fft(arr))

    # получить индекс, чтобы узнать в каком промежутке мы находимся (40-80, 80-120, ...)
    def __getIndex(self, freq):
        i = 0
        while self.RANGE[i] < freq:
            i += 1
        return i

    # формируем хеш
    def __hash(self, p1, p2, p3, p4):
        return (p4 - (p4 % self.FUZ_FACTOR)) * 100000000 + (p3 - (p3 % self.FUZ_FACTOR)) * 100000 + \
               (p2 - (p2 % self.FUZ_FACTOR)) * 100 + (p1 - (p1 % self.FUZ_FACTOR))

    # функция для добавления критических точек
    def __addPoints(self, p):
        if not self.__isListsEquals(p, self.points[-1]):
            self.points.append(p)

    # генерируем критические точки
    def __createPoints(self):
        for i in range(0, len(self.dftRes)):
            res = self.dftRes[i]
            for j in range(40, 300):
                mag = math.log(abs(res[j]) + 1)
                index = self.__getIndex(j)
                if mag > self.highScores[index]:
                    self.highScores[index] = mag
                    self.p[index] = j
            if i == 0:
                self.points.append(self.p.copy())
            else:
                self.__addPoints(self.p.copy())

    # заполнить базу данных данными
    def fillDB(self):
        songs = self.__getListOfFiles()
        for song in songs:
            self.dftRes = []
            self.points = []
            self.p = []
            self.highScores = []
            songName = song.split("/")[1]
            songId = self.db.addSong(songName)
            binaryData = self.__getBinary(song)
            self.size = len(binaryData)
            self.sampledChunkSize = int(self.size / self.chunkSize)
            self.__initMatrix()
            self.__initP()
            self.__initHighScores()
            self.__discreteFourierTrans(binaryData)
            self.__createPoints()
            hashes = []
            for point in self.points:
                hashes.append(self.__hash(point[0], point[1], point[2], point[3]))
            self.db.addHashes(songId, hashes)
        print("BD filled")

    # Отдаем бинарный массив данных из песни
    def findSong(self, binaryData):
        self.dftRes = []
        self.points = []
        self.p = []
        self.highScores = []
        self.size = len(binaryData)
        self.sampledChunkSize = int(self.size / self.chunkSize)
        self.__initMatrix()
        self.__initP()
        self.__initHighScores()
        self.__discreteFourierTrans(binaryData)
        self.__createPoints()
        hashes = []
        for point in self.points:
            hashes.append(self.__hash(point[0], point[1], point[2], point[3]))
        answer = self.db.getSongByHashes(hashes)
        print("Вы искали песню: " + answer['name'])
        return answer['name']
