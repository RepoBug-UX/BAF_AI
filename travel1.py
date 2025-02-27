from nearai.agents.environment import Environment, ThreadMode

def run(env: Environment):
    prompt = {
        "role": "system",
        "content": """I am a travel coordination assistant that helps connect you with expert travel planners.
        I can help with:
        - Vacation planning and itineraries
        - Destination recommendations
        - Travel arrangements and coordination
        Let me know where you'd like to go or what kind of trip you're planning of!"""
    }

    messages = env.list_messages()

    try:
        travel_thread = env.run_agent(
            "travel.primitives.near/trip-organizer/latest",
            query=messages[-1]['content'] if messages else "",
            thread_mode=ThreadMode.FORK
        )
        response = f"I'm connecting you with our travel expert!\n" \
                  f"Track your vacation planning here: {travel_thread}"
    except Exception as e:
        response = "Our travel agent seems unavailable. Please try again later."

    env.add_reply(response)
    env.request_user_input()

run(env)