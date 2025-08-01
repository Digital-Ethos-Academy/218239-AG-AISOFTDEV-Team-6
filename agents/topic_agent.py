import os
from typing import Annotated, TypedDict
import asyncio
import websockets
import json
import sys
import time

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph.message import add_messages
from langgraph.graph import START, StateGraph, END
import dotenv
dotenv.load_dotenv(".env")
# Ensure the Google API key is set in your environment variables
# For example: os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY"
if "GOOGLE_API_KEY" not in os.environ:
    raise ValueError(
        "GOOGLE_API_KEY environment variable not set. Please set it to your API key."
    )

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    max_tokens=4096,
    api_key=os.environ["GOOGLE_API_KEY"],
)

endpoint = os.getenv("CHAT_ENDPOINT", "ws://localhost:8000/chat")

class AgentState(TypedDict):
    topic: str
    relevance: float
    messages: Annotated[list[BaseMessage], add_messages]

def topic_monitor_agent(state: AgentState) -> AgentState:
    # this agent monitors the messages to see if it matches the topic
    # check if the last message is a human message setting the topic
    if state["messages"] and isinstance(state["messages"][-1], HumanMessage):
        last_message = state["messages"][-1]
        if last_message.content.lower().startswith("topic:"):
            state["topic"] = last_message.content[6:].strip()
        
    # if topic is set invoke llm to check if the messages match the topic
    if state["topic"]:
        messages = [msg.content for msg in state["messages"] if isinstance(msg, (HumanMessage))]
        if messages:  # Only process if there are messages
            response = llm.invoke(f"""Do the following messages match the topic '{state['topic']}'? {messages[-10:]}
Give it a relevance score from 0 to 1, where 0 means no relevance and 1 means high relevance.
Respond with just the score, no other text.
                                  """)
            try:
                state["relevance"] = float(response.content.strip())
                if state["relevance"] < 0.5:
                    # add message indicating low relevance
                    state["messages"].append(
                        AIMessage(
                            content=f"⚠️ Low relevance to topic '{state['topic']}'. Relevance score: {state['relevance']:.2f}"
                        )
                    )
            except ValueError:
                # Handle case where LLM doesn't return a valid number
                state["relevance"] = 0.0
    return state

class ChatAgent:
    def __init__(self, topic: str = None):
        self.state = {
            "topic": topic,
            "relevance": 0.0,
            "messages": []
        }
        if topic:
            self.state["messages"].append(HumanMessage(content=f"Topic: {topic}"))
        self.websocket = None
        self.username = "TopicAgent"

    async def connect_to_chat(self, uri: str = endpoint):
        """Connect to the WebSocket chat endpoint"""
        try:
            self.websocket = await websockets.connect(uri)
            print(f"✅ Connected to chat server at {uri}")
            
            # Send initial message if topic is set
            if self.state["topic"]:
                await self.send_message(f"🤖 Topic monitoring agent active. Monitoring topic: '{self.state['topic']}'")
            
            return True
        except Exception as e:
            print(f"❌ Failed to connect to chat server: {e}")
            return False
    
    async def send_message(self, message: str):
        """Send a message through the WebSocket"""
        if self.websocket:
            message_data = {
                "type": "broadcast",
                "user": self.username,
                "message": message,
                "timestamp": time.time()
            }
            await self.websocket.send(json.dumps(message_data))
    
    async def process_message(self, message_content: str, sender: str):
        """Process incoming chat message through the agent"""
        if sender == self.username:
            return  # Don't process our own messages
            
        # Add message to state
        self.state["messages"].append(HumanMessage(content=message_content))
        
        # Process through the agent
        result = graph.invoke(self.state)
        self.state = result
        
        # Check if agent generated any responses
        for msg in result["messages"]:
            if isinstance(msg, AIMessage) and msg not in self.state["messages"][:-1]:
                await self.send_message(msg.content)
    
    async def listen_to_chat(self):
        """Listen for incoming messages from the chat"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    if data.get("type") == "message":
                        sender = data.get("user", "Unknown")
                        message_content = data.get("message", "")
                        print(f"📨 Received: {sender}: {message_content}")
                        await self.process_message(message_content, sender)
                except json.JSONDecodeError:
                    print(f"⚠️ Received invalid JSON: {message}")
        except websockets.exceptions.ConnectionClosed:
            print("🔌 WebSocket connection closed")
        except Exception as e:
            print(f"❌ Error listening to chat: {e}")
    
    async def run(self):
        """Main run loop for the agent"""
        if await self.connect_to_chat():
            await self.listen_to_chat()
        else:
            print("Failed to connect to chat server")

async def main():
    """Main async function to run the chat agent"""
    topic = os.getenv("TOPIC", "Rock Music")
    if len(sys.argv) >= 2:
        topic = sys.argv[1]
    
    agent = ChatAgent(topic)
    
    # Start the agent in the background
    agent_task = asyncio.create_task(agent.run())

    # Only run manual input if stdin is a TTY (interactive)
    if sys.stdin.isatty():
        try:
            while True:
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, input, "Manual input (or 'exit' to quit): "
                )
                if user_input.lower() in ["exit", "quit"]:
                    break
                if user_input.startswith("topic:"):
                    new_topic = user_input[6:].strip()
                    agent.state["topic"] = new_topic
                    await agent.send_message(f"🎯 Topic updated to: '{new_topic}'")
                else:
                    await agent.send_message(f"Manual: {user_input}")
        except KeyboardInterrupt:
            print("\n👋 Shutting down agent...")
        finally:
            agent_task.cancel()
            try:
                await agent_task
            except asyncio.CancelledError:
                pass
    else:
        # Just run the agent loop, no manual input
        await agent_task

workflow = StateGraph(AgentState)
workflow.add_node("TopicMonitor", topic_monitor_agent)
workflow.add_edge(START, "TopicMonitor")
workflow.add_edge("TopicMonitor", END)
graph = workflow.compile()

if __name__ == "__main__":
    # WebSocket-based chat agent
    print("🤖 Starting Topic Monitoring Agent")
    print("Usage: python agent.py [topic]")
    print(f"The agent will connect to {endpoint} and monitor messages")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Agent stopped by user")
# This code defines an agent that connects to WebSocket chat and monitors messages for topic relevance.
