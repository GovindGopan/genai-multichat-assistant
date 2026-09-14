import os
import streamlit as st
from dotenv import load_dotenv
from google import genai

from database.database import (
    create_tables,
    create_conversation,
    save_message,
    get_messages,
    get_latest_conversation
)


# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


# Create database tables
create_tables()


# Streamlit page
st.title("GenAI Chatbot")


# Initialize conversation ID
if "conversation_id" not in st.session_state:

    latest_conversation = get_latest_conversation()

    if latest_conversation is not None:
        st.session_state["conversation_id"] = latest_conversation[0]
    else:
        st.session_state["conversation_id"] = create_conversation()


# Get messages from the current conversation
conversation_id = st.session_state["conversation_id"]

messages = get_messages(conversation_id)


# Display previous messages
for role, content in messages:

    with st.chat_message(role):
        st.write(content)


# Chat input
user_input = st.chat_input("Type your message...")


if user_input:

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

