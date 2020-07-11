import requests
import telebot
from bs4 import BeautifulSoup as BS
from telebot import types

import config

bot = telebot.TeleBot(config.token)
response = requests.get(config.url).json()

@bot.message_handler(commands=['start'])
def start(message):
    send = f"Здравствуй,{message.from_user.first_name}!\nВведи интересующий тебя город!"
    bot.send_message(message.chat.id, send)

@bot.message_handler(content_types=['text'])
def city(message):
    
    try:
        city_name = ""
        get_message_bot = message.text.strip().lower()
        
    except Exception as e:
        bot.reply_to(message, 'Ой ой, незадача! Нужно вводить только текст.')
        city(message)
    bot.send_message(message.chat.id, f"Твой город: {get_message_bot}.\nЭта информация будет использоваться в дальнейшем", get_message_bot)    
    main(message)
    
@bot.message_handler(commands=['main'])
def main(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    itembtn1 = types.KeyboardButton('Погода')
    itembtn2 = types.KeyboardButton('Валюта')
    itembtn3 = types.KeyboardButton('События')
    
    markup.add(itembtn1, itembtn2, itembtn3)
    msg2 = bot.send_message(message.chat.id, "Приступим к делу. Ткни на кнопку!", reply_markup=markup)
    bot.register_next_step_handler( msg2, process_switch_step )

def main_extra(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    itembtn1 = types.KeyboardButton('Погода')
    itembtn2 = types.KeyboardButton('Валюта')
    itembtn3 = types.KeyboardButton('События')
    
    markup.add(itembtn1, itembtn2, itembtn3)
    msg2 = bot.send_message(message.chat.id,'Хочешь узнать что-нибудь еще?', reply_markup=markup)
    bot.register_next_step_handler( msg2, process_switch_step )

def process_switch_step(message):

    if (message.text == 'Погода'):
        weather(message)
        main_extra(message)
    elif (message.text == 'Валюта'):
        monet(message)
    elif(message.text == 'События'):
        events_main(message)

def weather(message):
    
    r1 = requests.get('https://sinoptik.ua/погода-киев' )
    html1 = BS(r1.content, 'html.parser')

    for el in html1.select('#content'):
        t_min = el.select('.temperature .min')[0].text
        t_max = el.select('.temperature .max')[0].text
        desc = el.select('.wDescription .description')[0].text

    bot.send_message( message.chat.id, 'Погода на сегодня:\n' +
        t_min + ', ' + t_max + '\n' + desc)

@bot.message_handler(commands=['currency'])
def monet(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    itembtn1 = types.KeyboardButton('USD')
    itembtn2 = types.KeyboardButton('EUR')
    itembtn3 = types.KeyboardButton('RUR')
    itembtn4 = types.KeyboardButton('Предыдущее меню')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4)
    msg = bot.send_message(message.chat.id, "Курс по ПриватБанку", reply_markup=markup)
    bot.register_next_step_handler( msg, process_monet_step )

def monet_extra(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    itembtn1 = types.KeyboardButton('USD')
    itembtn2 = types.KeyboardButton('EUR')
    itembtn3 = types.KeyboardButton('RUR')
    itembtn4 = types.KeyboardButton('Предыдущее меню')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4)
    msg = bot.send_message(message.chat.id, "Попробуешь другую валюту?", reply_markup=markup)
    bot.register_next_step_handler( msg, process_monet_step )

def process_monet_step(message):
    try:
        if (message.text == 'Предыдущее меню'):
            main_extra(message)     
        for monet in response:
            if (message.text == monet['ccy']):
                bot.send_message(message.chat.id, printmonet(monet['buy'], monet['sale']), parse_mode="Markdown")
                monet_extra(message)
                
    except Exception as e:
        bot.reply_to(message, 'Ой ой, незадача!')

def printmonet(buy, sale):
    return "*Курс покупки:* " + str(buy) +"\n*Курс продажи:* " + str(sale)

@bot.message_handler(commands=['news'])
def events_main(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    itembtn1 = types.KeyboardButton('В этот день')
    itembtn2 = types.KeyboardButton('Знаете ли Вы?')
    itembtn3 = types.KeyboardButton('Новости')
    itembtn4 = types.KeyboardButton('Предыдущее меню')
    
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4)
    msg = bot.send_message(message.chat.id, "Полезную информацию в студию!", reply_markup=markup)
    bot.register_next_step_handler( msg, process_events_step )

def events_main_extra(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    itembtn1 = types.KeyboardButton('В этот день')
    itembtn2 = types.KeyboardButton('Знаете ли Вы?')
    itembtn3 = types.KeyboardButton('Новости')
    itembtn4 = types.KeyboardButton('Предыдущее меню')
    
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4)
    msg = bot.send_message(message.chat.id, "И помни - знаний много не бывает!", reply_markup=markup)
    bot.register_next_step_handler( msg, process_events_step )

def process_events_step(message):
    if (message.text == 'В этот день'):
        today(message)
        events_main_extra(message)
    elif (message.text == 'Знаете ли Вы?'):
        you_know(message)
        events_main_extra(message)
    elif(message.text == 'Новости'):
        news(message)
        events_main_extra(message)
    elif(message.text == 'Предыдущее меню'):
        main_extra(message)
#В этот день
def today(message):
    r = requests.get('https://ru.wikipedia.org/wiki/%D0%97%D0%B0%D0%B3%D0%BB%D0%B0%D0%B2%D0%BD%D0%B0%D1%8F_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0')
    soup = BS(r.text, 'html.parser')
    
    for i in soup.find_all(class_='main-box-subtitle'):
        if  'В' in i.text:
            list_with_news = i.parent.ul.find_all('li')
            for j in list_with_news:
                    bot.send_message( message.chat.id, j.text)    
#Знаете ли вы?
def you_know(message):
     r2 = requests.get('https://ru.wikipedia.org/wiki/%D0%97%D0%B0%D0%B3%D0%BB%D0%B0%D0%B2%D0%BD%D0%B0%D1%8F_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0')
     html2 = BS(r2.text, 'html.parser')

     test1 = html2.find('div', id='main-dyk')
     for i in test1.find_all('ul'):
         for j in i.find_all('li'):
             print(j.text)
             bot.send_message(message.chat.id, j.text)
#Новости
def news(message):

    r4 = requests.get('https://112.ua/')
    html4 = BS(r4.text, 'html.parser')


    test2 = html4.find('div', id='tabs-top-news')
    for i in test2.find_all('ul'):
        for j in i.find_all('li'):
             print(j.text)
             bot.send_message( message.chat.id, j.text)
        
if __name__ =='__main__':
    bot.polling(none_stop=True)

