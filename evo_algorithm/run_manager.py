import json
from pathlib import Path
from datetime import datetime


class RunManager:
    def __init__(self):
        self.runs_dir = Path(__file__).resolve().parent.parent / "results" / "runs"
        self.run_dir = None
        self.metadata = {}

    def setup_run(self, run_name, parameters, fitness_function=None):
        """Create run directory and initialize metadata."""
        self.run_dir = self.runs_dir / run_name
        self.run_dir.mkdir(parents=True, exist_ok=True)

        self.metadata = {
            "run_name": run_name,
            "timestamp": datetime.now().isoformat(),
            "parameters": parameters
        }

        if fitness_function:
            self.metadata["fitness_function"] = fitness_function

        self._save_metadata()
        return self.run_dir

    def _save_metadata(self):
        """Save metadata to JSON file."""
        metadata_path = self.run_dir / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(self.metadata, f, indent=2)

    def get_run_dir(self):
        """Return the current run directory."""
        return self.run_dir
