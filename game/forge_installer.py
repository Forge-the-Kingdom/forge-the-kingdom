"""
forge_installer.py — Ren'Py installer module for "Forge the Kingdom"

Installs and configures OpenClaw + Gemini Wizard agent behind the scenes
while the visual novel narrative drives the player experience.

Every public function is safe to call from Ren'Py — exceptions are caught
internally and returned as user-friendly error strings. The game never crashes.
"""

import json
import os
import platform
import re
import shutil
import ssl
import subprocess
import sys
import threading
import time
from datetime import datetime

# SSL context for Ren'Py's bundled Python (lacks system CA certs)
try:
    _fi_ssl_ctx = ssl.create_default_context()
    _fi_ssl_ctx.load_default_certs()
except Exception:
    _fi_ssl_ctx = ssl.create_default_context()
    _fi_ssl_ctx.check_hostname = False
    _fi_ssl_ctx.verify_mode = ssl.CERT_NONE
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

NODE_DOWNLOAD_URL = "https://nodejs.org/en/download"
OPENCLAW_NPM_PACKAGE = "openclaw"

# Cron definitions for the kingdom
DEFAULT_CRONS = {
    "scrying_glass": {
        "name": "Scrying Glass",
        "schedule": "*/30 * * * *",
        "description": "Scan for threats and anomalies every 30 minutes",
        "command": "openclaw invoke scrying-glass --scan",
    },
    "knights_patrol": {
        "name": "Knights Patrol",
        "schedule": "0 */4 * * *",
        "description": "Run security patrols every 4 hours",
        "command": "openclaw invoke knights-patrol --sweep",
    },
    "daily_digest": {
        "name": "Daily Digest",
        "schedule": "0 8 * * *",
        "description": "Morning kingdom status report at 8 AM",
        "command": "openclaw invoke daily-digest --report",
    },
}

# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------

def detect_platform():
    """Return a dict with platform info and standard paths."""
    system = platform.system().lower()  # 'darwin', 'windows', 'linux'
    home = Path.home()

    if system == "darwin":
        label = "mac"
        openclaw_paths = [
            home / ".nvm" / "versions",  # nvm installs
            Path("/usr/local/bin/openclaw"),
            Path("/opt/homebrew/bin/openclaw"),
            home / ".npm-global" / "bin" / "openclaw",
        ]
        config_dir = home / ".openclaw"
    elif system == "windows":
        label = "windows"
        appdata = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
        openclaw_paths = [
            appdata / "npm" / "openclaw.cmd",
            appdata / "npm" / "openclaw",
            Path("C:/Program Files/nodejs/openclaw.cmd"),
        ]
        config_dir = appdata / "openclaw"
    else:
        label = "linux"
        openclaw_paths = [
            Path("/usr/local/bin/openclaw"),
            Path("/usr/bin/openclaw"),
            home / ".npm-global" / "bin" / "openclaw",
            home / ".nvm" / "versions",
        ]
        config_dir = home / ".openclaw"

    return {
        "system": system,
        "label": label,
        "home": str(home),
        "config_dir": str(config_dir),
        "openclaw_search_paths": [str(p) for p in openclaw_paths],
        "arch": platform.machine(),
    }

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

_log_dir = Path.home() / ".forge-kingdom"
_log_file = _log_dir / "install.log"

def _ensure_log_dir():
    _log_dir.mkdir(parents=True, exist_ok=True)

def _mask_key(key):
    """Show first 4 chars of an API key, mask the rest."""
    if not key or len(key) < 5:
        return "****"
    return key[:4] + "..." + ("*" * 4)

def log(message, level="INFO"):
    """Append a timestamped line to the install log."""
    try:
        _ensure_log_dir()
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] [{level}] {message}\n"
        with open(_log_file, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass  # Logging must never crash the game

# ---------------------------------------------------------------------------
# Subprocess helpers
# ---------------------------------------------------------------------------

def _run(cmd, timeout=120, shell=None):
    """Run a shell command, return (returncode, stdout, stderr).
    
    cmd can be a string (uses shell=True) or a list (uses shell=False).
    """
    if shell is None:
        shell = isinstance(cmd, str)
    # Mask potential secrets in log output
    log_cmd = re.sub(r'(sk-ant-\S+|AIza\S+|sk-\S{8,})', '***MASKED***', str(cmd))
    log(f"Running command: {log_cmd}")
    try:
        env = os.environ.copy()
        # Ensure common bin dirs are on PATH for macOS/Linux
        extra = ":".join([
            str(Path.home() / ".nvm" / "versions" / "node"),
            "/usr/local/bin",
            "/opt/homebrew/bin",
            str(Path.home() / ".npm-global" / "bin"),
        ])
        env["PATH"] = extra + ":" + env.get("PATH", "")

        result = subprocess.run(
            cmd, shell=shell, capture_output=True, text=True,
            timeout=timeout, env=env,
        )
        log(f"Command finished: rc={result.returncode}")
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        log(f"Command timed out after {timeout}s: {cmd}", "WARN")
        return -1, "", "Command timed out"
    except Exception as e:
        log(f"Command failed: {e}", "ERROR")
        return -1, "", str(e)


def _run_async(cmd, callback=None):
    """Run a command in a background thread. Calls callback(rc, stdout, stderr) when done."""
    def _worker():
        rc, out, err = _run(cmd, timeout=300)
        if callback:
            callback(rc, out, err)
    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    return t

# ---------------------------------------------------------------------------
# Progress persistence
# ---------------------------------------------------------------------------

def _progress_path():
    _ensure_log_dir()
    return _log_dir / "install_progress.json"

def save_progress(step, data=None):
    """Mark an install step as complete. `data` is optional extra info."""
    try:
        progress = load_progress()
        progress["steps"][step] = {
            "completed": True,
            "timestamp": datetime.now().isoformat(),
            "data": data,
        }
        progress["last_step"] = step
        with open(_progress_path(), "w", encoding="utf-8") as f:
            json.dump(progress, f, indent=2)
        log(f"Progress saved: step={step}")
        return True
    except Exception as e:
        log(f"Failed to save progress: {e}", "ERROR")
        return False

def load_progress():
    """Load install progress. Returns dict with 'steps' and 'last_step'."""
    try:
        p = _progress_path()
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        log(f"Failed to load progress: {e}", "WARN")
    return {"steps": {}, "last_step": None}

def is_step_complete(step):
    """Check if a specific install step has been completed."""
    progress = load_progress()
    return progress.get("steps", {}).get(step, {}).get("completed", False)

def reset_progress():
    """Clear all progress (for debugging / replay)."""
    try:
        p = _progress_path()
        if p.exists():
            p.unlink()
        log("Progress reset")
        return True
    except Exception as e:
        log(f"Failed to reset progress: {e}", "ERROR")
        return False

# ---------------------------------------------------------------------------
# Node.js detection
# ---------------------------------------------------------------------------

def check_nodejs():
    """Check if Node.js is installed. Returns (installed: bool, version: str, error: str)."""
    try:
        rc, out, _ = _run("node --version")
        if rc == 0 and out:
            log(f"Node.js found: {out}")
            return True, out, ""
        return False, "", "Node.js not found in PATH"
    except Exception as e:
        return False, "", str(e)

def check_npm():
    """Check if npm is available. Returns (installed: bool, version: str, error: str)."""
    try:
        rc, out, _ = _run("npm --version")
        if rc == 0 and out:
            log(f"npm found: {out}")
            return True, out, ""
        return False, "", "npm not found in PATH"
    except Exception as e:
        return False, "", str(e)

def nodejs_install_instructions():
    """Return human-readable instructions for installing Node.js."""
    info = detect_platform()
    label = info["label"]
    lines = [f"Node.js is required but not installed on your {label} system.", ""]
    if label == "mac":
        lines += [
            "Option 1 — Homebrew (recommended):",
            "  Open Terminal and run: brew install node",
            "",
            "Option 2 — Official installer:",
            f"  Download from {NODE_DOWNLOAD_URL}",
        ]
    elif label == "windows":
        lines += [
            "Download the Windows installer from:",
            f"  {NODE_DOWNLOAD_URL}",
            "",
            "Run the .msi and follow the prompts.",
        ]
    else:
        lines += [
            "Option 1 — Package manager:",
            "  Ubuntu/Debian: sudo apt install nodejs npm",
            "  Fedora: sudo dnf install nodejs",
            "",
            "Option 2 — Official installer:",
            f"  {NODE_DOWNLOAD_URL}",
        ]
    return "\n".join(lines)

# ---------------------------------------------------------------------------
# OpenClaw detection & installation
# ---------------------------------------------------------------------------

def check_openclaw_installed():
    """
    Check if OpenClaw is installed.
    Returns (installed: bool, path: str, version: str, error: str).
    """
    try:
        # First try which/where
        which_cmd = "where" if platform.system().lower() == "windows" else "which"
        rc, out, _ = _run(f"{which_cmd} openclaw")
        if rc == 0 and out:
            oc_path = out.split("\n")[0].strip()
            rc2, ver, _ = _run("openclaw --version")
            version = ver if rc2 == 0 else "unknown"
            log(f"OpenClaw found at {oc_path} (v{version})")
            return True, oc_path, version, ""

        # Search common paths
        info = detect_platform()
        for p in info["openclaw_search_paths"]:
            if os.path.isfile(p) and os.access(p, os.X_OK):
                log(f"OpenClaw found at {p}")
                return True, p, "unknown", ""

        return False, "", "", "OpenClaw not found"
    except Exception as e:
        log(f"Error checking OpenClaw: {e}", "ERROR")
        return False, "", "", str(e)

def install_openclaw(callback=None):
    """
    Install OpenClaw via npm. Non-blocking — runs in a background thread.
    
    callback(success: bool, message: str) is called when done.
    Returns the thread handle.
    """
    log("Starting OpenClaw installation")

    # Pre-flight: check Node.js
    node_ok, _, node_err = check_nodejs()
    if not node_ok:
        msg = f"Cannot install OpenClaw: {node_err}\n\n{nodejs_install_instructions()}"
        log(msg, "ERROR")
        if callback:
            callback(False, msg)
        return None

    def _on_done(rc, stdout, stderr):
        if rc == 0:
            save_progress("openclaw_installed")
            log("OpenClaw installed successfully")
            if callback:
                callback(True, "OpenClaw installed successfully!")
        else:
            err = stderr or stdout or "Unknown error"
            log(f"OpenClaw install failed: {err}", "ERROR")
            if callback:
                callback(False, f"Installation failed: {err}")

    return _run_async(f"npm install -g {OPENCLAW_NPM_PACKAGE}", callback=_on_done)

# ---------------------------------------------------------------------------
# API key validation
# ---------------------------------------------------------------------------

def validate_anthropic_key(key):
    """
    Validate an Anthropic API key with a minimal API call.
    Returns (success: bool, error: str).
    """
    log(f"Validating Anthropic key {_mask_key(key)}")
    try:
        # Use urllib since we can't assume requests is installed in Ren'Py
        import urllib.request
        import urllib.error

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=json.dumps({
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1,
                "messages": [{"role": "user", "content": "hi"}],
            }).encode("utf-8"),
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            method="POST",
        )

        resp = urllib.request.urlopen(req, timeout=15, context=_fi_ssl_ctx)
        log("Anthropic key validated successfully")
        return True, ""

    except urllib.error.HTTPError as e:
        if e.code == 401:
            return False, "Invalid API key — authentication failed."
        elif e.code == 403:
            return False, "API key lacks required permissions."
        elif e.code == 429:
            # Rate limited but key is valid
            log("Anthropic key valid (rate-limited)")
            return True, ""
        elif e.code == 400:
            # Bad request but auth passed — key is valid
            return True, ""
        else:
            body = e.read().decode("utf-8", errors="replace")[:200]
            return False, f"API error (HTTP {e.code}): {body}"
    except urllib.error.URLError as e:
        return False, f"Network error: {e.reason}"
    except Exception as e:
        return False, f"Validation error: {e}"

def validate_gemini_key(key):
    """
    Validate a Google Gemini API key.
    Returns (success: bool, error: str).
    """
    log(f"Validating Gemini key {_mask_key(key)}")
    try:
        import urllib.request
        import urllib.error

        # List models endpoint is a lightweight way to verify the key
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
        req = urllib.request.Request(url, method="GET")
        resp = urllib.request.urlopen(req, timeout=15, context=_fi_ssl_ctx)
        log("Gemini key validated successfully")
        return True, ""

    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            return False, "Invalid API key — authentication failed."
        elif e.code == 429:
            return True, ""  # rate-limited but valid
        else:
            body = e.read().decode("utf-8", errors="replace")[:200]
            return False, f"API error (HTTP {e.code}): {body}"
    except urllib.error.URLError as e:
        return False, f"Network error: {e.reason}"
    except Exception as e:
        return False, f"Validation error: {e}"

# ---------------------------------------------------------------------------
# OpenClaw configuration
# ---------------------------------------------------------------------------

def configure_openclaw(anthropic_key):
    """
    Configure OpenClaw gateway with the Anthropic API key.
    Returns (success: bool, error: str).
    """
    log(f"Configuring OpenClaw with Anthropic key {_mask_key(anthropic_key)}")
    try:
        # Try CLI first (use list args to prevent shell injection)
        rc, out, err = _run(
            ["openclaw", "configure", "set", "anthropic_api_key", anthropic_key],
            shell=False,
        )
        if rc == 0:
            save_progress("openclaw_configured", {"key_prefix": anthropic_key[:4]})
            log("OpenClaw configured via CLI")
            return True, ""

        # Fall back to writing config directly
        log("CLI configure failed, writing config file directly", "WARN")
        info = detect_platform()
        config_dir = Path(info["config_dir"])
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "gateway.json"

        config = {}
        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except (json.JSONDecodeError, OSError):
                config = {}

        config["anthropic_api_key"] = anthropic_key

        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        # Secure the file (non-Windows)
        if platform.system().lower() != "windows":
            os.chmod(config_file, 0o600)

        save_progress("openclaw_configured", {"key_prefix": anthropic_key[:4]})
        log("OpenClaw configured via direct file write")
        return True, ""

    except Exception as e:
        log(f"Failed to configure OpenClaw: {e}", "ERROR")
        return False, f"Configuration failed: {e}"

def configure_wizard(gemini_key):
    """
    Configure the Merith wizard agent with the Gemini API key.
    Returns (success: bool, error: str).
    """
    log(f"Configuring Merith wizard with Gemini key {_mask_key(gemini_key)}")
    try:
        # Try CLI (use list args to prevent shell injection)
        rc, out, err = _run(
            ["openclaw", "configure", "set", "gemini_api_key", gemini_key],
            shell=False,
        )
        cli_ok = rc == 0

        # Write the wizard agent config
        info = detect_platform()
        config_dir = Path(info["config_dir"])
        agents_dir = config_dir / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)

        wizard_config = {
            "name": "merith",
            "display_name": "Merith the Wizard",
            "description": "Kingdom wizard powered by Gemini — your magical advisor and agent orchestrator",
            "provider": "gemini",
            "model": "gemini-2.0-flash",
            "api_key": gemini_key,
            "system_prompt": (
                "You are Merith, a wise and powerful wizard serving the kingdom. "
                "You help the ruler manage their domain through magical insight, "
                "strategic counsel, and arcane automation. Speak with warmth and "
                "a touch of mysticism."
            ),
            "enabled": True,
        }

        wizard_file = agents_dir / "merith.json"
        with open(wizard_file, "w", encoding="utf-8") as f:
            json.dump(wizard_config, f, indent=2)

        if platform.system().lower() != "windows":
            os.chmod(wizard_file, 0o600)

        save_progress("wizard_configured", {"key_prefix": gemini_key[:4]})
        log("Merith wizard configured")
        return True, ""

    except Exception as e:
        log(f"Failed to configure wizard: {e}", "ERROR")
        return False, f"Wizard configuration failed: {e}"

# ---------------------------------------------------------------------------
# Cron setup
# ---------------------------------------------------------------------------

def setup_default_crons():
    """
    Configure the standard kingdom cron jobs.
    Returns (success: bool, results: dict, error: str).
    """
    log("Setting up default kingdom crons")
    results = {}

    try:
        info = detect_platform()
        config_dir = Path(info["config_dir"])
        crons_dir = config_dir / "crons"
        crons_dir.mkdir(parents=True, exist_ok=True)

        for cron_id, cron_def in DEFAULT_CRONS.items():
            try:
                # Try CLI first (use list args to prevent injection)
                rc, _, err = _run(
                    ["openclaw", "cron", "add", cron_def["name"],
                     "--schedule", cron_def["schedule"],
                     "--command", cron_def["command"]],
                    shell=False,
                )
                if rc == 0:
                    results[cron_id] = {"success": True, "method": "cli"}
                    log(f"Cron '{cron_id}' added via CLI")
                    continue

                # Fall back to file
                cron_file = crons_dir / f"{cron_id}.json"
                with open(cron_file, "w", encoding="utf-8") as f:
                    json.dump(cron_def, f, indent=2)
                results[cron_id] = {"success": True, "method": "file"}
                log(f"Cron '{cron_id}' written to file")

            except Exception as e:
                results[cron_id] = {"success": False, "error": str(e)}
                log(f"Failed to set up cron '{cron_id}': {e}", "WARN")

        all_ok = all(r.get("success") for r in results.values())
        if all_ok:
            save_progress("crons_configured")

        return all_ok, results, ""

    except Exception as e:
        log(f"Cron setup failed: {e}", "ERROR")
        return False, results, str(e)

# ---------------------------------------------------------------------------
# Status checks
# ---------------------------------------------------------------------------

def check_openclaw_running():
    """Check if the OpenClaw gateway daemon is running. Returns (running: bool, error: str)."""
    try:
        rc, out, _ = _run("openclaw gateway status", timeout=10)
        if rc == 0:
            # Look for signs it's running
            running = any(w in out.lower() for w in ["running", "active", "listening"])
            return running, ""
        return False, "Gateway not running"
    except Exception as e:
        return False, str(e)

def start_openclaw():
    """Start the OpenClaw gateway. Returns (success: bool, error: str)."""
    log("Starting OpenClaw gateway")
    try:
        rc, out, err = _run("openclaw gateway start", timeout=30)
        if rc == 0:
            save_progress("gateway_started")
            log("Gateway started")
            return True, ""
        return False, err or "Failed to start gateway"
    except Exception as e:
        log(f"Failed to start gateway: {e}", "ERROR")
        return False, str(e)

def full_status():
    """
    Return a comprehensive status dict for all components.
    Safe to call at any time — never raises.
    """
    status = {
        "platform": {},
        "nodejs": {"installed": False, "version": ""},
        "openclaw": {"installed": False, "path": "", "version": "", "running": False},
        "wizard": {"configured": False},
        "crons": {"configured": False},
        "progress": {},
    }

    try:
        status["platform"] = detect_platform()
    except Exception:
        pass

    try:
        ok, ver, _ = check_nodejs()
        status["nodejs"] = {"installed": ok, "version": ver}
    except Exception:
        pass

    try:
        ok, path, ver, _ = check_openclaw_installed()
        running, _ = check_openclaw_running() if ok else (False, "")
        status["openclaw"] = {
            "installed": ok,
            "path": path,
            "version": ver,
            "running": running,
        }
    except Exception:
        pass

    try:
        progress = load_progress()
        status["wizard"]["configured"] = is_step_complete("wizard_configured")
        status["crons"]["configured"] = is_step_complete("crons_configured")
        status["progress"] = progress
    except Exception:
        pass

    return status

# ---------------------------------------------------------------------------
# Skip / convenience
# ---------------------------------------------------------------------------

def skip_all():
    """
    Mark all install steps as skipped. For players who just want the story.
    Returns True on success.
    """
    log("Player chose to skip all installation steps")
    skip_steps = [
        "openclaw_installed",
        "openclaw_configured",
        "wizard_configured",
        "crons_configured",
        "gateway_started",
    ]
    for step in skip_steps:
        save_progress(step, {"skipped": True})
    save_progress("all_complete", {"skipped": True})
    return True

def is_all_complete():
    """Check if all install steps are done (or skipped)."""
    required = [
        "openclaw_installed",
        "openclaw_configured",
        "wizard_configured",
        "crons_configured",
    ]
    return all(is_step_complete(s) for s in required)

# ---------------------------------------------------------------------------
# High-level orchestrator (for Ren'Py to call step-by-step)
# ---------------------------------------------------------------------------

def get_next_step():
    """
    Determine the next installation step to perform.
    Returns a step name string, or None if all done.
    
    Step order:
      1. check_nodejs
      2. install_openclaw
      3. configure_openclaw
      4. configure_wizard
      5. setup_crons
      6. start_gateway
    """
    if not is_step_complete("openclaw_installed"):
        installed, _, _, _ = check_openclaw_installed()
        if installed:
            save_progress("openclaw_installed", {"pre_existing": True})
        else:
            return "install_openclaw"

    if not is_step_complete("openclaw_configured"):
        return "configure_openclaw"

    if not is_step_complete("wizard_configured"):
        return "configure_wizard"

    if not is_step_complete("crons_configured"):
        return "setup_crons"

    if not is_step_complete("gateway_started"):
        return "start_gateway"

    return None  # All done!


# ---------------------------------------------------------------------------
# Facade API — bridges .rpy files to internal functions
# These aliases ensure installer_integration.rpy and installer_screens.rpy
# can call consistent, expected function names.
# ---------------------------------------------------------------------------

# Aliases for installer_integration.rpy (which uses `fi.` prefix)
check_node_installed = lambda: check_nodejs()[0]
check_npm_installed = lambda: check_npm()[0]


def install_openclaw_sync(timeout=300):
    """
    Blocking install of OpenClaw. Returns (success: bool, message: str).
    Used by installer_integration.rpy which expects a synchronous call.
    """
    result = {"done": False, "success": False, "message": "Prerequisites not met"}

    def _cb(success, message):
        result["success"] = success
        result["message"] = message
        result["done"] = True

    thread = install_openclaw(callback=_cb)
    if thread is None:
        return False, result["message"]

    thread.join(timeout=timeout)
    if not result["done"]:
        return False, "Installation timed out"
    return result["success"], result["message"]


def flat_status():
    """
    Flattened status dict for Ren'Py templates.
    installer_integration.rpy reads keys like status["openclaw_installed"].
    """
    try:
        s = full_status()
        return {
            "openclaw_installed": s.get("openclaw", {}).get("installed", False),
            "openclaw_running": s.get("openclaw", {}).get("running", False),
            "anthropic_configured": is_step_complete("openclaw_configured"),
            "gemini_configured": is_step_complete("wizard_configured"),
            "crons_active": is_step_complete("crons_configured"),
        }
    except Exception:
        return {
            "openclaw_installed": False,
            "openclaw_running": False,
            "anthropic_configured": False,
            "gemini_configured": False,
            "crons_active": False,
        }


def check_online():
    """Quick connectivity check. Returns True if we can reach the internet."""
    try:
        import urllib.request
        urllib.request.urlopen("https://registry.npmjs.org", timeout=5, context=_fi_ssl_ctx)
        return True
    except Exception:
        return False


# --- Facade for installer_screens.rpy ---

def validate_key(key_type, value):
    """Unified key validation for screens. Raises ValueError on failure."""
    if key_type in ("anthropic", "openclaw"):
        ok, err = validate_anthropic_key(value)
    elif key_type == "gemini":
        ok, err = validate_gemini_key(value)
    else:
        raise ValueError(f"Unknown key type: {key_type}")
    if not ok:
        raise ValueError(err)
    return True


def check_existing(key_type):
    """Check if a key type is already configured."""
    try:
        if key_type in ("anthropic", "openclaw"):
            return is_step_complete("openclaw_configured")
        elif key_type == "gemini":
            return is_step_complete("wizard_configured")
    except Exception:
        pass
    return False


def save_key(key_type, value):
    """Save a validated key to the appropriate config."""
    if key_type in ("anthropic", "openclaw"):
        return configure_openclaw(value)
    elif key_type == "gemini":
        return configure_wizard(value)
    return False, f"Unknown key type: {key_type}"


def detect_prerequisites():
    """Return list of prerequisite checks for installer_screens.rpy."""
    checks = []
    try:
        node_ok, ver, _ = check_nodejs()
        checks.append({
            "label": f"Node.js {'v' + ver if node_ok else 'not found'}",
            "ok": node_ok,
        })
    except Exception:
        checks.append({"label": "Node.js — check failed", "ok": False})

    try:
        npm_ok, ver, _ = check_npm()
        checks.append({
            "label": f"npm {'v' + ver if npm_ok else 'not found'}",
            "ok": npm_ok,
        })
    except Exception:
        checks.append({"label": "npm — check failed", "ok": False})

    checks.append({
        "label": "Git " + ("detected" if shutil.which("git") else "not found"),
        "ok": shutil.which("git") is not None,
    })

    checks.append({
        "label": "Internet " + ("connected" if check_online() else "offline"),
        "ok": check_online(),
    })

    return checks
