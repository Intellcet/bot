import requests
import telebot

from SETTINGS import SETTINGS


class BotManager:

    bot = telebot.TeleBot(SETTINGS['BOT']['TOKEN'])
    token = None
    findSong = None

    def __init__(self, options):
        self.findSong = options['findSong']
        self.bot.polling()

    @bot.message_handler(content_types=['text', 'voice'])
    def get_text_messages(self, message):
        if message.voice:
            voice_info = self.bot.get_file(message.voice.file_id)
            file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(self.token, voice_info.file_path))
            # bot.send_message(message.from_user.id, len(bytearray(file.read())))
            content = bytearray(file.content)
            songName = self.findSong(content)
            self.bot.send_message(message.from_user.id, 'Вы искли песню: ' + songName)

        if message.text == "Привет":
            self.bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")
        elif message.text == "/help":
            self.bot.send_message(message.from_user.id, "Напиши привет")
        else:
            self.bot.send_message(message.from_user.id, "Я тебя не понимаю")
