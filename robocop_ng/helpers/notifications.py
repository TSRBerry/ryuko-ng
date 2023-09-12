import json
from typing import Optional, Union

from discord import Message, MessageReference, PartialMessage


MessageReferenceTypes = Union[Message, MessageReference, PartialMessage]


async def notify_management(
    bot, message: str, reference_message: Optional[MessageReferenceTypes] = None
):
    log_channel = await bot.get_channel_safe(bot.config.botlog_channel)
    bot_manager_role = log_channel.guild.get_role(bot.config.bot_manager_role_id)

    notification_message = f"{bot_manager_role.mention}:\n"

    if reference_message is not None and reference_message.channel != log_channel:
        notification_message += f"Message reference: {reference_message.jump_url}\n"
        notification_message += message

        return await log_channel.send(notification_message)
    else:
        notification_message += message

        return await log_channel.send(
            notification_message,
            reference=reference_message,
            mention_author=False,
        )


async def report_critical_error(
    bot,
    error: BaseException,
    reference_message: Optional[MessageReferenceTypes] = None,
    additional_info: Optional[dict] = None,
):
    message = "⛔ A critical error occurred!"

    if additional_info is not None:
        message += f"""
            ```json
            {json.dumps(additional_info)}
            ```"""

    message += f"""
        Exception:
        ```
        {error}
        ```"""

    return await notify_management(bot, message, reference_message)
