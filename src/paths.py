"""Repository paths and external-tool locations (override with environment variables)."""
import os, subprocess, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CELLS_DIR = ROOT / "cells"
LIB_PATH = Path(os.environ.get("SKY130_LIB", ROOT / "lib" / "sky130_fd_sc_hd__tt_025C_1v80.lib"))
STA_BIN = os.environ.get("STA", "sta")                 # OpenSTA executable
PDK_VERILOG = os.environ.get("PDK_VERILOG", "")        # dir with sky130_fd_sc_hd.v + primitives.v (for glitch power)
FLOW_RESULTS = ROOT / "flow" / "results"

def run_sta(tcl_text: str, timeout: int = 300) -> str:
    """Run OpenSTA on a Tcl script; stdin is closed so it can never wait for a prompt."""
    with tempfile.NamedTemporaryFile("w", suffix=".tcl", delete=False) as f:
        f.write(tcl_text); name = f.name
    r = subprocess.run([STA_BIN, "-no_init", "-no_splash", name], capture_output=True, text=True,
                       stdin=subprocess.DEVNULL, timeout=timeout)
    os.unlink(name)
    return r.stdout + r.stderr
