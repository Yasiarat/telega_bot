from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from key import TOKEN
from connect_to_bd import stickers, replies, insert_sticker, in_database, insert_user


def main():
    updater = Updater(
        token=TOKEN,
        use_context=True
    )
    # диспетчер распределяет сообщения по обработчикам
    dispatcher = updater.dispatcher

    # создаём обработчик
    echo_handler = MessageHandler(Filters.all, do_echo)
    new_sticker_handler = MessageHandler(Filters.text('Добавь, добавь'), new_sticker)
    text_handler = MessageHandler(Filters.text, say_smth)
    hello_handler = MessageHandler(Filters.text('Привет'), say_hello)
    bye_handler = MessageHandler(Filters.text('пока'), say_bye)
    keyboard_handler = MessageHandler(Filters.text('Клавиатура, клавиатура'), keyboard)

    # регестрируем обработчик
    dispatcher.add_handler(hello_handler)
    dispatcher.add_handler(keyboard_handler)
    dispatcher.add_handler(text_handler)
    dispatcher.add_handler(new_sticker_handler)
    dispatcher.add_handler(bye_handler)
    dispatcher.add_handler(echo_handler)

    updater.start_polling()
    print('Бот успешно запустился')
    updater.idle()


def do_echo(update: Update, context: CallbackContext) -> None:
    id = update.message.chat_id
    user = update.message.from_user.username
    text = update.message.text
    sticker = update.message.sticker
    if sticker:
        sticker_id = sticker.file_id
        update.message.reply_sticker(sticker_id)
    update.message.reply_text(text=
                              f' держи своё {text}\n'
                              f'а это твой айдишник {id}\n'
                              f'и вообще ты @{user}\n'

                              )


def say_hello(update: Update, context: CallbackContext):
    name = update.message.from_user.first_name
    update.message.reply_text(text=f'Привет, {name}, \n'
                                f'приятно познакомиться с живым человеком\n'
                                f'Я - бот'
                              )


def say_bye(update: Update, context: CallbackContext):
    update.message.reply_sticker(stickers['пока'])


def say_smth(update: Update, context: CallbackContext):
    name = update.message.from_user.first_name
    text = update.message.text
    for keyword in stickers:
        if keyword in text:
            if stickers[keyword]:
                update.message.reply_sticker(stickers[keyword])
            if replies[keyword]:
                update.message.reply_text(replies[keyword].format(name))
            break
    else:
        do_echo(update, context)


def new_sticker(update: Update, context: CallbackContext) -> None:
    sticker_id = update.message.sticker.file_id
    for keyword in stickers:
        if sticker_id == stickers[keyword]:
            update.message.reply_text('у меня тоже такой есть')
            update.message.reply_sticker(sticker_id)
            break
    else:
        context.user_data['new_sticker'] = sticker_id
        update.message.reply_text('введи ключевое слово')


def new_keyword(update: Update, context: CallbackContext) -> None:
    if 'new_sticker' not in context.user_data:
        say_smth(update, context)
    else:
        keyword = update.message.text
        sticker_id = context.user_data['new_sticker']
        insert_sticker(keyword, sticker_id)
        context.user_data.clear()


def keyboard(update: Update, context: CallbackContext) -> None:
    buttons = [
        ['Добавить стикер', '2', '3'],
        ['Привет', 'Пока']
    ]
    keys = ReplyKeyboardMarkup(
        buttons
    )
    update.message.reply_text(
        text='Смотри, у тебя появились кнопки!',
        reply_markup=ReplyKeyboardMarkup(
            buttons,
            resize_keyboard=True,
            # one_time_keyboard=True,

        )
    )


def meet(update: Update, context: CallbackContext):
    '''
    старт диалога по добавлению пользователя в базу данных
    будут собраны последовательно
        id пользователя
        имя
        пол
        класс
    '''
    user_id = update.message.from_user.id
    if in_database(user_id):
        pass # выход из диалога
    ask_name(update, context, user_id)


def ask_name(update: Update, context: CallbackContext, user_id):
    update.message.reply_text(
        'Привет, меня зовут Бот\n' 
        'А тебя?'
    )
    name = update.message.text
    if name.isalpha():
        ask_sex(update, context, name)


def ask_sex(update: Update, context: CallbackContext, user_id, name):
    buttons = [
        ['м', 'ж'],
    ]
    update.message.reply_text(
        text=f'{name}, укажи пожалуйста свой пол',
        reply_markup=ReplyKeyboardMarkup(
            buttons,
            resize_keyboard=True
        )
    )
    sex = update.message.text

    ask_grade(update, context, name, sex)


def ask_grade(update: Update, context: CallbackContext, user_id, name, sex):
    buttons = [
        ['8', '9', '10', '11'],
    ]
    update.message.reply_text(
        text='Укажи пожалуйста свой класс',
        reply_markup=ReplyKeyboardMarkup(
            buttons,
            resize_keyboard=True
        )
    )
    grade = update.message.text
    insert_user(user_id, name, sex, grade)


if __name__ == '__main__':
    main()