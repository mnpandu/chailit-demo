import chainlit as cl
from chat_data_vector_store import build_vectorstore
from graph import build_graph
from time import sleep
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    vectorstore = build_vectorstore("data.txt")
    graph = build_graph(vectorstore)
except Exception as e:
    logger.error(f"Initialization failed: {str(e)}")
    raise

def create_action(name, label, description="", payload=None):
    return cl.Action(
        name=name,
        label=label,
        description=description,
        payload=payload or {"type": "system", "action": name}
    )

@cl.on_chat_start
async def start():
    try:
        #cl.user_session.set("mode", "chat")

        await cl.Message(
            content="## 🚀 Business Data Assistant\nSelect a mode:",
            actions=[
                create_action("set_chat_mode", "💬 Chat Mode", "Ask business questions", {"mode": "chat"}),
                create_action("set_similarity_mode", "🔍 Similarity Search", "Find similar cases", {"mode": "similarity"}),
                create_action("set_qc_mode", "🧪 QC Nurse (Agentic AI)", "Run QC automation", {"mode": "qc"})
            ]
        ).send()
    except Exception as e:
        logger.error(f"Start failed: {str(e)}")
        await cl.Message(content="⚠️ Initialization error. Please refresh.").send()

@cl.action_callback("set_chat_mode")
async def on_chat_action(action: cl.Action):
    await handle_mode_change("chat", "💬 **Chat Mode Activated**\nAsk business questions:")

@cl.action_callback("set_similarity_mode")
async def on_similarity_action(action: cl.Action):
    await handle_mode_change("similarity", "🔍 **Similarity Mode Activated**\nEnter case references:")

@cl.action_callback("set_qc_mode")
async def on_qc_action(action: cl.Action):
    await handle_mode_change("qc", "🧪 **QC Nurse Mode Activated**\nEnter Case Number for QC Task:")

async def handle_mode_change(new_mode: str, message: str):
    try:
        cl.user_session.set("mode", new_mode)
        actions = [
            create_action("set_chat_mode", "💬 Chat Mode", {"mode": "chat"}),
            create_action("set_similarity_mode", "🔍 Similarity Mode", {"mode": "similarity"}),
            create_action("set_qc_mode", "🧪 QC Nurse (Agentic AI)", {"mode": "qc"})
        ]
        await cl.Message(content=message, actions=actions).send()
    except Exception as e:
        logger.error(f"Mode change failed: {str(e)}")
        await cl.Message(content="⚠️ Mode change failed").send()

@cl.on_message
async def on_message(message: cl.Message):
    try:
        mode = cl.user_session.get("mode")

        if not mode:
            await cl.Message(content="⚠️ Please select at least one mode to continue.").send()
            return

        question = message.content.strip()
        if not question:
            await cl.Message(content="❌ Please enter a question").send()
            return

        msg = cl.Message(content="")
        await msg.send()

        result = graph.invoke({
            "question": question,
            "context": "",
            "answer": "",
            "mode": mode
        })

        answer = result.get("answer", "No answer generated")

        if mode == "similarity" and "| Rank |" in answer:
            # Send the table as a single markdown block
            await msg.stream_token(f"**Answer:**\n\n{answer}\n")
        else:
            # Stream regular text word-by-word
            await msg.stream_token("**Answer:** ")
            for word in answer.split():
                await msg.stream_token(word + " ")
                sleep(0.03)

        await msg.update()

    except Exception as e:
        logger.error(f"Message error: {str(e)}")
        await cl.Message(content=f"⚠️ Error: {str(e)}").send()

if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    graph.get_graph().print_ascii()
    run_chainlit(__file__)