from pydantic import BaseModel, Field
from google.genai import types

class CreateEvent(BaseModel):
    summary: str = Field(description="Summary of the created event")
    start_time: str = Field(description="Starting time of the event in ISO 8601 format")
    end_time: str = Field(description="Ending time of the event in ISO 8601 format")
    location: str | None = Field(default=None, description="Location of the event")
    guests: str | None = Field(default=None, description="Specified guests for the event")

class UpdateEvent(BaseModel):
    summary: str = Field(description="Updated summary of the event")
    previous_start_time: str = Field(description="Original starting time of the event in ISO 8601 format")
    previous_end_time: str | None = Field(default=None, description="Original ending time of the event in ISO 8601 format")
    new_start_time: str | None = Field(default=None, description="Updated starting time of the event in ISO 8601 format")
    new_end_time: str | None = Field(default=None, description="Updated starting time of the event in ISO 8601 format")
    location: str | None = Field(default=None, description="Location of the event")
    guests: str | None = Field(default=None, description="Specified guests for the event")

class DeleteEvent(BaseModel):
    summary: str = Field(description="Updated summary of the event")
    start_time: str = Field(description="Starting time of the event in ISO 8601 format")

def get_tool_schemas():
    tools = [CreateEvent, UpdateEvent, DeleteEvent]
    declarations = []

    for tool in tools:
        schema = tool.model_json_schema()

        properties = {}
        # Iterate through properties to extract the types
        for prop, prop_val in schema.get("properties", {}).items():
            # Required types like summary: str
            if "type" in prop_val:
                prop_type = prop_val["type"]
            # For optional types like location: str | None
            elif "anyOf" in prop_val:
                prop_type = "string"

                for option in prop_val["anyOf"]:
                    option_type = option.get("type")

                    if option_type == "null":
                        continue
                    
                    if option_type:
                        prop_type = option_type
                        break
            else:
                prop_type = "string"

            # Create OpenAPI property object
            properties[prop] = {
                "type": prop_type.upper(),
                "description": prop_val.get("description", "")
            }
        # Build parameters object
        extracted_params = types.Schema(
            type=types.Type.OBJECT,
            properties=properties,
            required=schema.get("required", [])
        )
        declarations.append(
            types.FunctionDeclaration(
                name=tool.__name__,
                description=f"Executes the {tool.__name__} operation on Google Calendar",
                parameters=extracted_params
            )
        )
    return declarations