from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import logging

# Настройка логирования
logging.basicConfig(
    filename="bot_logs.txt",
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Этапы разговора
ASK_SITUATION, SUMMARIZE_CONFIRM, ASK_SMEP, IDENTIFY_DISTORTION, RESTRUCTURE, ADAPTIVE_THOUGHT = range(6)


# Стартовое сообщение
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"User {update.effective_user.id} started the conversation.")
    await update.message.reply_text(
        "Привет! Я помогу тебе с когнитивной реструктуризацией. Опиши проблемную ситуацию."
    )
    return ASK_SITUATION


# Функция получения описания ситуации
async def ask_situation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['situation'] = update.message.text
    # Резюмирование (заглушка вместо LangChain)
    summary = f"Вы описали ситуацию как: '{update.message.text[:50]}...'."  # Ограничение для простоты
    context.user_data['summary'] = summary

    reply_keyboard = [["Да", "Нет", "Уточнить"]]
    await update.message.reply_text(
        f"Вы имеете в виду: '{summary}'? Ответьте 'Да', 'Нет' или 'Уточнить'.",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return SUMMARIZE_CONFIRM


# Функция подтверждения резюме
async def summarize_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "Да":
        await update.message.reply_text("Хорошо, теперь разложим ситуацию на Ситуацию, Мысли, Эмоции и Реакции.")
        return ASK_SMEP
    elif update.message.text == "Нет":
        await update.message.reply_text("Опишите проблему другими словами.")
        return ASK_SITUATION
    elif update.message.text == "Уточнить":
        await update.message.reply_text("Дополните описание ситуации.")
        return ASK_SITUATION


# СМЭР: сбор данных по Ситуации, Мысли, Эмоции, Реакции
async def ask_smep(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Опишите, пожалуйста, ситуацию.")
    context.user_data['SMER'] = {}
    return IDENTIFY_DISTORTION


# Функция для классификации искажений (заглушка вместо LangChain)
async def identify_distortion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_thought = update.message.text
    context.user_data['SMER']['thought'] = user_thought
    # Эмуляция определения искажения
    distortion = "черно-белое мышление"  # Предположим, что это тип искажения
    context.user_data['distortion'] = distortion

    await update.message.reply_text(
        f"Выявлено когнитивное искажение: {distortion}. Давайте подумаем над этим."
    )
    return RESTRUCTURE


# Функция для реструктуризации, использующая get_restructuring_questions
async def restructure(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    distortion_type = context.user_data.get('distortion', 'общего характера')
    questions = get_restructuring_questions(distortion_type)

    # Отправляем вопросы пользователю
    for question in questions:
        await update.message.reply_text(question)

    await update.message.reply_text("После того, как ответите на вопросы, пожалуйста, сформулируйте новую мысль.")
    return ADAPTIVE_THOUGHT


# Финальный этап: формулирование новой мысли
async def adaptive_thought(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    adaptive_thought = update.message.text
    context.user_data['adaptive_thought'] = adaptive_thought
    await update.message.reply_text(f"Отлично! Вот новая мысль: {adaptive_thought}")
    return ConversationHandler.END


# Функция для генерации вопросов реструктуризации
def get_restructuring_questions(distortion_type: str):
    """Возвращает список вопросов для когнитивной реструктуризации в зависимости от типа когнитивного искажения."""
    questions = []

    if distortion_type == "черно-белое мышление":
        questions = [
            "Есть ли что-то между крайними вариантами? Как выглядит 'серая зона'?",
            "Могу ли я увидеть эту ситуацию более гибко, а не только в крайностях?",
            "Как бы я оценил ситуацию, если бы не видел её в крайностях?"
        ]

    elif distortion_type == "сверхобобщение":
        questions = [
            "Не делаю ли я поспешные выводы, основываясь на единичном случае?",
            "Есть ли примеры, когда ситуация складывалась иначе?",
            "Как выглядит ситуация, если рассмотреть её в контексте более широкого опыта?"
        ]

    elif distortion_type == "персонализация":
        questions = [
            "Не приписываю ли я ответственность себе, когда есть и другие факторы?",
            "Есть ли у меня объективные причины полагать, что я виноват?",
            "Какие ещё факторы могли повлиять на эту ситуацию, кроме моих действий?"
        ]

    elif distortion_type == "катастрофизация":
        questions = [
            "Насколько вероятно, что произойдет худший сценарий?",
            "Как я буду справляться с ситуацией, если худший вариант действительно случится?",
            "Есть ли другие, более реалистичные исходы этой ситуации?"
        ]

    elif distortion_type == "обесценивание позитивного":
        questions = [
            "Почему я игнорирую положительные моменты?",
            "Какие положительные факты в этой ситуации я могу признать?",
            "Могу ли я найти примеры того, что ситуация развивалась успешно?"
        ]

    elif distortion_type == "чтение мыслей":
        questions = [
            "Почему я предполагаю, что знаю, что думают другие?",
            "Спросил ли я у кого-то, что они действительно думают?",
            "Есть ли доказательства, что мои предположения об их мыслях верны?"
        ]

    elif distortion_type == "эмоциональное обоснование":
        questions = [
            "Почему я воспринимаю свои эмоции как доказательство реальности?",
            "Есть ли объективные данные, подтверждающие мои ощущения?",
            "Как бы я рассматривал ситуацию, если бы испытывал другие эмоции?"
        ]

    elif distortion_type == "долженствование":
        questions = [
            "Почему я считаю, что обязательно должен поступить именно так?",
            "Что произойдет, если я не буду следовать этому 'долженствованию'?",
            "Откуда возникло это правило, и реально ли оно в этой ситуации?"
        ]

    elif distortion_type == "сравнение с другими":
        questions = [
            "Почему я сравниваю себя с другими в этой ситуации?",
            "Есть ли у меня уникальные обстоятельства, отличающие мою ситуацию от других?",
            "Какие мои личные достижения могут быть значимыми независимо от других?"
        ]

    else:
        questions = [
            "Что вызывает у меня эту мысль?",
            "Какие у меня есть факты, подтверждающие или опровергающие эту мысль?",
            "Могу ли я сформулировать свою мысль в более конструктивном ключе?"
        ]

    return questions


# Основная функция для работы бота
def main():
    application = ApplicationBuilder().token("7956210811:AAEG2I9XPAuvx62c849v21GeTsuxGkl6x7Q").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_SITUATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_situation)],
            SUMMARIZE_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, summarize_confirm)],
            ASK_SMEP: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_smep)],
            IDENTIFY_DISTORTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, identify_distortion)],
            RESTRUCTURE: [MessageHandler(filters.TEXT & ~filters.COMMAND, restructure)],
            ADAPTIVE_THOUGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, adaptive_thought)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
