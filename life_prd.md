Product Requirements Document (PRD)

Project Title: Personal Life Dashboard

Owner: Nigel

Date: April 1, 2025

# 1. Purpose

To develop a modular, RPG-inspired personal life dashboard web application that tracks a user's core and life stats, quests, skills, achievements, and journals, offering a unified overview of progress across health, wealth, and relationships. The dashboard should be intuitive, visually appealing, and extensible.

# 2. Goals and Objectives

Provide a holistic overview of personal development inspired by RPG mechanics.

Track classical RPG stats and life stats (health, wealth, relationships).

Maintain a log of quests and habits aligned with short- and long-term goals.

Track skills development and achievements.

Present high-level trend overviews (e.g., health, wealth).

Enable journaling for reflection and insights.

Design for modularity, extensibility, and future integration.

# 3. User Stories

As a user, I want to see an overview of my stats so I can reflect on personal growth.

As a user, I want to update and track my health, wealth, and relationship metrics.

As a user, I want to define and track my goals as quests.

As a user, I want to track recurring behaviours as habits.

As a user, I want to gain achievements and titles based on my progress.

As a user, I want to view skills I'm developing and how they progress.

As a user, I want to journal and reflect on my progress and insights.

# 4. Features

## A. Core Stats (RPG-style)

Strength, Endurance, Agility, Intelligence, Wisdom, Charisma

## B. Life Stats

Health

Physical

Mental & Emotional

Food & Nutrients

Other

Wealth

Work & Company

Finance / Savings & Investments

Personal Growth & Reading

Relationships

Family

Friendships

Romance

Social Skills

Adventure & Exploration

## C. Quest Log

Life Goals

Annual Goals

Main Quests

Side Quests

Weekly Quests

Daily Quests

Habits

## D. Journal

Daily reflections

Weekly or milestone-based entries

## E. Milestone Tracker

Visual tracker of key personal events and accomplishments

## F. Skills

Skills categorized by Health, Wealth, and Social areas

Level tracking

## . Achievements & Titles

Badges: Bronze, Silver, Gold, Platinum

Custom Titles

Levels per category

## H. Overview Pages

Health Overview: Metrics, Attributes, Trends

Wealth Overview: Metrics, Attributes, Trends, Financial Dashboard

Relationships Overview: Metrics, Attributes, Trends

## . Home/Base Page

Central hub for user stats, quests, and quick actions

# 5. Technical Requirements

Framework: Django (Python)

Frontend Styling: Materialize CSS

Database: SQLite (dev), PostgreSQL (prod)

Architecture:

Modular Django apps: core_stats, life_stats, quests, skills, achievements, journals, dashboard

Composition-based object model for extensibility

Data Model:

Class inheritance scheme using BaseStat, LifeStatCategory, Quest, Habit, Skill, Achievement, Overview

Authentication:

User registration and login

# 6. Non-Functional Requirements

Modular and extensible codebase

Intuitive and attractive UI/UX

Maintainable and testable class structure

Responsive design for desktop and mobile

# 7. Success Criteria

Users can register, log in, and access their dashboard.

Users can view, update, and track their core stats and life stats.

Quests, habits, and journals are stored and rendered properly.

Health, wealth, and relationship overviews show metrics and trends.

The system supports adding skills and achievements.

The architecture allows for easy expansion of modules or features.

# 8. Future Considerations

Integration with health apps (e.g., Apple Health, Google Fit)

Financial data import (e.g., bank API, CSVs)

Gamification mechanics: XP, unlockables

Dark mode and custom themes

API for external use
