--
-- Seed Data for Momentum AI Meeting Assistant
-- Generated based on the provided PRD and Schema
--

-- Organizations: Representing different company types from the PRD.
INSERT INTO organizations (id, name) VALUES
(1, 'Innovate Inc.'),                            -- Tech company for Sarah, James, and Maria
(2, 'Global Research University'),                -- University for Dr. Ahmed
(3, 'Acme Corporation'),                          -- Corporate entity for Priya
(4, 'Momentum AI');                               -- Internal organization for system agents

-- Users: Personas from the PRD, plus additional team members and system agents.
-- Passwords are placeholders, not secure hashes.
INSERT INTO users (id, organization_id, full_name, email, password_hash, timezone) VALUES
(1, 1, 'Sarah Chen', 'sarah.chen@innovate.inc', 'hash_placeholder_sarah', 'America/Los_Angeles'),
(2, 2, 'Dr. Ahmed Al-Jamil', 'ahmed.jamil@globalresearch.edu', 'hash_placeholder_ahmed', 'America/New_York'),
(3, 3, 'Priya Sharma', 'priya.sharma@acme.corp', 'hash_placeholder_priya', 'America/Chicago'),
(4, 1, 'James Franklin', 'james.franklin@innovate.inc', 'hash_placeholder_james', 'America/Los_Angeles'),
(5, 1, 'Maria Rodriguez', 'maria.rodriguez@innovate.inc', 'hash_placeholder_maria', 'America/Los_Angeles'),
(6, 2, 'Kenji Tanaka', 'kenji.tanaka@globalresearch.edu', 'hash_placeholder_kenji', 'Asia/Tokyo'),
(7, 2, 'Lena Müller', 'lena.muller@globalresearch.edu', 'hash_placeholder_lena', 'Europe/Berlin'),
(8, 1, 'David Lee', 'david.lee@innovate.inc', 'hash_placeholder_david', 'America/Los_Angeles'),
(9, 3, 'Charles Montgomery', 'charles.montgomery@acme.corp', 'hash_placeholder_ceo', 'America/New_York'),
(10, 4, 'Note-Taker Agent', 'note-taker@momentum.ai', 'system_account', 'UTC'),
(11, 4, 'Facilitator Agent', 'facilitator@momentum.ai', 'system_account', 'UTC');

-- Meetings: A variety of meetings reflecting different statuses and scenarios.
INSERT INTO meetings (id, organization_id, title, status, scheduled_start_time, actual_start_time, actual_end_time) VALUES
(1, 1, 'Project Phoenix: Q4 Kick-off', 'completed', '2023-11-10 09:00:00', '2023-11-10 09:01:15', '2023-11-10 09:55:45'),
(2, 2, 'Cross-Continental Research Sync', 'scheduled', '2023-11-20 13:00:00', NULL, NULL),
(3, 3, 'Q3 Board of Directors Review', 'completed', '2023-11-01 10:00:00', '2023-11-01 10:05:00', '2023-11-01 12:15:20'),
(4, 1, 'Weekly Engineering Stand-up', 'in_progress', '2023-11-15 10:00:00', '2023-11-15 10:02:30', NULL),
(5, 1, 'Marketing Strategy Brainstorm', 'cancelled', '2023-11-08 14:00:00', NULL, NULL),
(6, 1, 'API Integration Deep Dive', 'completed', '2023-11-13 11:00:00', '2023-11-13 11:00:55', '2023-11-13 11:48:10');

-- Meeting Participants: Linking users to meetings, including AI agents.
-- IDs map to (meeting_id, user_id)
INSERT INTO meeting_participants (id, meeting_id, user_id, role, joined_at) VALUES
-- Meeting 1: Project Phoenix Kick-off (Sarah's Meeting)
(1, 1, 1, 'host', '2023-11-10 09:00:50'),
(2, 1, 4, 'attendee', '2023-11-10 09:01:10'),
(3, 1, 5, 'attendee', '2023-11-10 09:02:05'),
(4, 1, 8, 'attendee', '2023-11-10 09:01:15'),
(5, 1, 10, 'note_taker_agent', '2023-11-10 09:01:15'),
(6, 1, 11, 'facilitator_agent', '2023-11-10 09:01:15'),
-- Meeting 2: Research Sync (Dr. Ahmed's Meeting)
(7, 2, 2, 'host', NULL),
(8, 2, 6, 'attendee', NULL),
(9, 2, 7, 'attendee', NULL),
(10, 2, 10, 'note_taker_agent', NULL),
-- Meeting 3: Board Review (Priya's Meeting)
(11, 3, 9, 'host', '2023-11-01 10:04:30'),
(12, 3, 3, 'attendee', '2023-11-01 10:03:50'),
(13, 3, 10, 'note_taker_agent', '2023-11-01 10:05:00'),
-- Meeting 4: Engineering Stand-up (James's in-progress meeting)
(14, 4, 4, 'host', '2023-11-15 10:02:15'),
(15, 4, 5, 'attendee', '2023-11-15 10:02:30'),
(16, 4, 8, 'attendee', '2023-11-15 10:03:00'),
(17, 4, 10, 'note_taker_agent', '2023-11-15 10:02:30'),
-- Meeting 6: API Deep Dive (Completed, with Maria the New Hire)
(18, 6, 4, 'host', '2023-11-13 11:00:40'),
(19, 6, 8, 'attendee', '2023-11-13 11:00:55'),
(20, 6, 5, 'attendee', '2023-11-13 11:01:15'),
(21, 6, 10, 'note_taker_agent', '2023-11-13 11:00:55');

-- Meeting Agendas: One agenda per meeting.
INSERT INTO meeting_agendas (id, meeting_id) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 4),
(5, 6);

-- Agenda Items: Topics for discussion in the meetings.
INSERT INTO agenda_items (agenda_id, topic, description, presenter_user_id, display_order, estimated_duration_minutes) VALUES
-- Agenda for Meeting 1
(1, 'Introductions & Goals', 'Align on the objectives for Project Phoenix in Q4.', 1, 1, 5),
(1, 'Review of Q3 Learnings', 'Quick recap of what went well and what didn''t in the last quarter.', 4, 2, 10),
(1, 'Roadmap & Key Milestones', 'Walkthrough of the proposed timeline and deliverables.', 1, 3, 20),
(1, 'Open Discussion & Next Steps', 'Q&A and assignment of initial tasks.', 1, 4, 15),
-- Agenda for Meeting 2
(2, 'Review of Last Meeting''s Action Items', NULL, 2, 1, 5),
(2, 'Dr. Tanaka''s Findings on Particle Simulation', 'Presentation of latest results from Tokyo lab.', 6, 2, 25),
(2, 'Dr. Müller''s Cross-Validation Analysis', 'Analysis of the Berlin team''s validation data.', 7, 3, 25),
(2, 'Planning Next Experimental Phase', 'Define goals and resource needs for the upcoming experiments.', 2, 4, 15),
-- Agenda for Meeting 3
(3, 'Approval of Q2 Minutes', 'Formal approval of the previous meeting''s record.', 9, 1, 5),
(3, 'CFO''s Financial Report for Q3', 'Presentation on quarterly financial performance.', NULL, 2, 30),
(3, 'CEO''s Strategic Update', 'Overview of market position and strategic initiatives.', 9, 3, 45),
-- Agenda for Meeting 6
(5, 'Goals for Jira Integration', 'Define what success looks like for the new API integration.', 4, 1, 10),
(5, 'Technical Design Proposal', 'David to present the proposed architecture.', 8, 2, 20),
(5, 'Identifying Blockers & Dependencies', 'Discuss potential risks and external team dependencies.', 4, 3, 15);

-- Transcripts: For completed meetings, with varying quality.
INSERT INTO transcripts (id, meeting_id, word_error_rate, processing_status) VALUES
(1, 1, 0.045, 'completed'),  -- Good quality transcript for Sarah's kick-off
(2, 3, 0.08, 'completed'),   -- Lower quality for board meeting (more crosstalk)
(3, 6, 0.02, 'completed');   -- High quality for technical deep dive

-- Transcript Entries: Snippets of conversation from completed meetings.
INSERT INTO transcript_entries (transcript_id, participant_id, text, start_time_offset_seconds, end_time_offset_seconds) VALUES
-- Entries for Transcript 1 (Meeting 1)
(1, 1, 'Alright everyone, let''s kick things off. Welcome to the Project Phoenix kick-off. Our main goal today is to align on the Q4 roadmap.', 10, 19),
(1, 4, 'Thanks, Sarah. Before we dive into the new roadmap, I can quickly summarize the key takeaways from Q3.', 22, 28),
(1, 1, 'Perfect, James, take it away.', 29, 31),
(1, 5, 'This is really helpful context, especially for me. Thanks, James.', 305, 309),
(1, 1, 'Great point, Maria. Okay, based on this, the first action item is for David to spec out the new auth service.', 950, 958),
(1, 8, 'Got it. I''ll have a draft ready by end of week.', 959, 962),
(1, 1, 'So we''ve made a decision to use OAuth2 for the public API. Everyone in agreement?', 1830, 1836),
-- Entries for Transcript 3 (Meeting 6)
(3, 4, 'Okay team, let''s discuss the Jira integration. David, can you walk us through the technical design?', 60, 66),
(3, 8, 'Sure. The core idea is to use a webhook-based system. When a new action item is created in Momentum, we push it to a dedicated Jira project as a new issue.', 70, 81),
(3, 5, 'That makes sense. Will we be able to link back from the Jira ticket to the meeting transcript?', 85, 91),
(3, 8, 'Yes, that''s a key requirement. We''ll include a backlink in the Jira issue description. The action item for me is to confirm the exact API endpoint for that.', 92, 102);


-- Action Items: Generated from discussions in completed meetings.
INSERT INTO action_items (meeting_id, description, assignee_participant_id, due_date, status, source_transcript_entry_id) VALUES
(1, 'Spec out the new authentication service.', 4, '2023-11-17', 'in_progress', 5),
(1, 'Draft initial user stories for the Q4 roadmap.', 2, '2023-11-20', 'open', NULL),
(6, 'Confirm the Jira API endpoint for creating issues with backlinks.', 19, '2023-11-15', 'completed', 11),
(6, 'Create a test project in Jira for the integration proof-of-concept.', 20, '2023-11-16', 'open', NULL);

-- Decisions: Key decisions made during meetings.
INSERT INTO decisions (meeting_id, description, source_transcript_entry_id) VALUES
(1, 'The team will proceed with using OAuth2 for the public API authentication.', 7),
(3, 'The Q3 financial report is approved as presented.', NULL),
(6, 'The integration will use a webhook-based system to create Jira issues from Momentum action items.', 9);

-- Meeting Summaries: AI-generated summaries for completed meetings.
INSERT INTO meeting_summaries (meeting_id, summary_text) VALUES
(1, 'The Project Phoenix Q4 Kick-off successfully aligned the team on the upcoming roadmap. Key decisions included adopting OAuth2 for the public API. Action items were assigned to Sarah, James, and David to begin foundational work for the quarter.'),
(3, 'The Board of Directors reviewed and approved the Q3 financial report. The CEO provided a strategic update on market positioning and key initiatives for the upcoming year.'),
(6, 'This technical deep dive finalized the architectural approach for the Jira API integration. The team decided on a webhook-based system. Key action items involve confirming API endpoints and setting up a test environment in Jira.');

-- User Integrations: Connecting users to external services as per NFRs.
INSERT INTO user_integrations (user_id, service_name, auth_token_encrypted, refresh_token_encrypted, status) VALUES
(1, 'Jira', 'enc_token_jira_sarah_123', 'enc_refresh_jira_sarah_456', 'active'),
(1, 'Slack', 'enc_token_slack_sarah_789', NULL, 'active'),
(2, 'Google Workspace', 'enc_token_gws_ahmed_abc', 'enc_refresh_gws_ahmed_def', 'active'),
(4, 'Jira', 'enc_token_jira_james_123', 'enc_refresh_jira_james_456', 'active'),
(3, 'Microsoft 365', 'enc_token_m365_priya_xyz', 'enc_refresh_m365_priya_pqr', 'active');

-- Meeting Analytics: Data for the "Facilitator Agent" feature (US-004).
-- Analytics for Meeting 6, reflecting James's team lead scenario.
INSERT INTO meeting_analytics (id, meeting_id, participation_equity_score) VALUES
(1, 6, 0.78);

-- Participant Analytics: Speaking time breakdown for a specific meeting.
-- For Meeting 6: James (host) spoke a lot, David (presenter) spoke a lot, Maria (new hire) spoke less.
INSERT INTO participant_analytics (meeting_analytics_id, participant_id, speaking_time_seconds, prompt_count) VALUES
(1, 18, 1150, 0), -- James (host)
(1, 19, 1320, 0), -- David (presenter)
(1, 20, 210, 1);  -- Maria (quieter member, received 1 prompt)