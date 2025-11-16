import os
import logging
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class LLMModel:

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("GROQ_MODEL") or "llama-3.3-70b-versatile"

        if not self.api_key:
            raise ValueError("Missing GROQ_API_KEY in .env")

        self.client = Groq(api_key=self.api_key)

    # -----------------------------
    # GENERATE (Single Prompt)
    # -----------------------------
    def generate(self, prompt: str, temperature: float = 0.7):
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert education advisor."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature
            )
            return completion.choices[0].message.content

        except Exception as e:
            logger.error("LLM generation error: %s", e)
            return "⚠️ Sorry, I couldn't generate the roadmap right now."

    # -----------------------------
    # CHAT (Conversation Mode)
    # -----------------------------
    def chat(self, user_message: str, history):
        try:
            # history already formatted in retriever
            history.append({"role": "user", "content": user_message})

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=history,
                temperature=0.7,
            )

            return completion.choices[0].message.content

        except Exception as e:
            logger.error("Chat continuation failed: %s", e)
            return "⚠️ Sorry, I could not continue the conversation."
