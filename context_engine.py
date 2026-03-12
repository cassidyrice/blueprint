import os

class ContextEngine:
    """
    Manages the 'Brain' of the production system.
    Loads personas and templates to assemble high-fidelity prompts for LLMs.
    """
    PROMPTS_DIR = os.path.join(os.path.dirname(__file__), ".prompts")

    @classmethod
    def get_persona(cls, persona_name: str) -> str:
        """Load a system persona from the .prompts/personas directory."""
        path = os.path.join(cls.PROMPTS_DIR, "personas", f"{persona_name}.md")
        if not os.path.exists(path):
            return "You are a helpful assistant."
        with open(path, "r") as f:
            return f.read().strip()

    @classmethod
    def build_prompt(cls, persona: str, template: str, **kwargs) -> tuple[str, str]:
        """
        Assembles a full context payload.
        Returns (system_prompt, user_prompt)
        """
        system = cls.get_persona(persona)
        user = template.format(**kwargs)
        return system, user

# Singleton instance
engine = ContextEngine()
