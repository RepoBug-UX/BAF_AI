from nearai.agents.environment import Environment, ThreadMode

def run(env: Environment):
    prompt = {
        "role": "system",
        "content": """I am a multi-threaded assistant that can handle multiple tasks simultaneously.
        I can:
        - Process multiple requests in parallel
        - Maintain separate conversation threads
        - Coordinate between different agents
        Just use keywords like 'travel', 'crypto', or 'code' to trigger different threads!"""
    }

    messages = env.list_messages()

    user_query = next((msg['content'] for msg in reversed(messages) if msg['role'] == 'user'), "")
    user_query_lower = user_query.lower()

    triggers = {
        'travel': "travel.primitives.near/trip-organizer/latest",
        'crypto': "jasonbalayev.near/crypto-analyzer/0.0.1",
        'story': "souheila_jutsu.near/Story/0.0.5"
    }

    active_threads = []
    response_parts = []

    for keyword, agent_path in triggers.items():
        if keyword in user_query_lower:
            try:
                thread = env.run_agent(
                    agent_path,
                    query=user_query,
                    thread_mode=ThreadMode.FORK
                )
                active_threads.append((keyword, thread))
                response_parts.append(f" {keyword.title()} thread: {thread}")
            except Exception as e:
                response_parts.append(f"{keyword.title()} agent unavailable")

    if active_threads:
        response = "🚀 Multiple threads started!\n\n" + "\n\n".join(response_parts)
        response += "\n\nYou can interact with each thread separately!"
    else:
        response = "No specific triggers found. Use keywords like 'travel', 'crypto', or 'story' to start threads!"

    env.add_reply(response)
    env.request_user_input()

run(env)