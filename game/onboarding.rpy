## =========================================================================
## FORGE THE KINGDOM — Onboarding & Requirements Check
## "Every journey begins with a checklist." — Merith
##
## Runs BEFORE the story. Shows what you're getting, checks your system,
## guides you through API key setup, and lets you choose your path.
## =========================================================================

init python:
    import subprocess
    import os
    import shutil
    import ssl
    import urllib.request

    # SSL context for Ren'Py's bundled Python (lacks system CA certs)
    try:
        _onboard_ssl_ctx = ssl.create_default_context()
        _onboard_ssl_ctx.load_default_certs()
    except Exception:
        _onboard_ssl_ctx = ssl.create_default_context()
        _onboard_ssl_ctx.check_hostname = False
        _onboard_ssl_ctx.verify_mode = ssl.CERT_NONE

    # ── Onboarding requirement checks ─────────────────────────────────

    _onboard_results = {}

    def _onboard_check_all():
        """Run all requirement checks and store results."""
        global _onboard_results
        r = {}

        # Node.js
        try:
            out = subprocess.check_output(["node", "--version"], stderr=subprocess.STDOUT, timeout=5)
            ver = out.decode().strip()
            r["node"] = (True, ver)
        except Exception:
            r["node"] = (False, "Not found")

        # npm
        try:
            out = subprocess.check_output(["npm", "--version"], stderr=subprocess.STDOUT, timeout=5)
            ver = out.decode().strip()
            r["npm"] = (True, "v" + ver)
        except Exception:
            r["npm"] = (False, "Not found")

        # Internet
        try:
            urllib.request.urlopen("https://www.google.com", timeout=5, context=_onboard_ssl_ctx)
            r["internet"] = (True, "Connected")
        except Exception:
            r["internet"] = (False, "No connection")

        # Disk space
        try:
            usage = shutil.disk_usage(os.path.expanduser("~"))
            free_mb = usage.free // (1024 * 1024)
            if free_mb >= 500:
                r["disk"] = (True, "{:,} MB free".format(free_mb))
            else:
                r["disk"] = (False, "Only {:,} MB free (need 500+)".format(free_mb))
        except Exception:
            r["disk"] = (False, "Could not check")

        # API keys
        r["gemini"] = _onboard_check_api_key("GEMINI_API_KEY")
        r["anthropic"] = _onboard_check_api_key("ANTHROPIC_API_KEY")

        _onboard_results = r

    def _onboard_check_api_key(key_name):
        """Check if a key exists in api-keys.conf."""
        conf_path = os.path.join(renpy.config.gamedir, "api-keys.conf")
        try:
            with open(conf_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(key_name + "="):
                        val = line.split("=", 1)[1].strip()
                        if val and len(val) > 5:
                            return (True, "Configured ✓")
            return (False, "Not set")
        except FileNotFoundError:
            return (False, "api-keys.conf missing")
        except Exception as e:
            return (False, str(e))

    def _onboard_story_ready():
        """Check if minimum requirements for story-only mode are met."""
        return _onboard_results.get("gemini", (False,))[0]

    def _onboard_kingdom_ready():
        """Check if all requirements for full kingdom mode are met."""
        return (
            _onboard_results.get("node", (False,))[0]
            and _onboard_results.get("npm", (False,))[0]
            and _onboard_results.get("internet", (False,))[0]
            and _onboard_results.get("disk", (False,))[0]
            and _onboard_results.get("gemini", (False,))[0]
            and _onboard_results.get("anthropic", (False,))[0]
        )

## ── Onboarding state ────────────────────────────────────────────────
default persistent.onboarding_complete = False
## _onboard_page removed — unused state variable (QA: Sage)


## =========================================================================
## WELCOME SCREEN
## =========================================================================

screen onboarding_welcome():
    modal True
    add Solid("#0e0a16")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 900
        background Solid("#1a1028e0")
        padding (50, 40)

        has vbox:
            spacing 20
            xalign 0.5

        text "{size=44}{b}{color=#f1c40f}Welcome to Forge the Kingdom.{/color}{/b}{/size}" xalign 0.5

        null height 5

        text "{size=22}{color=#c8b8d8}This is more than a game.{/color}{/size}" xalign 0.5

        null height 10

        text "{size=22}{color=#e8dff0}By the end of this story, you'll have:{/color}{/size}" xalign 0.0

        null height 5

        for icon, desc in [
            ("🤖", "12 autonomous AI agents — each with their own personality"),
            ("🏰", "A fully running AI Kingdom on YOUR machine"),
            ("🛡️", "Security monitoring and automated patrols"),
            ("💬", "A Discord server where your agents live and talk"),
            ("📊", "Daily briefings, automated audits, and more"),
            ("🎨", "AI-generated art, portraits, and scene paintings"),
        ]:
            text "{size=22}  [icon]  [desc]{/size}" color "#e8dff0"

        null height 15

        text "{size=20}{color=#a89ab8}{i}Everything runs locally. You own it all.{/i}{/color}{/size}" xalign 0.5

        null height 10

        text "{size=20}{color=#c8b8d8}To make this work, you'll need a few things.\nLet's check your setup.{/color}{/size}" xalign 0.5

        null height 20

        textbutton "{size=28}{b}  ⚔️  Let's Check  {/b}{/size}":
            xalign 0.5
            action Return("check")
            text_color "#f1c40f"
            text_outlines [(2, "#000000", 0, 0)]

        null height 10

        textbutton "{size=18}{color=#666}Skip — I just want the story →{/color}{/size}":
            xalign 0.5
            action Return("skip")


## =========================================================================
## REQUIREMENTS CHECKER SCREEN
## =========================================================================

screen onboarding_requirements():
    modal True
    add Solid("#0e0a16")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 950
        background Solid("#1a1028e0")
        padding (50, 35)

        has vbox:
            spacing 12
            xalign 0.5

        text "{size=36}{b}{color=#f1c40f}⚙️  System Check{/color}{/b}{/size}" xalign 0.5
        text "{size=18}{i}{color=#a89ab8}\"Preparation is the first spell of any wise wizard.\" — Merith{/color}{/i}{/size}" xalign 0.5

        null height 10

        # Requirements list
        for key, label, hint in [
            ("node", "Node.js", "Download from https://nodejs.org — grab the LTS version"),
            ("npm", "npm", "Comes with Node.js — install Node first"),
            ("internet", "Internet Connection", "Check your network connection"),
            ("disk", "Disk Space (500 MB)", "Free up some space and re-check"),
            ("gemini", "Gemini API Key", "Free — click \"Setup Guide\" below"),
            ("anthropic", "Anthropic API Key", "Pay-as-you-go — click \"Setup Guide\" below"),
        ]:
            $ ok, detail = _onboard_results.get(key, (False, "Not checked"))
            frame:
                xsize 850
                background Solid("#2d1f4280")
                padding (20, 10)
                has hbox:
                    spacing 15
                    yalign 0.5

                if ok:
                    text "{size=24}{color=#44dd66}✅{/color}{/size}" yalign 0.5
                else:
                    text "{size=24}{color=#dd4466}❌{/color}{/size}" yalign 0.5

                vbox:
                    spacing 2
                    text "{size=20}{b}[label]{/b}{/size}" color "#e8dff0"
                    if ok:
                        text "{size=16}{color=#44dd66}[detail]{/color}{/size}"
                    else:
                        text "{size=16}{color=#dd4466}[detail]{/color}{/size}"
                        text "{size=14}{color=#a89ab8}[hint]{/color}{/size}"

        null height 15

        # Action buttons
        hbox:
            spacing 20
            xalign 0.5

            textbutton "{size=22}{b} 🔄 Re-check {/b}{/size}":
                action Function(_onboard_check_all)
                text_color "#f1c40f"
                text_outlines [(2, "#000000", 0, 0)]

            if not _onboard_results.get("gemini", (False,))[0] or not _onboard_results.get("anthropic", (False,))[0]:
                textbutton "{size=22}{b} 🔑 API Key Guide {/b}{/size}":
                    action Return("api_guide")
                    text_color "#f1c40f"
                    text_outlines [(2, "#000000", 0, 0)]

        null height 15

        # Path selection
        hbox:
            spacing 20
            xalign 0.5

            textbutton "{size=20}{b} 🏰 Forge a Real Kingdom {/b}{/size}":
                action Return("kingdom")
                text_color "#f1c40f"
                text_outlines [(2, "#000000", 0, 0)]
                sensitive _onboard_kingdom_ready()

            textbutton "{size=20}{b} 🎮 Play the Story {/b}{/size}":
                action Return("story")
                text_color "#c8b8d8"
                text_outlines [(2, "#000000", 0, 0)]
                sensitive _onboard_story_ready()

        if not _onboard_story_ready():
            text "{size=16}{color=#dd4466}You need at least a Gemini API key to play. See the guide below.{/color}{/size}" xalign 0.5

        null height 5

        textbutton "{size=16}{color=#666}Skip everything — play without AI features →{/color}{/size}":
            xalign 0.5
            action Return("skip")


## =========================================================================
## API KEY GUIDE SCREEN
## =========================================================================

screen onboarding_api_guide():
    modal True
    add Solid("#0e0a16")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 950
        ysize 620
        background Solid("#1a1028e0")
        padding (40, 30)

        has vbox:
            spacing 10
            xalign 0.5

        text "{size=36}{b}{color=#f1c40f}🔑  API Key Setup Guide{/color}{/b}{/size}" xalign 0.5

        null height 5

        viewport:
            scrollbars "vertical"
            mousewheel True
            xsize 870
            ysize 430

            vbox:
                spacing 20

                # ── Gemini ──────────────────────────────────
                frame:
                    xsize 850
                    background Solid("#2d1f42a0")
                    padding (25, 20)
                    has vbox:
                        spacing 8

                    $ gem_ok = _onboard_results.get("gemini", (False,))[0]
                    if gem_ok:
                        text "{size=24}{b}{color=#44dd66}✅ Gemini API Key — Done!{/color}{/b}{/size}"
                    else:
                        text "{size=24}{b}{color=#f1c40f}🌟 Gemini API Key{/color}  {color=#44dd66}(FREE){/color}{/b}{/size}"

                    if not gem_ok:
                        null height 5
                        for step in [
                            "Step 1: Open your browser to {u}https://aistudio.google.com/apikey{/u}",
                            "Step 2: Sign in with your Google account",
                            "Step 3: Click \"Create API Key\"",
                            "Step 4: Copy the key",
                            "Step 5: Open the file {b}game/api-keys.conf{/b} in any text editor",
                            "Step 6: Paste after GEMINI_API_KEY=",
                            "Step 7: Save and come back here",
                        ]:
                            text "{size=17}  [step]{/size}" color "#e8dff0"

                # ── Anthropic ───────────────────────────────
                frame:
                    xsize 850
                    background Solid("#2d1f42a0")
                    padding (25, 20)
                    has vbox:
                        spacing 8

                    $ anth_ok = _onboard_results.get("anthropic", (False,))[0]
                    if anth_ok:
                        text "{size=24}{b}{color=#44dd66}✅ Anthropic API Key — Done!{/color}{/b}{/size}"
                    else:
                        text "{size=24}{b}{color=#f1c40f}🧠 Anthropic API Key{/color}  {color=#c8b8d8}(pay-as-you-go){/color}{/b}{/size}"

                    if not anth_ok:
                        null height 5
                        for step in [
                            "Step 1: Open your browser to {u}https://console.anthropic.com/{/u}",
                            "Step 2: Create an account",
                            "Step 3: Set up billing (Settings → Billing)",
                            "Step 4: Go to API Keys → Create Key",
                            "Step 5: Copy the key",
                            "Step 6: Open {b}game/api-keys.conf{/b} in any text editor",
                            "Step 7: Paste after ANTHROPIC_API_KEY=",
                            "Step 8: Save and come back here",
                        ]:
                            text "{size=17}  [step]{/size}" color "#e8dff0"

                        null height 5
                        text "{size=17}{color=#f1c40f}💡 Tip:{/color} Set a monthly spending limit in Settings → Limits{/size}" color "#a89ab8"
                        text "{size=17}   $20/month is plenty to start.{/size}" color "#a89ab8"

                # ── Where is api-keys.conf? ─────────────────
                frame:
                    xsize 850
                    background Solid("#1a102880")
                    padding (25, 15)
                    has vbox:
                        spacing 5

                    text "{size=20}{b}{color=#f1c40f}📂 Where is api-keys.conf?{/color}{/b}{/size}"
                    text "{size=16}It's in the {b}game/{/b} folder — right next to this game's files.{/size}" color "#e8dff0"
                    text "{size=16}Open it in any text editor (Notepad, TextEdit, VS Code, etc).{/size}" color "#e8dff0"
                    text "{size=16}You'll see lines like: GEMINI_API_KEY={/size}" color "#a89ab8"
                    text "{size=16}Just paste your key right after the = sign. No quotes needed.{/size}" color "#a89ab8"

        null height 10

        hbox:
            spacing 20
            xalign 0.5

            textbutton "{size=22}{b} 🔄 Re-check Keys {/b}{/size}":
                action Function(_onboard_check_all)
                text_color "#f1c40f"
                text_outlines [(2, "#000000", 0, 0)]

            textbutton "{size=22}{b} ← Back to Checklist {/b}{/size}":
                action Return("back")
                text_color "#c8b8d8"
                text_outlines [(2, "#000000", 0, 0)]


## =========================================================================
## PATH SELECTION SCREEN (enhanced)
## =========================================================================

screen onboarding_path_select():
    modal True
    add Solid("#0e0a16")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 950
        background Solid("#1a1028e0")
        padding (50, 40)

        has vbox:
            spacing 20
            xalign 0.5

        text "{size=38}{b}{color=#f1c40f}Choose Your Path{/color}{/b}{/size}" xalign 0.5

        null height 10

        # Story path
        button:
            xsize 850
            background Solid("#2d1f4280")
            hover_background Solid("#3d2f52a0")
            padding (30, 25)
            action Return("story")

            has vbox:
                spacing 8

            text "{size=26}{b}{color=#f1c40f}🎮  PLAY THE STORY{/color}{/b}{/size}"
            text "{size=18}Experience the visual novel with AI-generated art.{/size}" color "#e8dff0"
            text "{size=18}No installation. Just the story.{/size}" color "#e8dff0"
            text "{size=16}{i}Requirements: Gemini API key only{/i}{/size}" color "#a89ab8"

        # Kingdom path
        button:
            xsize 850
            background Solid("#2d1f4280")
            hover_background Solid("#3d2f52a0")
            padding (30, 25)
            action Return("kingdom")
            sensitive _onboard_kingdom_ready()

            has vbox:
                spacing 8

            text "{size=26}{b}{color=#f1c40f}🏰  FORGE A REAL KINGDOM{/color}{/b}{/size}"
            text "{size=18}Play the story AND install your own AI Kingdom.{/size}" color "#e8dff0"
            text "{size=18}By the end, you'll have 12 agents running on your machine.{/size}" color "#e8dff0"
            text "{size=16}{i}Requirements: Both API keys + Node.js{/i}{/size}" color "#a89ab8"

            null height 5
            text "{size=16}{b}{color=#f1c40f}This is the full experience. This is what we built for you.{/color}{/b}{/size}"

        if not _onboard_kingdom_ready():
            text "{size=16}{color=#a89ab8}Some requirements are missing for the full Kingdom path. Go back to set them up.{/color}{/size}" xalign 0.5

        null height 5

        textbutton "{size=18}{color=#666}← Back to checklist{/color}{/size}":
            xalign 0.5
            action Return("back")


## =========================================================================
## ONBOARDING FLOW LABEL — Entry point
## =========================================================================

label onboarding:

    ## Skip if already completed onboarding
    if persistent.onboarding_complete:
        return

    ## Run initial checks
    $ _onboard_check_all()

    ## Welcome screen
    call screen onboarding_welcome
    $ _onboard_welcome_result = _return

    if _onboard_welcome_result == "skip":
        $ persistent.onboarding_complete = True
        $ persistent.install_mode = "story_only"
        return

    ## Requirements loop
    label .requirements_loop:
        $ _onboard_check_all()
        call screen onboarding_requirements
        $ _onboard_req_result = _return

        if _onboard_req_result == "api_guide":
            label .api_guide_loop:
                call screen onboarding_api_guide
                $ _onboard_guide_result = _return
                if _onboard_guide_result == "back":
                    jump onboarding.requirements_loop
                jump onboarding.api_guide_loop

        if _onboard_req_result == "skip":
            $ persistent.onboarding_complete = True
            $ persistent.install_mode = "story_only"
            return

        if _onboard_req_result == "kingdom":
            $ persistent.install_mode = "full"
            $ persistent.onboarding_complete = True
            return

        if _onboard_req_result == "story":
            $ persistent.install_mode = "story_only"
            $ persistent.onboarding_complete = True
            return

        ## Fallback
        jump onboarding.requirements_loop
