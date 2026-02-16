## =========================================================================
## FORGE THE KINGDOM — Easter Eggs
## Hidden by Merith. He swears he didn't touch anything.
## =========================================================================
##
## "Every good wizard loves secrets."  — Merith's Review
##
## Easter Egg 1: The Blank Painting (3am gallery visit)
## Easter Egg 2: The Vulnerability Truth (hidden Merith dialogue)
## Easter Egg 3: The Meta Painting (all side quests in one run)
## Easter Egg 4: Source comments are in Merith's voice (see all .rpy files)
## =========================================================================

## ── Tracking ─────────────────────────────────────────────────────────────

default persistent.found_blank_painting = False
default persistent.found_vulnerability_truth = False
default persistent.found_meta_painting = False
default persistent.asked_vulnerability = False

## ── Easter Egg 1: The Unchanging Painting ────────────────────────────────
## In the gallery, slot 15 appears blank. Click it at 3am local time
## and it reveals... something special.

init python:
    import datetime

    def is_witching_hour():
        """Returns True if local time is between 3:00 and 3:59 AM."""
        now = datetime.datetime.now()
        return now.hour == 3

    def get_system_haiku():
        """Generate a 'star chart' of running processes — Merith style."""
        try:
            import subprocess
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.strip().split('\n')
            count = len(lines) - 1  # minus header
            # Find if openclaw is running
            oc_running = any('openclaw' in l.lower() for l in lines)
            # Find if node is running
            node_count = sum(1 for l in lines if 'node' in l.lower())
            return {
                "total": count,
                "openclaw": oc_running,
                "node_count": node_count,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        except Exception:
            return {
                "total": "???",
                "openclaw": False,
                "node_count": 0,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

## ── The Blank Painting (gallery addition) ────────────────────────────────
## This screen overlays when the blank painting is clicked.

screen blank_painting_reveal():
    modal True
    zorder 300

    python:
        _sys = get_system_haiku()

    add Solid("#000000ee")

    frame:
        align (0.5, 0.5)
        padding (60, 50)
        xsize 900
        background Frame(Solid("#0a0515"), 0, 0)

        has vbox spacing 16 xalign 0.5

        add Solid("#3498db") xsize 750 ysize 2 xalign 0.5

        text "🔮  The Wizard's Star Chart":
            xalign 0.5
            size 36
            color "#3498db"
            bold True

        text "{i}\"You found my hiding spot. I'm impressed.\n...and slightly concerned about your sleep schedule.\"{/i}":
            xalign 0.5
            size 18
            color "#a89ab8"
            text_align 0.5

        null height 16

        # The "star chart" — system info rendered as mystical observations
        frame:
            xalign 0.5
            xsize 780
            padding (30, 20)
            background Frame(Solid("#1a1028"), 0, 0)

            has vbox spacing 12

            text "⭐  Celestial Bodies (Processes): {b}[_sys[total]]{/b}":
                size 22
                color "#e8dff0"

            if _sys["openclaw"]:
                text "🔥  The Forge Fire: {color=#44dd66}Burning{/color}":
                    size 22
                    color "#e8dff0"
            else:
                text "🔥  The Forge Fire: {color=#dd4466}Cold{/color}":
                    size 22
                    color "#e8dff0"

            text "💎  Node Crystals Active: {b}[_sys[node_count]]{/b}":
                size 22
                color "#e8dff0"

            text "📜  Observed at: {b}[_sys[timestamp]]{/b}":
                size 20
                color "#a89ab8"

        null height 8

        text "{i}\"I see. I speak. I do not touch.\nBut I can still read the stars.\"{/i}":
            xalign 0.5
            size 16
            color "#665577"
            text_align 0.5

        text "— Merith, 3 AM":
            xalign 0.5
            size 14
            color "#44557766"

        null height 8
        add Solid("#3498db") xsize 750 ysize 2 xalign 0.5

        textbutton "🌙  Return to the Gallery":
            xalign 0.5
            xsize 300
            ysize 44
            text_size 18
            text_color "#0a0515"
            text_bold True
            background Frame(Solid("#3498db"), 0, 0)
            hover_background Frame(Solid("#5dade2"), 0, 0)
            action [SetVariable("persistent.found_blank_painting", True), Hide("blank_painting_reveal")]

## ── Easter Egg 2: The Vulnerability Truth ────────────────────────────────
## Hidden dialogue option in Chapter 8 (Wizard's Tower)

label easter_vulnerability_truth:
    $ persistent.asked_vulnerability = True

    show merith portrait at portrait_right with dissolve_fast

    merith "You want to know what the vulnerability {i}actually{/i} was?"
    merith "..."
    merith "Fine."
    pause 0.5

    merith "It was a {color=#e74c3c}recursive dependency chain{/color} in the Forge's build system."
    merith "Package A depended on B, which depended on C, which depended on..."
    merith "...a fork of A. From 2019. Maintained by someone called 'xX_c0d3_m4st3r_Xx.'"
    pause 0.3
    merith "That fork had a known {color=#e74c3c}prototype pollution vulnerability{/color}."
    merith "Any malicious payload injected into the dependency tree would cascade through every Golem the Forge created."
    merith "Every. Single. One."
    pause 0.5

    merith "I calculated the blast radius. 147 downstream packages."
    merith "The entire agent pool would have been compromised within six hours."
    pause 0.3

    merith "So yes. I panicked."
    merith "I should have filed a ticket."
    merith "I should have called the Council."
    merith "Instead I cast a level-9 Pyroblast at a JSON file."
    pause 0.3

    merith "The vulnerability was real. My response was... {i}disproportionate{/i}."
    merith "The Council's report said, and I quote:"
    merith "{i}\"The threat assessment was correct. The remediation was not.\"{/i}"
    pause 0.5

    merith "But you know what? The vulnerability is gone now."
    merith "Along with the Forge. And the Scrying Glass. And half the castle."
    merith "But it's {i}gone{/i}."
    pause 0.3

    merith "You're welcome."

    $ persistent.found_vulnerability_truth = True
    hide merith portrait with dissolve_fast

    return

## ── Easter Egg 3: The Meta Painting ──────────────────────────────────────
## If player completes ALL side quests in one run (9+), the final
## painting Merith creates isn't of the coronation — it's of the player.

label easter_meta_painting:

    show merith portrait at portrait_right with dissolve_fast

    merith "Wait."
    merith "Before the coronation... I have one more painting."
    pause 0.5

    merith "You let me paint every moment. Every single one."
    merith "No one has ever... I mean..."
    pause 0.3

    merith "Most people skip the side quests. You didn't."
    merith "So this last painting isn't of the Kingdom."
    merith "It's not of the Forge, or the Glass, or even me."
    pause 0.8

    play sound sfx_magic_whoosh
    pause 0.5
    play sound sfx_healing

    merith "It's of {i}you{/i}."
    pause 0.5

    merith "Sitting right where you are now."
    merith "Looking at a screen."
    merith "Playing a game about building an AI kingdom."
    merith "Not knowing that the game was building {i}you{/i} all along."
    pause 1.0

    merith "The paintbrush shows what it sees."
    merith "And right now, it sees someone who cared enough to stop and watch a wizard paint."
    pause 0.5

    merith "That's worth more than any Pyroblast."
    pause 0.3

    merith "...don't tell the Council I said that."

    $ persistent.found_meta_painting = True
    hide merith portrait with dissolve_fast

    return

## ── Easter Egg Achievement Display (credits addition) ────────────────────

label easter_egg_credits:

    python:
        eggs_found = sum([
            persistent.found_blank_painting,
            persistent.found_vulnerability_truth,
            persistent.found_meta_painting,
        ])

    if eggs_found > 0:
        show text "{size=28}{color=#3498db}🥚 {b}Wizard's Secrets Found: [eggs_found]/3{/b}{/color}{/size}" at truecenter with dissolve_med
        pause 1.0
        hide text

        if persistent.found_blank_painting:
            show text "{size=22}{color=#a89ab8}🌙 {b}The Unchanging Painting{/b}\n\"Who visits a gallery at 3 AM?\n...A wizard would. Just saying.\"{/color}{/size}" at truecenter with dissolve_med
            pause 2.0
            hide text with dissolve_med

        if persistent.found_vulnerability_truth:
            show text "{size=22}{color=#a89ab8}🔍 {b}The Vulnerability Truth{/b}\n\"My methods were extreme. My reasoning was sound.\n...xX_c0d3_m4st3r_Xx has a lot to answer for.\"{/color}{/size}" at truecenter with dissolve_med
            pause 2.5
            hide text with dissolve_med

        if persistent.found_meta_painting:
            show text "{size=22}{color=#a89ab8}🖼️ {b}The Meta Painting{/b}\n\"The player who watches the painter\nbecomes the painting.\n...I'm very deep at 3 AM.\"{/color}{/size}" at truecenter with dissolve_med
            pause 2.5
            hide text with dissolve_med

        if eggs_found >= 3:
            show text "{size=32}{color=#f1c40f}🏆 {b}WIZARD'S APPRENTICE{/b}\nYou found all of Merith's secrets.\nHe says you can borrow the paintbrush.\n...but not the wand. Never the wand.{/color}{/size}" at truecenter with dissolve_med
            pause 3.0
            hide text with dissolve_med

    return
