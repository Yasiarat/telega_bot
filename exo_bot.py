from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import CallbackContext
from telegram.ext import ConversationHandler
from key import TOKEN
from connect_to_bd import stickers, replies, insert_sticker, in_database, insert_user

grades = ['8а', '8б', '9н', '9о', '10н', '10о', '11']
grades_buttons = [
    [grades[0], grades[1]],
    [grades[2], grades[3]],
    [grades[4], grades[5]],
    [grades[0]],
]

WAIT_NAME, WAIT_SEX, WAIT_GRADE = range(3)


def main():
    updater = Updater(
        token=TOKEN,
        use_context=True
    )
    # диспетчер распределяет сообщения по обработчикам
    dispatcher = updater.dispatcher

    # создаём обработчик
    echo_handler = MessageHandler(Filters.all, do_echo)
    say_handler = MessageHandler(Filters.text, say_smth)
    new_sticker_handler = MessageHandler(Filters.text('Добавить стикер'), new_sticker)
    text_handler = MessageHandler(Filters.text('/start'), meet)
    hello_handler = MessageHandler(Filters.text('Привет'), say_hello)
    keyboard_handler = MessageHandler(Filters.text('Клавиатура, клавиатура'), keyboard)
    conv_handler = ConversationHandler(
        entry_points=[text_handler],  # Точка старта
        states={
            WAIT_NAME: [MessageHandler(Filters.text, ask_sex)],
            WAIT_SEX: [MessageHandler(Filters.text, ask_grade)],
            WAIT_GRADE: [MessageHandler(Filters.text, greet)],
        },  # Состояния конечного автомата для диалога
        fallbacks=[],  # общие точки выхода или отмены
    )

    # регестрируем обработчик
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(say_handler)
    dispatcher.add_handler(hello_handler)
    dispatcher.add_handler(keyboard_handler)
    dispatcher.add_handler(new_sticker_handler)
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
        update.message.reply_text(
            f'Добро пожаловать, {update.message.from_user.username}',
            reply_markup=ReplyKeyboardRemove()

        )
        return ConversationHandler.END
    return ask_name(update, context)


def ask_name(update: Update, context: CallbackContext):
    '''
    спрашиваем имя
    TODO проверить имя пользователя в телеграме
    '''
    update.message.reply_text(
        'Привет, меня зовут Бот\n'
        'А тебя?',
        reply_markup=ReplyKeyboardRemove()
    )
    return WAIT_NAME


def ask_sex(update: Update, context: CallbackContext):
    '''
    спрашиваем пол, выводим клавиатуру
    '''
    name = update.message.text
    if not name_is_valid(name):
        update.message.reply_text(
            'Некорректное имя\n'
            'Имя должно состоять из букв и начинаться с заглавной\n'
            'Попробуй ещё раз'
        )
        return WAIT_NAME
    context.user_data['name'] = name  # запоминаем имя
    buttons = [
        ['м', 'ж']
    ]
    keys = ReplyKeyboardMarkup(
        buttons,
        resize_keyboard=True  # размер
    )
    update.message.reply_text(
        text=f'Приятно познакомиться, {name}, укажи пожалуйста свой пол',
        reply_markup=keys  # разметка
    )
    return WAIT_SEX


def ask_grade(update: Update, context: CallbackContext):
    '''
    спрашиваем класс с помощью клавиатуры
    '''
    sex = update.message.text
    if not sex_is_valid(sex):
        update.message.reply_text(
            'Некорректное пол\n'
            'Воспользуйся клавиатурой\n'
            'Попробуй ещё раз'
        )
        return WAIT_SEX
    context.user_data['sex'] = sex
    keys = ReplyKeyboardMarkup(
        grades_buttons,
        resize_keyboard=True  # размер
    )
    update.message.reply_text(
        text='Укажи пожалуйста свой класс',
        reply_markup=keys
    )
    return WAIT_GRADE


def greet(update: Update, context: CallbackContext):
    '''
    Записывает в БД:
        user_id(из сообщения)
        name(из контекста)
        sex(из контекста)
        grade(из сообщения)
    приветствует нового пользователя
    '''
    grade = update.message.text
    if not grade_is_valid(grade):
        update.message.reply_text(
            'Некорректный класс\n'
            'Воспользуйся клавиатурой\n'
            'Попробуй ещё раз'
        )
        return WAIT_GRADE
    name = context.user_data['name']
    sex = context.user_data['sex']
    user_id = update.message.from_user.id
    insert_user(user_id, name, sex, grade)

    update.message.reply_text(
        f'Новая запись в БД\n'
        f'{user_id}\n'
        f'{name}\n'
        f'{sex}\n'
        f'{grade}',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def name_is_valid(name: str) -> bool:
    return name.isalpha() and name[0].isupper() and name[1:].islower()


def sex_is_valid(sex: str) -> bool:
    return sex == 'м' or sex == 'ж'


def grade_is_valid(grade: str) -> bool:
    return grade in grades


if __name__ == '__main__':
    main()
