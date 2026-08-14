import sys
from pathlib import Path

# Add project directory (01-agent-durable-runtime) to sys.path so tests can import `src`
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
