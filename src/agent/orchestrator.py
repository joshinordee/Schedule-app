from tools.schemas import get_tool_schemas, CreateEvent, UpdateEvent, DeleteEvent
from agent.prompts import system_prompt
from config import get_settings
from google import genai
from google.genai import types
import httpx

settings = get_settings()
client = genai.Client(api_key=settings.gemini_api_key)
calendar_tools = [
    types.Tool(
        function_declarations=get_tool_schemas()
    )
]

# Map string names to pydantic classes for runtime validation
TOOL_MAPPING = {
    "CreateEvent": CreateEvent,
    "UpdateEvent": UpdateEvent,
    "DeleteEvent": DeleteEvent
}

# Create a chat session to keep chat history tracked 
chat = client.chats.create(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction=system_prompt,
        tools=calendar_tools,
        temperature=0.0 # Tool calling should be accurate and deterministic 
    )
)

def execute_mock_tool(name: str, raw_args: dict) -> dict:
    try:
        model_class = TOOL_MAPPING.get(name)
        if not model_class:
            return {
                "status": "Error",
                "message": f"Tool: {name} not found"
            }
        
        validated_data = model_class(**raw_args)
        print(f"🔧 Successfully validated schema for {name}: {validated_data.model_dump()}")
        return {
            "status": "Success",
            "message": f"Successfully processed {name}"
        }
    except Exception as e:
        print(f"❌ LLM failed validation for {name}: {str(e)}")
        return {
            "status": "Error", 
            "message": f"Invalid arguments provided: {str(e)}"
        }

def run_agent(user_input: str):
    print(f"\nUser: {user_input}")
    try:

        response = chat.send_message(user_input)

        # Tool is used
        if response.function_calls:
            tool_calls = []

            for tool_call in response.function_calls:
                print(f"🔧 LLM requested: {tool_call.name}")

                result = execute_mock_tool(tool_call.name, tool_call.args)

                tool_calls.append(
                    types.Part.from_function_response(
                        name=tool_call.name,
                        response=result
                    )
                )
            final_summary = chat.send_message(tool_calls)
            print(f"Agent: {final_summary.text}")
        else:
            # No tool was used
            print(f"Agent: {response.text}")
    except httpx.ConnectTimeout:
        print("Agent: I'm having trouble connecting to the server right now. Could you please try that again?")
    except Exception as e:
        print(f"Agent: An unexpected error occurred with the AI service: {e}")


if __name__ == "__main__":
    while True:
        user_msg = input("\nType a request (or 'exit'): ")
        if user_msg.lower() == 'exit':
            break
        run_agent(user_msg)