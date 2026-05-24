import sys
from pathlib import Path

from streamlit.web import cli as stcli


def main():
    dashboard = Path(__file__).parent / "dashboard.py"
    sys.argv = ["streamlit", "run", str(dashboard), "--server.headless=false"]
    sys.exit(stcli.main())
