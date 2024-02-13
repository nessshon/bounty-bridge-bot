import asyncio
import logging
import traceback
from contextlib import suppress

from aiogram import Router, F
from aiogram.types import ErrorEvent, BufferedInputFile
from aiogram.utils.markdown import hcode, hbold
from aiogram.exceptions import TelegramBadRequest

from project.bot.manager import Manager
from project.bot.utils import keyboards
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
    logging.exception(f'Update: {event.update}\nException: {event.exception}')

    with suppress(Exception):
        # Handle unknown error
        await unknown_error_window(manager)
        await event.update.message.delete()

    # Prepare data for document
    update_json = event.update.model_dump_json(indent=2, exclude_none=True)
    exc_text, exc_name = str(event.exception), type(event.exception).__name__

    update_data = str(update_json + "\n\n").encode()
    traceback_data = str(traceback.format_exc() + "\n\n").encode()

    try:
        # Send document with error details
        document_data = update_data + traceback_data
        document_name = f'error_{event.update.update_id}.txt'
        document = BufferedInputFile(document_data, filename=document_name)
        caption = f'{hbold(exc_name)}:\n{hcode(exc_text[:1024 - len(exc_name) - 2])}'
        message = await manager.bot.send_document(
            manager.config.bot.DEV_ID, document, caption=caption,
        )
        await asyncio.sleep(.1)

        # Send update_json in chunks
        for text in [update_json[i:i + 4096] for i in range(0, len(update_json), 4096)]:
            await message.reply(hcode(text))
            await asyncio.sleep(.1)

    except TelegramBadRequest:
        pass
