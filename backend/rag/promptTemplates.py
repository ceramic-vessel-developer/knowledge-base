from backend.common.GeneratorConfigs import PromptType

_PROMPT_BASIC = """
Answer the question using only the provided context.
If the answer cannot be found in the context, say that
you do not have enough information.

Context:
{context}

Question:
{question}
"""
_PROMPTS_MAP = {PromptType.BASIC: _PROMPT_BASIC}


class PromptWrapper:
    def __init__(self, prompt: str):
        self.prompt = prompt

    def format_prompt(self, question: str, context: str):
        return self.prompt.format(context=context, question=question)


class PromptFactory:
    @staticmethod
    def create_prompt(prompt_type: PromptType) -> PromptWrapper:
        return PromptWrapper(_PROMPTS_MAP[prompt_type])
