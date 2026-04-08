import os
import re
from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter
from langchain.agents import create_agent
from products import products_list

load_dotenv()

# -------------------------------
# Customer Care Data
# -------------------------------
COMPANY_NAME = "Rock Jock Dummy"

PRODUCT_LIST = products_list

ABOUT_TEXT = (
    f"{COMPANY_NAME} is a car parts company providing high-quality automotive components. "
    "We help customers choose the right parts and provide after-sale support."
)

GREETINGS = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]

# -------------------------------
# Utils
# -------------------------------
def clean_text(text: str):
    text = re.sub(r'[#*_`>-]', '', text)
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

# -------------------------------
# Initialize Model
# -------------------------------
model = ChatOpenRouter(
    model="nvidia/nemotron-3-super-120b-a12b:free",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# -------------------------------
# Agent
# -------------------------------
class CustomerCareAgent:
    def __init__(self, model, product_list, about_text, greetings, tools=[]):
        self.model = model
        self.product_list = product_list
        self.about_text = about_text
        self.greetings = greetings
        self.agent = create_agent(model=model, tools=tools)

        # Memory per user
        self.memory = {}  # {user_id: [messages]}

    def is_greeting(self, message: str):
        return any(word in message.lower() for word in self.greetings)

    def get_response(self, message: str, user_id: int, fresh_user=False):

        # Greeting logic
        # if self.is_greeting(message) or fresh_user:
        #     return f"Hello. Welcome to {COMPANY_NAME}. How can I assist you?"

        # Initialize memory
        if user_id not in self.memory:
            self.memory[user_id] = []

        # Add user message
        self.memory[user_id].append({
            "role": "user",
            "content": message
        })

        # Keep last 5 messages (avoid token overflow)
        self.memory[user_id] = self.memory[user_id][-5:]

        # System context
        system_context = (
            f"You are a customer support assistant for {COMPANY_NAME}.\n"
            f"Company info: {self.about_text}\n"
            f"Products: {', '.join(self.product_list)}\n"
            f"Rules:\n"
            f"- Keep responses very short (max 5-6 sentences)\n"
            f"- No markdown or formatting symbols\n"
            f"- Be direct and helpful\n"
            f"- If unsure, say you don't know\n"
        )

        # Invoke agent
        response = self.agent.invoke({
            "messages": [
                {"role": "system", "content": system_context},
                *self.memory[user_id]
            ]
        })

        # Extract last assistant message safely
        reply = response["messages"][-1].content

        # Save assistant reply in memory
        self.memory[user_id].append({
            "role": "assistant",
            "content": reply
        })

        return clean_text(reply)

# -------------------------------
# Example usage
# -------------------------------
if __name__ == "__main__":
    agent_instance = CustomerCareAgent(
        model=model,
        product_list=PRODUCT_LIST,
        about_text=ABOUT_TEXT,
        greetings=GREETINGS,
    )

    # Test
    print(agent_instance.get_response("Hi there!", user_id=1, fresh_user=True))
    print(agent_instance.get_response("Can you tell me about your spark plugs?", user_id=1))