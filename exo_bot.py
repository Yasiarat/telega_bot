from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from key import TOKEN


def main():
    updater = Updater(
        token=TOKEN,
        use_context=True
    )
    # диспечер распределяет сообщения по обработчикам
    dispatcher = updater.dispatcher

    # создаём обработчик
    echo_handler = MessageHandler(Filters.all, do_echo)
    hello_handler = MessageHandler(Filters.text('Привет'), say_hello)

    '''hello_handler = MessageHandler(if 'привет' in text.lower():
        say_hello)
    '''
    # регестрируем обработчик
    dispatcher.add_handler(hello_handler)
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


if __name__ == '__main__':
    main()
