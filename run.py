"""
Convenience CLI Runner for the Credit Risk Intelligence Platform.
Usage:
    python run.py
"""
import sys
import subprocess
from pathlib import Path

# Windows asyncio WinError 10054 connection reset silencer
try:
    import backend.patch_asyncio  # noqa: F401
except ImportError:
    pass

def main():
    app_path = Path(__file__).resolve().parent / "app.py"
    cmd = [sys.executable, "-m", "streamlit", "run", str(app_path)]
    print(f"Launching Credit Risk Intelligence Platform: {' '.join(cmd)}")
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")

if __name__ == "__main__":
    main()
