from google.adk.agents.llm_agent import Agent
from google.adk.tools.agent_tool import AgentTool
from pydantic import BaseModel, Field

from .tools import generate_football_podcast_audio, get_world_cup_result

# --------------------------------------------------------------------
# SCHEMAS
# --------------------------------------------------------------------

class CupSummary(BaseModel):
    year: int = Field(description="World Cup year requested by the user")
    champion: str = Field(description="Champion country")
    runner_up: str = Field(description="Runner-up country")
    summary: str = Field(description="Short description of the tournament result")

class PodcastOutput(BaseModel):
    audio_file: str = Field(description="Path to generated audio file")
    script: str = Field(description="Script used for the podcast")


# 1. Research Agent
research_agent = Agent(
    name="world_cup_researcher",
    model="gemini-2.0-flash",
    instruction="""
    You are a football researcher. Given a year from the user, call the
    `get_world_cup_result` tool to retrieve the champion and runner-up.
    Then summarize the result using the CupSummary schema.
    """,
    tools=[get_world_cup_result],
    output_schema=CupSummary
)



# 3. Podcaster Agent (TTS)
podcaster_agent = Agent(
    name="football_podcaster_agent",
    model="gemini-2.0-flash",
    instruction="""
    Your job is to generate audio using the generate_football_podcast_audio tool.
    When given a script, call the tool immediately and return the result.
    """,
    tools=[generate_football_podcast_audio],
    output_schema=PodcastOutput
)