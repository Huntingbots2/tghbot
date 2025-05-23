#!/usr/bin/env python3
from pyrogram.handlers import MessageHandler
from pyrogram.filters import command

from tghbot import bot
from tghbot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from tghbot.helper.telegram_helper.message_utils import deleteMessage, sendMessage
from tghbot.helper.telegram_helper.filters import CustomFilters
from tghbot.helper.telegram_helper.bot_commands import BotCommands
from tghbot.helper.ext_utils.bot_utils import (
    is_gdrive_link,
    sync_to_async,
    new_task,
    get_readable_file_size,
)
from tghbot.helper.themes import BotTheme


@new_task
async def countNode(_, message):
    args = message.text.split()
    if username := message.from_user.username:
        tag = f"@{username}"
    else:
        tag = message.from_user.mention

    link = args[1] if len(args) > 1 else ""
    if len(link) == 0 and (reply_to := message.reply_to_message):
        link = reply_to.text.split(maxsplit=1)[0].strip()

    if is_gdrive_link(link):
        msg = await sendMessage(message, BotTheme("COUNT_MSG", LINK=link))
        gd = GoogleDriveHelper()
        name, mime_type, size, files, folders = await sync_to_async(gd.count, link)
        if mime_type is None:
            await sendMessage(message, name)
            return
        await deleteMessage(msg)
        msg = BotTheme("COUNT_NAME", COUNT_NAME=name)
        msg += BotTheme("COUNT_SIZE", COUNT_SIZE=get_readable_file_size(size))
        msg += BotTheme("COUNT_TYPE", COUNT_TYPE=mime_type)
        if mime_type == "Folder":
            msg += BotTheme("COUNT_SUB", COUNT_SUB=folders)
            msg += BotTheme("COUNT_FILE", COUNT_FILE=files)
        msg += BotTheme("COUNT_CC", COUNT_CC=tag)
    else:
        msg = (
            "Send Gdrive link along with command or by replying to the link by command"
        )
    await sendMessage(message, msg, photo="IMAGES")


bot.add_handler(
    MessageHandler(
        countNode,
        filters=command(BotCommands.CountCommand)
        & CustomFilters.authorized
        & ~CustomFilters.blacklisted,
    )
)
