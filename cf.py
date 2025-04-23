import logging
import random
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN", "8000401706:AAErIaSiOzrBeL3pxqG7W19yLZJrwCoEXkM")
PORT = int(os.environ.get("PORT", "8443"))
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")

user_scores = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Hi {user.first_name}! I'm your Rock Paper Scissors Bot!\n\n"
        "Use /play to start a game."
    )

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Rock 🪨", callback_data="rock"),
            InlineKeyboardButton("Paper 📄", callback_data="paper"),
            InlineKeyboardButton("Scissors ✂️", callback_data="scissors"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("Choose your move:", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    user_choice = query.data
    user_id = query.from_user.id
    
    bot_choice = random.choice(["rock", "paper", "scissors"])
    
    result = determine_winner(user_choice, bot_choice)
    
    if user_id not in user_scores:
        user_scores[user_id] = {"wins": 0, "losses": 0, "ties": 0}
    
    if "win" in result:
        user_scores[user_id]["wins"] += 1
    elif "lose" in result:
        user_scores[user_id]["losses"] += 1
    else:
        user_scores[user_id]["ties"] += 1
    
    choice_emojis = {
        "rock": "🪨",
        "paper": "📄",
        "scissors": "✂️"
    }
    
    user_emoji = choice_emojis[user_choice]
    bot_emoji = choice_emojis[bot_choice]
    
    score = user_scores[user_id]
    score_message = f"Score: {score['wins']} wins, {score['losses']} losses, {score['ties']} ties"
    
    keyboard = [
        [InlineKeyboardButton("Play Again", callback_data="play_again")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"You chose: {user_choice.capitalize()} {user_emoji}\n"
        f"I chose: {bot_choice.capitalize()} {bot_emoji}\n\n"
        f"{result}\n\n"
        f"{score_message}",
        reply_markup=reply_markup
    )

async def play_again_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("Rock 🪨", callback_data="rock"),
            InlineKeyboardButton("Paper 📄", callback_data="paper"),
            InlineKeyboardButton("Scissors ✂️", callback_data="scissors"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("Choose your move:", reply_markup=reply_markup)

def determine_winner(user_choice, bot_choice):
    if user_choice == bot_choice:
        return "It's a tie!"
    
    winning_combinations = {
        "rock": "scissors",
        "paper": "rock",
        "scissors": "paper"
    }
    
    if winning_combinations[user_choice] == bot_choice:
        return "You win! 🎉"
    else:
        return "You lose! 😢"

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    
    if user_id not in user_scores:
        await update.message.reply_text("You haven't played any games yet!")
        return
    
    score = user_scores[user_id]
    total_games = score["wins"] + score["losses"] + score["ties"]
    win_percentage = (score["wins"] / total_games) * 100 if total_games > 0 else 0
    
    await update.message.reply_text(
        f"📊 Your Stats 📊\n\n"
        f"Total games: {total_games}\n"
        f"Wins: {score['wins']}\n"
        f"Losses: {score['losses']}\n"
        f"Ties: {score['ties']}\n"
        f"Win rate: {win_percentage:.1f}%"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🎮 Rock Paper Scissors Bot Commands 🎮\n\n"
        "/start - Start the bot\n"
        "/play - Start a new game\n"
        "/stats - View your game statistics\n"
        "/help - Show this help message"
    )

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("play", play))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("help", help_command))
    
    application.add_handler(CallbackQueryHandler(play_again_callback, pattern="^play_again$"))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Use webhook when in production environment
    if ENVIRONMENT == "production":
        WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
        )
    else:
        # Use polling for local development
        application.run_polling()

if __name__ == "__main__":
    main()
