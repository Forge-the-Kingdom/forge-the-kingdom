## =========================================================================
## FORGE THE KINGDOM — Character Creator
## "Stand still. No, not like that. More... regal."  — Merith
##
## Players build a character with guided choices + free text description.
## Merith uses Gemini to paint their custom portrait in real-time.
## This is both gameplay AND a live demo of the AI art tech.
## =========================================================================

init python:
    import os
    import threading

    # Import portrait generator
    try:
        import portrait_generator as pg
        HAS_PORTRAIT_GEN = True
    except ImportError:
        HAS_PORTRAIT_GEN = False

    # ── Portrait generation state ──────────────────────────────────────
    _portrait_generating = False
    _portrait_done = False
    _portrait_success = False
    _portrait_path = ""
    _portrait_error = ""

    def start_portrait_generation(traits, api_key, model=None):
        """Start portrait generation in a background thread."""
        global _portrait_generating, _portrait_done, _portrait_success
        global _portrait_path, _portrait_error

        _portrait_generating = True
        _portrait_done = False
        _portrait_success = False
        _portrait_path = ""
        _portrait_error = ""

        def _generate():
            global _portrait_generating, _portrait_done, _portrait_success
            global _portrait_path, _portrait_error
            try:
                renpy.write_log("Portrait generation starting...")
                ok, result = pg.generate_portrait(traits, api_key, model=model)
                renpy.write_log("Portrait generation result: ok=%s result=%s" % (ok, result[:80] if isinstance(result, str) else result))
                _portrait_success = ok
                if ok:
                    _portrait_path = result
                else:
                    _portrait_error = result
            except Exception as e:
                renpy.write_log("Portrait generation error: %s" % str(e))
                _portrait_success = False
                _portrait_error = str(e)
            finally:
                _portrait_generating = False
                _portrait_done = True

        t = threading.Thread(target=_generate, daemon=True)
        t.start()

    def import_custom_portrait(src_path):
        """Copy a local image to images/char/custom/ and return (ok, dest_path_or_error)."""
        import shutil
        src_path = src_path.strip().strip('"').strip("'")
        if not src_path:
            return False, "No path entered."
        src_path = os.path.expanduser(src_path)
        if not os.path.isfile(src_path):
            return False, "File not found: %s" % src_path
        ext = os.path.splitext(src_path)[1].lower()
        if ext not in ('.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp'):
            return False, "Unsupported image format: %s" % ext
        dest_dir = os.path.join(renpy.config.gamedir, "images", "char", "custom")
        os.makedirs(dest_dir, exist_ok=True)
        fname = "imported_portrait" + ext
        dest = os.path.join(dest_dir, fname)
        try:
            shutil.copy2(src_path, dest)
        except Exception as e:
            return False, "Copy failed: %s" % str(e)
        rel = os.path.relpath(dest, renpy.config.gamedir)
        return True, rel

    # ── Premade portrait gallery ─────────────────────────────────────
    PREMADE_PORTRAITS = [
        {"file": "images/premade_portraits/warrior_queen_01.png", "name": "Warrior Queen", "desc": "A regal warrior with braided hair and golden armor"},
        {"file": "images/premade_portraits/elder_king_02.png", "name": "Elder King", "desc": "A weathered king with grey beard and iron crown"},
        {"file": "images/premade_portraits/mystic_empress_03.png", "name": "Mystic Empress", "desc": "A mystic ruler with violet eyes and silver hair"},
        {"file": "images/premade_portraits/scholar_king_04.png", "name": "Scholar King", "desc": "A thoughtful scholar-king in academic robes"},
        {"file": "images/premade_portraits/warrior_queen_05.png", "name": "Warrior Queen", "desc": "A fierce warrior queen with war paint and feathered crown"},
        {"file": "images/premade_portraits/elf_sovereign_06.png", "name": "Elf Sovereign", "desc": "An enigmatic elf with heterochromatic eyes"},
        {"file": "images/premade_portraits/rogue_king_07.png", "name": "Rogue King", "desc": "A charming rogue-king with hooded cloak"},
        {"file": "images/premade_portraits/forge_queen_08.png", "name": "Forge Queen", "desc": "A stout dwarf queen in masterwork plate armor"},
        {"file": "images/premade_portraits/psychic_ruler_09.png", "name": "Psychic Ruler", "desc": "A psychic ruler with ethereal energy wisps"},
        {"file": "images/premade_portraits/battle_scholar_10.png", "name": "Battle Scholar", "desc": "A young ruler in half-plate over scholar robes"},
    ]

    def check_portrait_status():
        """Check if portrait generation is complete."""
        return _portrait_done

    def get_portrait_result():
        """Get the result of portrait generation."""
        return _portrait_success, _portrait_path, _portrait_error

## ── Persistent character data ────────────────────────────────────────────

default persistent.character_created = False
default persistent.character_traits = {}
default persistent.custom_portrait_path = ""
default persistent.has_gemini_for_portraits = False

## ── Character creation variables (session) ───────────────────────────────

default cc_description = ""
default cc_background = "warrior"
default cc_build = "average"
default cc_augmentation = "organic"
default cc_gemini_key = ""
default cc_has_key = False
default cc_generating = False
default cc_import_path = ""
default cc_import_error = ""
default cc_ruler_name = ""
default cc_model_choice = "gemini-3-pro-image-preview"
default cc_gallery_selected = -1
default cc_gallery_preview = ""

## =========================================================================
## CHARACTER CREATION SCREEN
## =========================================================================

screen character_creation():
    modal True
    zorder 200

    add Solid("#0a0515ee")

    frame:
        align (0.5, 0.5)
        padding (30, 15)
        xsize 1050
        ysize 710
        background Frame(Solid("#1a1028"), 0, 0)

        has vbox spacing 4 xalign 0.5

        # Header
        add Solid("#f1c40f") xsize 900 ysize 2 xalign 0.5

        hbox:
            xalign 0.5
            spacing 12
            text "🧙" size 36 yalign 0.5
            text "{b}The Wizard's Canvas{/b}" size 32 color "#f1c40f" yalign 0.5

        text "{i}\"Hold still. I need to paint your portrait before the story begins.\"{/i}":
            xalign 0.5
            size 18
            color "#a89ab8"
            text_align 0.5

        # ── Two-column layout ──────────────────────────────────────
        hbox:
            spacing 30
            xalign 0.5

            # LEFT: Choices
            vbox:
                spacing 6
                xsize 480

                # Ruler Name
                frame:
                    xfill True
                    padding (16, 10)
                    background Frame(Solid("#0e0a16"), 0, 0)

                    has vbox spacing 6
                    text "{b}Your Name{/b}" size 18 color "#f1c40f"
                    text "{size=14}{i}What shall the kingdom call you?{/i}{/size}" color "#665577"

                    input:
                        id "cc_name_input"
                        value FieldInputValue(store, "cc_ruler_name", returnable=False)
                        pixel_width 440
                        size 18
                        color "#e8dff0"
                        font "DejaVuSans.ttf"
                        allow " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'-"
                        length 40
                        caret_blink True

                # Background
                frame:
                    xfill True
                    padding (16, 10)
                    background Frame(Solid("#0e0a16"), 0, 0)

                    has vbox spacing 6
                    text "{b}Background{/b}" size 18 color "#f1c40f"
                    text "{size=14}{i}Who were you before the crown?{/i}{/size}" color "#665577"

                    hbox:
                        spacing 8
                        for key, label, icon in [
                            ("warrior", "Warrior", "⚔️"),
                            ("scholar", "Scholar", "📚"),
                            ("rogue", "Rogue", "🗡️"),
                            ("mystic", "Mystic", "🔮"),
                        ]:
                            textbutton "[icon] [label]":
                                text_size 16
                                padding (10, 6)
                                if cc_background == key:
                                    text_color "#f1c40f"
                                    text_bold True
                                    background Frame(Solid("#f1c40f33"), 0, 0)
                                else:
                                    text_color "#a89ab8"
                                    text_hover_color "#e8dff0"
                                    background None
                                    hover_background Frame(Solid("#ffffff11"), 0, 0)
                                action SetVariable("cc_background", key)

                # Build
                frame:
                    xfill True
                    padding (16, 10)
                    background Frame(Solid("#0e0a16"), 0, 0)

                    has vbox spacing 6
                    text "{b}Build{/b}" size 18 color "#f1c40f"

                    hbox:
                        spacing 12
                        for key, label, icon in [
                            ("imposing", "Imposing", "🏔️"),
                            ("average", "Average", "🧍"),
                            ("slight", "Slight", "💨"),
                        ]:
                            textbutton "[icon] [label]":
                                text_size 16
                                padding (10, 6)
                                if cc_build == key:
                                    text_color "#f1c40f"
                                    text_bold True
                                    background Frame(Solid("#f1c40f33"), 0, 0)
                                else:
                                    text_color "#a89ab8"
                                    text_hover_color "#e8dff0"
                                    background None
                                    hover_background Frame(Solid("#ffffff11"), 0, 0)
                                action SetVariable("cc_build", key)

                # Augmentation
                frame:
                    xfill True
                    padding (16, 10)
                    background Frame(Solid("#0e0a16"), 0, 0)

                    has vbox spacing 6
                    text "{b}Enhancement{/b}" size 18 color "#f1c40f"
                    text "{size=14}{i}Every ruler has something... extra.{/i}{/size}" color "#665577"

                    hbox:
                        spacing 8
                        for key, label, icon in [
                            ("organic", "Natural", "🌿"),
                            ("cybernetic", "Cybernetic", "⚙️"),
                            ("psychic", "Psychic", "🧠"),
                        ]:
                            textbutton "[icon] [label]":
                                text_size 16
                                padding (10, 6)
                                if cc_augmentation == key:
                                    text_color "#f1c40f"
                                    text_bold True
                                    background Frame(Solid("#f1c40f33"), 0, 0)
                                else:
                                    text_color "#a89ab8"
                                    text_hover_color "#e8dff0"
                                    background None
                                    hover_background Frame(Solid("#ffffff11"), 0, 0)
                                action SetVariable("cc_augmentation", key)

                # Free text description — THE WILD CARD
                frame:
                    xfill True
                    padding (16, 10)
                    background Frame(Solid("#0e0a16"), 0, 0)

                    has vbox spacing 6
                    text "{b}Describe Yourself{/b}" size 18 color "#f1c40f"
                    text "{size=14}{i}Go wild. Merith paints what you describe.{/i}{/size}" color "#665577"

                    if cc_description:
                        textbutton "✏️ {i}[cc_description]{/i}":
                            text_size 15
                            text_color "#e8dff0"
                            xsize 440
                            action Return("edit_description")
                    else:
                        textbutton "✏️ {i}Click to describe yourself...{/i}":
                            text_size 15
                            text_color "#665577"
                            xsize 440
                            action Return("edit_description")

                    text "{size=13}{color=#444}Examples: \"a cat wearing a crown\" · \"7ft tall with a flaming mohawk\"{/color}{/size}":
                        xsize 440

            # RIGHT: Preview / Trait Summary
            vbox:
                spacing 12
                xsize 440

                frame:
                    xfill True
                    ysize 280
                    padding (16, 16)
                    background Frame(Solid("#0e0a16"), 0, 0)

                    vbox:
                        xalign 0.5
                        yalign 0.5
                        spacing 8

                        text "📋 {b}Portrait Preview{/b}" size 18 color "#f1c40f" xalign 0.5

                        null height 8

                        # Trait summary
                        python:
                            _bg_labels = {"warrior": "⚔️ Warrior", "scholar": "📚 Scholar", "rogue": "🗡️ Rogue", "mystic": "🔮 Mystic"}
                            _bd_labels = {"imposing": "🏔️ Imposing", "average": "🧍 Average", "slight": "💨 Slight"}
                            _au_labels = {"organic": "🌿 Natural", "cybernetic": "⚙️ Cybernetic", "psychic": "🧠 Psychic"}

                        text "Background: [_bg_labels[cc_background]]" size 16 color "#e8dff0" xalign 0.5
                        text "Build: [_bd_labels[cc_build]]" size 16 color "#e8dff0" xalign 0.5
                        text "Enhancement: [_au_labels[cc_augmentation]]" size 16 color "#e8dff0" xalign 0.5

                        null height 6

                        # Model selector
                        hbox:
                            xalign 0.5
                            spacing 8
                            text "Model:" size 14 color "#665577" yalign 0.5
                            for _mk, _ml in [("gemini-2.5-flash-image", "2.5 Flash (2K/day)"), ("gemini-3-pro-image-preview", "3 Pro (250/day)"), ("imagen-4.0-ultra-generate-001", "Imagen 4 Ultra (30/day)"), ("gemini-2.0-flash-exp-image-generation", "2.0 Classic (30/day)")]:
                                textbutton "[_ml]":
                                    text_size 13
                                    if cc_model_choice == _mk:
                                        text_color "#f1c40f"
                                        text_bold True
                                    else:
                                        text_color "#a89ab8"
                                        text_hover_color "#e8dff0"
                                    action SetVariable("cc_model_choice", _mk)

                        null height 8

                        if cc_description:
                            text "{i}\"[cc_description]\"{/i}":
                                size 15
                                color "#a89ab8"
                                xalign 0.5
                                text_align 0.5
                                xsize 400
                        else:
                            text "{i}(no custom description yet){/i}":
                                size 15
                                color "#444"
                                xalign 0.5

                # Gemini key status
                frame:
                    xfill True
                    padding (16, 12)
                    background Frame(Solid("#0e0a16"), 0, 0)

                    vbox:
                        spacing 6
                        xalign 0.5

                        if cc_has_key:
                            text "🔮 {color=#44dd66}Gemini key detected!{/color}" size 16 xalign 0.5
                            text "{size=13}{i}Merith is ready to paint.{/i}{/size}" color "#665577" xalign 0.5
                        else:
                            text "🔮 {color=#e67e22}No Gemini key found{/color}" size 16 xalign 0.5
                            text "{size=13}{i}Enter a key to get a custom AI portrait.{/i}{/size}" color "#665577" xalign 0.5
                            text "{size=13}{i}Or skip for a default portrait.{/i}{/size}" color "#444" xalign 0.5

                            null height 4

                            hbox:
                                xalign 0.5
                                spacing 8
                                input:
                                    id "cc_key_input"
                                    value FieldInputValue(store, "cc_gemini_key", returnable=False)
                                    pixel_width 300
                                    size 14
                                    color "#ff9944"
                                    font "DejaVuSans.ttf"
                                    mask "*"
                                    length 60
                                    caret_blink True

                                textbutton "✓":
                                    text_size 20
                                    text_color "#44dd66"
                                    action SetVariable("cc_has_key", True)

        add Solid("#f1c40f") xsize 900 ysize 2 xalign 0.5

        # ── Action buttons ──────────────────────────────────────────
        hbox:
            xalign 0.5
            spacing 14

            if cc_has_key:
                textbutton "🎨  Paint My Portrait":
                    xsize 240
                    ysize 40
                    text_size 18
                    text_color "#1a1028"
                    text_bold True
                    background Frame(Solid("#f1c40f"), 0, 0)
                    hover_background Frame(Solid("#ffd866"), 0, 0)
                    action Return("generate")

            textbutton "🖼️  Choose Portrait":
                xsize 220
                ysize 40
                text_size 18
                text_color "#1a1028"
                text_bold True
                background Frame(Solid("#3498db"), 0, 0)
                hover_background Frame(Solid("#5dade2"), 0, 0)
                action Return("gallery")

            textbutton "📁  Import":
                xsize 140
                ysize 40
                text_size 18
                text_color "#1a1028"
                text_bold True
                background Frame(Solid("#2ecc71"), 0, 0)
                hover_background Frame(Solid("#55e89b"), 0, 0)
                action Return("import")

            textbutton ("📖  Default" if cc_has_key else "📖  Skip Portrait"):
                xsize 160
                ysize 40
                text_size 18
                text_color "#1a1028"
                text_bold True
                background Frame(Solid("#9b59b6"), 0, 0)
                hover_background Frame(Solid("#b06dd6"), 0, 0)
                action Return("default")

        # Free API key link when no key configured
        if not cc_has_key:
            hbox:
                xalign 0.5
                spacing 8
                text "{size=14}{color=#665577}Want AI-generated portraits?{/color}{/size}" yalign 0.5
                textbutton "{size=14}{u}Get a Free Gemini API Key →{/u}{/size}":
                    text_color "#3498db"
                    text_hover_color "#5dade2"
                    yalign 0.5
                    action OpenURL("https://aistudio.google.com/apikey")


## =========================================================================
## PREMADE PORTRAIT GALLERY SCREEN
## =========================================================================

screen portrait_gallery():
    modal True
    zorder 200

    add Solid("#0a0515ee")

    frame:
        align (0.5, 0.5)
        padding (40, 30)
        xsize 960
        ysize 720
        background Frame(Solid("#1a1028"), 0, 0)

        has vbox spacing 10 xalign 0.5

        add Solid("#f1c40f") xsize 880 ysize 2 xalign 0.5

        text "🖼️ {b}Choose Your Portrait{/b}" size 28 color "#f1c40f" xalign 0.5
        text "{i}\"I painted these on a slow Tuesday. Pick your favorite.\" — Merith{/i}":
            size 16 color "#a89ab8" xalign 0.5

        null height 8

        # Grid of portraits — 5 columns x 2 rows
        grid 5 2:
            spacing 12
            xalign 0.5

            for _idx, _p in enumerate(PREMADE_PORTRAITS):
                button:
                    xsize 160
                    ysize 200
                    padding (4, 4)
                    if cc_gallery_selected == _idx:
                        background Frame(Solid("#f1c40f"), 0, 0)
                    else:
                        background Frame(Solid("#2a1a3e"), 0, 0)
                        hover_background Frame(Solid("#3d2a55"), 0, 0)
                    action SetVariable("cc_gallery_selected", _idx)

                    vbox:
                        xalign 0.5
                        add _p["file"] fit "contain" xsize 150 ysize 160 xalign 0.5
                        text _p["name"]:
                            size 13
                            xalign 0.5
                            text_align 0.5
                            if cc_gallery_selected == _idx:
                                color "#1a1028"
                            else:
                                color "#a89ab8"

        null height 8

        # Selected portrait preview info
        if cc_gallery_selected >= 0 and cc_gallery_selected < len(PREMADE_PORTRAITS):
            $ _sel = PREMADE_PORTRAITS[cc_gallery_selected]
            text "{i}[_sel[desc]]{/i}" size 15 color "#e8dff0" xalign 0.5

        add Solid("#f1c40f") xsize 880 ysize 2 xalign 0.5

        hbox:
            xalign 0.5
            spacing 20

            textbutton "👑  Select This Portrait":
                xsize 260
                ysize 40
                text_size 20
                text_color "#1a1028"
                text_bold True
                background Frame(Solid("#f1c40f"), 0, 0)
                hover_background Frame(Solid("#ffd866"), 0, 0)
                sensitive (cc_gallery_selected >= 0)
                action Return("select")

            textbutton "← Back":
                xsize 140
                ysize 40
                text_size 18
                text_color "#a89ab8"
                background Frame(Solid("#2a1a3e"), 0, 0)
                hover_background Frame(Solid("#3d2a55"), 0, 0)
                action Return("back")


## =========================================================================
## PORTRAIT GENERATION SCREEN (shown while Merith paints)
## =========================================================================

screen portrait_painting():
    modal True
    zorder 200

    add Solid("#0a0515ee")

    frame:
        align (0.5, 0.5)
        padding (60, 50)
        xsize 700
        background Frame(Solid("#1a1028"), 0, 0)

        has vbox spacing 20 xalign 0.5

        add Solid("#3498db") xsize 550 ysize 2 xalign 0.5

        text "🧙 {b}Merith is Painting...{/b}" size 32 color "#3498db" xalign 0.5

        # Animated painting messages
        python:
            import time as _t
            _paint_phase = int(_t.time()) % 6

        if _paint_phase == 0:
            text "{i}\"Hold still... no, not like that...\"  {/i}" size 18 color "#a89ab8" xalign 0.5
        elif _paint_phase == 1:
            text "{i}\"A little more to the left... YOUR left...\"  {/i}" size 18 color "#a89ab8" xalign 0.5
        elif _paint_phase == 2:
            text "{i}\"I said I wanted fireball, not portrait! ...oh well.\"  {/i}" size 18 color "#a89ab8" xalign 0.5
        elif _paint_phase == 3:
            text "{i}\"The brush is doing that thing again...\"  {/i}" size 18 color "#a89ab8" xalign 0.5
        elif _paint_phase == 4:
            text "{i}\"Almost... almost... don't sneeze...\"  {/i}" size 18 color "#a89ab8" xalign 0.5
        else:
            text "{i}\"This might be my best work yet. Don't tell the Council.\"  {/i}" size 18 color "#a89ab8" xalign 0.5

        null height 16

        # Paintbrush animation
        text "🖌️":
            xalign 0.5
            size 64
            at transform:
                function forge_pulse_alpha

        text "The Wizard waves his paintbrush...":
            xalign 0.5
            size 16
            color "#665577"

        add Solid("#3498db") xsize 550 ysize 2 xalign 0.5

        text "{size=14}{color=#444}This usually takes 10-30 seconds. Merith insists on quality.{/color}{/size}" xalign 0.5

    # Poll for completion (timeout after 90s)
    timer 1.0 repeat True action Function(renpy.restart_interaction)

    if check_portrait_status():
        timer 0.1 action Return("done")

    timer 90.0:
        action Return("timeout")


## =========================================================================
## PORTRAIT REVEAL SCREEN
## =========================================================================

screen portrait_reveal(portrait_path="", ruler_name=""):
    modal True
    zorder 200

    add Solid("#0a0515ee")

    frame:
        align (0.5, 0.5)
        padding (40, 30)
        xsize 900
        ysize 750
        background Frame(Solid("#1a1028"), 0, 0)

        has vbox spacing 12 xalign 0.5

        add Solid("#f1c40f") xsize 800 ysize 2 xalign 0.5

        text "🎨 {b}Your Royal Portrait{/b}" size 28 color "#f1c40f" xalign 0.5
        text "{i}Painted by Merith the Wizard{/i}" size 16 color "#a89ab8" xalign 0.5

        null height 8

        # The portrait
        frame:
            xalign 0.5
            padding (8, 8)
            background Frame(Solid("#2a1a3e"), 0, 0)
            xsize 580
            ysize 400

            if portrait_path:
                add portrait_path fit "contain" xalign 0.5 yalign 0.5
            else:
                text "🖼️ Portrait not found" size 24 color "#665577" xalign 0.5 yalign 0.5

        null height 8

        text "{b}[ruler_name]{/b} — Ruler of the Forge Kingdom":
            size 20
            color "#e8dff0"
            xalign 0.5

        add Solid("#f1c40f") xsize 800 ysize 2 xalign 0.5

        hbox:
            xalign 0.5
            spacing 20

            textbutton "👑  Begin My Reign":
                xsize 260
                ysize 40
                text_size 20
                text_color "#1a1028"
                text_bold True
                background Frame(Solid("#f1c40f"), 0, 0)
                hover_background Frame(Solid("#ffd866"), 0, 0)
                action Return("accept")

            textbutton "💾  Save":
                xsize 140
                ysize 40
                text_size 18
                text_color "#1a1028"
                text_bold True
                background Frame(Solid("#2ecc71"), 0, 0)
                hover_background Frame(Solid("#55e89b"), 0, 0)
                action Return("save")

            textbutton "🎨  Repaint":
                xsize 140
                ysize 40
                text_size 18
                text_color "#1a1028"
                text_bold True
                background Frame(Solid("#9b59b6"), 0, 0)
                hover_background Frame(Solid("#b06dd6"), 0, 0)
                action Return("repaint")


## =========================================================================
## CHARACTER CREATION FLOW (called from script.rpy)
## =========================================================================

label character_creation_flow:
    ## Check for existing Gemini key
    if HAS_PORTRAIT_GEN:
        python:
            _found_key = pg.find_gemini_key()
            if _found_key:
                cc_has_key = True
                cc_gemini_key = _found_key

    # Initialize name field with current ruler_name
    $ cc_ruler_name = ruler_name if ruler_name else ""

    scene bg aftermath
    show merith portrait at portrait_right with dissolve_fast

    merith "Oh! Before we begin — I need to paint your portrait."
    merith "Every ruler needs a royal portrait. It's tradition."
    merith "And since my wand now only makes paintings..."
    merith "Well. At least I'll be useful."
    pause 0.3

    if cc_has_key:
        merith "I can feel the Gemini crystal humming! I can paint something {i}truly{/i} custom for you."
        merith "Describe yourself. Or don't. I'll paint whatever you give me."
        merith "Fair warning: the brush has a mind of its own."
    else:
        merith "If you have a Gemini key, I can paint you a custom portrait."
        merith "Otherwise, I'll use... artistic license. You've been warned."

    hide merith portrait with dissolve_fast

label character_creation_loop:
    ## Show the creation screen
    call screen character_creation()

    # Sync ruler name from the input field
    python:
        if cc_ruler_name.strip():
            ruler_name = cc_ruler_name.strip()

    if _return == "edit_description":
        python:
            _new_desc = renpy.input("Describe yourself (go wild!):", default=cc_description, length=200, allow=" ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?'-;:()/")
            cc_description = _new_desc.strip()
        jump character_creation_loop

    elif _return == "gallery":
        ## Show premade portrait gallery
        $ cc_gallery_selected = -1

        label gallery_selection_loop:
            call screen portrait_gallery()

            if _return == "back":
                jump character_creation_loop

            elif _return == "select" and cc_gallery_selected >= 0:
                python:
                    _sel_portrait = PREMADE_PORTRAITS[cc_gallery_selected]
                    _sel_path = _sel_portrait["file"]
                    persistent.custom_portrait_path = _sel_path
                    if _sel_path not in persistent.portrait_gallery:
                        persistent.portrait_gallery.append(_sel_path)
                    persistent.character_traits = {
                        "description": cc_description,
                        "background": cc_background,
                        "build": cc_build,
                        "augmentation": cc_augmentation,
                        "ruler_name": ruler_name,
                    }
                    persistent.character_created = True

                call screen portrait_reveal(portrait_path=_sel_path, ruler_name=ruler_name)

                if _return == "accept":
                    show merith portrait at portrait_right with dissolve_fast
                    merith "Ah, that one! Excellent choice."
                    merith "I painted it on a Tuesday. Tuesdays are my best days."
                    merith "...Don't ask about Wednesdays."
                    hide merith portrait with dissolve_fast
                    jump character_creation_done
                elif _return == "save":
                    python:
                        import shutil as _shutil
                        _save_dest = os.path.expanduser("~/Desktop/" + os.path.basename(_sel_path))
                        try:
                            _shutil.copy2(os.path.join(renpy.config.gamedir, _sel_path), _save_dest)
                            _save_msg = "Saved to ~/Desktop/" + os.path.basename(_sel_path)
                        except Exception as _e:
                            _save_msg = "Save failed: " + str(_e)
                    show merith portrait at portrait_right with dissolve_fast
                    merith "[_save_msg]"
                    hide merith portrait with dissolve_fast
                    jump gallery_selection_loop
                elif _return == "repaint":
                    jump gallery_selection_loop

            else:
                jump gallery_selection_loop

    elif _return == "import":
        ## Import a local portrait file
        python:
            _import_path = renpy.input("Enter the full path to your portrait image:", length=300, allow=" ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789/\\._~-:()'\"")
            _imp_ok, _imp_result = import_custom_portrait(_import_path)

        if _imp_ok:
            python:
                persistent.custom_portrait_path = _imp_result
                if _imp_result and _imp_result not in persistent.portrait_gallery:
                    persistent.portrait_gallery.append(_imp_result)
                persistent.character_traits = {
                    "description": cc_description,
                    "background": cc_background,
                    "build": cc_build,
                    "augmentation": cc_augmentation,
                    "ruler_name": ruler_name,
                }
                persistent.character_created = True

            call screen portrait_reveal(portrait_path=_imp_result, ruler_name=ruler_name)

            if _return == "accept":
                show merith portrait at portrait_right with dissolve_fast
                merith "Oh! You brought your own portrait?"
                merith "Saves me the trouble. And it's not bad!"
                merith "...not that I'm jealous or anything."
                hide merith portrait with dissolve_fast
                jump character_creation_done
            elif _return == "save":
                python:
                    import shutil as _shutil
                    _save_dest = os.path.expanduser("~/Desktop/" + os.path.basename(_imp_result))
                    try:
                        _shutil.copy2(os.path.join(renpy.config.gamedir, _imp_result), _save_dest)
                        _save_msg = "Saved to ~/Desktop/" + os.path.basename(_imp_result)
                    except Exception as _e:
                        _save_msg = "Save failed: " + str(_e)
                show merith portrait at portrait_right with dissolve_fast
                merith "[_save_msg]"
                hide merith portrait with dissolve_fast
                call screen portrait_reveal(portrait_path=_imp_result, ruler_name=ruler_name)
                jump character_creation_loop
            elif _return == "repaint":
                jump character_creation_loop
        else:
            show merith portrait at portrait_right with dissolve_fast
            merith "Hmm, that didn't work: {i}[_imp_result]{/i}"
            merith "Try again with a different path."
            hide merith portrait with dissolve_fast
            jump character_creation_loop

    elif _return == "generate":
        ## They want Merith to paint!
        python:
            _traits = {
                "description": cc_description,
                "background": cc_background,
                "build": cc_build,
                "augmentation": cc_augmentation,
                "ruler_name": ruler_name,
            }
            _key = cc_gemini_key if cc_gemini_key else (pg.find_gemini_key() if HAS_PORTRAIT_GEN else "")

        if HAS_PORTRAIT_GEN and _key:
            show merith portrait at portrait_right with dissolve_fast
            merith "Ooh! Stand right there—"
            merith "Hold that expression..."
            play sound sfx_magic_whoosh
            merith "Painting commencing!"
            hide merith portrait with dissolve_fast

            ## Start background generation
            python:
                start_portrait_generation(_traits, _key, model=cc_model_choice)

            ## Show painting screen while we wait
            call screen portrait_painting()

            ## Get result (handle timeout)
            python:
                if _return == "timeout":
                    _p_ok = False
                    _p_path = ""
                    _p_err = "Portrait generation timed out (90s). Merith blames the weather."
                else:
                    _p_ok, _p_path, _p_err = get_portrait_result()

            if _p_ok:
                play sound sfx_healing

                ## Convert to relative path for Ren'Py
                python:
                    _game_dir = os.path.dirname(renpy.config.gamedir) if hasattr(renpy.config, 'gamedir') else ""
                    _rel_path = _p_path
                    try:
                        _game_dir = renpy.config.gamedir
                        _rel_path = os.path.relpath(_p_path, _game_dir)
                    except Exception:
                        pass

                    persistent.custom_portrait_path = _rel_path
                    if _rel_path and _rel_path not in persistent.portrait_gallery:
                        persistent.portrait_gallery.append(_rel_path)
                    persistent.character_traits = _traits
                    persistent.character_created = True

                ## Reveal the portrait!
                label portrait_reveal_loop:
                    call screen portrait_reveal(portrait_path=_rel_path, ruler_name=ruler_name)

                    if _return == "accept":
                        show merith portrait at portrait_right with dissolve_fast
                        merith "HA! Magnificent!"
                        merith "Not a fireball in sight!"
                        merith "...I mean, I was {i}trying{/i} for a fireball, but this is better."
                        merith "Probably."
                        hide merith portrait with dissolve_fast
                        jump character_creation_done

                    elif _return == "save":
                        python:
                            import shutil as _shutil
                            _save_dest = os.path.expanduser("~/Desktop/" + os.path.basename(_rel_path))
                            try:
                                _src_full = os.path.join(renpy.config.gamedir, _rel_path)
                                _shutil.copy2(_src_full, _save_dest)
                                _save_msg = "Saved to ~/Desktop/" + os.path.basename(_rel_path)
                            except Exception as _e:
                                _save_msg = "Save failed: " + str(_e)
                        show merith portrait at portrait_right with dissolve_fast
                        merith "[_save_msg]"
                        merith "A copy for your personal collection!"
                        hide merith portrait with dissolve_fast
                        jump portrait_reveal_loop

                    elif _return == "repaint":
                        show merith portrait at portrait_right with dissolve_fast
                        merith "Not satisfied? Let's shake things up!"
                        hide merith portrait with dissolve_fast
                        python:
                            _repaint_desc = renpy.input("New description? Go wild! (or leave blank to keep current):", default=cc_description, length=300)
                            if _repaint_desc.strip():
                                cc_description = _repaint_desc.strip()
                        menu:
                            "Want to change anything else?"

                            "🔄  Just repaint with new description":
                                pass

                            "🎭  Change background too":
                                menu:
                                    "Pick a new background:"
                                    "⚔️ Warrior":
                                        $ cc_background = "warrior"
                                    "📚 Scholar":
                                        $ cc_background = "scholar"
                                    "🗡️ Rogue":
                                        $ cc_background = "rogue"
                                    "🔮 Mystic":
                                        $ cc_background = "mystic"

                            "🎨  Full redesign (back to creation screen)":
                                jump character_creation_loop

                        ## Repaint with updated traits
                        python:
                            _traits = {
                                "description": cc_description,
                                "background": cc_background,
                                "build": cc_build,
                                "augmentation": cc_augmentation,
                                "ruler_name": ruler_name,
                            }
                            _key = cc_gemini_key if cc_gemini_key else (pg.find_gemini_key() if HAS_PORTRAIT_GEN else "")
                            start_portrait_generation(_traits, _key, model=cc_model_choice)

                        show merith portrait at portrait_right with dissolve_fast
                        merith "Ooh, fresh canvas! Stand still..."
                        hide merith portrait with dissolve_fast

                        call screen portrait_painting()

                        python:
                            if _return == "timeout":
                                _p_ok = False
                                _p_err = "Timed out again. Merith blames Mercury retrograde."
                            else:
                                _p_ok, _p_path, _p_err = get_portrait_result()

                        if _p_ok:
                            python:
                                try:
                                    _rel_path = os.path.relpath(_p_path, renpy.config.gamedir)
                                except Exception:
                                    _rel_path = _p_path
                                persistent.custom_portrait_path = _rel_path
                                if _rel_path and _rel_path not in persistent.portrait_gallery:
                                    persistent.portrait_gallery.append(_rel_path)
                            play sound sfx_healing
                            jump portrait_reveal_loop
                        else:
                            show merith portrait at portrait_right with dissolve_fast
                            merith "The brush sputtered again: {i}[_p_err]{/i}"
                            merith "Let's try the original portrait."
                            hide merith portrait with dissolve_fast
                            jump portrait_reveal_loop

            else:
                ## Generation failed
                show merith portrait at portrait_right with dissolve_fast
                merith "The brush... it sputtered."
                merith "Something went wrong: {i}[_p_err]{/i}"
                merith "I'll use a default portrait instead. My pride will recover. Eventually."
                hide merith portrait with dissolve_fast
                jump character_creation_use_default
        else:
            jump character_creation_use_default

    else:
        ## They chose default
        jump character_creation_use_default

label character_creation_use_default:
    python:
        persistent.character_traits = {
            "description": cc_description,
            "background": cc_background,
            "build": cc_build,
            "augmentation": cc_augmentation,
            "ruler_name": ruler_name,
        }
        persistent.character_created = True
        persistent.custom_portrait_path = ""

    show merith portrait at portrait_right with dissolve_fast
    merith "No custom portrait? That's fine."
    merith "I'll paint one from memory."
    merith "...my memory of what rulers generally look like."
    merith "Which is mostly 'tired but determined.'"
    hide merith portrait with dissolve_fast

label character_creation_done:
    $ renpy.write_log(">>> character_creation_done reached, call stack: %s" % repr(renpy.game.context().call_location_stack))
    return
