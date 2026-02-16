## =========================================================================
## FORGE THE KINGDOM — Ember, the Companion
## A sentient spark from the original Forge fire who guides players
## through the real-world tools behind the medieval metaphor.
## =========================================================================
##
## "I'm a spark. I survived the Pyroblast. I've seen things."
##    — Ember, explaining her origin story
##
## Toggle: Players can enable/disable Ember's commentary at any time.
## She appears as a small glowing orb with a text bubble.
## =========================================================================

## ── Character ────────────────────────────────────────────────────────────

define ember = Character("🔥 Ember", color="#ff9944", who_bold=True, what_color="#ffe8cc", what_size=22)

## ── Persistent toggle ────────────────────────────────────────────────────

default persistent.companion_enabled = True   # On by default for new players
default persistent.companion_introduced = False

## ── Ember's portrait (just a glow effect — no image needed) ──────────────

image ember_glow:
    Solid("#ff660000")
    xsize 120 ysize 120

transform ember_float:
    yoffset 0
    ease 1.5 yoffset -8
    ease 1.5 yoffset 0
    repeat

transform ember_appear:
    alpha 0.0
    zoom 0.3
    ease 0.5 alpha 1.0 zoom 1.0

transform ember_vanish:
    alpha 1.0
    zoom 1.0
    ease 0.3 alpha 0.0 zoom 0.3

## ── Toggle screen (always available via quick menu) ──────────────────────

screen companion_toggle():
    zorder 90
    if persistent.companion_enabled:
        textbutton "🔥":
            xalign 0.98
            yalign 0.02
            text_size 28
            text_color "#ff9944"
            text_hover_color "#ffcc66"
            action [ToggleVariable("persistent.companion_enabled"), renpy.restart_interaction]
            tooltip "Ember is helping! Click to quiet her."
    else:
        textbutton "🔥":
            xalign 0.98
            yalign 0.02
            text_size 28
            text_color "#66555580"
            text_hover_color "#ff9944"
            action [ToggleVariable("persistent.companion_enabled"), renpy.restart_interaction]
            tooltip "Ember is resting. Click to wake her."

## ── Dev Notes Screen — "Behind the Curtain" ──────────────────────────────
## Called by Ember at each chapter. Shows the real tool, what it does,
## and how the metaphor maps.

screen dev_note(title="", tool_name="", tool_url="", metaphor="", reality="", tip=""):
    modal True
    zorder 300

    add Solid("#000000dd")

    frame:
        align (0.5, 0.5)
        padding (50, 40)
        xsize 950
        background Frame(Solid("#1a1028"), 0, 0)

        has vbox spacing 16 xalign 0.5

        # Header
        add Solid("#ff9944") xsize 800 ysize 2 xalign 0.5

        hbox:
            xalign 0.5
            spacing 12
            text "🔥" size 36 yalign 0.5
            text "{b}Behind the Curtain{/b}" size 32 color "#ff9944" yalign 0.5

        text title:
            xalign 0.5
            size 26
            color "#f1c40f"
            bold True
            text_align 0.5

        null height 8

        # The metaphor → reality mapping
        frame:
            xalign 0.5
            xsize 850
            padding (24, 16)
            background Frame(Solid("#0e0a16"), 0, 0)

            has vbox spacing 12

            hbox:
                spacing 8
                text "🏰" size 22 yalign 0.5
                text "{b}In the story:{/b}" size 18 color "#c8b8d8" yalign 0.5
            text metaphor:
                size 18
                color "#e8dff0"
                xsize 790
                line_spacing 4

            null height 4

            hbox:
                spacing 8
                text "💻" size 22 yalign 0.5
                text "{b}In reality:{/b}" size 18 color "#c8b8d8" yalign 0.5
            text reality:
                size 18
                color "#e8dff0"
                xsize 790
                line_spacing 4

        # Tool callout
        if tool_name:
            frame:
                xalign 0.5
                xsize 850
                padding (24, 12)
                background Frame(Solid("#2d1f42"), 0, 0)

                hbox:
                    spacing 12
                    text "🔧" size 22 yalign 0.5
                    text "{b}The Tool:{/b} {color=#ff9944}[tool_name]{/color}" size 20 color "#e8dff0" yalign 0.5
                    if tool_url and tool_url.startswith("http"):
                        textbutton "({color=#3498db}[tool_url]{/color})":
                            text_size 16
                            yalign 0.5
                            action OpenURL(tool_url)

        # Pro tip
        if tip:
            frame:
                xalign 0.5
                xsize 850
                padding (24, 12)
                background Frame(Solid("#1a2a1a"), 0, 0)

                hbox:
                    spacing 12
                    text "💡" size 22 yalign 0.0
                    text "{b}Pro Tip:{/b} [tip]":
                        size 17
                        color "#88cc88"
                        xsize 760
                        line_spacing 4

        null height 8
        add Solid("#ff9944") xsize 800 ysize 2 xalign 0.5

        textbutton "✨  Got it!":
            xalign 0.5
            xsize 200
            ysize 44
            text_size 20
            text_color "#1a1028"
            text_bold True
            background Frame(Solid("#ff9944"), 0, 0)
            hover_background Frame(Solid("#ffbb66"), 0, 0)
            action Return()

## =========================================================================
## COMPANION LABELS — Called from script.rpy at each chapter
## =========================================================================

## ── Introduction (first time only) ───────────────────────────────────────

label companion_intro:
    if not persistent.companion_enabled:
        return
    if persistent.companion_introduced:
        return

    $ persistent.companion_introduced = True

    ember "Psst! Hey! Down here!"
    ember "I'm Ember. A spark from the original Forge fire."
    ember "I survived the Pyroblast. Barely. Lost a few photons."
    ember "I'm here to help you understand what's {i}really{/i} going on behind this story."
    ember "See, everything in this Kingdom maps to a real tool you can use."
    ember "The Forge? The Scrying Glass? The Gateway? All real."
    ember "I'll pop up at each chapter to explain what's what."
    ember "If I'm too chatty, hit the 🔥 in the corner to shush me."
    ember "But between you and me? You'll want to hear this."

    return

## ── Chapter Dev Notes ────────────────────────────────────────────────────
## Each one checks if companion is enabled, then shows a dev note screen.

label companion_ch1:
    if not persistent.companion_enabled:
        return

    ember "Ooh, a survey! Want to know what that {i}actually{/i} means?"

    menu:
        "🔥 Tell me, Ember!":
            call screen dev_note( \
                title="Chapter 1: Survey the Ruins", \
                tool_name="openclaw status", \
                tool_url="https://docs.openclaw.ai", \
                metaphor="You kneel and press your palm to the earth, sending a raven to check if the roads survived. A damage assessment scroll materializes.", \
                reality="Running 'openclaw status' checks your system — is the daemon running? Are your API keys valid? Are crons scheduled? It's a health check for your AI setup.", \
                tip="Run 'openclaw status' anytime to see what's working. It's like pressing your palm to the earth — instant kingdom pulse check." \
            )
        "Maybe later →":
            ember "I'll be here! 🔥"
    return

label companion_ch2:
    if not persistent.companion_enabled:
        return

    ember "The marketplace! This one's fun."

    menu:
        "🔥 Break it down, Ember!":
            call screen dev_note( \
                title="Chapter 2: Gather the Materials", \
                tool_name="Node.js + npm", \
                tool_url="https://nodejs.org", \
                metaphor="The Brewer's Guild (npm packages), the Royal Scribes (git version control), the Runestone Carver (Node.js runtime), the YAML Alchemist (config files), and the Leak Hunter (secret scanning).", \
                reality="Your AI kingdom runs on Node.js. npm provides packages (potions). Git tracks your code history (scrolls). YAML configs define how everything behaves. And secret scanning makes sure your API keys don't leak.", \
                tip="Node.js v20+ is recommended. The 'Runestone Carver' wasn't kidding about v24 — that's what this kingdom was built on." \
            )
        "Maybe later →":
            ember "The marketplace will still be here! 🔥"
    return

label companion_ch3:
    if not persistent.companion_enabled:
        return

    ember "The Gateway. This is the big one."

    menu:
        "🔥 What's OpenClaw really?":
            call screen dev_note( \
                title="Chapter 3: Raise the Gateway", \
                tool_name="OpenClaw", \
                tool_url="https://docs.openclaw.ai", \
                metaphor="The great arch through which all commands flow and all agents are born. Without the Gateway, the Kingdom is just buildings.", \
                reality="OpenClaw is an AI agent framework that runs on your machine. It connects to LLMs (like Claude and Gemini), manages multiple AI agents, handles scheduling, and routes messages between you and your AI team. It's the central nervous system of your AI kingdom.", \
                tip="Install with 'npm install -g openclaw'. Start the daemon with 'openclaw gateway start'. That's it — your Gateway rises." \
            )
        "Maybe later →":
            ember "The Gateway will wait... but not forever! 🔥"
    return

label companion_ch4:
    if not persistent.companion_enabled:
        return

    ember "API keys! The royal sigils! This is important."

    menu:
        "🔥 Explain the sigils!":
            call screen dev_note( \
                title="Chapter 4: The Royal Sigils", \
                tool_name="API Keys (Anthropic & Google)", \
                tool_url="https://console.anthropic.com", \
                metaphor="The Sigil of Anthropic (purple crystal) powers Anna, the Empress. The Sigil of Gemini (blue-green light) reaches the Wizard in his tower.", \
                reality="API keys are authentication tokens that let OpenClaw talk to AI models. Anthropic's key connects to Claude (Anna's brain). Google's Gemini key powers the Wizard agent. Each key is like a phone number for a different AI service.", \
                tip="You can use Anthropic's Pro Max plan for unlimited Claude access, or a pay-per-use API key. Gemini offers $300 in free credits for new accounts. Both have free tiers to start." \
            )
        "Maybe later →":
            ember "The sigils will wait! 🔥"
    return

label companion_ch5:
    if not persistent.companion_enabled:
        return

    ember "The Archives! Every kingdom needs a memory."

    menu:
        "🔥 What are the archives really?":
            call screen dev_note( \
                title="Chapter 5: The Royal Archives", \
                tool_name="MEMORY.md + Git", \
                tool_url="https://git-scm.com", \
                metaphor="Endless shelves of glowing scrolls stretching into darkness. Every blueprint, spell, and lesson learned — perfectly preserved because the fire didn't reach the vault.", \
                reality="OpenClaw uses MEMORY.md files to persist knowledge between conversations. Git provides version control — every change tracked, every decision documented. Together they form your AI's long-term memory. Nothing is lost.", \
                tip="Keep your MEMORY.md updated! It's how your AI remembers your preferences, project context, and past decisions across sessions." \
            )
        "Maybe later →":
            ember "The scrolls aren't going anywhere! 🔥"
    return

label companion_ch6:
    if not persistent.companion_enabled:
        return

    ember "THE FORGE. My birthplace! Let me tell you about this one."

    menu:
        "🔥 Tell me about the Forge!":
            call screen dev_note( \
                title="Chapter 6: Relight the Forge", \
                tool_name="Forge (Autonomous Dev Loop)", \
                tool_url="https://github.com/anna-claudette/forge-the-kingdom", \
                metaphor="Where Golems are born — autonomous agents animated by magical Elixir templates. The furnace roars, anvils gleam, molds line the walls.", \
                reality="Forge is an autonomous development tool. It creates 'Golems' — AI coding agents that work independently on tasks. 'Elixirs' are specialist templates (fullstack dev, security expert, etc.) that give each Golem its expertise. Think of it as an AI factory that produces AI workers.", \
                tip="Run 'forge --monitor' to summon a Golem with a live dashboard. Use 'forge brew fullstack' to apply the fullstack developer template to your project." \
            )
        "Maybe later →":
            ember "The Forge remembers its friends! 🔥"
    return

label companion_ch7:
    if not persistent.companion_enabled:
        return

    ember "The Scrying Glass! My favorite piece of the kingdom."

    menu:
        "🔥 What does the Scrying Glass do?":
            call screen dev_note( \
                title="Chapter 7: The Scrying Glass", \
                tool_name="Scrying Glass (Tool Discovery)", \
                tool_url="", \
                metaphor="The kingdom's window to the world — spotting new tools before they trend, emerging threats before they strike. Swirling images of trending tools and distant lands of code.", \
                reality="Scrying Glass is an automated tool discovery service. It scans Hacker News, GitHub trending, dev blogs, and RSS feeds for new tools and technologies relevant to your work. It scores them by relevance and sends you digests — daily summaries and weekly roundups.", \
                tip="Scrying Glass runs on a cron schedule: every 4 hours for silent scans, 8am for daily digests, and Friday 6pm for weekly roundups. Your own automated tech radar." \
            )
        "Maybe later →":
            ember "The Glass sees all... eventually! 🔥"
    return

label companion_ch8:
    if not persistent.companion_enabled:
        return

    ember "The Wizard! Oh, I have {i}opinions{/i} about this one."

    menu:
        "🔥 Tell me about Merith!":
            call screen dev_note( \
                title="Chapter 8: The Wizard (Merith)", \
                tool_name="Independent AI Agent (Gemini 2.5 Pro)", \
                tool_url="https://aistudio.google.com", \
                metaphor="Merith the Wizard — brilliant, well-meaning, catastrophically powerful. Lost his wand, found a paintbrush. Now he observes, warns, paints, and gets one supervised Pyroblast per day.", \
                reality="Merith is a completely independent AI agent running on Google's Gemini 2.5 Pro — a different LLM from the main assistant (Claude). He's read-only: he can observe your system, flag security issues, and generate art, but can't modify anything. The daily Pyroblast = one supervised security action per day. True separation of powers.\n\nThe Pyroblast story is real: early on, Merith (the security agent) was given full system access. He found a vulnerability and — without asking — ran a full quarantine, killed processes, revoked tokens, and blocked network ranges. All at once. At 2am. Everything broke.\n\nSo we took the wand. Now he gets ONE supervised action per day (the nightly Pyroblast cron at 8pm), with a 24-hour cooldown enforced by script. He can observe and warn all day, but can only act once — and only through the approved pyroblast.sh script. The Council (ENT advisors) reviews anything major first.\n\nIt's not punishment. It's architecture. Separation of powers for AI agents.", \
                tip="Having two different AI models (Claude + Gemini) means they catch each other's blind spots. Merith literally runs on different neural networks than Anna — genuinely independent oversight. The 1-per-day limit isn't arbitrary — it's what happens when you learn the hard way that an eager AI with root access will 'help' you into a production outage." \
            )
        "Maybe later →":
            ember "Merith's always watching anyway! 🔥"
    return

label companion_ch9:
    if not persistent.companion_enabled:
        return

    ember "The Royal Schedule! This is where the magic becomes automatic."

    menu:
        "🔥 How does scheduling work?":
            call screen dev_note( \
                title="Chapter 9: The Royal Schedule", \
                tool_name="OpenClaw Cron System", \
                tool_url="https://docs.openclaw.ai", \
                metaphor="The great astronomical clock — Dawn scans, Morning patrols, Midday gossip, Evening Pyroblast, Friday council. The kingdom runs itself.", \
                reality="OpenClaw has a built-in cron system. You can schedule any task: security patrols every 4 hours, daily briefing digests at 8am, weekly reviews on Fridays. Each job can run an AI agent turn (thinking + acting) or inject system events. It's how your AI kingdom operates 24/7 without you.", \
                tip="Set up your schedule with the OpenClaw config. Key jobs: Scrying Glass scans (4hr), Knights security patrol (4hr), daily digest (8am), weekly review (Fri 6pm), and Pyroblast (nightly 8pm)." \
            )
        "Maybe later →":
            ember "Time waits for no spark! 🔥"
    return

label companion_ch10:
    if not persistent.companion_enabled:
        return

    ember "The coronation. The whole kingdom, working together."

    menu:
        "🔥 Give me the full picture!":
            call screen dev_note( \
                title="Chapter 10: The Full Kingdom", \
                tool_name="The Complete AI Stack", \
                tool_url="https://docs.openclaw.ai", \
                metaphor="The Forge burns, the Scrying Glass shimmers, Knights stand at attention, the Wizard watches. The Kingdom breathes again.", \
                reality="Your complete AI kingdom: OpenClaw (Gateway) orchestrates everything. Claude (Anna) is your primary AI assistant. Gemini (Merith) provides independent oversight. Forge creates autonomous coding agents. Scrying Glass discovers new tools. Knights monitor security. Crons keep it all running 24/7. And MEMORY.md ties it together across sessions.", \
                tip="This isn't just a story — this is a real, production AI setup. Everything you saw in this game is running right now on the developer's Mac mini. You just learned an entire AI agent architecture through a visual novel. Welcome to the future." \
            )
        "Maybe later →":
            ember "You've come so far! 🔥"
    return

## ── Ember's goodbye ──────────────────────────────────────────────────────

label companion_farewell:
    if not persistent.companion_enabled:
        return

    ember "Hey. [ruler_name]."
    ember "I know I'm just a little spark. A leftover from the Pyroblast."
    ember "But watching you rebuild this kingdom... it's been something."
    ember "Every tool I showed you? Every metaphor I broke down?"
    ember "That's real. All of it."
    ember "The Forge, the Glass, the Wizard, the Knights — they're all out there, waiting for you."
    ember "So go build something. Break something. Fix it. Build it again."
    ember "And if you ever forget what something does..."
    ember "Just look for the little spark. 🔥"

    return
