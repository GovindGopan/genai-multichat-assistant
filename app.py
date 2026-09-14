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


# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


# Create database tables
create_tables()


# Streamlit page
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


# Create a conversation if none exists
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


messages = get_messages(conversation_id)


# Display messages
for role, content in messages:

    with st.chat_message(role):
        st.write(content)


# --------------------------------------------------
# CHAT INPUT
# --------------------------------------------------

user_input = st.chat_input("Type your message...")


if user_input:

    # If this is the first message,
    # use it as the conversation title
    if len(messages) == 0:

        title = user_input.strip()

        if len(title) > 40:
            title = title[:40] + "..."

        update_conversation_title(
            conversation_id,
            title
        )


    # Save user message
    save_message(
        conversation_id,
        "user",
        user_input
    )


    # Display user message
    with st.chat_message("user"):
        st.write(user_input)


    # Send message to Gemini
    response = client.interactions.create(
        model="gemini-3.6-flash",
        input=user_input
    )

    answer = response.output_text


    # Save AI response
    save_message(
        conversation_id,
        "assistant",
        answer
    )


    # Display AI response
    with st.chat_message("assistant"):
        st.write(answer)
