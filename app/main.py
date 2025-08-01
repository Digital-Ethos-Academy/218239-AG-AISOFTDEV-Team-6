
from fastapi.concurrency import asynccontextmanager
from database import get_db, engine
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import validation_models.pd_models as pd_models
import validation_models.sql_models as sql_models
from validation_models.sql_models import Base
from typing import List
import json
import asyncio

#get db
db: Session = next(get_db())

# Functions to interact with the database.

def create_db_item(model, schema):
    data = schema.model_dump()
    
    # map password to password_hash if it exists
    if 'password' in data:
        data['password_hash'] = data.pop('password')
    db_item = model(**data)

    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_db_item(model, item_id: int):
    return db.query(model).filter(model.id == item_id).first()

def get_all_db_items(model, skip: int = 0, limit: int = 100):
    return db.query(model).offset(skip).limit(limit).all()

def update_db_item(db_item, schema):
    update_data = schema.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_db_item(db_item):
    db.delete(db_item)
    db.commit()


# --- 5. API Routers ---
# Grouping endpoints by entity for better organization.

# --- Generic CRUD Router Factory ---
def create_crud_router(
    *,
    router_name: str,
    prefix: str,
    db_model,
    create_schema,
    read_schema,
    update_schema = None,
    tags: list[str]
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=tags)

    @router.post("/", response_model=read_schema, status_code=status.HTTP_201_CREATED)
    def create_item(item_in: dict):
        schema_obj = create_schema.model_validate(item_in)
        return create_db_item(model=db_model, schema=schema_obj)

    @router.get("/", response_model=List[read_schema])
    def read_items(skip: int = 0, limit: int = 100):
        return get_all_db_items(model=db_model, skip=skip, limit=limit)

    @router.get("/{item_id}", response_model=read_schema)
    def read_item(item_id: int):
        db_item = get_db_item(model=db_model, item_id=item_id)
        if db_item is None:
            raise HTTPException(status_code=404, detail=f"{router_name} not found")
        return db_item

    if update_schema is not None:
        @router.put("/{item_id}", response_model=read_schema)
        def update_item(item_id: int, item_in: dict):
            db_item = get_db_item(model=db_model, item_id=item_id)
            if db_item is None:
                raise HTTPException(status_code=404, detail=f"{router_name} not found")
            schema_obj = update_schema.model_validate(item_in)
            return update_db_item(db_item=db_item, schema=schema_obj)

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_item(item_id: int):
        db_item = get_db_item(model=db_model, item_id=item_id)
        if db_item is None:
            raise HTTPException(status_code=404, detail=f"{router_name} not found")
        delete_db_item(db_item=db_item)
        return None

    return router

# Create routers for each entity
router_orgs = create_crud_router(router_name="Organization", prefix="/organizations", db_model=sql_models.Organization, create_schema=pd_models.OrganizationCreate, read_schema=pd_models.Organization, update_schema=pd_models.OrganizationUpdate, tags=["Organizations"])
router_users = create_crud_router(router_name="User", prefix="/users", db_model=sql_models.User, create_schema=pd_models.UserCreate, read_schema=pd_models.User, update_schema=pd_models.UserUpdate, tags=["Users"])
router_meetings = create_crud_router(router_name="Meeting", prefix="/meetings", db_model=sql_models.Meeting, create_schema=pd_models.MeetingCreate, read_schema=pd_models.Meeting, update_schema=pd_models.MeetingUpdate, tags=["Meetings"])
router_participants = create_crud_router(router_name="Meeting Participant", prefix="/meeting_participants", db_model=sql_models.MeetingParticipant, create_schema=pd_models.MeetingParticipantCreate, read_schema=pd_models.MeetingParticipant, update_schema=pd_models.MeetingParticipantUpdate, tags=["Meeting Participants"])
router_agendas = create_crud_router(router_name="Meeting Agenda", prefix="/meeting_agendas", db_model=sql_models.MeetingAgenda, create_schema=pd_models.MeetingAgendaCreate, read_schema=pd_models.MeetingAgenda, tags=["Meeting Agendas"])
router_agenda_items = create_crud_router(router_name="Agenda Item", prefix="/agenda_items", db_model=sql_models.AgendaItem, create_schema=pd_models.AgendaItemCreate, read_schema=pd_models.AgendaItem, update_schema=pd_models.AgendaItemUpdate, tags=["Agenda Items"])
router_transcripts = create_crud_router(router_name="Transcript", prefix="/transcripts", db_model=sql_models.Transcript, create_schema=pd_models.TranscriptCreate, read_schema=pd_models.Transcript, update_schema=pd_models.TranscriptUpdate, tags=["Transcripts"])
router_transcript_entries = create_crud_router(router_name="Transcript Entry", prefix="/transcript_entries", db_model=sql_models.TranscriptEntry, create_schema=pd_models.TranscriptEntryCreate, read_schema=pd_models.TranscriptEntry, tags=["Transcript Entries"])
router_action_items = create_crud_router(router_name="Action Item", prefix="/action_items", db_model=sql_models.ActionItem, create_schema=pd_models.ActionItemCreate, read_schema=pd_models.ActionItem, update_schema=pd_models.ActionItemUpdate, tags=["Action Items"])
router_decisions = create_crud_router(router_name="Decision", prefix="/decisions", db_model=sql_models.Decision, create_schema=pd_models.DecisionCreate, read_schema=pd_models.Decision, update_schema=pd_models.DecisionUpdate, tags=["Decisions"])
router_summaries = create_crud_router(router_name="Meeting Summary", prefix="/meeting_summaries", db_model=sql_models.MeetingSummary, create_schema=pd_models.MeetingSummaryCreate, read_schema=pd_models.MeetingSummary, update_schema=pd_models.MeetingSummaryUpdate, tags=["Meeting Summaries"])
router_integrations = create_crud_router(router_name="User Integration", prefix="/user_integrations", db_model=sql_models.UserIntegration, create_schema=pd_models.UserIntegrationCreate, read_schema=pd_models.UserIntegration, update_schema=pd_models.UserIntegrationUpdate, tags=["User Integrations"])
router_meeting_analytics = create_crud_router(router_name="Meeting Analytics", prefix="/meeting_analytics", db_model=sql_models.MeetingAnalytics, create_schema=pd_models.MeetingAnalyticsCreate, read_schema=pd_models.MeetingAnalytics, tags=["Meeting Analytics"])
router_participant_analytics = create_crud_router(router_name="Participant Analytics", prefix="/participant_analytics", db_model=sql_models.ParticipantAnalytics, create_schema=pd_models.ParticipantAnalyticsCreate, read_schema=pd_models.ParticipantAnalytics, tags=["Participant Analytics"])

# --- WebSocket Chat Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove connection if sending fails
                self.disconnect(connection)

manager = ConnectionManager()

# --- 6. MAIN APP ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    Base.metadata.create_all(bind=engine)
    yield
    # (Optional) Shutdown logic

app = FastAPI(
    title="Meeting Intelligence Platform API",
    description="API for managing organizations, users, meetings, and related data.",
    version="1.0.0",
    lifespan=lifespan,
)

# Include all the routers in the main FastAPI app
app.include_router(router_orgs)
app.include_router(router_users)
app.include_router(router_meetings)
app.include_router(router_participants)
app.include_router(router_agendas)
app.include_router(router_agenda_items)
app.include_router(router_transcripts)
app.include_router(router_transcript_entries)
app.include_router(router_action_items)
app.include_router(router_decisions)
app.include_router(router_summaries)
app.include_router(router_integrations)
app.include_router(router_meeting_analytics)
app.include_router(router_participant_analytics)

# --- WebSocket Chat Endpoint ---
@app.websocket("/chat")
async def chat_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle different message types
            if message_data.get("type") == "broadcast":
                # Broadcast message to all connected clients
                formatted_message = json.dumps({
                    "type": "message",
                    "user": message_data.get("user", "Anonymous"),
                    "message": message_data.get("message", ""),
                    "timestamp": message_data.get("timestamp")
                })
                await manager.broadcast(formatted_message)
            elif message_data.get("type") == "private":
                # Send private message (for now just echo back)
                response = json.dumps({
                    "type": "response",
                    "message": f"Echo: {message_data.get('message', '')}",
                    "timestamp": message_data.get("timestamp")
                })
                await manager.send_personal_message(response, websocket)
            else:
                # Default: broadcast the message
                formatted_message = json.dumps({
                    "type": "message",
                    "user": message_data.get("user", "Anonymous"),
                    "message": message_data.get("message", ""),
                    "timestamp": message_data.get("timestamp")
                })
                await manager.broadcast(formatted_message)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"Chat error: {e}")
        manager.disconnect(websocket)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Meeting Intelligence Platform API. See /docs for documentation."}

# To run this application:
# 1. Install necessary packages: pip install "fastapi[all]" sqlalchemy
# 2. Save the code as main.py
# 3. Run from your terminal: uvicorn main:app --reload
# 4. Open your browser to http://127.0.0.1:8000/docs