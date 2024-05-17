import html
import json
import traceback

from telegram import Update, BotCommand
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.constants import ParseMode

import asyncio

import typing

from . import log

log.getLogger("httpx").setLevel(log.logging.WARNING)
logger = log.getLogger(__name__)


class Agent(typing.Protocol):
    def __call__(self, text: str) -> str:
        pass


class BotAgent:
    def __init__(
        self,
        token: str,
        root_id: int,
        greetings_message: str,
        help_message: str,
        agent: Agent,
    ):
        self._client = ApplicationBuilder().token(token).build()
        self._greetings_message = greetings_message
        self._help_message = help_message

        self._client.add_handler(CommandHandler("start", self.greetings))
        self._client.add_handler(CommandHandler("switch", self.switch))
        self._client.add_handler(CommandHandler("abort", self.abort))
        self._client.add_handler(CommandHandler("help", self.help))
        self._client.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.answer)
        )
        self._client.add_error_handler(self.error_handler)
        asyncio.get_event_loop().run_until_complete(
            self._client.bot.setMyCommands(
                [
                    BotCommand("start", "приветственное сообщение"),
                    BotCommand("help", "примеры использования"),
                ]
            )
        )

        self._agent = agent
        self._is_paused = False
        self._root_id = int(root_id)

    async def greetings(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        logger.info(f"got {update.message.text}")
        await update.message.reply_text(self._greetings_message)
        await self.inform_root(update, "greetings message", context)

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.info(f"got {update.message.text}")
        await update.message.reply_text(self._help_message)
        await self.inform_root(update, "help message", context)

    async def switch(self, update: Update, _) -> None:
        logger.info(f"got {update.message.text}")
        if not self.from_root(update):
            logger.info("not root, skipping...")
            return
        self._is_paused = not self._is_paused
        action = "поставлен на паузу" if self._is_paused else "снят с паузы"
        await update.message.reply_text(f"Бот {action}")

    async def abort(self, update: Update) -> None:
        if not self.from_root(update):
            logger.info("not root, skipping...")
            return
        logger.info("got abort call...")
        exit(1)

    async def answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.info(f"got {update.message.text}")
        response = ""
        if not self._is_paused:
            response = self._agent(update.message.text)
            await update.message.reply_text(response)
        await self.inform_root(update, response, context)

    async def inform_root(
        self, update: Update, response: str, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if self.from_root(update):
            logger.info("root, skipping inform...")
            return
        await context.bot.send_message(
            self._root_id, text=self.__format_inform_text(update, response)
        )
        logger.info("info sent")

    def __format_inform_text(self, update: Update, response: str) -> str:
        return f"input={update.message.text}\n{update.message.from_user}\n{response=}"

    def from_root(self, update: Update) -> bool:
        return update.message.from_user.id == self._root_id

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Log the error and send a telegram message to notify the developer."""
        logger.error("Exception while handling an update:", exc_info=context.error)
        tb_list = traceback.format_exception(
            None, context.error, context.error.__traceback__
        )
        tb_string = "".join(tb_list)
        update_str = update.to_dict() if isinstance(update, Update) else str(update)
        message = (
            "An exception was raised while handling an update\n"
            f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
            "</pre>\n\n"
            f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
            f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
            f"<pre>{html.escape(tb_string)}</pre>"
        )
        await context.bot.send_message(
            chat_id=self._root_id, text=message, parse_mode=ParseMode.HTML
        )

    def start(self):
        logger.info("bot starting...")
        self._client.run_polling()


