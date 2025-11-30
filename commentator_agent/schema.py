from pydantic import BaseModel, Field

class CupSummary(BaseModel):
    year: int = Field(description="World Cup year requested by the user")
    host: str = Field(description="Host country of the World Cup")
    champion: str = Field(description="Champion country")
    runner_up: str = Field(description="Runner-up country")
    topscorer: str = Field(description="Top scorer of the tournament")
    summary: str = Field(description="Short description of the tournament result")

class PodcastOutput(BaseModel):
    audio_file: str = Field(description="Path to generated audio file")
    script: str = Field(description="Script used for the podcast")