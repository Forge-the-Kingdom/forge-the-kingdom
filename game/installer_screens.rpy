## installer_screens.rpy — Forge the Kingdom API Key & Installation UI
## Medieval-themed screens for OpenClaw setup woven into the narrative.

init python:
    import importlib
    try:
        forge_installer = importlib.import_module("forge_installer")
    except ImportError:
        forge_installer = None

    # ── Colours ──────────────────────────────────────────────
    FORGE_GOLD        = "#f0c040"
    FORGE_GOLD_DIM    = "#b8942e"
    FORGE_PURPLE_DARK = "#1a1028"
    FORGE_PURPLE_MID  = "#2d1f42"
    FORGE_PURPLE_BG   = "#0e0a16"
    FORGE_GREEN       = "#44dd66"
    FORGE_RED         = "#dd4466"
    FORGE_WHITE       = "#e8e0f0"
    FORGE_GREY        = "#665577"

    # ── Action: Validate an API key ─────────────────────────
    class ForgeValidateKey(Action):
        """Call forge_installer.validate_key(key_type, value). Sets store results."""
        def __init__(self, key_type):
            self.key_type = key_type

        def __call__(self):
            store.forge_validating = True
            store.forge_valid_result = None
            store.forge_error_msg = ""
            renpy.restart_interaction()

        def get_sensitive(self):
            return True

    class ForgeDoValidation(Action):
        """Actually run the validation (called from a timer after state flip)."""
        def __init__(self, key_type):
            self.key_type = key_type

        def __call__(self):
            key_val = getattr(store, "forge_key_value", "")
            if not key_val.strip():
                store.forge_validating = False
                store.forge_valid_result = False
                store.forge_error_msg = "The scroll is blank. Paste thy key first."
                renpy.restart_interaction()
                return
            try:
                if forge_installer:
                    ok = forge_installer.validate_key(self.key_type, key_val.strip())
                else:
                    # Demo/fallback: accept non-empty keys
                    ok = len(key_val.strip()) > 10
                store.forge_validating = False
                store.forge_valid_result = ok
                store.forge_error_msg = "" if ok else "The rune was rejected. Check thy key and try again."
            except Exception as e:
                store.forge_validating = False
                store.forge_valid_result = False
                store.forge_error_msg = str(e)
            renpy.restart_interaction()

    class ForgeCheckExisting(Action):
        """Check if a key_type is already configured."""
        def __init__(self, key_type):
            self.key_type = key_type

        def __call__(self):
            try:
                if forge_installer:
                    ok = forge_installer.check_existing(self.key_type)
                else:
                    ok = False
                if ok:
                    store.forge_valid_result = True
                    store.forge_error_msg = ""
                else:
                    store.forge_error_msg = "No existing rune found for this seal."
                    store.forge_valid_result = None
            except Exception as e:
                store.forge_error_msg = str(e)
            renpy.restart_interaction()

    class ForgeSubmitKey(Action):
        """Save a validated key and return."""
        def __init__(self, key_type):
            self.key_type = key_type

        def __call__(self):
            key_val = getattr(store, "forge_key_value", "")
            if forge_installer:
                forge_installer.save_key(self.key_type, key_val.strip())
            renpy.return_statement(True)

    class ForgeSkip(Action):
        def __call__(self):
            renpy.return_statement(False)

    # ── Pulse transform ─────────────────────────────────────
    def forge_pulse_alpha(trans, st, at):
        import math
        trans.alpha = 0.55 + 0.45 * math.sin(st * 3.0)
        return 0.02

    def forge_spin(trans, st, at):
        trans.rotate = (st * 180.0) % 360.0
        return 0.02

    def forge_fire_flicker(trans, st, at):
        import math
        trans.alpha = 0.7 + 0.3 * math.sin(st * 5.0 + 1.3) * math.cos(st * 3.7)
        return 0.02

# ── Default store variables ─────────────────────────────────
default forge_key_value = ""
default forge_show_key = False
default forge_validating = False
default forge_valid_result = None   # None = untested, True/False
default forge_error_msg = ""
default forge_detect_checks = []

###############################################################################
## 1. forge_key_input — API Key Entry
###############################################################################

screen forge_key_input(title="Ignite the Forge", description="Paste the sacred rune to proceed.", key_type="openclaw"):

    modal True
    zorder 200

    # Reset on show
    on "show" action [
        SetVariable("forge_key_value", ""),
        SetVariable("forge_show_key", False),
        SetVariable("forge_validating", False),
        SetVariable("forge_valid_result", None),
        SetVariable("forge_error_msg", ""),
    ]

    # Dark overlay
    add Solid("#000000aa")

    # Main frame
    frame:
        align (0.5, 0.5)
        padding (60, 50)
        xsize 900
        background Frame(Solid(FORGE_PURPLE_DARK), 0, 0)

        has vbox spacing 24 xalign 0.5

        # Gold decorative rule
        add Solid(FORGE_GOLD) xsize 700 ysize 2 xalign 0.5

        # Title
        text title:
            xalign 0.5
            size 42
            color FORGE_GOLD
            bold True
            text_align 0.5
            # Cinzel via gui if available; fallback bold serif
            font "DejaVuSans.ttf"

        # Description
        text description:
            xalign 0.5
            size 20
            color FORGE_WHITE
            text_align 0.5
            xsize 780
            line_spacing 6

        null height 8

        # ── Input area ───────────────────────────────────────
        frame:
            xalign 0.5
            xsize 780
            ysize 64
            padding (16, 12)
            background Frame(Solid(FORGE_PURPLE_BG), 0, 0)
            # Gold border via nested frame trick
            left_margin 2
            right_margin 2
            top_margin 2
            bottom_margin 2

            hbox:
                spacing 12
                yalign 0.5

                # The actual input
                input:
                    id "forge_key_input_field"
                    value ScreenVariableInputValue("forge_key_value", default=True, returnable=False)
                    pixel_width 640
                    size 20
                    color FORGE_GOLD
                    font "DejaVuSans.ttf"
                    if not forge_show_key:
                        mask "*"
                    caret_blink True
                    allow "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_=+/."

                # Toggle visibility
                textbutton ("👁" if not forge_show_key else "🔒"):
                    yalign 0.5
                    text_size 22
                    action ToggleVariable("forge_show_key")

        # Gold border below input
        add Solid(FORGE_GOLD) xsize 784 ysize 2 xalign 0.5

        null height 4

        # ── Status / feedback area ───────────────────────────
        hbox:
            xalign 0.5
            spacing 16
            ysize 36

            if forge_validating:
                text "⚙":
                    size 28
                    color FORGE_GOLD
                    at transform:
                        function forge_spin
                text "Consulting the Oracle...":
                    size 18
                    color FORGE_GOLD_DIM
                    yalign 0.5
                # Fire the actual validation after a beat
                timer 0.6 action ForgeDoValidation(key_type)

            elif forge_valid_result is True:
                text "✓":
                    size 30
                    color FORGE_GREEN
                text "The rune is accepted!":
                    size 18
                    color FORGE_GREEN
                    yalign 0.5

            elif forge_valid_result is False:
                text "✗":
                    size 30
                    color FORGE_RED
                text forge_error_msg:
                    size 16
                    color FORGE_RED
                    yalign 0.5
                    xsize 600

            else:
                text " ":
                    size 18

        null height 8

        # ── Buttons ──────────────────────────────────────────
        hbox:
            xalign 0.5
            spacing 20

            # Validate
            textbutton "⚔  Validate":
                xsize 220
                ysize 50
                text_size 22
                text_color FORGE_PURPLE_DARK
                text_bold True
                background Frame(Solid(FORGE_GOLD), 0, 0)
                hover_background Frame(Solid("#ffd866"), 0, 0)
                action ForgeValidateKey(key_type)
                sensitive (not forge_validating)

            # Accept (only after validation)
            if forge_valid_result is True:
                textbutton "⚜  Accept & Continue":
                    xsize 260
                    ysize 50
                    text_size 20
                    text_color FORGE_PURPLE_DARK
                    text_bold True
                    background Frame(Solid(FORGE_GREEN), 0, 0)
                    hover_background Frame(Solid("#66ff88"), 0, 0)
                    action ForgeSubmitKey(key_type)

        null height 12

        # ── Secondary actions ────────────────────────────────
        hbox:
            xalign 0.5
            spacing 30

            textbutton "I already have this configured":
                text_size 16
                text_color FORGE_GOLD_DIM
                text_hover_color FORGE_GOLD
                action ForgeCheckExisting(key_type)

            textbutton "Skip (story-only mode)":
                text_size 14
                text_color FORGE_GREY
                text_hover_color FORGE_WHITE
                action ForgeSkip()

        # Bottom rule
        add Solid(FORGE_GOLD) xsize 700 ysize 2 xalign 0.5


###############################################################################
## 2. forge_progress — Quest-Log Installation Progress
###############################################################################

screen forge_progress(steps=None):

    # steps: list of dicts  {"name": str, "label": str, "status": "done"|"active"|"pending"}
    # e.g. [{"name":"install","label":"Install OpenClaw","status":"done"}, ...]

    modal True
    zorder 200

    default _steps = steps if steps else [
        {"name": "install",   "label": "Install OpenClaw",   "icon": "🔨", "status": "pending"},
        {"name": "api",       "label": "Configure API",      "icon": "🔑", "status": "pending"},
        {"name": "wizard",    "label": "Summon the Wizard",   "icon": "🧙", "status": "pending"},
        {"name": "crons",     "label": "Set the Watch",       "icon": "⏳", "status": "pending"},
        {"name": "verify",    "label": "Verify the Kingdom",  "icon": "👑", "status": "pending"},
    ]

    add Solid("#000000cc")

    frame:
        align (0.5, 0.5)
        padding (60, 50)
        xsize 750
        background Frame(Solid(FORGE_PURPLE_DARK), 0, 0)

        has vbox spacing 16 xalign 0.5

        add Solid(FORGE_GOLD) xsize 600 ysize 2 xalign 0.5

        text "⚒  The Forging Begins":
            xalign 0.5
            size 36
            color FORGE_GOLD
            bold True
            font "DejaVuSans.ttf"

        text "Each step draws thy kingdom closer to life.":
            xalign 0.5
            size 18
            color FORGE_WHITE
            text_align 0.5

        null height 16

        # Steps list
        for step in (steps if steps else _steps):
            hbox:
                spacing 20
                xalign 0.5
                xsize 560
                ysize 48

                # Icon / status indicator
                if step.get("status") == "done":
                    text "⚔":
                        size 26
                        color FORGE_GOLD
                        yalign 0.5
                        min_width 40
                elif step.get("status") == "active":
                    text step.get("icon", "⚙"):
                        size 26
                        color FORGE_GOLD
                        yalign 0.5
                        min_width 40
                        at transform:
                            function forge_pulse_alpha
                else:
                    text "·":
                        size 26
                        color FORGE_GREY
                        yalign 0.5
                        min_width 40

                # Label
                text step.get("label", "???"):
                    size 22
                    yalign 0.5
                    if step.get("status") == "done":
                        color FORGE_GOLD
                    elif step.get("status") == "active":
                        color FORGE_WHITE
                        bold True
                    else:
                        color FORGE_GREY

                # Trailing mark
                if step.get("status") == "done":
                    text "✓":
                        size 20
                        color FORGE_GREEN
                        yalign 0.5

        null height 16
        add Solid(FORGE_GOLD) xsize 600 ysize 2 xalign 0.5


###############################################################################
## 3. forge_status_check — Final Verification
###############################################################################

screen forge_status_check(results=None):

    # results: list of dicts {"name": str, "label": str, "ok": bool}
    modal True
    zorder 200

    default _results = results if results else [
        {"name": "openclaw",  "label": "The Forge",            "detail": "OpenClaw daemon",     "ok": False},
        {"name": "gemini",    "label": "The Wizard's Tower",   "detail": "Gemini agent",        "ok": False},
        {"name": "crons",     "label": "The Night Watch",      "detail": "Scheduled tasks",     "ok": False},
        {"name": "node",      "label": "The Foundation Stone",  "detail": "Node.js runtime",    "ok": False},
    ]

    python:
        _r = results if results else _results
        _all_ok = all(r.get("ok", False) for r in _r)

    add Solid("#000000cc")

    frame:
        align (0.5, 0.5)
        padding (60, 50)
        xsize 800
        background Frame(Solid(FORGE_PURPLE_DARK), 0, 0)

        has vbox spacing 20 xalign 0.5

        add Solid(FORGE_GOLD) xsize 650 ysize 2 xalign 0.5

        if _all_ok:
            text "👑  The Kingdom Stands":
                xalign 0.5
                size 40
                color FORGE_GOLD
                bold True
                font "DejaVuSans.ttf"
        else:
            text "⚠  The Kingdom Stirs":
                xalign 0.5
                size 40
                color FORGE_GOLD_DIM
                bold True

        null height 8

        # Component rows
        for res in _r:
            hbox:
                spacing 16
                xalign 0.5
                xsize 620
                ysize 44

                # Status dot
                if res.get("ok"):
                    text "●":
                        size 22
                        color FORGE_GREEN
                        yalign 0.5
                        min_width 32
                else:
                    text "●":
                        size 22
                        color FORGE_RED
                        yalign 0.5
                        min_width 32

                # Medieval name
                text res.get("label", "Unknown"):
                    size 22
                    color FORGE_WHITE
                    bold True
                    yalign 0.5
                    min_width 280

                # Technical detail
                text ("— " + res.get("detail", "")):
                    size 16
                    color FORGE_GREY
                    yalign 0.5

        null height 20
        add Solid(FORGE_GOLD) xsize 650 ysize 2 xalign 0.5
        null height 8

        # Action buttons
        if _all_ok:
            textbutton "👑  Enter Your Kingdom":
                xalign 0.5
                xsize 340
                ysize 56
                text_size 24
                text_color FORGE_PURPLE_DARK
                text_bold True
                background Frame(Solid(FORGE_GOLD), 0, 0)
                hover_background Frame(Solid("#ffd866"), 0, 0)
                action Return(True)
        else:
            hbox:
                xalign 0.5
                spacing 24

                textbutton "🔄  Retry Checks":
                    xsize 220
                    ysize 48
                    text_size 18
                    text_color FORGE_PURPLE_DARK
                    text_bold True
                    background Frame(Solid(FORGE_GOLD_DIM), 0, 0)
                    hover_background Frame(Solid(FORGE_GOLD), 0, 0)
                    action Return("retry")

                textbutton "Continue Without Setup":
                    xsize 260
                    ysize 48
                    text_size 16
                    text_color FORGE_GREY
                    text_hover_color FORGE_WHITE
                    action Return(False)


###############################################################################
## 4. node_detect — Platform / Prerequisite Detection
###############################################################################

screen node_detect():

    modal True
    zorder 200

    default _detect_status = "Surveying the realm..."
    default _checks = []
    default _detecting = True

    on "show" action [
        SetVariable("forge_detect_checks", []),
        SetScreenVariable("_detecting", True),
        SetScreenVariable("_detect_status", "Surveying the realm..."),
    ]

    add Solid("#000000cc")

    frame:
        align (0.5, 0.5)
        padding (60, 50)
        xsize 700
        background Frame(Solid(FORGE_PURPLE_DARK), 0, 0)

        has vbox spacing 20 xalign 0.5

        add Solid(FORGE_GOLD) xsize 550 ysize 2 xalign 0.5

        text "🔥  Detecting Your Realm":
            xalign 0.5
            size 36
            color FORGE_GOLD
            bold True
            font "DejaVuSans.ttf"

        null height 8

        # Animated fire / spinner
        if _detecting:
            text "🜂":
                xalign 0.5
                size 64
                color FORGE_GOLD
                at transform:
                    function forge_fire_flicker

            text _detect_status:
                xalign 0.5
                size 18
                color FORGE_WHITE
                text_align 0.5
                at transform:
                    function forge_pulse_alpha

        null height 8

        # Completed checks
        for check in forge_detect_checks:
            hbox:
                spacing 12
                xalign 0.5
                xsize 500
                ysize 36

                if check.get("ok"):
                    text "✓":
                        size 20
                        color FORGE_GREEN
                        yalign 0.5
                        min_width 30
                else:
                    text "✗":
                        size 20
                        color FORGE_RED
                        yalign 0.5
                        min_width 30

                text check.get("label", ""):
                    size 18
                    color FORGE_WHITE
                    yalign 0.5

        null height 8

        if not _detecting:
            python:
                _all_detected = all(c.get("ok") for c in forge_detect_checks)

            if _all_detected:
                text "All foundations are strong.":
                    xalign 0.5
                    size 20
                    color FORGE_GREEN

                null height 12

                textbutton "⚔  Proceed":
                    xalign 0.5
                    xsize 220
                    ysize 48
                    text_size 20
                    text_color FORGE_PURPLE_DARK
                    text_bold True
                    background Frame(Solid(FORGE_GOLD), 0, 0)
                    hover_background Frame(Solid("#ffd866"), 0, 0)
                    action Return(True)
            else:
                text "Some foundations are missing.":
                    xalign 0.5
                    size 20
                    color FORGE_RED

                null height 12

                hbox:
                    xalign 0.5
                    spacing 20

                    textbutton "🔄  Re-check":
                        xsize 180
                        ysize 44
                        text_size 18
                        text_color FORGE_PURPLE_DARK
                        text_bold True
                        background Frame(Solid(FORGE_GOLD_DIM), 0, 0)
                        action Return("retry")

                    textbutton "Continue anyway":
                        xsize 200
                        ysize 44
                        text_size 16
                        text_color FORGE_GREY
                        text_hover_color FORGE_WHITE
                        action Return(False)

        add Solid(FORGE_GOLD) xsize 550 ysize 2 xalign 0.5

        # ── Auto-detection timer chain ───────────────────────
        # In practice, the calling label would drive these via
        # forge_installer.detect_prerequisites() and update
        # forge_detect_checks / _detecting. This timer is a
        # fallback demo that runs the detector if available.
        if _detecting:
            timer 1.0:
                action [
                    Function(forge_run_detection),
                    SetScreenVariable("_detecting", False),
                ]

init python:
    def forge_run_detection():
        """Run prerequisite detection, populating forge_detect_checks."""
        checks = []
        if forge_installer and hasattr(forge_installer, "detect_prerequisites"):
            raw = forge_installer.detect_prerequisites()
            for item in raw:
                checks.append({"label": item.get("label", ""), "ok": item.get("ok", False)})
        else:
            # Demo fallback
            import subprocess, shutil
            for cmd, label in [
                ("node",  "Node.js detected"),
                ("npm",   "npm detected"),
                ("git",   "Git detected"),
                ("curl",  "curl detected"),
            ]:
                found = shutil.which(cmd) is not None
                checks.append({"label": label, "ok": found})
        store.forge_detect_checks = checks
        renpy.restart_interaction()


## =========================================================================
## INSTALLATION WAIT SCREEN — non-blocking progress during npm install
## Polls _oc_install_done every 0.5s via restart_interaction.
## =========================================================================

screen forge_install_wait(result_dict):
    ## result_dict is a mutable dict: {"done": bool, "success": bool, "message": str}
    ## Updated by the background install thread's callback.

    modal True
    zorder 200

    add Solid("#000000cc")

    frame:
        align (0.5, 0.5)
        padding (60, 50)
        xsize 650
        background Frame(Solid(FORGE_PURPLE_DARK), 0, 0)

        has vbox spacing 20 xalign 0.5

        add Solid(FORGE_GOLD) xsize 500 ysize 2 xalign 0.5

        text "⚒  Raising the Gateway":
            xalign 0.5
            size 32
            color FORGE_GOLD
            bold True
            font "DejaVuSans.ttf"

        text "The masons are installing OpenClaw...\nThis may take a minute or two.":
            xalign 0.5
            size 18
            color FORGE_WHITE
            text_align 0.5

        null height 10

        if result_dict["done"]:
            if result_dict["success"]:
                text "✓  Gateway raised!":
                    xalign 0.5
                    size 22
                    color FORGE_GREEN
                    bold True
            else:
                text "✗  The Gateway sputters...":
                    xalign 0.5
                    size 22
                    color FORGE_RED

            null height 10

            textbutton "Continue →":
                xalign 0.5
                text_size 22
                text_color FORGE_GOLD
                action Return()
        else:
            text "⚙  Working...":
                xalign 0.5
                size 20
                color FORGE_GREY

    ## Poll every 0.5s — restart_interaction forces re-evaluation of result_dict
    timer 0.5:
        repeat True
        action Function(renpy.restart_interaction)
