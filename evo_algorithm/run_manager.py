import json
from pathlib import Path
from datetime import datetime


class RunManager:
    def __init__(self):
        self.runs_dir = Path(__file__).resolve().parent.parent / "results" / "runs"
        self.run_dir = None
        self.metadata = {}

    def _get_next_run_id(self):
        """Get the next run ID by finding the highest existing number prefix."""
        if not self.runs_dir.exists():
            return 1

        existing_runs = [d.name for d in self.runs_dir.iterdir() if d.is_dir()]
        max_id = 0

        for run_name in existing_runs:
            if run_name[0].isdigit():
                # Extract leading number
                num_str = ""
                for char in run_name:
                    if char.isdigit():
                        num_str += char
                    else:
                        break
                if num_str:
                    max_id = max(max_id, int(num_str))

        return max_id + 1

    def setup_run(self, run_name, parameters, fitness_function=None):
        """Create run directory and initialize metadata with auto-incrementing ID."""
        # Add auto-incrementing ID prefix
        run_id = self._get_next_run_id()
        run_name_with_id = f"{run_id}_{run_name}"

        self.run_dir = self.runs_dir / run_name_with_id
        self.run_dir.mkdir(parents=True, exist_ok=True)

        self.metadata = {
            "run_name": run_name_with_id,
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
