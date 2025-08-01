# Momentum 🚀

**Transforming Meetings into Actionable Outcomes**

[
![Status](https://img.shields.io/badge/status-in_development-orange.svg)
](https://github.com/your-org/momentum)
[
![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
](https://www.python.org/)
[
![Framework](https://img.shields.io/badge/Framework-FastAPI-teal.svg)
](https://fastapi.tiangolo.com/)
[
![License](https://img.shields.io/badge/License-MIT-green.svg)
](LICENSE)

---

## 📖 Table of Contents

*   [Overview](#-overview)
*   [🌟 Key Features](#-key-features)
*   [⚙️ Tech Stack](#️-tech-stack)
*   [🚀 Getting Started](#-getting-started)
    *   [Prerequisites](#prerequisites)
    *   [Installation](#installation)
    *   [Running the Application](#running-the-application)
*   [🔌 API Endpoints](#-api-endpoints)
    *   [Organizations](#organizations)
    *   [Users](#users)
    *   [Meetings](#meetings)
    *   [Meeting Participants](#meeting-participants)
    *   [Meeting Agendas](#meeting-agendas)
    *   [Agenda Items](#agenda-items)
    *   [Transcripts](#transcripts)
    *   [Transcript Entries](#transcript-entries)
    *   [Action Items](#action-items)
    *   [Decisions](#decisions)
    *   [Meeting Summaries](#meeting-summaries)
    *   [User Integrations](#user-integrations)
    *   [Meeting Analytics](#meeting-analytics)
    *   [Participant Analytics](#participant-analytics)

---

## 🌐 Overview

Momentum is an intelligent, AI-powered platform designed to automate the entire meeting lifecycle. Our vision is to solve the universal problem of inefficient, poorly documented meetings by transforming them from a necessary chore into a focused, productive, and collaborative engine for progress.

This repository contains the backend API for the Momentum platform, built with FastAPI and SQLAlchemy. It provides a robust, scalable foundation for managing users, meetings, transcriptions, and the intelligence that powers the Momentum experience.

## 🌟 Key Features

Based on our product vision, the Momentum platform provides the following core features:

*   🤖 **AI-Powered Transcription & Intelligence:** Automatically transcribe meetings, identify speakers, and extract action items and decisions in real-time.
*   🗓️ **Smart Scheduling & Preparation:** Coordinate meeting times across multiple time zones and automatically distribute agendas, ensuring everyone is prepared.
*   👨‍🏫 **In-Meeting Facilitation:** Monitor participation to encourage more inclusive conversations and provide post-meeting analytics on speaker equity.
*   📊 **Live Meeting Dashboard:** A unified view of the agenda, real-time notes, and captured action items, perfect for keeping everyone on the same page, especially new hires.
*   🔗 **Seamless Integrations:** Sync meeting minutes, action items, and summaries to your favorite tools like Google Workspace, Microsoft 365, Slack, and Jira.
*   🔍 **Searchable Archive:** A permanent, searchable record of all meeting discussions, decisions, and outcomes.

## ⚙️ Tech Stack

*   **Backend Framework:** [FastAPI](https://fastapi.tiangolo.com/)
*   **Database ORM:** [SQLAlchemy](https://www.sqlalchemy.org/)
*   **Data Validation:** [Pydantic](https://pydantic-docs.helpmanual.io/)
*   **Language:** Python 3.9+
*   **Server:** [Uvicorn](https://www.uvicorn.org/)

## 🚀 Getting Started

Follow these instructions to get the API server up and running on your local machine for development and testing purposes.

### Prerequisites

*   Python 3.9+
*   `pip` and `venv`
*   [Git](https://git-scm.com/)

### Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/your-org/momentum.git
    cd momentum
    ```

2.  **Create and activate a virtual environment:**
    *   On macOS and Linux:
        ```sh
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   On Windows:
        ```sh
        python -m venv venv
        .\venv\Scripts\activate
        ```

3.  **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```
    *(Note: A `requirements.txt` file should be created with the following content)*
    ```txt
    fastapi[all]
    sqlalchemy
    uvicorn
    # Add other dependencies like psycopg2-binary if using PostgreSQL
    ```

4.  **Configure your database:**
    The application uses SQLAlchemy to connect to a database. The database connection string is configured in `database.py`. The system automatically creates the required tables on startup. For local development, you can use SQLite.

### Running the Application

1.  **Start the server:**
    ```sh
    uvicorn main:app --reload
    ```
    The `--reload` flag will automatically restart the server when you make code changes.

2.  **Access the API:**
    The API will be available at `http://127.0.0.1:8000`.

3.  **Explore the documentation:**
    FastAPI automatically generates interactive API documentation. Open your browser and navigate to:
    *   **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
    *   **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🔌 API Endpoints

All endpoints are prefixed with the base URL: `http://127.0.0.1:8000`

### Organizations

Manages company or team accounts.

*   **POST** `/organizations/` - Create a new organization.
    ```bash
    curl -X POST "http://127.0.0.1:8000/organizations/" \
    -H "Content-Type: application/json" \
    -d '{"name": "Innovate Corp", "domain": "innovatecorp.com"}'
    ```

*   **GET** `/organizations/` - Retrieve a list of all organizations.
    ```bash
    curl -X GET "http://127.0.0.1:8000/organizations/"
    ```

*   **GET** `/organizations/{id}` - Retrieve a specific organization.
    ```bash
    curl -X GET "http://127.0.0.1:8000/organizations/1"
    ```

*   **PUT** `/organizations/{id}` - Update an organization.
    ```bash
    curl -X PUT "http://127.0.0.1:8000/organizations/1" \
    -H "Content-Type: application/json" \
    -d '{"name": "Innovate Corporation"}'
    ```

*   **DELETE** `/organizations/{id}` - Delete an organization.
    ```bash
    curl -X DELETE "http://127.0.0.1:8000/organizations/1"
    ```

### Users

Manages user accounts.

*   **POST** `/users/` - Create a new user.
    ```bash
    curl -X POST "http://127.0.0.1:8000/users/" \
    -H "Content-Type: application/json" \
    -d '{"username": "sarah_pm", "email": "sarah.p@innovatecorp.com", "password": "securepassword123", "organization_id": 1}'
    ```

*   **GET** `/users/` - Retrieve all users.
    ```bash
    curl -X GET "http://127.0.0.1:8000/users/"
    ```

*   **GET** `/users/{id}` - Retrieve a specific user.
    ```bash
    curl -X GET "http://127.0.0.1:8000/users/1"
    ```

*   **PUT** `/users/{id}` - Update a user.
    ```bash
    curl -X PUT "http://127.0.0.1:8000/users/1" \
    -H "Content-Type: application/json" \
    -d '{"email": "sarah.projectmanager@innovatecorp.com"}'
    ```

*   **DELETE** `/users/{id}` - Delete a user.
    ```bash
    curl -X DELETE "http://127.0.0.1:8000/users/1"
    ```

### Meetings

Manages meeting records.

*   **POST** `/meetings/` - Schedule a new meeting.
    ```bash
    curl -X POST "http://127.0.0.1:8000/meetings/" \
    -H "Content-Type: application/json" \
    -d '{"title": "Q4 Project Kickoff", "start_time": "2023-12-01T14:00:00Z", "end_time": "2023-12-01T15:00:00Z", "organization_id": 1}'
    ```

*   **GET** `/meetings/` - Retrieve all meetings.
    ```bash
    curl -X GET "http://127.0.0.1:8000/meetings/"
    ```

*   **GET** `/meetings/{id}` - Retrieve a specific meeting.
    ```bash
    curl -X GET "http://127.0.0.1:8000/meetings/1"
    ```

*   **PUT** `/meetings/{id}` - Update a meeting's details.
    ```bash
    curl -X PUT "http://127.0.0.1:8000/meetings/1" \
    -H "Content-Type: application/json" \
    -d '{"title": "Q4 Project Kickoff & Brainstorm"}'
    ```

*   **DELETE** `/meetings/{id}` - Delete a meeting.
    ```bash
    curl -X DELETE "http://127.0.0.1:8000/meetings/1"
    ```

### Meeting Participants

Manages the relationship between users and meetings.

*   **POST** `/meeting_participants/` - Add a participant to a meeting.
    ```bash
    curl -X POST "http://127.0.0.1:8000/meeting_participants/" \
    -H "Content-Type: application/json" \
    -d '{"user_id": 1, "meeting_id": 1, "role": "host"}'
    ```

*   **GET** `/meeting_participants/` - Retrieve all participant records.
    ```bash
    curl -X GET "http://127.0.0.1:8000/meeting_participants/"
    ```

*   **GET** `/meeting_participants/{id}` - Retrieve a specific participant record.
    ```bash
    curl -X GET "http://127.0.0.1:8000/meeting_participants/1"
    ```

*   **PUT** `/meeting_participants/{id}` - Update a participant's role.
    ```bash
    curl -X PUT "http://127.0.0.1:8000/meeting_participants/1" \
    -H "Content-Type: application/json" \
    -d '{"role": "presenter"}'
    ```

*   **DELETE** `/meeting_participants/{id}` - Remove a participant from a meeting.
    ```bash
    curl -X DELETE "http://127.0.0.1:8000/meeting_participants/1"
    ```

### Meeting Agendas

Manages the agenda for a specific meeting. *(Note: Update is not supported for the top-level agenda).*

*   **POST** `/meeting_agendas/` - Create an agenda for a meeting.
    ```bash
    curl -X POST "http://127.0.0.1:8000/meeting_agendas/" \
    -H "Content-Type: application/json" \
    -d '{"meeting_id": 1, "title": "Kickoff Agenda"}'
    ```

*   **GET** `/meeting_agendas/` - Retrieve all agendas.
    ```bash
    curl -X GET "http://127.0.0.1:8000/meeting_agendas/"
    ```

*   **GET** `/meeting_agendas/{id}` - Retrieve a specific agenda.
    ```bash
    curl -X GET "http://127.0.0.1:8000/meeting_agendas/1"
    ```

*   **DELETE** `/meeting_agendas/{id}` - Delete an agenda.
    ```bash
    curl -X DELETE "http://127.0.0.1:8000/meeting_agendas/1"
    ```

### Agenda Items

Manages individual items within a meeting agenda.

*   **POST** `/agenda_items/` - Create a new agenda item.
    ```bash
    curl -X POST "http://127.0.0.1:8000/agenda_items/" \
    -H "Content-Type: application/json" \
    -d '{"agenda_id": 1, "title": "Introductions", "duration_minutes": 5}'
    ```

*   **GET** `/agenda_items/` - Retrieve all agenda items.
    ```bash
    curl -X GET "http://127.0.0.1:8000/agenda_items/"
    ```

*   **GET** `/agenda_items/{id}` - Retrieve a specific agenda item.
    ```bash
    curl -X GET "http://127.0.0.1:8000/agenda_items/1"
    ```

*   **PUT** `/agenda_items/{id}` - Update an agenda item.
    ```bash
    curl -X PUT "http://127.0.0.1:8000/agenda_items/1" \
    -H "Content-Type: application/json" \
    -d '{"title": "Team Introductions", "duration_minutes": 10}'
    ```

*   **DELETE** `/agenda_items/{id}` - Delete an agenda item.
    ```bash
    curl -X DELETE "http://127.0.0.1:8000/agenda_items/1"
    ```

### Transcripts

Manages the top-level container for a meeting transcript.

*   **POST** `/transcripts/` - Create a new transcript record for a meeting.
    ```bash
    curl -X POST "http://127.0.0.1:8000/transcripts/" \
    -H "Content-Type: application/json" \
    -d '{"meeting_id": 1}'
    ```

*   **GET** `/transcripts/{id}` - Retrieve a transcript record.
    ```bash
    curl -X GET "http://127.0.0.1:8000/transcripts/1"
    ```

### Transcript Entries

Manages individual spoken entries within a transcript. *(Note: Update is not supported for entries).*

*   **POST** `/transcript_entries/` - Add a new entry to a transcript.
    ```bash
    curl -X POST "http://127.0.0.1:8000/transcript_entries/" \
    -H "Content-Type: application/json" \
    -d '{"transcript_id": 1, "participant_id": 1, "text": "Welcome everyone to the Q4 kickoff.", "timestamp": "2023-12-01T14:01:15Z"}'
    ```

*   **GET** `/transcript_entries/` - Retrieve all transcript entries.
    ```bash
    curl -X GET "http://127.0.0.1:8000/transcript_entries/?limit=10"
    ```

### Action Items

Manages action items identified during a meeting.

*   **POST** `/action_items/` - Create a new action item.
    ```bash
    curl -X POST "http://127.0.0.1:8000/action_items/" \
    -H "Content-Type: application/json" \
    -d '{"meeting_id": 1, "description": "Draft project brief", "assignee_id": 2, "due_date": "2023-12-08", "status": "pending"}'
    ```

*   **GET** `/action_items/{id}` - Retrieve an action item.
    ```bash
    curl -X GET "http://127.0.0.1:8000/action_items/1"
    ```

*   **PUT** `/action_items/{id}` - Update an action item.
    ```bash
    curl -X PUT "http://127.0.0.1:8000/action_items/1" \
    -H "Content-Type: application/json" \
    -d '{"status": "completed"}'
    ```

### Decisions

Manages key decisions made during a meeting.

*   **POST** `/decisions/` - Record a new decision.
    ```bash
    curl -X POST "http://127.0.0.1:8000/decisions/" \
    -H "Content-Type: application/json" \
    -d '{"meeting_id": 1, "description": "We will proceed with Option A for the main framework."}'
    ```

*   **GET** `/decisions/{id}` - Retrieve a decision.
    ```bash
    curl -X GET "http://127.0.0.1:8000/decisions/1"
    ```

### Meeting Summaries

Manages AI-generated or manually created meeting summaries.

*   **POST** `/meeting_summaries/` - Create a summary for a meeting.
    ```bash
    curl -X POST "http://127.0.0.1:8000/meeting_summaries/" \
    -H "Content-Type: application/json" \
    -d '{"meeting_id": 1, "summary_text": "The team aligned on the project goals for Q4..."}'
    ```

*   **GET** `/meeting_summaries/{id}` - Retrieve a summary.
    ```bash
    curl -X GET "http://127.0.0.1:8000/meeting_summaries/1"
    ```

### User Integrations

Manages user connections to third-party services (Slack, Jira, etc.).

*   **POST** `/user_integrations/` - Add a new integration for a user.
    ```bash
    curl -X POST "http://127.0.0.1:8000/user_integrations/" \
    -H "Content-Type: application/json" \
    -d '{"user_id": 1, "integration_type": "slack", "auth_token": "xoxb-some-secret-token"}'
    ```

*   **GET** `/user_integrations/{id}` - Retrieve an integration.
    ```bash
    curl -X GET "http://127.0.0.1:8000/user_integrations/1"
    ```

### Meeting Analytics

Stores high-level analytics for a meeting. *(Note: Update is not supported).*

*   **POST** `/meeting_analytics/` - Create an analytics record for a meeting.
    ```bash
    curl -X POST "http://127.0.0.1:8000/meeting_analytics/" \
    -H "Content-Type: application/json" \
    -d '{"meeting_id": 1, "participation_equity": 0.85, "sentiment_score": 0.7}'
    ```

*   **GET** `/meeting_analytics/{id}` - Retrieve meeting analytics.
    ```bash
    curl -X GET "http://127.0.0.1:8000/meeting_analytics/1"
    ```

### Participant Analytics

Stores analytics for a specific participant in a meeting. *(Note: Update is not supported).*

*   **POST** `/participant_analytics/` - Create a participant analytics record.
    ```bash
    curl -X POST "http://127.0.0.1:8000/participant_analytics/" \
    -H "Content-Type: application/json" \
    -d '{"participant_id": 1, "meeting_id": 1, "speaking_time_seconds": 540}'
    ```

*   **GET** `/participant_analytics/{id}` - Retrieve participant analytics.
    ```bash
    curl -X GET "http://127.0.0.1:8000/participant_analytics/1"
    ```