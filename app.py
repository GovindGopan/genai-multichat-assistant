import os
import streamlit as st
from dotenv import load_dotenv
from google import genai

from database.database import (
    create_tables,
    create_conversation,
    get_conversations,
    save_message,
    get_messages,
    update_conversation_title
)

from memory.memory import (
    add_memory,
    search_memories
)


# --------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


# --------------------------------------------------
# DATABASE SETUP
# --------------------------------------------------

create_tables()


# --------------------------------------------------
# STREAMLIT PAGE
# --------------------------------------------------

st.title("GenAI Chatbot")


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("Conversations")


if st.sidebar.button("+ New Chat"):

    new_conversation_id = create_conversation()

    st.session_state.conversation_id = new_conversation_id

    st.rerun()


# Get all conversations
conversations = get_conversations()


# Create first conversation if none exists
if not conversations:

    new_conversation_id = create_conversation()

    st.session_state.conversation_id = new_conversation_id

    st.rerun()


# Initialize selected conversation
if "conversation_id" not in st.session_state:

    st.session_state.conversation_id = conversations[0][0]


# Display conversations
for conversation_id, title in conversations:

    if st.sidebar.button(
        title,
        key=f"conversation_{conversation_id}"
    ):

        st.session_state.conversation_id = conversation_id

        st.rerun()


# --------------------------------------------------
# CURRENT CONVERSATION
# --------------------------------------------------

conversation_id = st.session_state.conversation_id


# Get messages for current conversation
messages = get_messages(conversation_id)


# Display previous messages
for role, content in messages:

    with st.chat_message(role):
        st.write(content)


# --------------------------------------------------
# CHAT INPUT
# --------------------------------------------------

user_input = st.chat_input("Type your message...")


if user_input:

    # --------------------------------------------------
    # BUILD SHORT-TERM CONVERSATION HISTORY
    # --------------------------------------------------

    conversation_history = ""

    for role, content in messages:

        if role == "user":

            conversation_history += (
                f"User: {content}\n"
            )

        elif role == "assistant":

            conversation_history += (
                f"Assistant: {content}\n"
            )


    # Add current question
    conversation_history += (
        f"User: {user_input}\n"
    )


    # --------------------------------------------------
    # CONVERSATION TITLE
    # --------------------------------------------------

    if len(messages) == 0:

        title = user_input.strip()

        if len(title) > 40:

            title = title[:40] + "..."

        update_conversation_title(
            conversation_id,
            title
        )


    # --------------------------------------------------
    # SAVE USER MESSAGE
    # --------------------------------------------------

    save_message(
        conversation_id,
        "user",
        user_input
    )


    # Display user message
    with st.chat_message("user"):

        st.write(user_input)


    # --------------------------------------------------
    # LONG-TERM MEMORY
    # --------------------------------------------------

    memory_keywords = [
        "my name is",
        "i am learning",
        "i'm learning",
        "i like",
        "i love",
        "my goal is",
        "i want to learn",
        "i prefer"
    ]


    user_input_lower = user_input.lower()


    for keyword in memory_keywords:

        if keyword in user_input_lower:

            add_memory(
                f"User said: {user_input}"
            )

            break


    # --------------------------------------------------
    # RETRIEVE RELEVANT LONG-TERM MEMORIES
    # --------------------------------------------------

    relevant_memories = search_memories(
        user_input
    )


    memory_context = ""

    if relevant_memories:

        memory_context = "\n".join(
            relevant_memories
        )


    # --------------------------------------------------
    # CREATE GEMINI PROMPT
    # --------------------------------------------------

    prompt = f"""
You are a helpful personal AI assistant.

Use the conversation history to understand the
current conversation.

Use the long-term memories only when they are
relevant to the user's current question.

Do not invent information that is not present
in the conversation or memories.

Conversation history:
{conversation_history}

Long-term memories:
{memory_context}

User's latest message:
{user_input}

Respond naturally and helpfully.
"""


    # --------------------------------------------------
    # CALL GEMINI
    # --------------------------------------------------

    try:

        response = client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt
        )

        answer = response.output_text


    except Exception as e:

        answer = (
            "Sorry, I couldn't connect to the AI service."
        )

        print("Gemini API error:", e)


    # --------------------------------------------------
    # SAVE AI RESPONSE
    # --------------------------------------------------

    save_message(
        conversation_id,
        "assistant",
        answer
    )


    # Display AI response
    with st.chat_message("assistant"):

        st.write(answer)
