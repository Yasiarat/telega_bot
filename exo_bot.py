from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from key import TOKEN
from connect_to_bd import stickers, replies, insert_sticker, in_database, insert_user

grades = [
    ['8', '9', '10', '11'],
]


def main():
    updater = Updater(
        token=TOKEN,
        use_context=True
    )
    # диспетчер распределяет сообщения по обработчикам
    dispatcher = updater.dispatcher

    # создаём обработчик
    echo_handler = MessageHandler(Filters.all, do_echo)
    new_sticker_handler = MessageHandler(Filters.text('Добавить стикер'), new_sticker)
    text_handler = MessageHandler(Filters.text, ask_grade)
    hello_handler = MessageHandler(Filters.text('Привет'), say_hello)
    bye_handler = MessageHandler(Filters.text('пока'), say_bye)
    keyboard_handler = MessageHandler(Filters.text('Клавиатура, клавиатура'), keyboard)

    # регестрируем обработчик
    dispatcher.add_handler(text_handler)
    dispatcher.add_handler(hello_handler)
    dispatcher.add_handler(keyboard_handler)
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
    update.message.reply_text(text=f'Привет, {name} \n'
                                f' приятно познакомиться с живым человеком\n'
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
        return
    ask_name(update, context, user_id)


def ask_name(update: Update, context: CallbackContext, user_id):
    '''
    спрашиваем имя
    TODO проверить имя пользователя в телеграме
    '''
    update.message.reply_text(
        'Привет, меня зовут Бот\n' 
        'А тебя?'
    )
    ask_sex(update, context)


def ask_sex(update: Update, context: CallbackContext):
    '''
    спрашиваем пол, выводим клавиатуру
    '''
    name = update.message.text
    if not name.isalpha():
        ask_name(update, context)
    context.user_data['name'] = name
    buttons = [
        ['м', 'ж'],
    ]
    keys = ReplyKeyboardMarkup(
        buttons,
        resize_keyboard=True#размер
    )
    update.message.reply_text(
        text=f'Приятно познакомиться, {name}, укажи пожалуйста свой пол',
        reply_markup=keys# разметка
    )


def ask_grade(update: Update, context: CallbackContext):
    '''
    спрашиваем класс с помощью клавиатуры
    '''
    sex = update.message.text
    if sex != 'м' and sex != 'ж':
        ask_sex(update, context)
    context.user_data['sex'] = sex
    keys = ReplyKeyboardMarkup(
        grades,
        resize_keyboard=True  # размер
    )
    update.message.reply_text(
        text='Укажи пожалуйста свой класс',
        reply_markup=keys
    )


def greet(update: Update, context: CallbackContext):
    grade = update.message.text
    if grade in grades:
        ask_grade(update, context)
    name = context.user_data['name']
    sex = context.user_data['sex']
    user_id = update.message.from_user.id
    insert_user(user_id, name, sex, grade)


if __name__ == '__main__':
    main()
