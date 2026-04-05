from dataclasses import dataclass, field
from typing import Optional

@dataclass
class PromptTemplate:
    id: str
    version: str
    description: str
    template: str
    filename: str  # Track which file this came from for hot-reloading
    metadata: dict = field(default_factory=dict)

    def render(self, **kwargs) -> str:
        """Renders the template with the provided variables."""
        from jinja2 import Template
        j2_template = Template(self.template)
        return j2_template.render(**kwargs)
