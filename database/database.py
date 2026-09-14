import sqlite3
from pathlib import Path


# Database location
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_NAME = BASE_DIR / "chatbot.db"


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id)
                REFERENCES conversations(id)
        )
    """)

    connection.commit()
    connection.close()


def create_conversation(title="New Conversation"):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO conversations (title) VALUES (?)",
        (title,)
    )

    conversation_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return conversation_id


def update_conversation_title(conversation_id, title):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE conversations
        SET title = ?
        WHERE id = ?
        """,
        (title, conversation_id)
    )

    connection.commit()
    connection.close()


def get_conversations():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, title
        FROM conversations
        ORDER BY id DESC
        """
    )

    conversations = cursor.fetchall()

    connection.close()

    return conversations


def save_message(conversation_id, role, content):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO messages (conversation_id, role, content)
        VALUES (?, ?, ?)
        """,
        (conversation_id, role, content)
    )

    connection.commit()
    connection.close()


def get_messages(conversation_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT role, content
        FROM messages
        WHERE conversation_id = ?
        ORDER BY id
        """,
        (conversation_id,)
    )

    messages = cursor.fetchall()

    connection.close()

    return messages


def delete_conversation(conversation_id):
    connection = get_connection()
    cursor = connection.cursor()

    # Delete all messages belonging to the conversation
    cursor.execute(
        """
        DELETE FROM messages
        WHERE conversation_id = ?
        """,
        (conversation_id,)
    )

    # Delete the conversation
    cursor.execute(
        """
        DELETE FROM conversations
        WHERE id = ?
        """,
        (conversation_id,)
    )

    connection.commit()
    connection.close()

