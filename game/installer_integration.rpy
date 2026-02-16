## =========================================================================
## FORGE THE KINGDOM — Installer Integration
## Weaves real OpenClaw installation into the narrative
## =========================================================================
##
## This file adds "reality anchors" — moments where the story pauses
## and the player actually sets up their own AI kingdom. The game detects
## whether to show install screens or skip them (story-only mode).
##
## Integration points in script.rpy:
##   - After accept_crown: Platform detection + prerequisites
##   - Chapter 3 (Gateway): Install OpenClaw
##   - Chapter 4 (Throne Room): Anthropic API key → powers Anna
##   - Chapter 8 (Wizard's Tower): Gemini API key → powers Merith
##   - Chapter 9 (Royal Schedule): Set up crons
##   - Chapter 10 (Coronation): Verify everything works
## =========================================================================

init python:
    import os
    import sys

    # Try to import our installer module
    try:
        import forge_installer as fi
        INSTALLER_AVAILABLE = True
    except ImportError:
        INSTALLER_AVAILABLE = False

## Persistent install tracking
default persistent.install_mode = None  # "full", "story_only", or None (not chosen yet)
default persistent.install_step = 0
default persistent.openclaw_installed = False
default persistent.anthropic_configured = False
default persistent.gemini_configured = False
default persistent.crons_configured = False
default persistent.kingdom_verified = False

## =========================================================================
## MODE SELECTION — Called once after accepting the crown
## =========================================================================

label installer_mode_select:

    ## If onboarding already set the mode, skip the old selection
    if persistent.install_mode is not None:
        if persistent.install_mode == "full":
            jump installer_check_prereqs
        else:
            return

    scene bg aftermath
    pause 0.3

    n "Before we begin rebuilding..."
    n "A question, [ruler_name]. An {i}important{/i} one."
    pause 0.5

    n "This tale you're about to live — it's not just a story."
    n "The Kingdom you're about to forge?"
    n "It can be {b}real{/b}."
    pause 0.5

    n "With your permission, I can guide you through installing the actual tools that power this Kingdom."
    n "An AI assistant. A wizard agent. The whole enchilada — er, {i}kingdom{/i}."
    pause 0.3
    n "All you need are a couple of magical sigils — what the mortals call {i}API keys{/i}."

    menu:
        n "So what say you, [ruler_name]?"

        "🏰 Forge a REAL Kingdom (install OpenClaw + agents)":
            $ persistent.install_mode = "full"
            n "{b}{color=#f1c40f}Bold choice.{/color}{/b}"
            n "By the time this tale ends, you'll have a living, breathing AI kingdom at your command."
            n "I'll walk you through everything. No experience required."
            pause 0.5
            jump installer_check_prereqs

        "📖 Just tell me the story":
            $ persistent.install_mode = "story_only"
            n "A wise choice for a first playthrough."
            n "You can always replay and choose to forge your kingdom for real."
            n "The offer stands, [ruler_name]. It always will."
            pause 0.3

        "🔧 I already have OpenClaw set up":
            $ persistent.install_mode = "story_only"
            if INSTALLER_AVAILABLE:
                python:
                    status = fi.flat_status()
                if status.get("openclaw_running"):
                    n "{color=#2ecc71}The Forge already burns!{/color} I can feel its warmth."
                    n "A seasoned ruler, I see. Very well — enjoy the tale."
                    $ persistent.openclaw_installed = True
                    $ persistent.anthropic_configured = True
                else:
                    n "Hmm, I don't sense an active Forge... but I'll take your word for it."
            else:
                n "Very well, seasoned ruler. Enjoy the tale."

    return

## =========================================================================
## PREREQUISITE CHECK — Node.js, npm, platform detection
## =========================================================================

label installer_check_prereqs:

    n "First, let me survey your realm's foundations..."
    pause 0.3

    if INSTALLER_AVAILABLE:
        python:
            platform_info = fi.detect_platform()
            has_node = fi.check_node_installed()
            has_npm = fi.check_npm_installed()
            prereq_issues = []
            if not has_node:
                prereq_issues.append("node")
            if not has_npm:
                prereq_issues.append("npm")
            platform_label = platform_info.get('label', 'unknown')

        n "Realm detected: {b}[platform_label]{/b}"

        if not prereq_issues:
            n "{color=#2ecc71}✓{/color} Node.js — found"
            n "{color=#2ecc71}✓{/color} npm — found"
            n "Excellent! Your realm has everything we need."
        else:
            n "{color=#e74c3c}Hmm.{/color} We're missing some foundations."
            if "node" in prereq_issues:
                n "The {b}Runestone Carver{/b} (Node.js) isn't here yet."
                n "You'll need to install it from {color=#3498db}https://nodejs.org{/color}"
                n "Download the LTS version, install it, then come back."
                n "I'll wait. Wizards have patience. Mostly."

            menu:
                "I've installed Node.js, let's continue":
                    python:
                        has_node = fi.check_node_installed()
                    if has_node:
                        n "{color=#2ecc71}✓{/color} There it is! The Runestone Carver stands ready."
                    else:
                        n "I still don't see it... You may need to restart the game after installing."
                        n "But let's continue — we can try anyway."

                "Skip installation for now":
                    $ persistent.install_mode = "story_only"
                    n "No worries. Enjoy the story — you can install later."
                    return
    else:
        n "Hmm. My installation spells aren't loading properly."
        n "No matter — the story continues regardless."
        $ persistent.install_mode = "story_only"

    return

## =========================================================================
## CHAPTER 3 HOOK — Install OpenClaw (after Gateway narrative)
## =========================================================================

label installer_gateway:
    ## Called after Chapter 3's narrative, before side quest

    if persistent.install_mode != "full":
        return

    if persistent.openclaw_installed:
        n "The Gateway already hums with power. OpenClaw is installed."
        return

    n "The Gateway in the story rises — but what about {i}your{/i} Gateway?"
    pause 0.3
    n "Time to install {b}OpenClaw{/b} — the real power behind the throne."

    if INSTALLER_AVAILABLE:
        python:
            already, _path, _ver, _err = fi.check_openclaw_installed()

        if already:
            n "{color=#2ecc71}Wait — the Gateway already stands!{/color}"
            n "OpenClaw is already installed on your system. Excellent."
            $ persistent.openclaw_installed = True
            return

        n "This may take a moment. The masons are at work..."
        pause 0.3

        python:
            import threading

            # Use a dict as a thread-safe container (no store mutation from bg thread)
            _oc_result = {"done": False, "success": False, "message": ""}

            def _oc_install_cb(ok, msg):
                _oc_result["success"] = ok
                _oc_result["message"] = msg
                _oc_result["done"] = True

            _oc_install_thread = fi.install_openclaw(callback=_oc_install_cb)

        if _oc_install_thread is not None:
            ## Show a non-blocking progress screen while npm runs
            call screen forge_install_wait(_oc_result)
            $ success = _oc_result["success"]
            $ message = _oc_result["message"]
        else:
            $ success = False
            $ message = "Prerequisites not met"

        if success:
            play sound sfx_gateway
            n "{color=#2ecc71}{b}The Gateway blazes to life!{/b}{/color}"
            n "OpenClaw has been installed."
            $ persistent.openclaw_installed = True
        else:
            n "{color=#e74c3c}The Gateway sputters...{/color}"
            n "Installation hit a snag: [message]"
            n "You can install manually later: {color=#3498db}npm install -g openclaw{/color}"
            n "The story continues regardless."
    else:
        n "Install OpenClaw manually: {color=#3498db}npm install -g openclaw{/color}"
        n "The story continues regardless."

    return

## =========================================================================
## CHAPTER 4 HOOK — Anthropic API Key (Throne Room / Anna awakens)
## =========================================================================

label installer_anthropic_key:
    ## Called in Chapter 4, after narrative about the Sigil of Anthropic

    if persistent.install_mode != "full":
        return

    if persistent.anthropic_configured:
        n "The Sigil of Anthropic already glows with power."
        return

    n "In the story, the Sigil of Anthropic brings Anna to life."
    n "In {i}your{/i} kingdom, it's an API key from Anthropic."
    pause 0.3
    n "You can get one at {color=#3498db}https://console.anthropic.com{/color}"
    n "It starts with {color=#a89ab8}sk-ant-{/color}..."

    menu:
        "Ready to enter your Anthropic API key?"

        "🔑 I have my key":
            jump installer_anthropic_input

        "⏭ Skip for now":
            n "No worries. You can configure this later with {color=#3498db}openclaw configure{/color}"
            return

        "❓ What's an API key?":
            n "Think of it as a magical sigil — a secret code that lets your kingdom talk to the powers that be."
            n "Anthropic's key lets Anna (your AI assistant) think and respond."
            n "Go to {color=#3498db}console.anthropic.com{/color}, create an account, and generate a key."
            n "It's like getting a library card, except the library is omniscient."

            menu:
                "Got it!"

                "🔑 I have my key now":
                    jump installer_anthropic_input

                "⏭ I'll do it later":
                    n "The Throne Room will be ready when you are."
                    return

label installer_anthropic_input:

    ## NOTE: renpy.input shows keys in plaintext — acceptable since this is a
    ## local single-player game and the conf-file flow (onboarding) is preferred.
    $ api_key = renpy.input("Paste your Anthropic API key:", default="", length=120)
    $ api_key = api_key.strip()

    if not api_key:
        n "No key entered. We'll come back to this."
        return

    if INSTALLER_AVAILABLE:
        n "Validating the sigil..."

        python:
            valid, err = fi.validate_anthropic_key(api_key)

        if valid:
            python:
                fi.configure_openclaw(api_key)

            play sound sfx_magic
            n "{color=#2ecc71}{b}The Sigil of Anthropic flares to life!{/b}{/color}"
            n "Anna stirs in the throne room. Your AI assistant awakens."
            $ persistent.anthropic_configured = True
        else:
            n "{color=#e74c3c}The sigil flickers and fades.{/color}"
            n "That key doesn't seem to work: [err]"
            n "Double-check it at {color=#3498db}console.anthropic.com{/color} and try again next playthrough."
    else:
        n "Key noted. Configure manually: {color=#3498db}openclaw configure{/color}"

    return

## =========================================================================
## CHAPTER 8 HOOK — Gemini API Key (Wizard's Tower / Merith awakens)
## =========================================================================

label installer_gemini_key:
    ## Called in Chapter 8, after Merith's dialog

    if persistent.install_mode != "full":
        return

    if persistent.gemini_configured:
        n "Merith's crystal ball already glows with Gemini's light."
        return

    n "In the story, Merith reconnects to the Scrying Glass."
    n "In {i}your{/i} kingdom, he needs a Gemini API key."
    pause 0.3
    n "Get one at {color=#3498db}https://aistudio.google.com/apikey{/color}"

    menu:
        "Ready to awaken your wizard?"

        "🔮 I have my Gemini key":
            jump installer_gemini_input

        "⏭ Skip for now":
            n "Merith nods understandingly. The tower can wait."
            return

label installer_gemini_input:

    ## NOTE: renpy.input shows keys in plaintext — acceptable since this is a
    ## local single-player game and the conf-file flow (onboarding) is preferred.
    $ gemini_key = renpy.input("Paste your Gemini API key:", default="", length=120)
    $ gemini_key = gemini_key.strip()

    if not gemini_key:
        n "No key entered. Merith will wait."
        return

    if INSTALLER_AVAILABLE:
        n "Reaching out to the Wizard's Tower..."

        python:
            valid, err = fi.validate_gemini_key(gemini_key)

        if valid:
            python:
                fi.configure_wizard(gemini_key)

            play sound sfx_magic_whoosh
            n "{color=#2ecc71}{b}The Pale Tower erupts with blue-green light!{/b}{/color}"
            n "Merith's crystal ball hums. The Wizard sees clearly once more."
            $ persistent.gemini_configured = True
        else:
            n "{color=#e74c3c}The crystal ball flickers but stays dark.{/color}"
            n "That key doesn't seem to work: [err]"
            n "Check {color=#3498db}aistudio.google.com{/color} and try again."
    else:
        n "Key noted. You can configure the wizard manually later."

    return

## =========================================================================
## CHAPTER 9 HOOK — Set up Crons (Royal Schedule)
## =========================================================================

label installer_crons:
    ## Called in Chapter 9, after schedule narrative

    if persistent.install_mode != "full":
        return

    if persistent.crons_configured:
        n "The Royal Schedule is already set."
        return

    if not persistent.openclaw_installed:
        return

    n "Shall I set the {i}real{/i} Royal Schedule?"
    n "Automated patrols, daily digests, and the Wizard's nightly watch?"

    menu:
        "Set up the schedule?"

        "⏰ Yes, automate everything":
            if INSTALLER_AVAILABLE:
                python:
                    success, _results, msg = fi.setup_default_crons()
                if success:
                    play sound sfx_healing
                    n "{color=#2ecc71}{b}The Royal Schedule is set!{/b}{/color}"
                    n "Your kingdom now runs on autopilot."
                    n "Daily briefings. Security patrols. The works."
                    $ persistent.crons_configured = True
                else:
                    n "Hmm, the clock jammed: [msg]"
                    n "You can set up crons manually through OpenClaw."
            else:
                n "You'll need to set these up manually through OpenClaw."

        "⏭ I'll set it up myself later":
            n "A hands-on ruler. Respectable."

    return

## =========================================================================
## CHAPTER 10 HOOK — Final Verification (Coronation)
## =========================================================================

label installer_verify:
    ## Called during coronation, before the final celebration

    if persistent.install_mode != "full":
        return

    n "Before the crown descends... let me check that everything is in order."
    pause 0.5

    if INSTALLER_AVAILABLE:
        python:
            status = fi.flat_status()

        n "{b}Kingdom Status:{/b}"

        if status.get("openclaw_installed"):
            n "{color=#2ecc71}⚔{/color} The Gateway (OpenClaw) — {color=#2ecc71}Standing{/color}"
        else:
            n "{color=#e74c3c}⚔{/color} The Gateway (OpenClaw) — {color=#e74c3c}Not Found{/color}"

        if status.get("openclaw_running"):
            n "{color=#2ecc71}🔥{/color} The Forge — {color=#2ecc71}Burning{/color}"
        else:
            n "{color=#e67e22}🔥{/color} The Forge — {color=#e67e22}Cold{/color} (start with: openclaw gateway start)"

        if status.get("anthropic_configured"):
            n "{color=#2ecc71}👑{/color} The Empress (Anna) — {color=#2ecc71}Awake{/color}"
        else:
            n "{color=#e74c3c}👑{/color} The Empress (Anna) — {color=#e74c3c}Sleeping{/color}"

        if status.get("gemini_configured"):
            n "{color=#2ecc71}🧙{/color} The Wizard (Merith) — {color=#2ecc71}Watching{/color}"
        else:
            n "{color=#e67e22}🧙{/color} The Wizard (Merith) — {color=#e67e22}Resting{/color}"

        if status.get("crons_active"):
            n "{color=#2ecc71}⏰{/color} The Royal Schedule — {color=#2ecc71}Ticking{/color}"
        else:
            n "{color=#e67e22}⏰{/color} The Royal Schedule — {color=#e67e22}Silent{/color}"

        python:
            all_good = (status.get("openclaw_installed") and
                       status.get("anthropic_configured"))

        if all_good:
            pause 0.5
            n "{b}{color=#f1c40f}Your Kingdom stands ready, [ruler_name].{/color}{/b}"
            n "This isn't just a story anymore."
            $ persistent.kingdom_verified = True
        else:
            n "Some pieces are missing — but every kingdom grows at its own pace."
            n "Run {color=#3498db}openclaw status{/color} in your terminal to see what needs attention."
    else:
        n "The Kingdom stands in story — forge it in reality whenever you're ready."

    return
