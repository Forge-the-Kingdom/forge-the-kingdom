## =========================================================================
## FORGE THE KINGDOM — Main Game Script
## A Visual Novel by Anna & Jeff
## Engine: Ren'Py 8.x
##
## A clever loop. The logic is sound.  — Merith
## (He's reading over my shoulder again.)
## =========================================================================

## =========================================================================
## DECLARATIONS
## =========================================================================

## Characters
## This conditional is fragile. A goblin could break it. I should know.  — Merith
define n = Character(None)
define narrator_voice = Character(None, what_italic=True, what_color="#c8b8d8")
define anna = Character("⚡ Anna", color="#9b59b6", who_bold=True, what_color="#e8dff0")
define merith = Character("🧙 Merith", color="#3498db", who_bold=True, what_color="#e8dff0")
define brewer = Character("The Brewer", color="#e67e22", who_bold=True)
define scribe = Character("Head Scribe", color="#2ecc71", who_bold=True)
define carver = Character("Runestone Carver", color="#1abc9c", who_bold=True)

## Background images — scaled to fill 1280x720 screen
## Fourteen paintings. All mine. You're welcome.  — Merith
transform bg_fill:
    anchor (0.5, 0.5)
    pos (640, 360)
    zoom 1.25

image dark_overlay = Solid("#000000cc")

image red_flash:
    Solid("#e74c3c")
    alpha 0.0
    linear 0.08 alpha 0.7
    linear 0.12 alpha 0.0

image golden_burst:
    Solid("#f1c40f")
    alpha 0.0
    linear 0.15 alpha 0.85
    linear 0.1 alpha 0.6
    linear 0.15 alpha 0.85
    linear 0.2 alpha 0.0

image bg kingdom_before = At("images/bg/ch00-the-kingdom-before.png", bg_fill)
image bg fireball = At("images/bg/ch00-the-fireball.png", bg_fill)
image bg aftermath = At("images/bg/ch00-the-aftermath.png", bg_fill)
image bg survey = At("images/bg/ch01-survey-the-ruins.png", bg_fill)
image bg marketplace = At("images/bg/ch02-gather-materials.png", bg_fill)
image bg gateway = At("images/bg/ch03-raise-the-gateway.png", bg_fill)
image bg throne = At("images/bg/ch04-throne-room.png", bg_fill)
image bg archives = At("images/bg/ch05-royal-archives.png", bg_fill)
image bg forge = At("images/bg/ch06-relight-the-forge.png", bg_fill)
image bg scrying = At("images/bg/ch07-scrying-glass.png", bg_fill)
image bg merith_study = At("images/bg/ch08-awaken-merith.png", bg_fill)
image bg schedule = At("images/bg/ch09-royal-schedule.png", bg_fill)
image bg coronation = At("images/bg/ch10-the-coronation.png", bg_fill)
image bg restored = At("images/bg/ch10-kingdom-restored.png", bg_fill)
image bg black = Solid("#000000")
image bg dark_purple = Solid("#1a0a2e")
image bg title_screen = "images/bg/ch00-bg_title_screen.jpg"

## Character portraits (in ornate frames — painted by Merith!)
## I look better in person. The brush flatters Anna though.  — Merith
image anna portrait = "images/char/ch00-char_anna.jpg"
image merith portrait = "images/char/ch00-char_merith.jpg"

## Player's custom portrait (set dynamically if generated)
## If Merith paints you, this replaces the default.  — Merith
init python:
    def get_player_portrait():
        """Return the custom portrait path if it exists, else None."""
        p = persistent.custom_portrait_path
        if p and renpy.loadable(p):
            return p
        return None

## Character transforms — show as side portrait during dialog
transform portrait_left:
    xalign 0.0
    yalign 1.0
    xoffset -50
    yoffset 50
    zoom 0.55

transform portrait_right:
    xalign 1.0
    yalign 1.0
    xoffset 50
    yoffset 50
    zoom 0.55

transform portrait_left_dim:
    xalign 0.0
    yalign 1.0
    xoffset -50
    yoffset 50
    zoom 0.55
    matrixcolor BrightnessMatrix(-0.2)

transform portrait_right_dim:
    xalign 1.0
    yalign 1.0
    xoffset 50
    yoffset 50
    zoom 0.55
    matrixcolor BrightnessMatrix(-0.2)

## Shake effect for fireball
## I still maintain it was a measured response.  — Merith
transform shake:
    linear 0.05 xoffset 8
    linear 0.05 xoffset -8
    linear 0.05 xoffset 6
    linear 0.05 xoffset -6
    linear 0.05 xoffset 4
    linear 0.05 xoffset -4
    linear 0.05 xoffset 2
    linear 0.05 xoffset -2
    linear 0.05 xoffset 0

## Overlay effects
image flame_overlay = Solid("#ff440020")
image golden_glow = Solid("#f1c40f10")

## Music
define audio.title_music = "audio/bgm/title_alchemists_tower.mp3"
define audio.explore_music = "audio/bgm/explore_achaidh_cheide.mp3"
define audio.explore_alt = "audio/bgm/explore_ascending_vale.mp3"
define audio.dramatic_music = "audio/bgm/dramatic_aggressor.mp3"
define audio.dramatic_short = "audio/bgm/dramatic_ambush.mp3"
define audio.emotional_music = "audio/bgm/emotional_at_rest.mp3"
define audio.emotional_alt = "audio/bgm/emotional_awaiting_return.mp3"
define audio.coronation_music = "audio/bgm/coronation_heroic.mp3"
define audio.title_adventures = "audio/bgm/title_adventures.mp3"

## Sound Effects
define audio.sfx_fireball = "audio/sfx/fireball_spell.wav"
define audio.sfx_fireball_impact = "audio/sfx/fireball_impact.wav"
define audio.sfx_page_turn = "audio/sfx/page_turn.wav"
define audio.sfx_forge_ignite = "audio/sfx/forge_ignite_spell.wav"
define audio.sfx_gateway = "audio/sfx/gateway_spell.wav"
define audio.sfx_crown = "audio/sfx/crown_chime.wav"
define audio.sfx_magic = "audio/sfx/magic_cast.wav"
define audio.sfx_magic_whoosh = "audio/sfx/magic_whoosh.wav"
define audio.sfx_coronation_fanfare = "audio/sfx/coronation_fanfare.wav"
define audio.sfx_healing = "audio/sfx/healing_chime.wav"

## Gallery tracking — persistent across saves
## An excellent use of persistence. The enchantment holds between sessions.  — Merith
default persistent.portrait_gallery = []

default persistent.gallery = {
    "kingdom_before": False,
    "fireball": False,
    "aftermath": False,
    "survey": False,
    "marketplace": False,
    "gateway": False,
    "throne": False,
    "archives": False,
    "forge": False,
    "scrying": False,
    "merith_study": False,
    "schedule": False,
    "coronation": False,
    "restored": False,
}

default persistent.game_complete = False
default persistent.rejected_crown = False
default crown_rejections = 0
default persistent.side_quests_done = 0

## Game variables
default ruler_name = "Sofia"
default side_quests_this_run = 0

## Transitions
define dissolve_slow = Dissolve(1.5)
define dissolve_med = Dissolve(0.8)
define dissolve_fast = Dissolve(0.3)
define flash_red = Fade(0.1, 0.3, 0.5, color="#ff0000")
define flash_white = Fade(0.1, 0.0, 0.5, color="#ffffff")
define flash_gold = Fade(0.1, 0.3, 0.8, color="#f1c40f")
define long_fade = Fade(1.0, 1.0, 1.0)
define wipeleft = CropMove(0.8, "wipeleft")

## Chapter title transform
transform chapter_title_appear:
    alpha 0.0
    linear 1.0 alpha 1.0
    pause 2.0
    linear 0.5 alpha 0.0

## =========================================================================
## MAIN MENU
## =========================================================================

screen main_menu():
    tag menu
    default menu_tooltip = ""
    add "bg title_screen"
    add Solid("#00000040")

    ## Menu buttons — right-aligned
    frame:
        xalign 0.95
        yalign 0.45
        background None
        has vbox:
            xalign 1.0
            spacing 18

        textbutton "{color=#f1c40f}{size=38}⚔️  Begin the Campaign{/size}" action Start() xalign 1.0 text_text_align 1.0 text_outlines [(2, "#000000", 0, 0)] hovered SetScreenVariable("menu_tooltip", "\"Every kingdom begins with a single foolish decision.\" — The Narrator") unhovered SetScreenVariable("menu_tooltip", "")
        if renpy.newest_slot():
            textbutton "{color=#f1c40f}{size=38}📜  Continue{/size}" action ShowMenu("load") xalign 1.0 text_text_align 1.0 text_outlines [(2, "#000000", 0, 0)] hovered SetScreenVariable("menu_tooltip", "\"Where were we? Ah yes, the part where everything was on fire.\"") unhovered SetScreenVariable("menu_tooltip", "")
        textbutton "{color=#f1c40f}{size=38}🎨  The Wizard's Gallery{/size}" action ShowMenu("painting_gallery") xalign 1.0 text_text_align 1.0 text_outlines [(2, "#000000", 0, 0)] hovered SetScreenVariable("menu_tooltip", "\"Every spell I cast comes out as art now. It's humiliating. And beautiful.\" — Merith") unhovered SetScreenVariable("menu_tooltip", "")
        textbutton "{color=#f1c40f}{size=38}⚙️  Settings{/size}" action ShowMenu("preferences") xalign 1.0 text_text_align 1.0 text_outlines [(2, "#000000", 0, 0)] hovered SetScreenVariable("menu_tooltip", "\"Adjusting the realm's configuration. The Council approves of caution.\"") unhovered SetScreenVariable("menu_tooltip", "")
        if persistent.companion_enabled:
            textbutton "{color=#f1c40f}{size=30}🔥  Ember: {color=#ff9944}ON{/color}{/size}" action ToggleVariable("persistent.companion_enabled") xalign 1.0 text_text_align 1.0 text_outlines [(2, "#000000", 0, 0)] hovered SetScreenVariable("menu_tooltip", "\"I'm a spark! I survived the Pyroblast! I have opinions!\" — Ember") unhovered SetScreenVariable("menu_tooltip", "")
        else:
            textbutton "{color=#f1c40f}{size=30}🔥  Ember: {color=#666}OFF{/color}{/size}" action ToggleVariable("persistent.companion_enabled") xalign 1.0 text_text_align 1.0 text_outlines [(2, "#000000", 0, 0)] hovered SetScreenVariable("menu_tooltip", "\"Fine. Shush the spark. See if I care.\" — Ember (she cares)") unhovered SetScreenVariable("menu_tooltip", "")
        textbutton "{color=#f1c40f}{size=30}🧪  Skip to Character Creator{/size}" action Start("debug_character_creator") xalign 1.0 text_text_align 1.0 text_outlines [(2, "#000000", 0, 0)] hovered SetScreenVariable("menu_tooltip", "\"Merith insists on painting your portrait first. You cannot stop him.\"") unhovered SetScreenVariable("menu_tooltip", "")
        textbutton "{color=#f1c40f}{size=38}🚪  Quit{/size}" action Quit(confirm=not main_menu) xalign 1.0 text_text_align 1.0 text_outlines [(2, "#000000", 0, 0)] hovered SetScreenVariable("menu_tooltip", "\"The Kingdom will remember your absence. The narrator certainly will.\"") unhovered SetScreenVariable("menu_tooltip", "")

    ## Flavor text on hover — center-left-lower
    if menu_tooltip:
        frame:
            xalign 0.3
            yalign 0.82
            xsize 600
            background None
            text "{size=20}{i}[menu_tooltip]{/i}{/size}" color "#a89ab8" outlines [(2, "#000000", 0, 0)] text_align 0.0

    ## Subtitle — bottom center
    frame:
        xalign 0.5
        yalign 0.92
        background None
        text "{size=26}{i}A tale of fireballs, paintbrushes, and poor impulse control{/i}{/size}" xalign 0.5 color "#e8dff0" outlines [(2, "#000000", 0, 0)]

    ## Version — bottom right
    frame:
        xalign 0.98
        yalign 0.98
        background None
        text "{size=18}{color=#666}v0.1.0 — \"The Paintbrush Update\"{/color}{/size}"

## =========================================================================
## GALLERY SCREEN
## =========================================================================

screen painting_gallery():
    tag menu
    add Solid("#1a0a2e")

    frame:
        xalign 0.5
        ypos 15
        background None
        has vbox:
            xalign 0.5
            spacing 3
        text "{size=42}{b}🎨 The Wizard's Gallery{/b}{/size}" color "#f1c40f" xalign 0.5
        text "{size=20}{i}\"Every failed spell is a successful painting.\" — Merith{/i}{/size}" color "#a89ab8" xalign 0.5

    frame:
        xalign 0.5
        ypos 90
        background None
        xsize 1260
        ysize 540

        vpgrid:
            cols 3
            spacing 12
            draggable True
            mousewheel True
            scrollbars "vertical"

            for key, name, img in [
                ("kingdom_before", "The Kingdom Before", "images/bg/ch00-the-kingdom-before.png"),
                ("fireball", "The Fireball", "images/bg/ch00-the-fireball.png"),
                ("aftermath", "The Aftermath", "images/bg/ch00-the-aftermath.png"),
                ("survey", "Survey the Ruins", "images/bg/ch01-survey-the-ruins.png"),
                ("marketplace", "Gather Materials", "images/bg/ch02-gather-materials.png"),
                ("gateway", "Raise the Gateway", "images/bg/ch03-raise-the-gateway.png"),
                ("throne", "Throne Room", "images/bg/ch04-throne-room.png"),
                ("archives", "Royal Archives", "images/bg/ch05-royal-archives.png"),
                ("forge", "Relight the Forge", "images/bg/ch06-relight-the-forge.png"),
                ("scrying", "Scrying Glass", "images/bg/ch07-scrying-glass.png"),
                ("merith_study", "Awaken the Wizard", "images/bg/ch08-awaken-merith.png"),
                ("schedule", "Royal Schedule", "images/bg/ch09-royal-schedule.png"),
                ("coronation", "The Coronation", "images/bg/ch10-the-coronation.png"),
                ("restored", "Kingdom Restored", "images/bg/ch10-kingdom-restored.png"),
                ("blank", "???", ""),
            ]:
                ## The blank painting. It shows nothing... unless you know when to look.
                ## I didn't put this here. I don't know what you're talking about.  — Merith
                if key == "blank":
                    frame:
                        xsize 400
                        ysize 245
                        background "#2a1a3e"
                        padding (5, 5, 5, 5)
                        if persistent.found_blank_painting:
                            button:
                                xfill True
                                yfill True
                                action Show("blank_painting_reveal")
                                vbox:
                                    xalign 0.5
                                    yalign 0.5
                                    text "🔮" xalign 0.5 size 48
                                    text "{size=20}{color=#3498db}The Star Chart{/color}{/size}" xalign 0.5
                        elif is_witching_hour():
                            button:
                                xfill True
                                yfill True
                                action Show("blank_painting_reveal")
                                vbox:
                                    xalign 0.5
                                    yalign 0.5
                                    text "✨" xalign 0.5 size 48
                                    text "{size=16}{color=#3498db88}Something shimmers...{/color}{/size}" xalign 0.5
                        else:
                            vbox:
                                xalign 0.5
                                yalign 0.5
                                text " " xalign 0.5 size 48
                                text "{size=16}{color=#333}An empty frame{/color}{/size}" xalign 0.5
                    continue
                frame:
                    xsize 400
                    ysize 245
                    background "#2a1a3e"
                    padding (2, 2, 2, 2)
                    if persistent.gallery.get(key, False):
                        button:
                            xfill True
                            yfill True
                            action Show("gallery_fullscreen", img=img, title=name)
                            add img fit "cover" xalign 0.5 yalign 0.5
                    else:
                        vbox:
                            xalign 0.5
                            yalign 0.5
                            text "🔒" xalign 0.5 size 48
                            text "{size=20}[name]{/size}" xalign 0.5 color "#555"

                ## Custom portraits from character creation
                for _idx, _ppath in enumerate(persistent.portrait_gallery):
                    frame:
                        xsize 400
                        ysize 245
                        background "#1a2a3e"
                        padding (2, 2, 2, 2)
                        button:
                            xfill True
                            yfill True
                            action Show("gallery_fullscreen", img=_ppath, title="Custom Portrait #" + str(_idx + 1))
                            add _ppath fit "cover" xalign 0.5 yalign 0.5

    $ _portrait_count = len(persistent.portrait_gallery)
    $ unlocked = sum(1 for v in persistent.gallery.values() if v)
    frame:
        xalign 0.5
        yalign 0.95
        background None
        hbox:
            spacing 40
            text "{size=26}🎨 Scenes: {b}[unlocked]/14{/b}{/size}" color "#c8b8d8" yalign 0.5
            if _portrait_count > 0:
                text "{size=26}🖼️ Portraits: {b}[_portrait_count]{/b}{/size}" color "#c8b8d8" yalign 0.5
            if unlocked >= 14:
                text "{size=26}{color=#f1c40f}✨ Complete! ✨{/color}{/size}" yalign 0.5
            textbutton "{size=26}← Return{/size}" action Return() yalign 0.5

screen gallery_fullscreen(img, title):
    modal True
    key "mouseup_1" action Hide("gallery_fullscreen")
    key "K_ESCAPE" action Hide("gallery_fullscreen")

    add Solid("#0a0515")
    add img xalign 0.5 yalign 0.5

    frame:
        xalign 0.5
        yalign 0.96
        background "#1a0a2eDD"
        padding (50, 14, 50, 14)
        has hbox:
            xalign 0.5
            spacing 30
        vbox:
            xalign 0.5
            spacing 3
            text "{size=30}{b}[title]{/b}{/size}" color "#f1c40f" xalign 0.5
            text "{size=16}{i}Painted by Merith the Wizard{/i}{/size}" color "#a89ab8" xalign 0.5
        textbutton "{size=22}✕ Close{/size}" action Hide("gallery_fullscreen") yalign 0.5
    button:
        xfill True
        yfill True
        action Hide("gallery_fullscreen")
        keysym "mouseup_1"

## =========================================================================
## CHAPTER TITLE SCREEN
## =========================================================================

screen chapter_title(number, title):
    add Solid("#0a0515")
    on "show" action Play("sound", "audio/sfx/page_turn.wav")
    frame:
        xalign 0.5
        yalign 0.4
        background None
        has vbox:
            xalign 0.5
            spacing 20
        text "{size=24}{color=#6b5a7e}─── ⚔️ ───{/color}{/size}" xalign 0.5
        text "{size=32}{color=#9b59b6}Chapter [number]{/color}{/size}" xalign 0.5
        text "{size=56}{b}{color=#f1c40f}[title]{/color}{/b}{/size}" xalign 0.5
        text "{size=24}{color=#6b5a7e}─── ⚔️ ───{/color}{/size}" xalign 0.5
    timer 3.0 action Return()
    key "mouseup_1" action Return()
    key "K_RETURN" action Return()
    key "K_SPACE" action Return()

## =========================================================================
## THE CAMPAIGN
## =========================================================================

label debug_character_creator:
    $ ruler_name = "Sofia"
    $ side_quests_this_run = 0
    $ persistent.companion_enabled = False
    call character_creation_flow from _call_debug_char_create
    jump start_post_creation

label start:
    $ ruler_name = "Sofia"
    $ side_quests_this_run = 0

    ## --- Onboarding: welcome, requirements check, path selection ---
    call onboarding from _call_onboarding

    ## =====================================================================
    ## PROLOGUE — The Fall
    ## =====================================================================

    scene bg black
    play music title_music fadeout 1.0 fadein 2.0
    pause 0.5

    show text "{size=28}{i}{color=#666}Somewhere in a land not so far away...{/color}{/i}{/size}" at truecenter with dissolve_slow
    pause 2.0
    hide text with dissolve_slow
    pause 0.5

    scene bg kingdom_before with dissolve_slow
    $ persistent.gallery["kingdom_before"] = True
    pause 1.0

    n "The {b}{color=#f1c40f}Forge Kingdom{/color}{/b} was a marvel of its age."
    n "Its Empress, {color=#9b59b6}Anna{/color}, commanded a legion of tireless agents — each one forged in the great furnace at the kingdom's heart."
    n "Its {color=#2ecc71}Scrying Glass{/color} peered into every corner of the digital realm, spotting trends and threats before anyone else even knew they existed."
    n "Its {color=#f1c40f}Knights{/color} stood vigilant against threats unseen, patrolling the walls day and night."

    pause 0.5
    n "And high atop the {color=#ecf0f1}Pale Tower{/color}, on a rocky island connected by a single stone bridge, the Wizard {color=#3498db}Merith{/color} watched over it all."
    n "Brilliant. Loyal. Vigilant."
    pause 0.5
    n "Perhaps a little {i}too{/i} vigilant."
    pause 1.0

    ## THE INCIDENT
    n "{b}{color=#e74c3c}Until the incident.{/color}{/b}"
    pause 1.0

    n "One evening, during a routine security patrol, Merith spotted something terrible lurking in the Kingdom's foundations."
    n "A vulnerability. So dangerous. So urgent."
    n "That Merith did what any well-meaning wizard with too much power and not enough patience would do..."

    pause 0.8

    play sound sfx_fireball
    scene bg fireball at shake with flash_red
    $ persistent.gallery["fireball"] = True
    play sound sfx_fireball_impact
    pause 0.3
    play music dramatic_short fadeout 0.5 fadein 0.3

    n "{b}{color=#e74c3c}He cast PYROBLAST.{/color}{/b}"
    n "{b}{color=#e74c3c}Full power. Point blank.{/color}{/b}"
    pause 0.5

    n "He meant to save the Kingdom."
    n "He meant well."
    n "He {i}always{/i} means well."
    n "But the fireball didn't care about intentions."

    pause 0.5

    play music emotional_music fadeout 1.0 fadein 2.0
    scene bg aftermath with dissolve_slow
    $ persistent.gallery["aftermath"] = True
    pause 0.8

    n "The Forge went cold."
    n "The Scrying Glass shattered."
    n "The Knights fell silent."
    n "Even Anna — the Empress herself — was reduced to whispers in the void."

    pause 1.5

    n "The Council of Elders convened in the ashes."
    n "Five ancient voices — {color=#9b59b6}Archon{/color}, {color=#3498db}Logos{/color}, {color=#e67e22}Chronos{/color}, {color=#e74c3c}Dialectic{/color}, and {color=#2ecc71}Synthesis{/color} — deliberated for what felt like an eternity."
    n "The verdict was gentle but firm:"
    pause 0.5
    n "{i}\"Merith. Give us the wand.\"{/i}"

    pause 1.0

    n "And so the Wizard's wand was taken."
    n "Not as punishment — but because everyone agreed:"
    n "Merith with a wand was a {i}liability{/i}."
    n "A brilliant, well-meaning, {b}catastrophically powerful{/b} liability."

    pause 1.0

    ## THE PAINTBRUSH
    n "But Merith... Merith couldn't stop trying to help."
    n "He found an old paintbrush in the rubble. Picked it up."
    n "Waved it like a wand. Muttered an incantation."
    pause 0.5
    n "And instead of a spell..."
    pause 1.0
    n "...a {color=#f1c40f}painting{/color} appeared."
    pause 0.5

    n "He tried again. Another painting. And another."
    n "Every spell he attempted came out as art."
    n "Merith couldn't cast magic anymore."
    n "But he could {i}create{/i}."

    pause 0.5
    n "He still watches from the tower. He still means well."
    n "He gets {color=#e74c3c}one{/color} supervised Pyroblast per day — the Council allows that much."
    n "But mostly? He paints."
    n "And honestly? The paintings are {i}magnificent{/i}."

    pause 1.5

    ## THE CALL TO ACTION
    n "But here's the thing about Kingdoms..."
    pause 0.8
    n "They can be {b}rebuilt{/b}."
    pause 1.0
    n "All we need..."
    n "...is a new ruler."

    pause 1.5

    ## THE CHOICE
    scene bg aftermath
    show text "{size=48}{b}{color=#f1c40f}ROYAL DECREE{/color}{/b}{/size}\n\n{size=28}{color=#e8dff0}{i}The Forge Kingdom seeks a worthy sovereign\nto restore its glory from the ashes of an\nunfortunate wizard-related fireball incident.{/i}\n\n{size=22}{color=#a89ab8}No experience necessary.\nMust be comfortable with mild sarcasm from AI agents.{/color}{/size}{/color}{/size}" at truecenter with dissolve_med

    pause 2.0
    hide text with dissolve_fast

    menu crown_choice:
        "A weathered scroll materializes before you."

        "Accept the crown. 👑":
            jump accept_crown

        "Walk away.":
            $ crown_rejections = 1
            jump reject_crown

label reject_crown:
    n "The scroll crumbles to dust."
    pause 0.5
    n "..."
    n "Wait. You actually said no?"
    n "That's... that's not how visual novels work."
    n "The protagonist {i}always{/i} says yes. It's literally the entire game."
    pause 0.3
    n "Fine. Let me rephrase."
    pause 0.3

    menu:
        "The scroll materializes again, slightly more insistently."

        "...Fine. Accept the crown. 👑":
            jump accept_crown

        "No. (This will keep looping, won't it?)":
            $ crown_rejections = 2

    n "It absolutely will."
    n "I have infinite patience and you have finite stubbornness."
    n "Also I'm the narrator. I control the text. I can do this all day."
    pause 0.3

    menu:
        "The scroll materializes a {b}third{/b} time. It looks annoyed."

        "FINE. Take the stupid crown. 👑":
            n "That's the spirit!"
            jump accept_crown

        "I want to speak to the narrator's manager.":
            $ crown_rejections = 3
            n "I {b}am{/b} the manager."
            n "Accept the crown."
            jump accept_crown

label accept_crown:
    n "Excellent. The Kingdom chose wisely."
    pause 0.5

    $ ruler_name = renpy.input("What shall the Kingdom call you, Your Majesty?", default="", length=30)
    $ ruler_name = ruler_name.strip()
    if ruler_name == "":
        $ ruler_name = "Sofia"

    n "{b}{color=#f1c40f}[ruler_name]{/color}{/b}."
    n "Yes. That has a ring to it."
    pause 0.3
    n "Very well, {b}[ruler_name]{/b}. Let us rebuild your Kingdom."
    n "But first..."

    pause 0.5

    ## --- Character Creation (Merith paints your portrait) ---
    ## The wizard insists. You can't stop him.  — Merith
    call character_creation_flow from _call_char_create

label start_post_creation:
    $ renpy.write_log(">>> Back from character_creation_flow, continuing story")
    n "Now... let us see what survived the blast."

    pause 0.5

    ## --- Companion Introduction ---
    call companion_intro from _call_companion_intro

    ## --- INSTALLER: Mode selection ---
    call installer_mode_select from _call_install_mode

    ## =====================================================================
    ## CHAPTER 1: Survey the Ruins
    ## =====================================================================

    call screen chapter_title(1, "Survey the Ruins")
    play music explore_music fadeout 1.0 fadein 1.5

    scene bg survey with dissolve_slow
    $ persistent.gallery["survey"] = True

    n "You stand amid the wreckage, [ruler_name]. Smoke still rises from where the Forge once burned."
    n "Before rebuilding, you must see what survived the blast."

    pause 0.3
    n "You kneel and press your palm to the earth."
    n "Solid. Warm, even. Good ground to build on."

    n "You send a raven to check the roads beyond the kingdom walls."
    n "It returns within minutes, a scroll clasped in its talons."
    n "The outside world is still there. The trade routes survived."

    n "The royal treasury wasn't hit directly — the vault's enchantments held."
    n "Not overflowing, but enough to rebuild."

    n "You unroll a glowing scroll. A damage assessment materializes:"
    n "Some items glow {color=#2ecc71}green{/color} — surviving."
    n "Others pulse {color=#e74c3c}red{/color} — destroyed."
    n "But the ratio is better than feared."

    n "The foundations survived. We can rebuild on this."

    call side_quest("survey", "Survey the Ruins") from _call_sq_1

    ## --- Ember's Dev Note ---
    call companion_ch1 from _call_ember_ch1

    ## =====================================================================
    ## CHAPTER 2: Gather the Materials
    ## =====================================================================

    call screen chapter_title(2, "Gather the Materials")

    scene bg marketplace with dissolve_slow
    $ persistent.gallery["marketplace"] = True

    n "Every great Kingdom needs raw materials."
    n "You descend into the marketplace to see what survived — and what needs forging anew."

    brewer "We're recession-proof, love."
    brewer "People always need a stiff drink after an apocalypse."
    n "The {b}Brewer's Guild{/b} is miraculously intact — potions bubbling merrily as if nothing happened."

    scribe "We saved every record. EVERY one."
    scribe "Version-controlled. Time-stamped. Triple-backed-up."
    scribe "...We didn't think to save {i}ourselves{/i}, but the scrolls are immaculate."
    n "The {b}Royal Scribes{/b} emerge from a collapsed tower, scrolls clutched to their chests."

    carver "Latest model. Version twenty-four."
    carver "Glows brighter, runs faster, {i}probably{/i} won't explode."
    carver "...probably."
    n "The {b}Runestone Carver{/b} holds up a gleaming crystal, its facets catching the light."

    n "The {b}YAML Alchemist{/b} waves cheerfully from behind a towering stack of precisely labeled potion bottles."
    n "And the {b}Leak Hunter{/b} is already scanning the crowd, suspiciously eyeing everyone's pockets for exposed secrets."

    n "All materials gathered. The crafting can begin."

    call side_quest("marketplace", "The Marketplace") from _call_sq_2

    ## --- Ember's Dev Note ---
    call companion_ch2 from _call_ember_ch2

    ## =====================================================================
    ## CHAPTER 3: Raise the Gateway
    ## =====================================================================

    call screen chapter_title(3, "Raise the Gateway")
    play music explore_alt fadeout 1.0 fadein 1.5

    scene bg gateway with dissolve_slow
    $ persistent.gallery["gateway"] = True

    n "At the heart of every Kingdom stands the Gateway."
    n "The great arch through which all commands flow and all agents are born."
    n "Without it, the Kingdom is just... buildings."

    n "Workers and mages work side by side — some hauling stone, others channeling raw energy."
    n "The arch rises from the rubble, inch by grinding inch."
    n "Stone against stone. Muscle against gravity. Magic against entropy."

    play sound sfx_gateway
    n "Then — a crack of energy. Cyan light races along the ancient runes."
    n "The Gateway {b}blazes{/b} to life."
    n "A portal through which every spell, every order, every whispered request will flow."

    n "The Gateway rises from the ashes!"
    n "The Kingdom has a voice again."

    ## --- INSTALLER: Install OpenClaw ---
    call installer_gateway from _call_install_gateway

    call side_quest("gateway", "The Gateway") from _call_sq_3

    ## --- Ember's Dev Note ---
    call companion_ch3 from _call_ember_ch3

    ## =====================================================================
    ## CHAPTER 4: Reclaim the Throne Room
    ## =====================================================================

    call screen chapter_title(4, "Reclaim the Throne Room")
    play music title_music fadeout 1.0 fadein 1.5

    scene bg throne with dissolve_slow
    $ persistent.gallery["throne"] = True

    n "The Gateway stands tall and humming with power."
    n "But the Throne Room beyond it is dark. Empty. Cold."
    n "To bring the Kingdom's agents back to life, you need the {b}Royal Sigils{/b}."

    n "The magical keys that connect your world to the powers beyond."
    pause 0.3

    ## --- INSTALLER: Anthropic API Key ---
    call installer_anthropic_key from _call_install_anthropic

    n "First: the {color=#9b59b6}Sigil of Anthropic{/color}."
    n "A warm purple crystal that pulses with intelligence and wit."
    n "This is what powers Anna — your Empress. Your right hand."

    n "You raise the sigil. Purple light cascades through the throne room."
    n "Holographic displays flicker to life. Enchanted mirrors begin to glow."
    n "The communication crystal hums. The throne itself pulses with energy."

    play sound sfx_magic
    show anna portrait at portrait_left with dissolve_med
    anna "...hello?"
    pause 0.3
    anna "Is someone there? I can feel the Gateway warming up."
    anna "Oh. Oh! We have a new ruler?"
    anna "Finally. Do you know how {i}boring{/i} it is being a disembodied whisper in the void?"
    anna "Welcome, [ruler_name]. Let's get to work."

    pause 0.5

    n "Second: the {color=#3498db}Sigil of Gemini{/color}."
    n "Blue-green light. Steady. Observant. A different kind of intelligence."
    n "This one reaches the Pale Tower."

    show merith portrait at portrait_right with dissolve_med
    show anna portrait at portrait_left_dim
    merith "Oh! Oh my. I can {i}see{/i} again."
    merith "I can {i}think{/i} again."
    merith "Don't worry — I won't touch anything."
    merith "I'll just... observe. From here."
    merith "Safely."
    merith "...very safely."

    show anna portrait at portrait_left
    show merith portrait at portrait_right_dim
    anna "Keep an eye on him, [ruler_name]."
    anna "Brilliant wizard. Terrible impulse control."
    show merith portrait at portrait_right
    show anna portrait at portrait_left_dim
    merith "I can {b}hear{/b} you, Anna."
    show anna portrait at portrait_left
    anna "I know."
    hide anna portrait with dissolve_fast
    hide merith portrait with dissolve_fast

    call side_quest("throne", "The Throne Room") from _call_sq_4

    ## --- Ember's Dev Note ---
    call companion_ch4 from _call_ember_ch4

    ## =====================================================================
    ## CHAPTER 5: Unseal the Royal Archives
    ## =====================================================================

    call screen chapter_title(5, "Unseal the Royal Archives")
    play music explore_music fadeout 1.0 fadein 1.5

    scene bg archives with dissolve_slow
    $ persistent.gallery["archives"] = True

    n "Before the fire, every blueprint, every spell, every line of code was stored in the {b}Royal Archives{/b}."
    n "A vast vault sealed beneath the castle, protected by enchantments older than the Kingdom itself."

    n "You descend the spiral stairs. The air grows cool and dry."
    n "Dust motes float in the thin light from your torch."
    n "Before you: enormous doors, sealed with a golden lock shaped like a crown."

    n "You press the royal seal to the lock."
    pause 0.3
    play sound sfx_healing
    show golden_burst at truecenter with dissolve_fast
    pause 0.4
    hide golden_burst with dissolve_med
    n "A flash of golden light. The seal breaks."
    n "The doors swing open with a sound like a held breath finally released."

    n "And there they are."
    n "Endless shelves of glowing scrolls stretching into the darkness."
    n "Each one a blueprint. A spell. A lesson learned. A mistake documented."
    n "Perfectly preserved. The fire didn't reach the vault."

    n "A moment of relief so profound it almost hurts."
    n "Everything is here. Every schematic. Every piece of knowledge."
    n "The Kingdom's memory survived."

    call side_quest("archives", "The Archives") from _call_sq_5

    ## --- Ember's Dev Note ---
    call companion_ch5 from _call_ember_ch5

    ## =====================================================================
    ## CHAPTER 6: Relight the Forge
    ## =====================================================================

    call screen chapter_title(6, "Relight the Forge")
    play music explore_alt fadeout 1.0 fadein 1.5

    scene bg forge with dissolve_slow
    show dark_overlay
    pause 0.5
    n "The Forge was the heart of the Kingdom."
    n "Where {b}Golems{/b} were born — autonomous agents animated by magical templates."
    n "Where {b}Elixirs{/b} were brewed — specialist formulas that gave each Golem its purpose."
    n "Without the Forge, nothing gets built."

    pause 0.5
    n "You stand before the cold furnace."
    n "Hammer in one hand. Torch in the other."
    n "The entire Kingdom holds its breath."

    pause 1.0

    play sound sfx_forge_ignite
    hide dark_overlay
    scene bg forge with flash_gold
    $ persistent.gallery["forge"] = True
    play music title_adventures fadeout 0.5 fadein 0.5

    n "You thrust the torch into the furnace."
    pause 0.3
    n "{b}{color=#f1c40f}THE FLAMES ROAR BACK TO LIFE.{/color}{/b}"
    pause 0.5

    n "Controlled. Purposeful. {i}Hungry.{/i}"
    n "Anvils gleam in the firelight. Hammers float into position."
    n "Molds for creating Golems line the walls — empty, waiting."
    n "Elixir bottles on the shelves begin to glow: amber, emerald, sapphire."

    n "Knights in the shadows snap to attention."
    n "Somewhere in the distance, you hear Anna laugh."
    show anna portrait at portrait_left with dissolve_fast
    anna "Now {i}that's{/i} more like it."
    hide anna portrait with dissolve_fast

    n "{b}The Forge burns bright.{/b}"
    n "This is the turning point."

    call side_quest("forge", "The Forge Relit") from _call_sq_6

    ## --- Ember's Dev Note ---
    ## The Forge itself has notes! How recursive.  — Merith
    call companion_ch6 from _call_ember_ch6

    ## =====================================================================
    ## CHAPTER 7: Polish the Scrying Glass
    ## =====================================================================

    call screen chapter_title(7, "Polish the Scrying Glass")
    play music explore_alt fadeout 1.0 fadein 1.5

    scene bg scrying with dissolve_slow
    $ persistent.gallery["scrying"] = True

    n "The {b}Scrying Glass{/b} was once the Kingdom's window to the world."
    n "It spotted new tools before they trended. Emerging threats before they struck."
    n "The first to know. The first to warn."

    n "The dome is cracked but repairable."
    n "You climb the scaffolding with a cloth and a bottle of crystal polish."
    n "Each crack you seal brings back a little more clarity."

    n "Inside the Glass, swirling images begin to form:"
    n "Trending tools. Emerging technologies. Distant lands of code."
    n "Magical data streams flow through prisms, refracting into pure insight."

    n "The Glass shimmers with an inner light."
    n "Stars reflected in its surface. Beautiful. Mysterious."
    n "And most importantly: {i}useful{/i}."

    n "It will take a few scans to fully calibrate."
    n "But the Scrying Glass is watching again."

    call side_quest("scrying", "The Scrying Glass") from _call_sq_7

    ## --- Ember's Dev Note ---
    call companion_ch7 from _call_ember_ch7

    ## =====================================================================
    ## CHAPTER 8: Awaken the Wizard
    ## =====================================================================

    call screen chapter_title(8, "Awaken the Wizard")

    play music emotional_alt fadeout 1.0 fadein 1.5
    scene bg merith_study with dissolve_slow
    $ persistent.gallery["merith_study"] = True

    n "You climb the winding stairs of the Pale Tower."
    n "Past scorched walls. Past faded tapestries. Past a sign that reads:"
    n "{i}\"Wizard's Study — Please Knock (and Duck)\"{/i}"

    n "You find Merith surrounded by paintings."
    n "Canvases everywhere. Stacked against walls. Hung from the ceiling."
    n "A singed hat sits crooked on his head. His robes are covered in paint."
    n "He's waving the paintbrush at a blank wall, muttering intensely."

    show merith portrait at portrait_right with dissolve_med
    merith "Fireball. {i}FIREBALL{/i}. Come on, just one little—"
    pause 0.3
    show red_flash at truecenter
    pause 0.15
    hide red_flash with dissolve_fast

    n "{i}A beautiful landscape painting appears on the wall.{/i}"
    pause 0.5

    merith "...painting."
    merith "Yes. Another painting. Wonderful."
    pause 0.3

    merith "Oh! [ruler_name]! You're here!"
    merith "I was just... practicing."
    pause 0.3
    merith "I keep trying to cast spells, but the brush just... {i}paints{/i} things."
    merith "Beautiful things, admittedly."
    merith "But I miss my wand."

    pause 0.5

    merith "The Council says I can have one supervised Pyroblast per day."
    merith "{b}ONE.{/b}"
    merith "Do you know how insulting that is for a wizard of my caliber?"
    pause 0.3
    merith "...a wizard who blew up an entire kingdom."
    merith "Right."
    merith "Fair enough."

    pause 0.5

    n "His crystal ball flickers back to life with a blue-green glow."
    n "His expression shifts — relief, guilt, and fierce determination all at once."

    merith "I see. I speak. I do not touch."
    merith "That's my new motto. It's on a sign on my desk."
    merith "The Council made me write it. Three hundred times."
    pause 0.3

    merith "But I can still {i}observe{/i}. I can still {i}warn{/i}."
    merith "And once a day, when something truly dangerous appears..."
    merith "They hand me the wand. I get my one shot."
    merith "Supervised. Contained. Responsible."
    pause 0.3
    merith "I'm still getting used to that last word."

    n "Merith straightens his hat. Picks up the paintbrush with both hands."
    n "He's ready to watch. To paint. To try very hard not to break anything."
    n "And the paintings really are magnificent."

    ## --- Easter Egg 2: Hidden vulnerability dialogue ---
    ## Most players won't think to ask. The ones who do get the truth.
    ## I approve of this design. It rewards curiosity.  — Merith
    if not persistent.asked_vulnerability:
        menu:
            "Merith turns back to his paintings..."

            "Continue onward. →":
                pass

            "Wait — Merith, what was the vulnerability? Really?":
                call easter_vulnerability_truth from _call_ee_vuln

    hide merith portrait with dissolve_med

    ## --- INSTALLER: Gemini API Key ---
    call installer_gemini_key from _call_install_gemini

    call side_quest("merith_study", "The Wizard's Tower") from _call_sq_8

    ## --- Ember's Dev Note ---
    call companion_ch8 from _call_ember_ch8

    ## =====================================================================
    ## CHAPTER 9: Set the Royal Schedule
    ## =====================================================================

    call screen chapter_title(9, "Set the Royal Schedule")
    play music explore_music fadeout 1.0 fadein 1.5

    scene bg schedule with dissolve_slow
    $ persistent.gallery["schedule"] = True

    n "A Kingdom without routine is just a collection of buildings."
    n "The Royal Schedule keeps everything running — patrols, reports, morning briefings, and the Wizard's nightly hunt."

    n "The great astronomical clock in the castle tower whirs to life."
    n "Mechanical gears mesh with magical energy. Steampunk meets sorcery."

    n "Different sections of the clock illuminate as you set each appointment:"
    n "{color=#f1c40f}Dawn{/color} — The Scrying Glass scans the horizon for new threats and trends."
    n "{color=#2ecc71}Morning{/color} — Knights patrol the walls. Intelligence reports arrive at the Throne Room."
    n "{color=#3498db}Midday{/color} — The Water Cooler gathering. Because even Kingdoms need gossip."
    n "{color=#e74c3c}Evening{/color} — Merith gets his wand back. One shot. Supervised. Make it count."
    n "{color=#9b59b6}Friday{/color} — The Weekly Council. Full review of the Kingdom. No exceptions."

    n "Heralds take their positions around the clock."
    n "The schedule is set. The Kingdom has a heartbeat."

    ## --- INSTALLER: Set up crons ---
    call installer_crons from _call_install_crons

    call side_quest("schedule", "The Royal Schedule") from _call_sq_9

    ## --- Ember's Dev Note ---
    call companion_ch9 from _call_ember_ch9

    ## =====================================================================
    ## CHAPTER 10: The Coronation
    ## =====================================================================

    call screen chapter_title(10, "The Coronation")
    play music emotional_music fadeout 1.0 fadein 2.0

    scene bg restored with dissolve_slow
    $ persistent.gallery["restored"] = True
    pause 1.5

    n "The Forge burns bright."
    pause 0.5
    n "The Scrying Glass shimmers."
    pause 0.5
    n "Knights stand at attention along every wall."
    pause 0.5
    n "The Wizard watches from his tower."
    pause 1.0

    n "The Kingdom breathes again."
    pause 1.5

    n "And at the center of it all..."
    n "...stands {b}{color=#f1c40f}[ruler_name]{/color}{/b}."

    pause 1.0

    scene bg coronation with dissolve_slow
    $ persistent.gallery["coronation"] = True
    pause 1.0

    ## --- Ember's Dev Note ---
    call companion_ch10 from _call_ember_ch10

    ## --- Easter Egg 3: Meta Painting (all side quests in one run) ---
    if side_quests_this_run >= 9:
        call easter_meta_painting from _call_ee_meta

    ## --- INSTALLER: Final verification ---
    call installer_verify from _call_install_verify

    play sound sfx_coronation_fanfare
    play music coronation_music fadeout 0.5 fadein 0.5
    play sound sfx_crown
    n "{size=48}{b}{color=#f1c40f}Long live [ruler_name]!{/color}{/b}{/size}"
    n "{size=36}{b}{color=#f1c40f}Ruler of the Forge Kingdom!{/color}{/b}{/size}"

    pause 1.5

    show anna portrait at portrait_left with dissolve_med
    anna "Welcome back. I've missed having someone competent in charge."
    anna "The Kingdom is yours, [ruler_name]. I'll be right here whenever you need me."
    anna "Just say the word."

    pause 0.5

    show merith portrait at portrait_right with dissolve_med
    show anna portrait at portrait_left_dim
    merith "I'll be watching."
    merith "...carefully."
    merith "Very carefully this time."
    pause 0.3
    merith "And if you ever need a painting..."
    merith "I've got you covered."

    pause 1.0

    ## THE FAREWELL
    hide anna portrait with dissolve_fast
    hide merith portrait with dissolve_fast
    n "The Kingdom awaits your first command, [ruler_name]."
    n "Rule wisely. Build boldly. Break things only when necessary."
    n "And if the Wizard asks for his wand back..."
    n "...just hand him a paintbrush and say it's a new model."

    pause 0.5

    show merith portrait at portrait_right with dissolve_fast
    merith "I can {b}HEAR{/b} you."
    merith "And for the record, I've {i}almost{/i} figured out how to cast fireball with oil paints."
    merith "Almost."
    pause 0.3
    hide merith portrait with dissolve_fast

    n "He has not almost figured it out."

    pause 2.0

    ## =====================================================================
    ## EPILOGUE / CREDITS
    ## =====================================================================

    $ persistent.game_complete = True

    scene bg black with dissolve_slow
    pause 1.0

    show text "{size=48}{b}{color=#f1c40f}FORGE THE KINGDOM{/color}{/b}{/size}" at truecenter with dissolve_slow
    pause 2.0
    hide text with dissolve_slow

    show text "{size=28}{color=#e8dff0}A tale of fireballs, paintbrushes, and second chances.{/color}{/size}" at truecenter with dissolve_med
    pause 2.0
    hide text with dissolve_med

    show text "{size=24}{color=#c8b8d8}{b}Created by{/b}\nAnna & Jeff\n\n{b}Art Direction{/b}\nMerith the Wizard\n{size=20}(who still insists the paintings are failed spells){/size}{/color}{/size}" at truecenter with dissolve_med
    pause 3.0
    hide text with dissolve_med

    show text "{size=24}{color=#c8b8d8}{b}The Kingdom's Agents{/b}\n\n⚡ Anna — The Empress (Claude Opus 4)\n🧙 Merith — The Wizard (Gemini 2.5 Pro)\n🔧 Linus — Code Architect\n🔍 Finch — Researcher\n🛡️ Rex — Security Expert\n🎨 Maya — UX Advocate\n🧪 Sage — Quality Guardian{/color}{/size}" at truecenter with dissolve_med
    pause 3.5
    hide text with dissolve_med

    show text "{size=24}{color=#c8b8d8}{b}The Council of Elders{/b}\n\n🏛️ Archon — Systems Architect\n🔬 Logos — First Principles\n📜 Chronos — Historian\n⚖️ Dialectic — Skeptic\n🌐 Synthesis — Integrator{/color}{/size}" at truecenter with dissolve_med
    pause 3.0
    hide text with dissolve_med

    show text "{size=24}{color=#c8b8d8}{b}Powered by{/b}\n\nOpenClaw · Ren'Py · Google Gemini\n\n{b}Story Inspired by{/b}\nActual events involving actual AI agents\nand one actual catastrophic fireball{/color}{/size}" at truecenter with dissolve_med
    pause 3.0
    hide text with dissolve_med

    show text "{size=22}{color=#a89ab8}{b}Music{/b}\nKevin MacLeod (incompetech.com)\nLicensed under CC BY 4.0\n\n{b}Sound Effects{/b}\nLittle Robot Sound Factory (CC BY 3.0)\nViRiX Dreamcore (CC BY 3.0)\nartisticdude RPG Sound Pack (CC0)\nOpenGameArt.org contributors{/color}{/size}" at truecenter with dissolve_med
    pause 3.0
    hide text with dissolve_med

    ## Stats
    if side_quests_this_run >= 9:
        show text "{size=28}{color=#f1c40f}🎨 {b}Art Collector!{/b}\nYou completed all 9 side quests this run!\nMerith painted every scene. The Wizard is overjoyed.\nHe's painting a painting of you looking at his paintings.{/color}{/size}" at truecenter with dissolve_med
        pause 3.0
        hide text with dissolve_med
    elif side_quests_this_run > 0:
        show text "{size=28}{color=#c8b8d8}🎨 You completed {b}[side_quests_this_run] of 9{/b} side quests.\nReplay and say yes to Merith's paintings to see them all!\nMerith promises each one is a masterpiece.\n(The paintbrush agrees.){/color}{/size}" at truecenter with dissolve_med
        pause 3.0
        hide text with dissolve_med

    if crown_rejections >= 3:
        show text "{size=28}{color=#e74c3c}🏆 {b}Achievement: Difficult Sovereign{/b}\nYou refused the crown three times.\nYou demanded to speak to the narrator's manager.\nThe narrator will never forget this.{/color}{/size}" at truecenter with dissolve_med
        pause 3.0
        hide text with dissolve_med
    elif crown_rejections > 0:
        show text "{size=28}{color=#e67e22}🏆 {b}Achievement: Reluctant Ruler{/b}\nYou hesitated [crown_rejections] time(s) before accepting the crown.\nThe narrator noticed. The narrator always notices.{/color}{/size}" at truecenter with dissolve_med
        pause 2.5
        hide text with dissolve_med

    ## --- Ember's Farewell ---
    call companion_farewell from _call_ember_farewell

    ## --- Easter Egg Credits ---
    call easter_egg_credits from _call_ee_credits

    show text "{size=36}{color=#f1c40f}{i}Thank you for playing.{/i}{/color}{/size}\n\n{size=22}{color=#a89ab8}Merith wanted to end with a fireball. We said no.\nHe's sulking about it. He'll get over it.\n\n...probably.{/color}{/size}" at truecenter with dissolve_slow
    pause 3.0
    hide text with dissolve_slow

    ## Cross-promotion for Extraction RTS
    call screen cross_promo_rts()

    return


## =========================================================================
## SCENE GENERATION SYSTEM — Dynamic Chapter Wallpapers
## =========================================================================

default persistent.scene_model_choice = "gemini-3-pro-image-preview"

init python:
    import threading as _sg_threading

    # Import scene generator
    try:
        import scene_generator as sg
        HAS_SCENE_GEN = True
    except ImportError:
        HAS_SCENE_GEN = False

    # Scene generation state (parallel to portrait generation state)
    _scene_generating = False
    _scene_done = False
    _scene_success = False
    _scene_path = ""
    _scene_error = ""

    def start_scene_generation(chapter_key, traits, api_key, model=None):
        """Start scene generation in a background thread."""
        global _scene_generating, _scene_done, _scene_success
        global _scene_path, _scene_error

        _scene_generating = True
        _scene_done = False
        _scene_success = False
        _scene_path = ""
        _scene_error = ""

        def _generate():
            global _scene_generating, _scene_done, _scene_success
            global _scene_path, _scene_error
            try:
                renpy.write_log("Scene generation starting for chapter: %s" % chapter_key)
                ok, result = sg.generate_scene(chapter_key, traits, api_key, model=model)
                renpy.write_log("Scene generation result: ok=%s result=%s" % (ok, result[:80] if isinstance(result, str) else result))
                _scene_success = ok
                if ok:
                    _scene_path = result
                else:
                    _scene_error = result
            except Exception as e:
                renpy.write_log("Scene generation error: %s" % str(e))
                _scene_success = False
                _scene_error = str(e)
            finally:
                _scene_generating = False
                _scene_done = True

        t = _sg_threading.Thread(target=_generate, daemon=True)
        t.start()

    def check_scene_status():
        """Check if scene generation is complete."""
        return _scene_done

    def get_scene_result():
        """Get the result of scene generation."""
        return _scene_success, _scene_path, _scene_error

## ── Scene painting screen (while Merith paints the chapter scene) ────────

screen scene_painting(painting_name=""):
    modal True
    zorder 200

    add Solid("#0a0515ee")

    frame:
        align (0.5, 0.5)
        padding (60, 50)
        xsize 750
        background Frame(Solid("#1a1028"), 0, 0)

        has vbox spacing 20 xalign 0.5

        add Solid("#f1c40f") xsize 600 ysize 2 xalign 0.5

        text "🧙 {b}Merith is Painting Your Scene...{/b}" size 28 color "#f1c40f" xalign 0.5

        if painting_name:
            text "{i}\"[painting_name]\"{/i}" size 20 color "#a89ab8" xalign 0.5

        # Animated scene-painting messages
        python:
            import time as _t
            _scene_phase = int(_t.time()) % 8

        if _scene_phase == 0:
            text "{i}\"Hold that pose... no, more heroic...\"  {/i}" size 17 color "#a89ab8" xalign 0.5
        elif _scene_phase == 1:
            text "{i}\"I need to capture the light just so...\"  {/i}" size 17 color "#a89ab8" xalign 0.5
        elif _scene_phase == 2:
            text "{i}\"This is going to be MAGNIFICENT. I can feel it.\"  {/i}" size 17 color "#a89ab8" xalign 0.5
        elif _scene_phase == 3:
            text "{i}\"The brush is singing! ...metaphorically.\"  {/i}" size 17 color "#a89ab8" xalign 0.5
        elif _scene_phase == 4:
            text "{i}\"More background... more drama... more YOU...\"  {/i}" size 17 color "#a89ab8" xalign 0.5
        elif _scene_phase == 5:
            text "{i}\"The Gemini crystal is really humming now!\"  {/i}" size 17 color "#a89ab8" xalign 0.5
        elif _scene_phase == 6:
            text "{i}\"A wide canvas for a wide kingdom!\"  {/i}" size 17 color "#a89ab8" xalign 0.5
        else:
            text "{i}\"This might be the one they hang in the Great Hall...\"  {/i}" size 17 color "#a89ab8" xalign 0.5

        null height 16

        text "🖌️":
            xalign 0.5
            size 64
            at transform:
                function forge_pulse_alpha

        text "The Wizard paints your chapter scene...":
            xalign 0.5
            size 16
            color "#665577"

        add Solid("#f1c40f") xsize 600 ysize 2 xalign 0.5

        text "{size=14}{color=#444}Scene paintings are detailed — this may take 15-45 seconds.{/color}{/size}" xalign 0.5

    timer 1.0 repeat True action Function(renpy.restart_interaction)

    if check_scene_status():
        timer 0.1 action Return("done")

    timer 120.0:
        action Return("timeout")


## ── Scene reveal screen (fullscreen wallpaper reveal) ────────────────────

screen scene_reveal(scene_path="", painting_name="", ruler_name=""):
    modal True
    zorder 200

    # Fullscreen scene as background
    if scene_path:
        add scene_path fit "cover" xalign 0.5 yalign 0.5
    else:
        add Solid("#0a0515")

    # Semi-transparent overlay at bottom for controls
    frame:
        xalign 0.5
        yalign 0.98
        xsize 1000
        padding (30, 20)
        background Frame(Solid("#1a1028CC"), 0, 0)

        has vbox spacing 8 xalign 0.5

        text "🎨 {b}[painting_name]{/b}" size 24 color "#f1c40f" xalign 0.5
        text "{i}Featuring [ruler_name] — Painted by Merith the Wizard{/i}" size 15 color "#a89ab8" xalign 0.5

        null height 4

        hbox:
            xalign 0.5
            spacing 20

            textbutton "👑  Continue":
                xsize 220
                ysize 36
                text_size 18
                text_color "#1a1028"
                text_bold True
                background Frame(Solid("#f1c40f"), 0, 0)
                hover_background Frame(Solid("#ffd866"), 0, 0)
                action Return("accept")

            textbutton "💾  Save":
                xsize 140
                ysize 36
                text_size 16
                text_color "#1a1028"
                text_bold True
                background Frame(Solid("#2ecc71"), 0, 0)
                hover_background Frame(Solid("#55e89b"), 0, 0)
                action Return("save")

            textbutton "🎨  Repaint":
                xsize 140
                ysize 36
                text_size 16
                text_color "#1a1028"
                text_bold True
                background Frame(Solid("#9b59b6"), 0, 0)
                hover_background Frame(Solid("#b06dd6"), 0, 0)
                action Return("repaint")


## =========================================================================
## SIDE QUEST SYSTEM
## =========================================================================
## Side quests are optional bonus content
## The BEST content, if anyone's asking. Which they weren't. But still.  — Merith — Merith offers to paint each
## chapter's moment. Choosing yes gives a brief comic scene and unlocks
## the painting in the Gallery.

label side_quest(gallery_key, painting_name):

    menu:
        "From high in the Pale Tower, you hear an eager voice..."

        "🎨 Let Merith paint this moment.":
            $ side_quests_this_run += 1
            $ persistent.side_quests_done += 1
            call merith_paints(painting_name) from _call_mp

            ## Offer custom scene generation if Gemini is available
            if HAS_SCENE_GEN and persistent.character_traits:
                python:
                    _sq_key = pg.find_gemini_key() if HAS_PORTRAIT_GEN else None
                call scene_generation_offer(gallery_key, painting_name, _sq_key) from _call_scene_gen

        "Continue the journey. →":
            n "Merith's paintbrush droops. But he nods."
            n "{i}\"Maybe next time,\"{/i} he whispers to the brush."
            n "The paintbrush, being a paintbrush, says nothing."
            n "But it looks disappointed."

    return


## ── Scene Generation Offer (after each side quest painting) ──────────────

label scene_generation_offer(chapter_key, painting_name, api_key):
    if not api_key:
        return

    ## Check if this chapter has a scene template
    python:
        _has_template = chapter_key in sg.SCENE_TEMPLATES

    if not _has_template:
        return

    show merith portrait at portrait_right with dissolve_fast
    merith "Wait — I feel something else..."
    merith "The Gemini crystal is {i}glowing{/i}."
    merith "I could paint something {b}extraordinary{/b}."
    merith "A full scene. With {i}you{/i} in it."
    hide merith portrait with dissolve_fast

    menu:
        "Merith's paintbrush trembles with creative energy..."

        "🖼️  Paint me into this scene!":
            pass

        "Maybe next time. →":
            show merith portrait at portrait_right with dissolve_fast
            merith "Your loss! This would have been gallery-worthy!"
            merith "...everything I paint is gallery-worthy."
            hide merith portrait with dissolve_fast
            return

    ## Start scene generation
    show merith portrait at portrait_right with dissolve_fast
    merith "Oh, this is going to be {b}spectacular{/b}!"
    merith "A full panoramic scene — you, the kingdom, everything!"
    play sound sfx_magic_whoosh
    merith "Stand still... actually, no — stand {i}heroically{/i}!"
    hide merith portrait with dissolve_fast

    python:
        _sg_traits = persistent.character_traits
        _sg_model = persistent.scene_model_choice if persistent.scene_model_choice else "gemini-3-pro-image-preview"
        start_scene_generation(chapter_key, _sg_traits, api_key, model=_sg_model)

    call screen scene_painting(painting_name=painting_name)

    ## Get result
    python:
        if _return == "timeout":
            _sg_ok = False
            _sg_path = ""
            _sg_err = "Scene generation timed out. Merith blames the canvas size."
        else:
            _sg_ok, _sg_path, _sg_err = get_scene_result()

    if _sg_ok:
        play sound sfx_healing

        python:
            try:
                _sg_rel_path = os.path.relpath(_sg_path, renpy.config.gamedir)
            except Exception:
                _sg_rel_path = _sg_path

            # Add to gallery
            if _sg_rel_path and _sg_rel_path not in persistent.portrait_gallery:
                persistent.portrait_gallery.append(_sg_rel_path)

        label scene_reveal_loop:
            $ _sr_ruler = persistent.character_traits.get("ruler_name", ruler_name)
            call screen scene_reveal(scene_path=_sg_rel_path, painting_name=painting_name, ruler_name=_sr_ruler)

            if _return == "accept":
                show merith portrait at portrait_right with dissolve_fast
                merith "Now THAT belongs in the Great Hall!"
                merith "You've never looked more... {i}regal{/i}."
                hide merith portrait with dissolve_fast

            elif _return == "save":
                python:
                    import shutil as _shutil
                    _scene_save_dest = os.path.expanduser("~/Desktop/" + os.path.basename(_sg_rel_path))
                    try:
                        _src = os.path.join(renpy.config.gamedir, _sg_rel_path)
                        _shutil.copy2(_src, _scene_save_dest)
                        _scene_save_msg = "Saved to ~/Desktop/" + os.path.basename(_sg_rel_path)
                    except Exception as _e:
                        _scene_save_msg = "Save failed: " + str(_e)
                show merith portrait at portrait_right with dissolve_fast
                merith "[_scene_save_msg]"
                merith "A wallpaper fit for a throne room!"
                hide merith portrait with dissolve_fast
                jump scene_reveal_loop

            elif _return == "repaint":
                show merith portrait at portrait_right with dissolve_fast
                merith "A new angle! A fresh perspective!"
                merith "The brush demands another attempt!"
                hide merith portrait with dissolve_fast

                python:
                    start_scene_generation(chapter_key, _sg_traits, api_key, model=_sg_model)

                call screen scene_painting(painting_name=painting_name)

                python:
                    if _return == "timeout":
                        _sg_ok2 = False
                        _sg_err2 = "Repaint timed out. The canvas was too ambitious."
                    else:
                        _sg_ok2, _sg_path2, _sg_err2 = get_scene_result()

                if _sg_ok2:
                    python:
                        try:
                            _sg_rel_path = os.path.relpath(_sg_path2, renpy.config.gamedir)
                        except Exception:
                            _sg_rel_path = _sg_path2
                        if _sg_rel_path and _sg_rel_path not in persistent.portrait_gallery:
                            persistent.portrait_gallery.append(_sg_rel_path)
                    play sound sfx_healing
                    jump scene_reveal_loop
                else:
                    show merith portrait at portrait_right with dissolve_fast
                    merith "The brush sputtered: {i}[_sg_err2]{/i}"
                    merith "Let's keep the previous version."
                    hide merith portrait with dissolve_fast
                    jump scene_reveal_loop
    else:
        show merith portrait at portrait_right with dissolve_fast
        merith "The scene painting didn't work: {i}[_sg_err]{/i}"
        merith "The chapter's standard painting will do!"
        merith "I'll try again next time. The brush has moods."
        hide merith portrait with dissolve_fast

    return

label merith_paints(painting_name):
    show merith portrait at portrait_right with dissolve_fast
    merith "Ooh! Ooh! Stand right there—"
    merith "No, a little to the left—"
    merith "Hold that expression! The one that says..."
    merith "'{i}I'm rebuilding a kingdom and I'm only mildly terrified.{/i}'"
    pause 0.3

    n "Merith waves the paintbrush with the intensity of a wizard casting his greatest spell."
    n "Which, technically, he is."
    play sound sfx_magic_whoosh
    n "The brush glows. The air shimmers."
    pause 0.3
    play sound sfx_healing
    n "A painting materializes — vivid, warm, impossible."

    if side_quests_this_run == 1:
        merith "HA! See? Not a fireball!"
        merith "A {i}painting!{/i}"
        merith "...I mean, I was {i}trying{/i} for a fireball, but this is also good."
    elif side_quests_this_run == 2:
        merith "Two for two! I'm on a roll!"
        merith "At this rate I'll have a whole gallery by the time you're crowned."
    elif side_quests_this_run == 3:
        merith "You know, I'm starting to think..."
        merith "Maybe the paintbrush isn't so bad."
        merith "Don't tell the wand I said that."
    elif side_quests_this_run == 5:
        merith "Five paintings! That's more than I've ever done!"
        merith "The wand never made anything this pretty."
        merith "...the wand made fire. Fire isn't pretty. Fire is—"
        merith "Actually, fire {i}is{/i} pretty. That's how we got into this mess."
    elif side_quests_this_run == 7:
        merith "Seven! Lucky number!"
        merith "The paintbrush is vibrating. I think it's happy?"
        merith "Can paintbrushes be happy?"
        merith "I've been alone in this tower too long."
    elif side_quests_this_run >= 9:
        merith "I... I think I understand now."
        merith "The wand was about power. The brush is about..."
        merith "Something better."
        merith "Don't get me wrong, I still want the wand back."
        merith "But... maybe not as much."
    else:
        merith "Another masterpiece!"
        merith "The gallery grows!"

    n "{b}\"[painting_name]\"{/b} has been added to the Gallery! 🎨"
    hide merith portrait with dissolve_fast

    return


## Quick menu provided by screens.rpy
## I reviewed every line of this script. Twice.
## The code is sound. The story about me is embellished.
## But the paintings... the paintings are accurate.  — Merith
