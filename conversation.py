from langchain import PromptTemplate
from langchain.chains import ConversationChain
from langchain.chat_models import AzureChatOpenAI
from langchain.memory import ConversationBufferMemory


class Conversation:
    def __init__(self, username):
        with open('system.txt', 'r') as f:
            template = f.read().replace('{username}', username)

        prompt = PromptTemplate(
            input_variables=["history", "input"],
            template=template,
        )

        llm = AzureChatOpenAI(
            openai_api_type="azure",
            deployment_name="chatgpt",
            openai_api_version="2023-03-15-preview",
            temperature=0.7,
        )
        memory = ConversationBufferMemory(memory_key="history", return_messages=True)
        self.conversation = ConversationChain(
            llm=llm,
            verbose=False,
            prompt=prompt,
            memory=memory
        )

    def __call__(self, text):
        return self.conversation.predict(input=text)
