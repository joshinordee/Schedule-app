from pydantic import BaseModel, Field
from google.genai import types

class CreateEvent(BaseModel):
    summary: str = Field(description="Summary of the created event")
    start_time: str = Field(description="Starting time of the event in ISO 8601 format")
    end_time: str | None = Field(description="Ending time of the event in ISO 8601 format")
    location: str | None = Field(description="Location of the event")
    guests: str | None = Field(description="Specified guests for the event")

class UpdateEvent(BaseModel):
    summary: str = Field(description="Updated summary of the event")
    previous_start_time: str = Field(description="Original starting time of the event in ISO 8601 format")
    previous_end_time: str | None = Field(description="Original ending time of the event in ISO 8601 format")
    new_start_time: str | None = Field(description="Updated starting time of the event in ISO 8601 format")
    new_end_time: str | None = Field(description="Updated starting time of the event in ISO 8601 format")
    location: str | None = Field(description="Location of the event")
    guests: str | None = Field(description="Specified guests for the event")

class DeleteEvent(BaseModel):
    summary: str = Field(description="Updated summary of the event")
    start_time: str = Field(description="Starting time of the event in ISO 8601 format")

def get_tool_schemas():
    tools = [CreateEvent, UpdateEvent, DeleteEvent]
    declarations = []

    for tool in tools:
        schema = tool.model_json_schema()

        declarations.append(
            types.FunctionDeclaration(
                name=schema["title"],
                description=f"Executes the {schema['title']} operation on Google Calendar",
                parameters=schema
            )
        )
    return declarations