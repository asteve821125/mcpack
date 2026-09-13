from pathlib import Path

root = Path(__file__).resolve().parent
source_dir = root / "source"
target = root / "scripts" / "main.js"
parts = sorted(source_dir.glob("main.part*.js.txt"))
if not parts:
    raise SystemExit("No source parts found")
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text("".join(p.read_text(encoding="utf-8") for p in parts), encoding="utf-8")
print(f"Rebuilt {target} from {len(parts)} parts")
