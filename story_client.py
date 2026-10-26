from ollama import AsyncClient
from Utils import State, History, Message
import asyncio
import aiofiles

class Client:
    def __init__(self, model, logs):
        self.state = State() 
        self.history : History = None
        self.conv_len = 0
        self.model = model if model is not None else 'gemma4:cloud'
        self.thinking_logs = True if logs is not None else logs
        self.thoughts = []
        self.async_client = AsyncClient()
        self.create_thoughts()

    def create_thoughts(self):
        thought = "This document highlights the agent thought during the game\n"
        with open(self.state.thoughts_path, mode = 'w', encoding='utf-8') as file:
            file.write(thought)

    async def update_thoughts(self, thought:str):
        if self.thinking_logs is False:
            return
        self.thoughts.append(thought)
        async with aiofiles.open(self.state.thoughts_path, mode='a', encoding='utf-8') as file:
            await file.write(f"conversation : {self.conv_len}\n =========== \n")
            await file.write(thought + '\n' + '========\n')

    async def stream_reply(self):
        stream = await self.async_client.chat(
            model = self.model,
            messages=self.history.get_messages(),
            stream = True
        )

        reply = ''
        thought = ''
        async for chunk in stream:
            if chunk.message.thinking and self.thinking_logs:
                # print(chunk.message.thinking, end='', flush=True)
                thought += chunk.message.thinking
            else:
                print(chunk.message.content, end='',flush=True)
                reply += chunk.message.content
        print('\n');

        self.conv_len += 1

        await self.update_thoughts(thought)
        self.history.add_message(Message(reply, 'assistant'))
        self.history.manage_list()

    async def load(self):
        prompt = self.state.prompt
        sys_message = Message(
            role='system',
            content=prompt,
        )
        self.history = History(sys_message)
        await self.stream_reply()


    async def call(self, message:Message):
        msgs = None
        if message is None:
            return

        self.history.add_message(message)
        await self.stream_reply()

    async def run(self):
        await self.load() # We are passing only system prompt
        print("Welcome to the game: ")
        while True:
            content = input("User: ")
            msg = Message(content, 'user')
            await self.call(msg)
            

if __name__ == "__main__":
    client = Client('gemma4:e2b', True)
    loop = client.run()
    asyncio.run(loop)
