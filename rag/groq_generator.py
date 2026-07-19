"""Groq implementation of the RAG response generator."""

import os

from groq import Groq

from .generator import ResponseGenerator
from .vector_store import SearchResult


class GroqResponseGenerator(ResponseGenerator):
    """Generate grounded answers using Groq."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "llama-3.3-70b-versatile",
    ):
        self.client = Groq(
            api_key=api_key or os.getenv("GROQ_API_KEY")
        )
        self.model = model

    def generate(
        self,
        question: str,
        context: list[SearchResult],
    ) -> str:

        context_text = "\n\n".join(
            result.record.content
            for result in context
        )

        prompt = f"""
You are an AI Credit Underwriting Assistant.

Answer ONLY using the supplied context.

If the answer is not present in the context,
reply:

"I don't have enough information from the knowledge base."

--------------------
Context

{context_text}

--------------------

Question:
{question}

Answer:
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You answer only from retrieved context.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.2,
                timeout=30,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Groq Error: {e}")
            raise