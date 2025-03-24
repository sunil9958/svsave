# Copyright (c) 2025 devgagan : https://github.com/devgaganin.  
# Licensed under the GNU General Public License v3.0.  
# See LICENSE file in the repository root for full license text.


#soon

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Bot ke admin ka Telegram ID
ADMIN_ID = 5390137933  # Yahan apna Telegram ID set karein
UPI_ID = "sunil.verma060@ybl"  # Yahan apni UPI ID set karein

# Pay command
@Client.on_message(filters.command("pay"))
async def pay_command(client, message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name

    # Payment message
    text = f"🤑 *Payment Details* 🤑\n\n👤 User: {first_name} (`{user_id}`)\n💰 Amount: ₹50\n📌 UPI ID: `{UPI_ID}`\n\n✅ Payment karne ke baad *screenshot* bhejein aur admin approve karega!"
    
    # Payment buttons
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Paid (Admin Approve)", callback_data=f"approve_{user_id}")]
    ])
    
    # User ko payment message bhejna
    await message.reply(text, reply_markup=keyboard, parse_mode="Markdown")

    # Admin ko notification
    admin_text = f"🔔 *New Payment Request!*\n👤 User: {first_name} (`{user_id}`)\n💰 Amount: ₹50\n📌 UPI ID: `{UPI_ID}`\n\n👀 *Approve karne ke liye button dabaye!*"
    await client.send_message(ADMIN_ID, admin_text, reply_markup=keyboard)

# Admin approval system
@Client.on_callback_query(filters.regex(r"approve_(\d+)"))
async def approve_payment(client, callback_query):
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("⛔ Sirf admin approve kar sakta hai!", show_alert=True)
        return

    user_id = int(callback_query.data.split("_")[1])
    await client.send_message(user_id, "✅ Aapka payment approve ho gaya! Shukriya! 🎉")

    await callback_query.answer("✅ Payment approved!")
    await callback_query.message.edit_text("✅ Payment Approved! 🎉", reply_markup=None)
