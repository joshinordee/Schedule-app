from tools.schemas import get_tool_schemas
from agent.prompts import system_prompt
from config import get_settings
from google import genai
from google.genai import types

settings = get_settings()
client = genai.Client(api_key=settings.gemini_api_key)
calendar_tools = [
    types.Tool(
        function_declarations=get_tool_schemas()
    )
]

# Create a chat session to keep chat history tracked 
chat = client.chats.create(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction=system_prompt,
        tools=calendar_tools,
        temperature=0.0 # Tool calling should be accurate and deterministic 
    )
)

def run_agent(user_input: str):
    print(f"\nUser: {user_input}")
    response = chat.send_message(user_input)

    # Tool is used
    if response.function_calls:
        for tool_call in response.function_calls:
            print(f"🔧 LLM triggered Tool: {tool_call.name}")
            print(f"📦 Payload: {tool_call.args}")

            mock_result = {
                "status": "Success",
                "message": "Calendar operation complete."
            }

            response = chat.send_message(
                types.Part.from_function_response(
                    name=tool_call.name,
                    response=mock_result
                )
            )
            print(f"Agent: {response.text}")
    else:
        # No tool was used
        print(f"Agent: {response.text}")


if __name__ == "__main__":
    while True:
        user_msg = input("\nType a request (or 'exit'): ")
        if user_msg.lower() == 'exit':
            break
        run_agent(user_msg)