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
    update_conversation_title,
    delete_conversation
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

if not api_key:
    st.error("GEMINI_API_KEY is not configured. Check your .env file.")
    st.stop()

client = genai.Client(api_key=api_key)


# --------------------------------------------------
# DATABASE SETUP
# --------------------------------------------------

try:
    create_tables()

except Exception as e:

    st.error("Could not initialize the database.")
    print("Database error:", e)
    st.stop()


# --------------------------------------------------
# STREAMLIT PAGE
# --------------------------------------------------

st.title("GenAI Chatbot")


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("Conversations")


# New Chat
if st.sidebar.button("+ New Chat"):

    try:

        new_conversation_id = create_conversation()

        st.session_state.conversation_id = new_conversation_id

        st.rerun()

    except Exception as e:

        st.sidebar.error("Could not create a new conversation.")
        print("Create conversation error:", e)


# Get conversations
try:

    conversations = get_conversations()

except Exception as e:

    st.error("Could not load conversations.")
    print("Get conversations error:", e)
    st.stop()


# Create initial conversation
if not conversations:

    try:

        new_conversation_id = create_conversation()

        st.session_state.conversation_id = new_conversation_id

        st.rerun()

    except Exception as e:

        st.error("Could not create the first conversation.")
        print("Create conversation error:", e)
        st.stop()


# Initialize conversation
if "conversation_id" not in st.session_state:

    st.session_state.conversation_id = conversations[0][0]


# --------------------------------------------------
# DISPLAY CONVERSATIONS
# --------------------------------------------------

for conversation_id, title in conversations:

    col1, col2 = st.sidebar.columns([4, 1])

    with col1:

        if st.button(
            title,
            key=f"conversation_{conversation_id}"
        ):

            st.session_state.conversation_id = conversation_id

            st.rerun()

    with col2:

        if st.button(
            "🗑",
            key=f"delete_{conversation_id}"
        ):

            try:

                delete_conversation(conversation_id)

                remaining_conversations = get_conversations()

                if remaining_conversations:

                    if st.session_state.conversation_id == conversation_id:

                        st.session_state.conversation_id = (
                            remaining_conversations[0][0]
                        )

                else:

                    st.session_state.conversation_id = (
                        create_conversation()
                    )

                st.rerun()

            except Exception as e:

                st.sidebar.error("Could not delete conversation.")
                print("Delete conversation error:", e)


# --------------------------------------------------
# CURRENT CONVERSATION
# --------------------------------------------------

conversation_id = st.session_state.conversation_id


try:

    messages = get_messages(conversation_id)

except Exception as e:

    st.error("Could not load conversation messages.")
    print("Get messages error:", e)
    st.stop()


# --------------------------------------------------
# DISPLAY MESSAGE HISTORY
# --------------------------------------------------

for role, content in messages:

    with st.chat_message(role):

        st.write(content)


# --------------------------------------------------
# CHAT INPUT
# --------------------------------------------------

user_input = st.chat_input("Type your message...")


if user_input:

    # --------------------------------------------------
    # BUILD SHORT-TERM MEMORY
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

        try:

            update_conversation_title(
                conversation_id,
                title
            )

        except Exception as e:

            print("Update title error:", e)


    # --------------------------------------------------
    # SAVE USER MESSAGE
    # --------------------------------------------------

    try:

        save_message(
            conversation_id,
            "user",
            user_input
        )

    except Exception as e:

        st.error("Could not save your message.")
        print("Save user message error:", e)
        st.stop()


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

            try:

                add_memory(
                    f"User said: {user_input}"
                )

            except Exception as e:

                print("Memory storage error:", e)

            break


    # --------------------------------------------------
    # RETRIEVE LONG-TERM MEMORY
    # --------------------------------------------------

    try:

        relevant_memories = search_memories(
            user_input
        )

    except Exception as e:

        print("Memory retrieval error:", e)

        relevant_memories = []


    # --------------------------------------------------
    # BUILD RAG CONTEXT
    # --------------------------------------------------

    rag_context = ""

    if relevant_memories:

        rag_context = "\n".join(
            relevant_memories
        )

    else:

        rag_context = "No relevant long-term memory found."


    # --------------------------------------------------
    # GEMINI PROMPT
    # --------------------------------------------------

    prompt = f"""
You are a helpful personal AI assistant.

Use the conversation history to understand the
current conversation.

Use retrieved long-term memory only when it is
relevant to the user's question.

If the information is not available in the
conversation or retrieved memory, do not invent it.

Conversation history:
{conversation_history}

Retrieved context from long-term memory:
{rag_context}

User's latest message:
{user_input}

Respond naturally and helpfully.
"""


    # --------------------------------------------------
    # GEMINI API
    # --------------------------------------------------

    try:

        response = client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt
        )

        answer = response.output_text

    except Exception as e:

        print("Gemini API error:", e)

        answer = (
            "Sorry, I couldn't connect to the AI service. "
            "Please try again."
        )


    # --------------------------------------------------
    # SAVE ASSISTANT RESPONSE
    # --------------------------------------------------

    try:

        save_message(
            conversation_id,
            "assistant",
            answer
        )

    except Exception as e:

        print("Save assistant message error:", e)


    # --------------------------------------------------
    # DISPLAY ASSISTANT RESPONSE
    # --------------------------------------------------

    with st.chat_message("assistant"):

        st.write(answer)

