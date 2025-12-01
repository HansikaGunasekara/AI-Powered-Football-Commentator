from google.adk.agents.llm_agent import Agent
from google.adk.tools.agent_tool import AgentTool
from pydantic import BaseModel, Field
import pandas as pd
import wave
import yaml
from google import genai
from google.genai import types
from google.adk.tools import ToolContext
import pathlib
from commentator_agent.schema import CupSummary, PodcastOutput
from commentator_agent.tools import save_cup_summary_to_mark_down

# load agent instructions from YAML file
with open("commentator_agent/instruction.yaml", "r") as f:
    instructions = yaml.safe_load(f)

# Load FIFA datasets
#fifa_rankings = pd.read_csv("fifa_dataset/fifa_ranking_2022-10-06.csv")
#matches = pd.read_csv("fifa_dataset/matches_1930_2022.csv")
world_cups = pd.read_csv("fifa_dataset/world_cup.csv")

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
    host = row.iloc[0]["Host"]
    topscorer = row.iloc[0]["TopScorrer"]

    return {
        "year": year,
        "host": host,
        "champion": champion,
        "runner_up": runner_up,
        "topscorer": topscorer,
        "summary": f"In {year}, {champion} won the World Cup, with {runner_up} finishing as runner up."
    }




# 1. Research Agent
research_agent = Agent(
    name="world_cup_researcher",
    model="gemini-2.0-flash",
    instruction=instructions['research_agent_instruction'],
    tools=[get_world_cup_result],
    output_schema=CupSummary
)

# 3. Podcaster Agent (TTS)
podcaster_agent = Agent(
    name="football_podcaster_agent",
    model="gemini-2.0-flash",
    instruction=instructions['podcaster_agent_instruction'],
    tools=[generate_football_podcast_audio],
    output_schema=PodcastOutput
)

root_agent = Agent(
    model='gemini-2.0-flash-live-001',
    name='football_commentary_assistant',
    description='A helpful assistant that provides football commentary and information about the FIFA World Cup.',
    instruction=instructions['root_agent_instruction'],
    tools = [
        AgentTool(agent=research_agent),
        save_cup_summary_to_mark_down,
        AgentTool(agent=podcaster_agent)
        ]
)

