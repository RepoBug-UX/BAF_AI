from nearai.agents.environment import Environment, ThreadMode

def run(env: Environment):
    prompt = {
        "role": "system",
        "content": """I am a travel planning assistant that can help organize your trips.
        I can help with:
        - Planning itineraries
        - Finding accommodations
        - Suggesting activities
        - Providing travel tips
        Just describe your travel plans or ask a travel-related question!"""
    }

    messages = env.list_messages()
    user_query = next((msg['content'] for msg in reversed(messages) if msg['role'] == 'user'), "")

    try:
        thread = env.run_agent(
            "travel.primitives.near/trip-organizer/latest",
            query=user_query,
            thread_mode=ThreadMode.FORK
        )
        response = f"Travel planning thread started!\n\nThread: {thread}\n\nI'm ready to help plan your trip!"
    except Exception as e:
        response = "Travel planning service is currently unavailable. Please try again later."

    env.add_reply(response)
    env.request_user_input()

run(env)