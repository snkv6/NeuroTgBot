from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass(frozen=True)
class Model:
    title: str
    openrouter_id: str
    vendor: str
    file_support: bool
    reasoning: bool
    premium_only: bool
    free_per_day: int
    premium_per_day: int


def load_models():
    path = str(Path(__file__).resolve().parent / "models.yaml")
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))

    models = {}
    for m in data["models"]:
        model = Model(
            title=m["title"],
            openrouter_id=m["openrouter_id"],
            vendor=m["vendor"],
            file_support=bool(m["file_support"]),
            reasoning=bool(m["reasoning"]),
            premium_only=bool(m["premium_only"]),
            free_per_day=int(m["free_per_day"]),
            premium_per_day=int(m["premium_per_day"]),
        )
        models[model.title] = model

    return models