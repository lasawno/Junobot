import os
import sys
from pathlib import Path

from streamlit.web import cli as stcli


def main():
    dashboard = Path(__file__).parent / "dashboard.py"
    port = os.environ.get("PORT", "8501")
    sys.argv = [
        "streamlit",
        "run",
        str(dashboard),
        f"--server.port={port}",
        "--server.address=0.0.0.0",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
    ]
    sys.exit(stcli.main())
