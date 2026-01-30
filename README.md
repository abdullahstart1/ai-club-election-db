# AI Club Election Database

This repository contains the SQL Server database for the AI Club Election project.  
It includes tables, views, stored procedures, users, privileges, and backup/restore scripts.

---

## Files

- `Ai_club_election.sql` – SQL script to create database, tables, views, stored procedures, users, and backups.  
- `mssql.py` – Flask application to connect to the SQL Server database and provide web endpoints (JUST FOR TESTING SOME FEATURES).

## Database Design and Diagrams

The repository also contains a `Charts` Folder that includes:
- 'Detailed_Charts.drawio': This file has the charts as drawings.
-'Screenshots': This folder includes charts screenshots (NOT very clear)

These are the charts:
- **Conceptual Design:** Entity-Relationship diagram (ERD)
- **Logical Design:** Tables, primary keys, and foreign keys
- **Physical Design:** Table structures and relationships
- **Flow Charts:** Processes of voting and campaign management
- **DFD:** Data Flow Diagrams showing interactions between voters, candidates, and campaign teams

You can open `Charts.drawio` using [draw.io](https://app.diagrams.net/) or its desktop application.

## Database Overview

**Database Name:** Ai_Club_Election

### Tables

- `Candidates`  
- `Voters`  
- `Advisors`  
- `CampaignTeams`  
- `CandidatesLocations`  
- `Votes`  

### Views

- `candidatesNames_view` – Candidate info with age  
- `NumberOfVotes_view` – Number of votes per candidate  
- `TheWinner_view` – The winner of the election  

### Stored Procedures

- `voter_votes(@voterId)` – Get votes of a voter  
- `CandidateInfo(@candidateId)` – Info about a candidate  
- `vote(@voterId,@candidateId)` – Insert a vote  
- `deleteVote(@voterId,@candidateId)` – Delete a vote  
- `updateVote(@voterId,@oldcandidateId,@newcandidateId)` – Update a vote  

### Users & Privileges

1. `voter1_Ali` – Can vote and check votes  
2. `candidate1_Ahmed` – Can view and update own info  
3. `advisor1_Khaled` – Can view and update advisors/candidates  
4. `campaignTeam1_Future` – Full access to manage database  