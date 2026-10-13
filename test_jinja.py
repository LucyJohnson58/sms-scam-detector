from pathlib import Path
from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).resolve().parent
templates_dir = BASE_DIR / "templates"

print("Looking in:", templates_dir)
print("Exists:", templates_dir.exists())

if templates_dir.exists():
    for f in templates_dir.iterdir():
        print("  Found file:", repr(f.name), "| extension:", repr(f.suffix))

env = Environment(loader=FileSystemLoader(str(templates_dir)))
try:
    tmpl = env.get_template("index.html")
    print("\n✅ Jinja2 found index.html!")
    print("First 100 chars:", repr(tmpl.render()[:100]))
except Exception as e:
    print("\n❌ Jinja2 error:", type(e).__name__, "-", e)