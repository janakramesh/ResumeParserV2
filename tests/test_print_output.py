import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
STRUCTURED_DIR = PROJECT_ROOT / "output" / "structured"
FIELDS = ("name", "email", "github", "linkedin", "education", "technical_skills")

def main():
    files = sorted(STRUCTURED_DIR.glob("*.json"))
    if not files:
        print(f"No structured JSON files found in: {STRUCTURED_DIR}")
        return

    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        print(f"\n========== {data.get('file_name', path.name)} ==========")
        for field in FIELDS:
            value = data.get(field) or "Not found"
            print(f"\n{field.replace('_', ' ').title()}:\n{value}")

if __name__ == "__main__":
    main()
