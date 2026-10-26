import os
from dotenv import load_dotenv

class State:
    def __init__(self):
        self.api_key = None
        self.prompt_path = None
        self.thoughts_path = None
        self.LOAD_ENV()

    def LOAD_ENV(self):
        load_dotenv()
    
        api_key = os.getenv('OLLAMA_API_KEY')
        if api_key == None:
            raise ValueError("API KEY not found")
        self.api_key = api_key

        story_prompt_path = os.getenv('STORY_PROMPT_PATH')
        if story_prompt_path == None:
            raise ValueError("System Prompt Path Not Found")
        self.prompt_path = story_prompt_path
        
        prompt = self.get_system_prompt()
        if not prompt:
            raise ValueError("System Prompt not found")
        self.prompt = prompt

        thought_path = os.getenv("AGENT_THOUGHTS_PATH")
        if thought_path == None:
            raise ValueError("Thoughts path not found")
        self.thoughts_path = thought_path

    def get_system_prompt(self):
        with open(self.prompt_path, 'r', encoding='utf-8') as file:
            story_prompt = file.read()
        return story_prompt
    

class Message:
    def __init__(self, content, role):
        self.content = content
        self.role = role

    def get_message(self):
        return {
            'role' : self.role,
            'content': self.content
        }
    
class History:
    def __init__(self, system_prompt_message: Message):
        self.system_prompt_message = system_prompt_message
        self.msg_history = [self.system_prompt_message.get_message()]

    def add_message(self, message: Message):
        self.msg_history.append(message.get_message())

    def __len__(self):
        return len(self.msg_history)

    def get_messages(self):
        return self.msg_history

    def manage_list(self):   
    ### To manage the context for the agent. 
        if len(self.msg_history) < 11:
            return

        self.msg_history = self.msg_history[9:]
        self.msg_history.insert(0, self.system_prompt_message)
        