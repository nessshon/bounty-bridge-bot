import logging
import traceback
from contextlib import suppress

from aiogram import Router, F
from aiogram.types import ErrorEvent, BufferedInputFile
from aiogram.utils.markdown import hcode, hbold

from project.bot.manager import Manager
from project.bot.utils import keyboards
from project.bot.utils.messages import send_message
from project.bot.utils.texts.messages import MessageCode

router = Router()


async def unknown_error_window(manager: Manager) -> None:
    """ Handles unknown errors. """
    text = await manager.text_message.get(MessageCode.UNKNOWN_ERROR)
    reply_markup = await keyboards.main(manager.text_button)

    await manager.send_message(text, reply_markup=reply_markup)
    await manager.state.set_state(None)


@router.errors(F.exception.message.contains("query is too old"))
async def query_too_old(_: ErrorEvent) -> None:
    """Handles errors containing 'query is too old'."""


@router.errors()
async def telegram_api_error(event: ErrorEvent, manager: Manager) -> None:
    """
    Handles Telegram API errors.

    :param event: The error event.
    :param manager: The manager instance.
    """
    logging.exception(f"Update: {event.update}\nException: {event.exception}")

    # Prepare data for document
    update_json = event.update.model_dump_json(indent=2, exclude_none=True)
    exc_text, exc_name = str(event.exception), type(event.exception).__name__
    update_data = str(update_json + "\n\n").encode()
    traceback_data = str(traceback.format_exc() + "\n\n").encode()

    # Send document with error details
    document_data = update_data + traceback_data
    document_name = f"error_{event.update.update_id}.txt"
    document = BufferedInputFile(document_data, filename=document_name)

    with suppress(Exception):
        # Handle unknown error
        await unknown_error_window(manager)
        await event.update.message.delete()

    text = f"{hbold(exc_name)}:\n{hcode(exc_text[:1024 - len(exc_name) - 2])}"
    await send_message(manager.bot, manager.config.bot.DEV_ID, text, document)
    await send_message(manager.bot, manager.config.bot.ADMIN_ID, text, document)

    # Send update_json in chunks
    for text in [update_json[i:i + 4096] for i in range(0, len(update_json), 4096)]:
        await send_message(manager.bot, manager.config.bot.DEV_ID, hcode(text))
        await send_message(manager.bot, manager.config.bot.ADMIN_ID, hcode(text))
