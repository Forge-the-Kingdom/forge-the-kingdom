"""
Game Pilot Bridge — Ren'Py TCP Interface
Exposes game state over localhost:47201 for AI control.
JSON-over-TCP, one object per line.

Built by Linus 🔧 for Anna's Game Pilot system.
"""

import json
import socket
import threading
import traceback
import os

PORT = 47201
HOST = "127.0.0.1"

# Global state tracked via hooks
_current_speaker = None
_current_dialogue = None
_current_choices = None
_choice_result = None
_choice_event = threading.Event()
_server_thread = None
_running = False


def _install_hooks():
    """Install hooks into Ren'Py to track dialogue and choices."""
    import renpy  # noqa — available inside Ren'Py process

    # Track current dialogue via say callback
    old_callback = renpy.config.say_menu_text_filter
    def text_filter(text):
        if old_callback:
            text = old_callback(text)
        return text

    # Use character callback to track speaker + text
    original_all_character_callbacks = list(renpy.config.all_character_callbacks) if hasattr(renpy.config, 'all_character_callbacks') else []

    def character_callback(event, interact=True, **kwargs):
        global _current_speaker, _current_dialogue
        if event == "begin":
            _current_speaker = kwargs.get("who", None)
            _current_dialogue = kwargs.get("what", None)
        for cb in original_all_character_callbacks:
            try:
                cb(event, interact=interact, **kwargs)
            except Exception:
                pass

    renpy.config.all_character_callbacks = [character_callback]

    # Track choices via menu callback
    original_choice_screen_cb = getattr(renpy.config, 'choice_screen_callback', None)

    print(f"[GamePilot] Hooks installed")


def _get_state():
    """Gather current game state. Must be called from main thread."""
    import renpy
    result = {
        "label": None,
        "speaker": _current_speaker,
        "dialogue": _current_dialogue,
        "choices": [],
        "variables": {}
    }

    # Current label
    try:
        if renpy.game.context().current:
            result["label"] = renpy.game.context().current
    except Exception:
        pass

    # Choices from choice screen
    try:
        scr = renpy.display.screen.get_screen("choice")
        if scr is not None:
            items = scr.scope.get("items", [])
            result["choices"] = [
                {"index": i, "caption": str(getattr(item, "caption", item))}
                for i, item in enumerate(items)
            ]
    except Exception:
        pass

    # Key variables
    key_vars = [
        "kingdom_name", "player_name", "player_title",
        "chapter", "quest_log", "forge_lit", "gateway_raised",
        "coronation_complete", "merith_awakened"
    ]
    for v in key_vars:
        try:
            if hasattr(renpy.store, v):
                val = getattr(renpy.store, v)
                # Only serialize JSON-safe types
                if isinstance(val, (str, int, float, bool, list, dict, type(None))):
                    result["variables"][v] = val
                else:
                    result["variables"][v] = str(val)
        except Exception:
            pass

    return result


def _get_choices():
    """Get current choice options."""
    import renpy
    try:
        scr = renpy.display.screen.get_screen("choice")
        if scr is not None:
            items = scr.scope.get("items", [])
            return {
                "ok": True,
                "choices": [
                    {"index": i, "caption": str(getattr(item, "caption", item))}
                    for i, item in enumerate(items)
                ]
            }
    except Exception as e:
        return {"ok": False, "error": str(e)}
    return {"ok": True, "choices": []}


def _choose(index):
    """Select a choice by index."""
    import renpy
    try:
        scr = renpy.display.screen.get_screen("choice")
        if scr is None:
            return {"ok": False, "error": "No choice screen active"}
        items = scr.scope.get("items", [])
        if index < 0 or index >= len(items):
            return {"ok": False, "error": f"Index {index} out of range (0-{len(items)-1})"}
        item = items[index]
        # The choice action is typically stored as item.action
        action = getattr(item, "action", None)
        if action is not None:
            renpy.display.behavior.run(action)
            return {"ok": True, "chosen": index}
        return {"ok": False, "error": "Choice has no action"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _advance():
    """Advance dialogue by injecting a proper pygame mouse click event."""
    import renpy
    # First try the Ren'Py dismiss mechanism
    try:
        renpy.display.interface.act("dismiss")
        return {"ok": True, "method": "dismiss"}
    except Exception:
        pass
    # Fallback: inject a proper pygame mouse click at center of game
    try:
        import pygame_sdl2 as pygame
        # Create proper mouse events with all required attributes
        center_x = renpy.config.screen_width // 2
        center_y = renpy.config.screen_height // 2
        down = pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                   pos=(center_x, center_y),
                                   button=1)
        up = pygame.event.Event(pygame.MOUSEBUTTONUP,
                                 pos=(center_x, center_y),
                                 button=1)
        pygame.event.post(down)
        pygame.event.post(up)
        return {"ok": True, "method": "mouse_click"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _read_variables(names):
    """Read store variables by name."""
    import renpy
    result = {}
    for name in names:
        try:
            if hasattr(renpy.store, name):
                val = getattr(renpy.store, name)
                if isinstance(val, (str, int, float, bool, list, dict, type(None))):
                    result[name] = val
                else:
                    result[name] = str(val)
            else:
                result[name] = None
        except Exception as e:
            result[name] = f"<error: {e}>"
    return {"ok": True, "variables": result}


def _set_variable(name, value):
    """Set a store variable."""
    import renpy
    try:
        setattr(renpy.store, name, value)
        return {"ok": True, "name": name, "value": value}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _screenshot(path):
    """Save a screenshot."""
    import renpy
    try:
        path = path or "/tmp/game-pilot-screenshot.png"
        # Try multiple screenshot approaches
        try:
            # Ren'Py 8.x approach
            surf = renpy.display.draw.screenshot(None)
            if surf is not None:
                import pygame_sdl2 as pygame
                pygame.image.save(surf, path)
                return {"ok": True, "path": path}
        except Exception:
            pass
        try:
            # Alternative: use renpy.exports
            renpy.exports.screenshot(path)
            return {"ok": True, "path": path}
        except Exception:
            pass
        # Fallback: use screencapture (macOS)
        import subprocess
        subprocess.run(["/usr/sbin/screencapture", "-R", "731,70,1281,749", path],
                       timeout=5, capture_output=True)
        import os
        if os.path.exists(path):
            return {"ok": True, "path": path, "method": "screencapture"}
        return {"ok": False, "error": "All screenshot methods failed"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _jump(label):
    """Jump to a label."""
    import renpy
    try:
        # Check label existence via the script object
        try:
            has = renpy.game.script.has_label(label)
        except Exception:
            try:
                has = label in renpy.game.script.namemap
            except Exception:
                has = True  # Assume it exists and let jump fail if not
        if has:
            renpy.jump(label)
            return {"ok": True, "label": label}
        return {"ok": False, "error": f"Label '{label}' not found"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _safe_main_thread(fn, *args):
    """Try invoke_in_main_thread, fall back to direct call."""
    import renpy
    try:
        return renpy.invoke_in_main_thread(fn, *args)
    except (AttributeError, Exception):
        # Fallback: call directly (safe for reads, risky for actions)
        return fn(*args)


def _handle_command(data):
    """Route a command dict to the appropriate handler."""
    cmd = data.get("cmd", "")

    if cmd == "ping":
        return {"ok": True, "engine": "renpy", "game": "Forge the Kingdom"}

    if cmd == "state":
        try:
            result = {"ok": True}
            state = _safe_main_thread(_get_state)
            result.update(state)
            return result
        except Exception as e:
            return {"ok": False, "error": str(e)}

    if cmd == "choices":
        try:
            return _safe_main_thread(_get_choices)
        except Exception as e:
            return {"ok": False, "error": str(e)}

    if cmd == "choose":
        index = data.get("index", 0)
        try:
            return _safe_main_thread(_choose, index)
        except Exception as e:
            return {"ok": False, "error": str(e)}

    if cmd == "advance":
        try:
            return _safe_main_thread(_advance)
        except Exception as e:
            return {"ok": False, "error": str(e)}

    if cmd == "variables":
        names = data.get("names", [])
        try:
            return _safe_main_thread(_read_variables, names)
        except Exception as e:
            return {"ok": False, "error": str(e)}

    if cmd == "set_variable":
        name = data.get("name", "")
        value = data.get("value", None)
        try:
            return _safe_main_thread(_set_variable, name, value)
        except Exception as e:
            return {"ok": False, "error": str(e)}

    if cmd == "screenshot":
        path = data.get("path", "/tmp/game-pilot-screenshot.png")
        try:
            return _safe_main_thread(_screenshot, path)
        except Exception as e:
            return {"ok": False, "error": str(e)}

    if cmd == "jump":
        label = data.get("label", "")
        try:
            return _safe_main_thread(_jump, label)
        except Exception as e:
            return {"ok": False, "error": str(e)}

    return {"ok": False, "error": f"Unknown command: {cmd}"}


def _handle_client(conn, addr):
    """Handle a single client connection."""
    try:
        conn.settimeout(10.0)
        buf = b""
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            buf += chunk
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line.decode("utf-8"))
                    response = _handle_command(data)
                except json.JSONDecodeError as e:
                    response = {"ok": False, "error": f"Invalid JSON: {e}"}
                except Exception as e:
                    response = {"ok": False, "error": str(e)}
                try:
                    conn.sendall(json.dumps(response).encode("utf-8") + b"\n")
                except Exception:
                    return
            # If buffer has no newline yet but looks complete, try parsing
            if buf and b"\n" not in buf:
                try:
                    data = json.loads(buf.decode("utf-8"))
                    response = _handle_command(data)
                    conn.sendall(json.dumps(response).encode("utf-8") + b"\n")
                    buf = b""
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass  # Wait for more data
                except Exception as e:
                    try:
                        conn.sendall(json.dumps({"ok": False, "error": str(e)}).encode("utf-8") + b"\n")
                    except Exception:
                        pass
                    buf = b""
    except socket.timeout:
        pass
    except Exception as e:
        print(f"[GamePilot] Client error: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass


def _server_loop():
    """Main server loop."""
    global _running
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((HOST, PORT))
        server.listen(5)
        server.settimeout(1.0)
        print(f"[GamePilot] Bridge listening on {HOST}:{PORT}")
        while _running:
            try:
                conn, addr = server.accept()
                t = threading.Thread(target=_handle_client, args=(conn, addr), daemon=True)
                t.start()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"[GamePilot] Accept error: {e}")
    except Exception as e:
        print(f"[GamePilot] Server error: {e}")
        traceback.print_exc()
    finally:
        try:
            server.close()
        except Exception:
            pass
        print("[GamePilot] Bridge stopped")


def start():
    """Start the Game Pilot bridge server."""
    global _server_thread, _running
    if _running:
        print("[GamePilot] Already running")
        return
    _running = True
    _install_hooks()
    _server_thread = threading.Thread(target=_server_loop, daemon=True, name="GamePilot")
    _server_thread.start()
    print("[GamePilot] Bridge started on port 47201")


def stop():
    """Stop the bridge server."""
    global _running
    _running = False
    print("[GamePilot] Bridge stopping...")
