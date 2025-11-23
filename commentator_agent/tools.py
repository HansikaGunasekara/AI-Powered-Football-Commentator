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


# --------------------------------------------------------------------
# AUDIO GENERATION TOOL
# --------------------------------------------------------------------

def save_wave(filename, pcm, rate=24000):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(pcm)

async def generate_football_podcast_audio(podcast_script: str, tool_context: ToolContext, filename="football_podcast") -> dict[str, str]:
    client = genai.Client()
    prompt = f"TTS the following football commentary between Tom and Sarah:\n\n{podcast_script}"

    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                    speaker_voice_configs=[
                        types.SpeakerVoiceConfig(
                            speaker="Tom",
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
                            )
                        ),
                        types.SpeakerVoiceConfig(
                            speaker="Sarah",
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
                            )
                        )
                    ]
                )
            )
        )
    )

    audio_data = response.candidates[0].content.parts[0].inline_data.data

    if not filename.endswith(".wav"):
        filename += ".wav"

    file_path = pathlib.Path.cwd() / filename
    save_wave(str(file_path), audio_data)

    return {"status": "success", "file": str(file_path), "size": len(audio_data)}

# --------------------------------------------------------------------
# TOOL: GET WORLD CUP INFO
# --------------------------------------------------------------------

def get_world_cup_result(year: int) -> dict:
    row = world_cups[world_cups["year"] == year]

    if row.empty:
        return {"error": f"No data for year {year}"}

    champion = row.iloc[0]["winner"]
    runner_up = row.iloc[0]["runners_up"]

    return {
        "year": year,
        "champion": champion,
        "runner_up": runner_up,
        "summary": f"In {year}, {champion} won the World Cup, with {runner_up} finishing as runner up."
    }
