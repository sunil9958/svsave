# Copyright (c) 2025 devgagan : https://github.com/devgaganin.  
# Licensed under the GNU General Public License v3.0.  
# See LICENSE file in the repository root for full license text.

import os as O, re as R, time, asyncio
from pyrogram import Client as C, filters as F
from pyrogram.types import Message as M
from config import API_ID as A, API_HASH as H, LOG_GROUP, STRING
from utils.func import get_user_data
from utils.func import screenshot, thumbnail, get_video_metadata, get_user_data_key, process_text_with_rules, is_premium_user, E
from shared_client import app as X
from plugins.settings import rename_file
from utils.custom_filters import login_in_progress
from plugins.start import subscribe

Y = None if not STRING else __import__('shared_client').userbot

Z, W, P = {}, {}, {}


async def update_dialogs(client):
    """Update client dialogs to avoid peer connect errors"""
    try:
        async for _ in client.get_dialogs(limit=100):
            pass
        return True
    except Exception as e:
        print(f'Failed to update dialogs: {e}')
        return False
async def J(C, U, I, D, link_type):
    """Fetch message from source with enhanced peer resolution"""
    try:
        if link_type == 'public':
            try:
                return await C.get_messages(I, D)
            except Exception as e:
                print(f'Bot failed to get message: {e}')
                if U:
                    try:
                        async for _ in U.get_dialogs(limit=50):
                            pass
                        if not str(I).startswith('-100'):
                            try:
                                peer = await U.resolve_peer(I)
                                chat_id = peer.channel_id if hasattr(peer,
                                    'channel_id') else peer.user_id if hasattr(
                                    peer, 'user_id') else None
                                if not chat_id:
                                    chat = await U.join_chat(I)
                                    chat_id = chat.id
                            except Exception as e:
                                print(f'Resolve/Join failed: {e}')
                                try:
                                    chat = await U.get_chat(I)
                                    chat_id = chat.id
                                except Exception as e:
                                    print(f'Get chat failed: {e}')
                                    async for _ in U.get_dialogs(limit=100):
                                        pass
                                    return await U.get_messages(I, D)
                        else:
                            try:
                                peer = await U.resolve_peer(I)
                                chat_id = I
                            except Exception as e:
                                print(f'Resolve peer for channel failed: {e}')
                                chat_id = I
                        return await U.get_messages(chat_id, D)
                    except Exception as e:
                        print(f'Userbot also failed: {e}')
                        return None
        else:
            if U:
                try:
                    async for _ in U.get_dialogs(limit=50):
                        pass
                    chat_id = I if str(I).startswith('-100'
                        ) else f'-100{I}' if I.isdigit() else I
                    try:
                        peer = await U.resolve_peer(chat_id)
                        if hasattr(peer, 'channel_id'):
                            resolved_id = f'-100{peer.channel_id}'
                        elif hasattr(peer, 'chat_id'):
                            resolved_id = f'-{peer.chat_id}'
                        elif hasattr(peer, 'user_id'):
                            resolved_id = peer.user_id
                        else:
                            resolved_id = chat_id
                        print(f'Successfully resolved peer: {resolved_id}')
                        return await U.get_messages(resolved_id, D)
                    except Exception as e:
                        print(f'Resolve peer error: {e}')
                        try:
                            chat = await U.get_chat(chat_id)
                            print(
                                f"Successfully got chat: {getattr(chat, 'title', chat.id)}"
                                )
                            return await U.get_messages(chat.id, D)
                        except Exception as e:
                            print(f'Get chat failed: {e}')
                            print('Attempting final dialog refresh...')
                            async for _ in U.get_dialogs(limit=200):
                                pass
                            return await U.get_messages(chat_id, D)
                except Exception as e:
                    print(f'Private channel error: {e}')
                    return None
            return None
    except Exception as e:
        print(f'Error fetching message: {e}')
        return None
async def K(c, t, C, h, m, start_time):
    global P
    p = c / t * 100
    if t < 10 * 1024 * 1024:
        interval = 50
    elif t < 50 * 1024 * 1024:
        interval = 30
    elif t < 100 * 1024 * 1024:
        interval = 20
    else:
        interval = 10
    step = int(p // interval) * interval
    if m not in P or P[m] != step or p >= 100:
        P[m] = step
        c_mb = c / (1024 * 1024)
        t_mb = t / (1024 * 1024)
        bar = '🟢' * int(p / 10) + '🔴' * (10 - int(p / 10))
        speed = c / (time.time() - start_time) / (1024 * 1024) if time.time(
            ) > start_time else 0
        eta = time.strftime('%M:%S', time.gmtime((t - c) / (speed * 1024 * 
            1024))) if speed > 0 else '00:00'
        await C.edit_message_text(h, m,
            f"""__**Pyro Handler...**__\n
{bar}\n
⚡**__Completed__**: {c_mb:.2f} MB / {t_mb:.2f} MB
📊 **__Done__**: {p:.2f}%
🚀 **__Speed__**: {speed:.2f} MB/s
⏳ **__ETA__**: {eta}\n
**__Powered by Team PvFilmsX__**"""
            )
        if p >= 100:
            P.pop(m, None)
async def V(C, U, m, d, link_type, u):
    """Process and forward media with direct send for public groups"""
    try:
        configured_chat = await get_user_data_key(d, 'chat_id', None)
        target_chat_id = d
        reply_to_message_id = None
        if configured_chat:
            if '/' in configured_chat:
                parts = configured_chat.split('/', 1)
                target_chat_id = int(parts[0])
                reply_to_message_id = int(parts[1]) if len(parts) > 1 else None
            else:
                target_chat_id = int(configured_chat)
        if m.media:
            original_text = m.caption if m.caption else ''
            processed_text = await process_text_with_rules(d, original_text)
            user_caption = await get_user_data_key(d, 'caption', '')
            if processed_text and user_caption:
                final_text = f'{processed_text}\n\n{user_caption}'
            elif user_caption:
                final_text = user_caption
            else:
                final_text = processed_text
            if link_type == 'public':
                if await send_via_file_id(C, m, target_chat_id, final_text,
                    reply_to_message_id):
                    return 'Media sent directly via file_id.'
            st = time.time()
            P = await C.send_message(d, 'Downloading...')
            W[u] = {'cancel': False, 'progress': P.id}
            F = await U.download_media(m, progress=K, progress_args=(C, d,
                P.id, st))
            if W.get(u, {}).get('cancel'):
                await C.edit_message_text(d, P.id, 'Canceled.')
                if O.path.exists(F):
                    O.remove(F)
                W.pop(u, None)
                return 'Canceled.'
            if not F:
                await C.edit_message_text(d, P.id, 'Failed.')
                W.pop(u, None)
                return 'Failed.'
            F = await rename_file(F, d, P)
            file_size = O.path.getsize(F) / (1024 * 1024 * 1024)
            th = thumbnail(d)
            if file_size > 2 and Y:
                st = time.time() # fixed uploading speed
                await C.edit_message_text(d, P.id,
                    'File is larger than 2GB. Sending via alternative method...'
                    )
                await update_dialogs(Y)
                mtd = await get_video_metadata(F)
                duration, h, w = mtd['duration'], mtd['width'], mtd['height']
                th = await screenshot(F, duration, d)
                send_funcs = {'video': Y.send_video, 'video_note': Y.
                    send_video_note, 'voice': Y.send_voice, 'audio': Y.
                    send_audio, 'photo': Y.send_photo, 'document': Y.
                    send_document}
                for media_type, func in send_funcs.items():
                    if F.endswith('.mp4'):
                        media_type = 'video'
                    if getattr(m, media_type, None):
                        sent_message = await func(LOG_GROUP, F, thumb=th if
                            media_type == 'video' else None, duration=
                            duration if media_type == 'video' else None,
                            height=h if media_type == 'video' else None,
                            width=w if media_type == 'video' else None,
                            caption=final_text if m.caption and media_type !=
                            'video_note' and media_type != 'voice' else
                            None, reply_to_message_id=reply_to_message_id,
                            progress=K, progress_args=(C, d, P.id, st))
                        break
                else:
                    sent_message = await Y.send_document(LOG_GROUP, F,
                        thumb=th, caption=final_text if m.caption else None,
                        reply_to_message_id=reply_to_message_id, progress=K,
                        progress_args=(C, d, P.id, st))
                await C.copy_message(target_chat_id, LOG_GROUP, sent_message.id
                    )
                O.remove(F)
                await C.delete_messages(d, P.id)
                W.pop(u, None)
                return 'Done (Large file sent via alternative method).'
            await C.edit_message_text(d, P.id, 'Uploading...')
            st = time.time() # uploading time 
            if m.video or O.path.splitext(F)[1].lower() == '.mp4':
                mtd = await get_video_metadata(F)
                duration, h, w = mtd['duration'], mtd['width'], mtd['height']
                th = await screenshot(F, duration, d)
                await C.send_video(target_chat_id, video=F, caption=
                    final_text if m.caption else None, thumb=th, width=w,
                    height=h, duration=duration, progress=K, progress_args=
                    (C, d, P.id, st), reply_to_message_id=reply_to_message_id)
            elif m.video_note:
                await C.send_video_note(target_chat_id, video_note=F,
                    progress=K, progress_args=(C, d, P.id, st),
                    reply_to_message_id=reply_to_message_id)
            elif m.voice:
                await C.send_voice(target_chat_id, F, progress=K,
                    progress_args=(C, d, P.id, st), reply_to_message_id=
                    reply_to_message_id)
            elif m.sticker:
                await C.send_sticker(target_chat_id, m.sticker.file_id)
            elif m.audio:
                await C.send_audio(target_chat_id, audio=F, caption=
                    final_text if m.caption else None, thumb=th, progress=K,
                    progress_args=(C, d, P.id, st), reply_to_message_id=
                    reply_to_message_id)
            elif m.photo:
                await C.send_photo(target_chat_id, photo=F, caption=
                    final_text if m.caption else None, progress=K,
                    progress_args=(C, d, P.id, st), reply_to_message_id=
                    reply_to_message_id)
            elif m.document:
                await C.send_document(target_chat_id, document=F, caption=
                    final_text if m.caption else None, progress=K,
                    progress_args=(C, d, P.id, st), reply_to_message_id=
                    reply_to_message_id)
            O.remove(F)
            await C.delete_messages(d, P.id)
            W.pop(u, None)
            return 'Done.'
        elif m.text:
            await C.send_message(target_chat_id, text=m.text.markdown,
                reply_to_message_id=reply_to_message_id)
            return 'Sent.'
    except Exception as e:
        return f'Error: {e}'
async def get_user_client(user_id):
    """Get or create user client"""
    user_data = await get_user_data(user_id)
    if not user_data:  # fixing kr ths nonetype
        print(f"User data not found for user_id: {user_id}")
        return X
    session_string = user_data.get('session_string')
    ss_name = f'{user_id}_bot'
    if session_string:
        try:
            gg = C(ss_name, api_id=A, api_hash=H, session_string=session_string
                )
            await gg.start()
            await update_dialogs(gg)
            return gg
        except Exception as e:
            print(f'User client error: {e}')
            if Y is None:
                return X
            if Y:
                await update_dialogs(Y)
            return Y
    elif Y is None:
        return X
    if Y:
        await update_dialogs(Y)
    return Y

async def prompt_userbot_login(user_id):
    """Prompt user to add session if default userbot not available"""
    chat = await X.get_chat(user_id)
    await X.send_message(chat.id,
        '⚠️ Default userbot not available. Please add your session using /addsession command.'
        )
    return None
async def send_via_file_id(C, m, target_chat_id, final_text=None,
    reply_to_message_id=None):
    """Try to send media directly using file_id without downloading"""
    try:
        if m.video:
            await C.send_video(target_chat_id, m.video.file_id, caption=
                final_text, duration=m.video.duration, width=m.video.width,
                height=m.video.height, reply_to_message_id=reply_to_message_id)
        elif m.video_note:
            await C.send_video_note(target_chat_id, m.video_note.file_id,
                reply_to_message_id=reply_to_message_id)
        elif m.voice:
            await C.send_voice(target_chat_id, m.voice.file_id,
                reply_to_message_id=reply_to_message_id)
        elif m.sticker:
            await C.send_sticker(target_chat_id, m.sticker.file_id,
                reply_to_message_id=reply_to_message_id)
        elif m.audio:
            await C.send_audio(target_chat_id, m.audio.file_id, caption=
                final_text, duration=m.audio.duration, performer=m.audio.
                performer, title=m.audio.title, reply_to_message_id=
                reply_to_message_id)
        elif m.photo:
            photo_file_id = m.photo.file_id if hasattr(m.photo, 'file_id'
                ) else m.photo[-1].file_id
            await C.send_photo(target_chat_id, photo_file_id, caption=
                final_text, reply_to_message_id=reply_to_message_id)
        elif m.document:
            await C.send_document(target_chat_id, m.document.file_id,
                caption=final_text, file_name=m.document.file_name,
                reply_to_message_id=reply_to_message_id)
        else:
            return False
        return True
    except Exception as e:
        print(f'Direct send error: {e}')
        return False
@X.on_message(F.command('batch'))
async def batch_cmd(C, m: M):
    U = m.from_user.id
    subscription_status = await subscribe(C, m)
    if subscription_status == 1:
        return
    
    if not await is_premium_user(U):
        await m.reply_text(
            'You need premium for this operation send /plan to proceed for payment'
            )
        return
    if U in W:
        await m.reply_text(
            'You have an active download in progress. Please wait or use /stop.'
            )
        return
    Z[U] = {'step': 'start'}
    await m.reply_text('Send start link.')
@X.on_message(F.command('single'))
async def single_cmd(C, m: M):
    U = m.from_user.id
    subscription_status = await subscribe(C, m)
    if subscription_status == 1:
        return
    if not await is_premium_user(U):
        await m.reply_text(
            'You need premium for this operation send /plan to proceed for payment'
            )
        return
    if U in W:
        await m.reply_text(
            'You have an active download in progress. Please wait or use /stop.'
            )
        return
    Z[U] = {'step': 'start_single'}
    await m.reply_text('Send the link you want to process.')
@X.on_message(F.command(['cancel', 'stop']))
async def cancel_cmd(C, m: M):
    U = m.from_user.id
    if U in W:
        W[U]['cancel'] = True
        await m.reply_text('Cancelling...')
    else:
        await m.reply_text('No active task.')



@X.on_message(F.text & ~login_in_progress & ~F.command([
    'start', 'batch', 'cancel', 'login', 'logout', 'stop', 'set', 
    'pay', 'redeem', 'gencode', 'single']))
async def text_handler(C, m: M):
    U = m.from_user.id
    if U not in Z:
        return

    S = Z[U].get('step')

    if S == 'start':
        L = m.text
        I, D, link_type = E(L)
        if not I or not D:
            await m.reply_text('Invalid link. Please check the format.')
            Z.pop(U, None)
            return
        Z[U].update({'step': 'count', 'cid': I, 'sid': D, 'lt': link_type})
        await m.reply_text('How many messages?')

    elif S == 'start_single':
        L = m.text
        I, D, link_type = E(L)
        if not I or not D:
            await m.reply_text('Invalid link. Please check the format.')
            Z.pop(U, None)
            return

        Z[U].update({'step': 'process_single', 'cid': I, 'sid': D, 'lt': link_type})
        I, S, link_type = Z[U]['cid'], Z[U]['sid'], Z[U]['lt']

        pt = await m.reply_text('Processing...')
        user_client = await get_user_client(U)
        if not user_client:
            await pt.edit('Cannot proceed without a user client. Add session or wait for admin to add default userbot.')
            Z.pop(U, None)
            return
        if U in W:
            await pt.edit('You already have an active task. Please wait or use /cancel.')
            Z.pop(U, None)
            return

        W[U] = {'cancel': False}
        try:
            msg = await J(C, user_client, I, S, link_type)
            if msg:
                res = await V(C, user_client, msg, str(m.chat.id), link_type, U)
                await pt.edit(f'1/1: {res}')
            else:
                await pt.edit('1/1: Message not found')
        except Exception:
            pass 
        finally:
            W.pop(U, None)
            Z.pop(U, None)

    elif S == 'count':
        if not m.text.isdigit():
            await m.reply_text('Enter a valid number.')
            return

        D = str(m.chat.id)
        Z[U].update({'step': 'process', 'did': D, 'num': int(m.text)})
        I, S, N, link_type = Z[U]['cid'], Z[U]['sid'], Z[U]['num'], Z[U]['lt']
        R = 0

        pt = await m.reply_text('Processing...')
        user_client = await get_user_client(U)
        if not user_client:
            await pt.edit('Cannot proceed without a user client. Add session or wait for admin to add default userbot.')
            Z.pop(U, None)
            return
        if U in W:
            await pt.edit('You already have an active task. Please wait or use /cancel.')
            Z.pop(U, None)
            return

        W[U] = {'cancel': False}
        try:
            for i in range(N):
                if W.get(U, {}).get('cancel'):
                    await pt.edit(f'Batch cancelled at {i}/{N}')
                    break

                M = S + i
                try:
                    msg = await J(C, user_client, I, M, link_type)
                    if msg:
                        res = await V(C, user_client, msg, D, link_type, U)
                        await pt.edit(f'{i + 1}/{N}: {res}')
                        if 'Done' in res or 'Copied' in res or 'Sent' in res:
                            R += 1
                    else:
                        await pt.edit(f'{i + 1}/{N}: Message not found')
                except Exception:
                    pass 
                
                await asyncio.sleep(10)

            await m.reply_text(f'Batch Completed ✅\nSuccessful: {R}/{N}')
        
        finally:
            W.pop(U, None)
            Z.pop(U, None)
            
