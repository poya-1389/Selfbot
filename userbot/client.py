from telethon import TelegramClient
from telethon.sessions import StringSession

class UserBotClient:
    def __init__(self, session_string, api_id, api_hash):
        self.client = TelegramClient(
            StringSession(session_string),
            api_id,
            api_hash
        )
    
    async def start(self):
        await self.client.start()
        return await self.client.get_me()
    
    async def disconnect(self):
        await self.client.disconnect()
