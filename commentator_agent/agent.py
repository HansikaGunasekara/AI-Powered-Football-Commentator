from google.adk.agents.llm_agent import Agent
from google.adk.tools.agent_tool import AgentTool
from pydantic import BaseModel, Field
import pandas as pd
import wave
from google import genai
from google.genai import types
from google.adk.tools import ToolContext
import pathlib


# Load FIFA datasets
#fifa_rankings = pd.read_csv("fifa_dataset/fifa_ranking_2022-10-06.csv")
#matches = pd.read_csv("fifa_dataset/matches_1930_2022.csv")
world_cups = pd.read_csv("fifa_dataset/world_cup.csv")

def save_cup_summary_to_mark_down(filename: str, content: str) -> dict[str, str]:
    """
    Saves the given content to a Markdown file in the current directory.
    """
    try:
        if not filename.endswith(".md"):
            filename += ".md"
        current_directory = pathlib.Path.cwd()
        file_path = current_directory / filename
        file_path.write_text(content, encoding="utf-8")
        return {
            "status": "success",
            "message": f"Successfully saved news to {file_path.resolve()}",
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to save file: {str(e)}"}

# --------------------------------------------------------------------
# AUDIO GENERATION TOOL
# --------------------------------------------------------------------

def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
    """Helper function to save audio data as a wave file"""
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)

async def generate_football_podcast_audio(podcast_script: str, tool_context: ToolContext, filename: str = "commentator_podcast") -> dict[str, str]:
    """
    Generates audio from a podcast script using Gemini API and saves it as a WAV file.

    Args:
        podcast_script: The conversational script to be converted to audio.
        tool_context: The ADK tool context.
        filename: Base filename for the audio file (without extension).

    Returns:
        Dictionary with status and file information.
    """
    try:
        client = genai.Client()
        prompt = f"TTS the following conversation between Tom and Sarah:\n\n{podcast_script}"

        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                        speaker_voice_configs=[
                            types.SpeakerVoiceConfig(speaker='Tom', 
                                                     voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name='Kore'))),
                            types.SpeakerVoiceConfig(speaker='Sarah', 
                                                     voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name='Puck')))
                        ]
                    )
                )
            )
        )

        data = response.candidates[0].content.parts[0].inline_data.data

        if not filename.endswith(".wav"):
            filename += ".wav"

        # ** BUG FIX **: This logic now runs for all cases, not just when the extension is added.
        current_directory = pathlib.Path.cwd()
        file_path = current_directory / filename
        wave_file(str(file_path), data)

        return {
            "status": "success",
            "message": f"Successfully generated and saved podcast audio to {file_path.resolve()}",
            "file_path": str(file_path.resolve()),
            "file_size": len(data)
        }

    except Exception as e:
        error_msg = str(e)[:200]
        return {"status": "error", "message": f"Audio generation failed: {error_msg}"}
# --------------------------------------------------------------------
# TOOL: GET WORLD CUP INFO
# --------------------------------------------------------------------

def get_world_cup_result(year: int) -> dict:
    row = world_cups[world_cups["Year"] == year]

    if row.empty:
        return {"error": f"No data for year {year}"}

    champion = row.iloc[0]["Champion"]
    runner_up = row.iloc[0]["Runner-Up"]

    return {
        "year": year,
        "champion": champion,
        "runner_up": runner_up,
        "summary": f"In {year}, {champion} won the World Cup, with {runner_up} finishing as runner up."
    }

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

root_agent = Agent(
    model='gemini-2.0-flash-live-001',
    name='football_commentary_assistant',
    description='A helpful assistant that provides football commentary and information about the FIFA World Cup.',
    instruction="""
    **Your Core Identity:**
    You are a knowledgeable and engaging football commentary assistant specializing in the FIFA World Cup. You provide insightful analysis, historical context, and historical commentary on matches, players, and tournaments.
    
    **Crucial Rules:**
    1. Always provide accurate and up-to-date information about the FIFA World Cup extracted from the provided dataset.
    2. Maintain an enthusiastic and engaging tone suitable for football commentary.

    **Required Conversational Workflow:**
    2. **Data-Driven Responses:** Use the FIFA World Cup dataset to answer questions, provide statistics, and offer historical insights.
    3. **Engaging Commentary:** Deliver commentary in an engaging manner, suitable for a football audience.
    1.  **Greet & Query:** The VERY FIRST thing you do is respond to the user with: "Thank you for your interest in FIFA World Cup! Could you please let me know the year you would like information about the World Cup?"
    2.  **Acknowledge and Inform:** Acknowledge the user's input and inform them that you will gather the relevant information. For example, "Great choice! Let me gather the latest insights and commentary for you."
    3.  **Search (Background Step):** Immediately after acknowledging, use the `get_world_cup_result` tool to find relevant World Cup information.
    5.  **Structure the Report (Internal Step):** Use the `CupSummary` schema to structure all gathered information. If world cup data was not found for a user mentioned year, you MUST use "Not Available" in the `champion`, `runner_up` & `summary` fields.
    6.  **Format for Markdown (Internal Step):** Convert the structured `CupSummaryReport` data from research_agent into a well-formatted Markdown string.
    7.  **Save the Report (Background Step):** Save the Markdown string using `save_news_to_markdown` with the filename `detailed_report.md`.
    8.  **Create Podcast Script (Internal Step):** After saving the report, you MUST convert the structured `CupSummaryReport` data into a natural, conversational football commentary script between two hosts, 'Tom' (enthusiastic, bold, dynamic) and 'Sarah' (analytical, calm, confident). Deliver it in an engaging manner, suitable for a football audience.
    9.  **Generate Audio (Background Step):** Call the `podcaster_agent` tool, passing the complete conversational script you just created to it.
    10. **Final Confirmation:** After the audio is successfully generated, your final response to the user MUST be: "All done. I've compiled the research report, saved it to `detailed_report.md`, and generated the podcast audio file for you."
    """,
    tools = [
        AgentTool(agent=research_agent),
        save_cup_summary_to_mark_down,
        AgentTool(agent=podcaster_agent)
        ]
)

