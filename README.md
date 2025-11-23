# AI-Powered Football Commentator: How Multi-Agent Systems are Changing Sports Media

## ⚽ A New Era of Football Storytelling
Football has always been fueled by stories - the heartbreaks, comebacks, rivalries, golden generations, and unforgettable finals. Fans don't just want scores; they want context, history and drama.

But producing high-quality football content takes time:
- Researching match history
- Understanding team trajectories
- Analysing championships
- Writing compelling stories
- Making quality commentary

The AI-Powered Football Commentator automates this entire workflow.

With nothing more than a request like:

```
    "Create a football commentary about the 2006 FIFA World Cup final"
```

This project implements a multi‑agent football commentary and research
assistant using **Google ADK**, **Gemini models**, and custom tools. It
retrieves FIFA World Cup results, generates structured summaries, saves
Markdown reports, and produces football commentary audio between two fictional hosts.

------------------------------------------------------------------------

## 🚀 Features

### 1. **World Cup Research Agent**

-   Takes a World Cup year as input
-   Uses the `get_world_cup_result` tool to gather statistics and information about the final match
-   Returns results in a validated `CupSummary` Pydantic model

------------------------------------------------------------------------

### 2. **Markdown Report Generator**

A tool (`save_cup_summary_to_mark_down`) that: 
- Accepts any filename + content
- Saves a Markdown file to the project directory

Used by the root agent to save a research report.

------------------------------------------------------------------------

### 3. **Podcast Script & TTS Generator**

-   Conversational script created between:
    -   **Tom** (enthusiastic host)
    -   **Sarah** (analytical host)
-   TTS is produced using Gemini:
    -   Model: `gemini-2.5-flash-preview-tts`
    -   Multi‑speaker configuration
-   Audio saved as a `.wav` file using the
    `generate_football_podcast_audio` tool

------------------------------------------------------------------------

### 4. **Root Orchestration Agent**

The main agent that: 
1. Greets the user
2. Requests a World Cup year
3. Calls the Research Agent
4. Saves a Markdown report
5. Generates a two‑host podcast script
6. Calls the Podcaster Agent to create audio
7. Returns a final confirmation message

------------------------------------------------------------------------

## 🗂 Directory Layout

    project/
    │
    ├── fifa_dataset/
    │   ├── world_cup.csv
    │   ├── matches_1930_2022.csv   (optional)
    │   └── fifa_ranking_2022-10-06.csv   (optional)
    │
    ├── main.py   ← main agent + tools
    ├── README.md ← this file
    ├── commentator_podcast.wav (generated at runtime)
    └── detailed_report.md   (generated at runtime)

------------------------------------------------------------------------

## 🧰 Tools Defined in the Project

### `get_world_cup_result(year: int)`

Loads from the `world_cup.csv` dataset and returns champion + runner‑up.

### `save_cup_summary_to_mark_down(filename, content)`

Stores research results into Markdown.

### `generate_football_podcast_audio(script)`

Creates a multi‑voice WAV audio file.

------------------------------------------------------------------------

## 🧪 Requirements

    google-genai
    google-adk
    pydantic
    pandas
    wave

------------------------------------------------------------------------

## ▶️ How to Run

1.  Install dependencies
3.  Run the main script:

```
    python main.py
```

4.  Follow the prompts from the root agent.

------------------------------------------------------------------------

## 🏆 Summary

This project demonstrates a complete **agent‑tool orchestration
pipeline** using **Google ADK**, combining:
- Data retrieval
- Pydantic validation
- Markdown report generation
- TTS audio creation
- Multi‑agent coordination

## 🚀 What's Next

This project is just the beginning.

Upcoming enhancements include:
- Custom tools to analyze & merge information about all the matches in a tournament
- Observability in Agentic AI Systems: Logging, Tracing, Metrics
- Agent evaluation