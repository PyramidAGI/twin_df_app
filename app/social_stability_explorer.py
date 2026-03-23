from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Any

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_JSON = BASE_DIR / "data" / "Examples" / "vase-table.json"
DEFAULT_LOG  = BASE_DIR / "logs" / "social_stability.log"

GRID_SIZE = 10
ROWS = list("ABCDEFGHIJ")
COLS = list(range(1, 11))


@dataclass
class SocialObject:
    object_id: str
    label: str
    domain: str
    cell: str
    properties: Dict[str, float | str]


class SocialStabilityExplorer:
    """
    Sparse 10x10 world-model explorer for the social domain.

    Idea:
    - keep a sparse pandas DataFrame as the outer-world grid
    - attach social objects with properties
    - scan the objects through the lens of stability
    - emit messages in the form: o1,o2,property,value
    - fire threshold crossings to a log file
    """

    def __init__(self, base_grid: List[List[str]], threshold: float = 0.65, log_path: str = "social_stability.log") -> None:
        self.df = pd.DataFrame(base_grid, index=ROWS, columns=COLS)
        self.threshold = threshold
        self.log_path = Path(log_path)
        self.objects: Dict[str, SocialObject] = {}
        self.message_buffer: List[str] = []
        self._configure_logging()

    def _configure_logging(self) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(f"social_stability_{id(self)}")
        self.logger.setLevel(logging.INFO)
        self.logger.handlers.clear()
        handler = logging.FileHandler(self.log_path, mode="w", encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s | %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def place_object(self, obj: SocialObject) -> None:
        row, col = self.cell_to_index(obj.cell)
        self.objects[obj.object_id] = obj
        self.df.loc[row, col] = obj.label

    @staticmethod
    def cell_to_index(cell: str) -> Tuple[str, int]:
        row = cell[0].upper()
        col = int(cell[1:])
        return row, col

    def emit_message(self, o1: str, o2: str, prop: str, value: Any) -> str:
        msg = f"{o1},{o2},{prop},{value}"
        self.message_buffer.append(msg)
        return msg

    def threshold_crossed(self, value: float) -> bool:
        return value >= self.threshold

    def evaluate_social_stability(self) -> pd.DataFrame:
        rows = []
        for obj in self.objects.values():
            stability = float(obj.properties.get("stability", 0.0))
            tension = float(obj.properties.get("tension", 0.0))
            trust = float(obj.properties.get("trust", 0.0))
            engagement = float(obj.properties.get("engagement", 0.0))

            state = self.classify_state(stability=stability, tension=tension, trust=trust, engagement=engagement)
            rows.append(
                {
                    "object_id": obj.object_id,
                    "label": obj.label,
                    "cell": obj.cell,
                    "stability": stability,
                    "tension": tension,
                    "trust": trust,
                    "engagement": engagement,
                    "state": state,
                }
            )

            self.emit_message("sensor", obj.object_id, "stability", stability)
            self.emit_message(obj.object_id, "social_field", "state", state)

            if self.threshold_crossed(tension):
                self.fire_alert(obj.object_id, "social_field", "tension", tension, "tension threshold passed")

            if trust < (1.0 - self.threshold):
                self.fire_alert(obj.object_id, "social_field", "trust", trust, "trust dropped below safe band")

            if stability < (1.0 - self.threshold):
                self.fire_alert(obj.object_id, "social_field", "stability", stability, "stability dropped below safe band")

        return pd.DataFrame(rows)

    def classify_state(self, *, stability: float, tension: float, trust: float, engagement: float) -> str:
        if tension >= 0.85:
            return "threshold_crossing"
        if stability >= 0.75 and tension <= 0.35 and trust >= 0.65:
            return "stable"
        if 0.45 <= tension < 0.65 and trust >= 0.5:
            return "stress_accumulation"
        if stability < 0.35 or trust < 0.3:
            return "drift"
        if engagement < 0.3:
            return "withdrawal"
        return "watch"

    def fire_alert(self, o1: str, o2: str, prop: str, value: Any, explanation: str) -> None:
        message = self.emit_message(o1, o2, prop, value)
        self.logger.info("ALERT | %s | %s", message, explanation)

    def neighborhood_messages(self) -> List[str]:
        """
        Emit simple adjacency-based messages for nearby social objects.
        This lets the sparse grid act as an outer-world map.
        """
        ids = list(self.objects.keys())
        for i, left_id in enumerate(ids):
            left = self.objects[left_id]
            lr, lc = self.cell_to_index(left.cell)
            for right_id in ids[i + 1 :]:
                right = self.objects[right_id]
                rr, rc = self.cell_to_index(right.cell)
                manhattan = abs(ROWS.index(lr) - ROWS.index(rr)) + abs(lc - rc)
                if manhattan <= 3:
                    self.emit_message(left_id, right_id, "social_distance", manhattan)
        return self.message_buffer


def load_example_grid(json_path: str) -> List[List[str]]:
    """
    Reads the uploaded sparse template and then maps it into a social-domain seed.
    The uploaded example contains a 10x10 sparse grid with anchor words such as
    'Vase', '90', 'Loc', 'Stability', and 'Table'.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    _ = raw["grid"]  # keeps the original shape as the template

    social_grid = [[f"{ROWS[r]}{c+1}" for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]

    # Social reinterpretation of the sparse anchor idea
    social_grid[2][2] = "Person_A"
    social_grid[4][4] = "0.82"         # example social stability score
    social_grid[5][4] = "Workplace"    # location / context
    social_grid[7][7] = "Stability"
    social_grid[8][8] = "SocialTable"

    return social_grid


def build_social_explorer(uploaded_json_path: str, log_path: str = "social_stability.log") -> SocialStabilityExplorer:
    grid = load_example_grid(uploaded_json_path)
    explorer = SocialStabilityExplorer(base_grid=grid, threshold=0.65, log_path=log_path)

    seed_objects = [
        SocialObject(
            object_id="o1",
            label="Alice",
            domain="social",
            cell="C3",
            properties={"stability": 0.82, "tension": 0.28, "trust": 0.74, "engagement": 0.71},
        ),
        SocialObject(
            object_id="o2",
            label="Bob",
            domain="social",
            cell="D4",
            properties={"stability": 0.42, "tension": 0.69, "trust": 0.46, "engagement": 0.61},
        ),
        SocialObject(
            object_id="o3",
            label="Manager",
            domain="social",
            cell="F5",
            properties={"stability": 0.31, "tension": 0.88, "trust": 0.22, "engagement": 0.67},
        ),
        SocialObject(
            object_id="o4",
            label="TeamMeeting",
            domain="social",
            cell="H8",
            properties={"stability": 0.58, "tension": 0.55, "trust": 0.52, "engagement": 0.83},
        ),
    ]

    for obj in seed_objects:
        explorer.place_object(obj)

    return explorer


def run_demo(uploaded_json_path: str = str(DEFAULT_JSON)) -> Tuple[pd.DataFrame, List[str], str]:
    explorer = build_social_explorer(uploaded_json_path=uploaded_json_path, log_path=str(DEFAULT_LOG))
    status_df = explorer.evaluate_social_stability()
    messages = explorer.neighborhood_messages()
    return status_df, messages, str(explorer.log_path)


if __name__ == "__main__":
    status_df, messages, log_path = run_demo()

    print("=== Sparse social world grid ===")
    print(build_social_explorer(str(DEFAULT_JSON)).df)
    print("\n=== Stability evaluation ===")
    print(status_df.to_string(index=False))
    print("\n=== Emitted messages ===")
    for msg in messages:
        print(msg)
    print(f"\nLog written to: {log_path}")
