from langgraph.graph import StateGraph,START,END
from langchain_google_genai import ChatGoogleGenerativeAI
from telegram import Update
from telegram.ext import ApplicationBuilder,CommandHandler,ContextTypes,MessageHandler,filters
from dotenv import load_dotenv
import os
from typing import TypedDict
load_dotenv()

llm=ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)


class AgentState(TypedDict):
    message :str
    response:str


def chatbot(state:AgentState):
    response=llm.invoke(state["message"])

    return {
        "response":response.content[0]['text']
    }


builder=StateGraph(AgentState)

builder.add_node("chatbot",chatbot)
builder.add_edge(START,"chatbot")
builder.add_edge("chatbot",END)
graph=builder.compile()


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(        "Hello! My name is AI Agent 🤖\n" "Ask me anything.")

async def chat(update:Update,context:ContextTypes.DEFAUIL_TYPE):
    user_message=update.message.text
    result= graph.invoke({
        "message": user_message,
        "response": ""


    })

    await update.message.reply_text(
        result["response"]
    )
app = ApplicationBuilder().token(os.getenv("bot_api")).build()


app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("start",start))
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        chat
    )
)


app.run_polling()
