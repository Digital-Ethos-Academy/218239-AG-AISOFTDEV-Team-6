import json
import os
from typing import Annotated, TypedDict
import asyncio
import websockets
import time

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph.message import add_messages
from langgraph.graph import START, StateGraph, END
import sys 
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

class ActionItem(TypedDict):
    content: str
    assignee: str
    due_date: str
    priority: str

class AgentState(TypedDict):
    notes: str
    action_items: list[ActionItem]
    messages: Annotated[list[BaseMessage], add_messages]

endpoint = os.getenv("CHAT_ENDPOINT", "ws://localhost:8000/chat")

def remove_markdown_wrapper(text: str) -> str:
    """Remove the markdown code block wrapper from the text."""
    if text.startswith("```") and text.endswith("```"):
        # might have a language specifier, so we split by newlines
        lines = text.split("\n")
        if len(lines) > 2:
            return "\n".join(lines[1:-1]).strip()
    return text.strip()

def note_taking_agent(state: AgentState) -> AgentState:
    # if last message contains "/show notes", return the notes
    if state["messages"] and isinstance(state["messages"][-1], HumanMessage):
        last_message = state["messages"][-1]
        # Check if the message content contains "/show notes" (case insensitive)
        if "/show notes" in last_message.content.lower():
            notes_display = f"📝 **Current Notes:**\n{state['notes']}\n\n✅ **Action Items:**\n"
            if state['action_items']:
                for i, item in enumerate(state['action_items'], 1):
                    notes_display += f"{i}. {item['content']} (Assignee: {item['assignee']}, Due: {item['due_date']}, Priority: {item['priority']})\n"
            else:
                notes_display += "No action items yet.\n"
            
            state["messages"].append(
                AIMessage(content=notes_display)
            )
            return state
        
    # this agent monitors the messages to take notes and action items
    human_messages = "\n".join(
        [msg.content for msg in state["messages"] if isinstance(msg, HumanMessage)][-10:]  # last 10 human messages
    )
    
    # Only process if there are actual messages to analyze
    if not human_messages.strip():
        return state
        
    prompt = f"""You are a note-taking agent. Your task is to extract notes and action items from the conversation.
    Current conversation:
    {human_messages}

    Current notes:
    ```markdown
    {state['notes']}
    ```
    Current action items:
    ```json
    {json.dumps(state['action_items'], indent=2)}
    ```
    Please update the notes and action items based on the conversation.
    Respond in raw JSON with the following format:
    {{
    "notes": "<markdown formatted notes>",
    "action_items": [
        {{
            "content": "<action item content>",
            "assignee": "<assignee name>",
            "due_date": "<due date in YYYY-MM-DD format>",
            "priority": "<priority level>"
        }}
    ]
    }}
    Do not wrap the response in any other text or markdown.
    """
    response = remove_markdown_wrapper(llm.invoke(prompt).content.strip())

    # Update the state with the new notes and action items
    if response:
        try:
            data = json.loads(response)
            # Check if notes or action items changed
            notes_changed = data["notes"] != state["notes"]
            action_items_changed = data["action_items"] != state["action_items"]
            
            state["notes"] = data["notes"]
            state["action_items"] = data["action_items"]
            
            # Don't add automatic update messages - agent is silent unless asked
            
        except json.JSONDecodeError:
            # Don't add error messages to chat - just log them
            print("⚠️ Error parsing response from note-taking agent.")
    return state

class NoteTakingAgent:
    def __init__(self):
        self.state = {
            "notes": "",
            "action_items": [],
            "messages": []
        }
        self.websocket = None
        self.username = "NoteTaker"

    async def connect_to_chat(self, uri: str = endpoint):
        """Connect to the WebSocket chat endpoint"""
        try:
            self.websocket = await websockets.connect(uri)
            print(f"✅ Connected to chat server at {uri}")
            
            # Send initial message
            await self.send_message("📝 Note-taking agent active. I'll track notes and action items from the conversation. Type '/show notes' to see current notes.")
            
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
        
        # Handle /show notes command directly
        if "/show notes" in message_content.lower():
            notes_summary = f"📝 **Current Notes:**\n{self.state['notes']}\n\n✅ **Action Items:**\n"
            if self.state['action_items']:
                for i, item in enumerate(self.state['action_items'], 1):
                    notes_summary += f"{i}. {item['content']} (Assignee: {item['assignee']}, Due: {item['due_date']}, Priority: {item['priority']})\n"
            else:
                notes_summary += "No action items yet.\n"
            await self.send_message(notes_summary)
            return
            
        # Add message to state for normal processing
        self.state["messages"].append(HumanMessage(content=f"{sender}: {message_content}"))
        
        # Process through the agent silently
        result = graph.invoke(self.state)
        self.state = result
        
        # Don't send automatic responses - agent only responds to /show notes
    
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
    """Main async function to run the note-taking agent"""
    agent = NoteTakingAgent()
    
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
                if user_input.lower() == "/show notes":
                    notes_summary = f"📝 Current Notes:\n{agent.state['notes']}\n\n✅ Action Items:\n"
                    for item in agent.state['action_items']:
                        notes_summary += f"- {item['content']} (Assignee: {item['assignee']}, Due: {item['due_date']}, Priority: {item['priority']})\n"
                    await agent.send_message(notes_summary)
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
workflow.add_node("NoteTaking", note_taking_agent)
workflow.add_edge(START, "NoteTaking")
workflow.add_edge("NoteTaking", END)
graph = workflow.compile()

if __name__ == "__main__":
    # WebSocket-based note-taking agent
    print("📝 Starting Note-Taking Agent")
    print("Usage: python agent2.py")
    print(f"The agent will connect to {endpoint} and track notes and action items")
    print("Commands:")
    print("  /show notes - Display current notes and action items")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Agent stopped by user")
# This code defines a note-taking agent that connects to WebSocket chat and tracks notes and action items.