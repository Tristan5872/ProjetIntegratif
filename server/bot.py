from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import logging

logging.basicConfig(level=logging.INFO)

# Fonction appelée lorsqu'on tape /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Commande /start reçue")
    await update.message.reply_text("Bonjour, je suis ton bot Telegram !")

# Fonction appelée lorsqu'on tape /aide
async def aide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Liste des commandes :\n/start - Démarrer\n/aide - Obtenir de l'aide")

# Configuration du bot
app = ApplicationBuilder().token("8038960549:AAE_FxbNxZ3RIiU_RUI79zMt98QcLaZWy_g").build()

# Ajout des handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("aide", aide))

# Lancement du bot
app.run_polling()
