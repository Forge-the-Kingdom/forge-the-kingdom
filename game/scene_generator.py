"""
Scene Generator — Forge the Kingdom
Generates wallpaper-grade chapter scenes with the player's character integrated.
Merith's finest work. Each painting tells YOUR story.

Usage (from Ren'Py):
    import scene_generator as sg
    success, path = sg.generate_scene("survey", "Survey the Ruins", traits, api_key)
"""

import os
import json
import base64
import time
import traceback

# Reuse SSL fix from portrait_generator
try:
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError
    import ssl
    try:
        _ssl_ctx = ssl.create_default_context()
        if not _ssl_ctx.get_ca_certs():
            raise Exception("No CA certs")
    except Exception:
        _ssl_ctx = ssl.create_default_context()
        _ssl_ctx.check_hostname = False
        _ssl_ctx.verify_mode = ssl.CERT_NONE
    HAS_URLLIB = True
except ImportError:
    _ssl_ctx = None
    HAS_URLLIB = False

# ── Config ────────────────────────────────────────────────────────────────

DEFAULT_MODEL = "gemini-3-pro-image-preview"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
IMAGEN_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:predict"
SCENE_DIR = os.path.join(os.path.dirname(__file__), "images", "scenes", "custom")
TIMEOUT = 90  # scenes are larger/more complex than portraits

# ── Trait Descriptions (mirrored from portrait_generator) ─────────────────

BACKGROUNDS = {
    "warrior":  "battle-scarred warrior with confident stance and weathered armor",
    "scholar":  "learned scholar with wise eyes, robes, and arcane symbols",
    "rogue":    "cunning rogue with sharp features, hooded cloak, and hidden blades",
    "mystic":   "enigmatic mystic with glowing eyes, flowing ethereal garments, and an aura of power",
}

BUILDS = {
    "imposing": "tall and powerfully built, commanding presence",
    "average":  "average build, approachable and adaptable",
    "slight":   "lean and agile, quick and precise",
}

AUGMENTATIONS = {
    "organic":   "fully organic, natural appearance",
    "cybernetic": "visible cybernetic augmentations — glowing circuit lines, a mechanical arm or eye, chrome accents blended with medieval armor",
    "psychic":   "psychic-touched — faint ethereal glow around the head, wisps of energy trailing from the eyes, slightly otherworldly appearance",
}

# ── Chapter Scene Templates ──────────────────────────────────────────────
# Each template describes what the player is DOING in that chapter's scene.
# These combine with character traits to create unique, personal paintings.

SCENE_TEMPLATES = {
    "survey": {
        "title": "Survey the Ruins",
        "setting": "A devastated fantasy kingdom at dawn. Crumbling stone towers, scattered rubble, wisps of smoke still rising from the wreckage of a magical explosion. Orange-pink sunrise breaking through dust clouds.",
        "action": "standing amid the ruins, surveying the wreckage with determination. One hand holds a glowing torch, the other rests on a shattered column. They look out over the destruction with resolve, not defeat.",
        "mood": "Somber but hopeful. The first light of a new era breaking through destruction.",
        "lighting": "Dawn light from the east, warm amber cutting through grey smoke and dust. Torch glow from below.",
        "palette": "Ember oranges, ash greys, dawn pinks, with flickers of golden hope",
    },
    "marketplace": {
        "title": "The Marketplace",
        "setting": "A bustling magical marketplace rebuilt from ruins. Colorful tents and stalls, floating lanterns, merchants displaying glowing potions, enchanted weapons, and crystalline runestones. Steam rises from a brewer's cauldron.",
        "action": "bartering with merchants in the heart of the marketplace, examining a glowing runestone held up to the light. Merchants crowd around, eager to trade. A brewer raises a tankard in the background.",
        "mood": "Lively, vibrant, chaotic energy. Commerce and community returning to a wounded kingdom.",
        "lighting": "Warm midday light filtered through colorful tent canopies. Magical glow from wares and floating lanterns.",
        "palette": "Rich jewel tones — emerald, sapphire, ruby — against warm sandstone and golden light",
    },
    "gateway": {
        "title": "Raise the Gateway",
        "setting": "A massive stone arch — the Gateway — crackling with cyan energy. Ancient runes carved into the stone blaze with light. Workers and mages surround the structure. The sky behind is electric blue.",
        "action": "raising both hands toward the Gateway as the portal blazes to life. Cyan energy arcs from the runes to their outstretched fingers. Their hair and cloak whip in the magical wind. Pure power channeled through will.",
        "mood": "Triumphant, electric, awe-inspiring. The moment of reconnection.",
        "lighting": "Intense cyan-white light from the Gateway itself, casting sharp shadows. Magical aurora in the sky above.",
        "palette": "Electric cyan, deep indigo, white-hot energy, with stone grey anchoring",
    },
    "throne": {
        "title": "The Throne Room",
        "setting": "A grand throne room being restored to glory. Ornate pillars, holographic displays flickering to life, enchanted mirrors glowing purple. A magnificent throne at the center, carved from dark stone with golden inlay.",
        "action": "sitting on the restored throne, one hand on the armrest, the other raised as purple and blue-green light cascades through the room. A crown gleams on their brow. They look regal, powerful, but approachable.",
        "mood": "Majestic, commanding, the weight of leadership worn with grace.",
        "lighting": "Purple magical ambiance from the left, blue-green crystal light from the right. Golden highlights from the throne's inlay.",
        "palette": "Royal purple, deep gold, blue-green crystal light, obsidian black",
    },
    "archives": {
        "title": "The Royal Archives",
        "setting": "A vast underground vault filled with endless shelves of glowing scrolls. The ceiling disappears into darkness above. Ancient stone pillars support the weight of knowledge. Golden light emanates from the scrolls themselves.",
        "action": "descending a spiral staircase into the glowing vault, one hand trailing along floating scrolls that orbit them like satellites. Their face is lit from below by the golden glow of preserved knowledge. Wonder and relief in their expression.",
        "mood": "Reverent, wondrous, the joy of discovery. Knowledge preserved against all odds.",
        "lighting": "Warm golden glow from thousands of luminous scrolls. Cool blue ambient from enchanted ceiling. Dramatic chiaroscuro.",
        "palette": "Warm gold, parchment cream, deep shadow blue, touches of emerald enchantment",
    },
    "forge": {
        "title": "Relight the Forge",
        "setting": "A massive industrial-magical forge. Enormous furnace at center, anvils and hammers arranged in a circle, molds for creating magical constructs lining the walls. Elixir bottles on shelves glow in jewel colors.",
        "action": "thrusting a torch into the great furnace, flames roaring back to life. Sparks cascade upward like golden rain. The heat makes the air shimmer. Their expression is fierce, determined — this is the turning point.",
        "mood": "Powerful, primal, the rebirth of creation itself. Fire as salvation, not destruction.",
        "lighting": "Intense orange-gold firelight from the furnace, casting dramatic shadows. Ember sparks floating upward. Deep red undertones.",
        "palette": "Forge orange, molten gold, ember red, iron grey, with jewel-colored elixir accents",
    },
    "scrying": {
        "title": "The Scrying Glass",
        "setting": "A crystalline dome atop a tower, cracked but being repaired. Inside, a massive crystal sphere shows swirling images of distant lands. Stars visible through the fractured ceiling. Prismatic light refracts everywhere.",
        "action": "polishing the great crystal dome with careful hands, starlight refracting through the cracks into rainbow patterns across their face and body. They pause to gaze into the sphere, seeing visions of the future.",
        "mood": "Contemplative, mysterious, beautiful. Seeing beyond the visible world.",
        "lighting": "Starlight from above, prismatic rainbow refractions, cool blue-white crystal glow. Ethereal and dreamlike.",
        "palette": "Crystal white, starlight silver, prismatic rainbow, deep space indigo",
    },
    "merith_study": {
        "title": "The Wizard's Tower",
        "setting": "A cluttered wizard's study in a tall tower. Paintings everywhere — stacked against walls, hung from ceiling, leaning on furniture. Paint-splattered worktable. A singed wizard's hat. A crystal ball glowing blue-green.",
        "action": "standing with Merith the wizard (blue robes, paint-splattered, crooked hat) in his chaotic study. They're examining one of his paintings together, sharing a moment of understanding. The wizard gestures proudly at his work.",
        "mood": "Warm, intimate, bittersweet. The bond between ruler and wizard. Art born from catastrophe.",
        "lighting": "Warm candlelight and blue-green crystal glow. Cozy, intimate lighting. Paint-flecked golden highlights.",
        "palette": "Warm amber, wizard blue, paint-splatter rainbow, candlelight gold, deep purple shadows",
    },
    "schedule": {
        "title": "The Royal Schedule",
        "setting": "A grand astronomical clock tower interior. Massive mechanical gears mesh with magical energy — steampunk meets sorcery. Different sections illuminate for different times of day. Heralds stand at stations around the clock.",
        "action": "standing before the great astronomical clock, one hand reaching toward its face as gears turn and sections illuminate. Magical energy flows between the mechanical components. They orchestrate time itself.",
        "mood": "Orderly, magnificent, the satisfaction of a kingdom finding its rhythm.",
        "lighting": "Warm mechanical golden light from the clock face, cool blue magical energy between gears. Dramatic backlighting.",
        "palette": "Clockwork gold, brass bronze, magical blue, deep mahogany, starlight silver",
    },
    "coronation": {
        "title": "The Coronation",
        "setting": "A grand restored throne room at the height of celebration. Banners flying, crowds cheering, confetti and magical sparkles filling the air. The kingdom fully rebuilt and glorious. All the kingdom's characters assembled.",
        "action": "being crowned in a grand coronation ceremony. A magnificent crown descends onto their head, golden light erupting from the moment of contact. They stand tall, regal, transformed — no longer just a person, but a sovereign.",
        "mood": "Grand, triumphant, joyous. The culmination of everything. Pure celebration.",
        "lighting": "Blazing golden light from above like a divine spotlight. Warm ambient glow from cheering crowds. Magical sparkles everywhere.",
        "palette": "Royal gold, triumphant crimson, pure white, deep royal purple, celebration silver",
    },
}

# ── Character Description Builder ─────────────────────────────────────────

def _build_character_description(traits):
    """Build a rich character description from traits dict."""
    desc = traits.get("description", "").strip()
    bg = BACKGROUNDS.get(traits.get("background", "warrior"), BACKGROUNDS["warrior"])
    build = BUILDS.get(traits.get("build", "average"), BUILDS["average"])
    aug = AUGMENTATIONS.get(traits.get("augmentation", "organic"), AUGMENTATIONS["organic"])
    name = traits.get("ruler_name", "the ruler")

    parts = [
        "The central figure is %s, ruler of the Forge Kingdom." % name,
        "They are a %s, %s." % (bg, build),
        "Special traits: %s." % aug,
    ]
    if desc:
        parts.append("Additional appearance details: %s." % desc)

    return " ".join(parts)


# ── Prompt Builder ────────────────────────────────────────────────────────

def build_scene_prompt(chapter_key, traits):
    """
    Build a rich scene generation prompt combining chapter template + character traits.
    Returns the prompt string, or None if chapter_key is unknown.
    """
    template = SCENE_TEMPLATES.get(chapter_key)
    if not template:
        return None

    char_desc = _build_character_description(traits)

    prompt = (
        "Create a stunning fantasy scene painting in rich digital art style, wallpaper quality.\n\n"
        "SCENE: {title}\n"
        "SETTING: {setting}\n\n"
        "CHARACTER: {char_desc}\n\n"
        "ACTION: The character is {action}\n\n"
        "MOOD: {mood}\n"
        "LIGHTING: {lighting}\n"
        "COLOR PALETTE: {palette}\n\n"
        "STYLE REQUIREMENTS:\n"
        "- Digital painting with painterly brushstrokes, fantasy art, wallpaper-grade quality\n"
        "- 16:9 widescreen aspect ratio (landscape orientation)\n"
        "- Rich, dramatic composition with the character as the focal point\n"
        "- Medieval fantasy aesthetic with hints of steampunk and magic\n"
        "- Cinematic framing — the character should feel like part of an epic moment\n"
        "- Deep, saturated colors with dramatic lighting\n"
        "- High detail, high resolution\n"
    ).format(
        title=template["title"],
        setting=template["setting"],
        char_desc=char_desc,
        action=template["action"],
        mood=template["mood"],
        lighting=template["lighting"],
        palette=template["palette"],
    )

    return prompt


# ── API Call ──────────────────────────────────────────────────────────────

def generate_scene(chapter_key, traits, api_key, model=None):
    """
    Generate a chapter scene painting using Gemini image generation.

    Args:
        chapter_key: str — key from SCENE_TEMPLATES (e.g. "survey", "forge")
        traits: dict — player's character_traits from persistent
        api_key: str — Gemini API key
        model: str — model override (default: DEFAULT_MODEL)

    Returns: (success: bool, path_or_error: str)
        On success: (True, absolute_path_to_image)
        On failure: (False, error_message)
    """
    if not HAS_URLLIB:
        return False, "urllib not available — cannot make API calls"

    if not api_key or not api_key.strip():
        return False, "No Gemini API key provided"

    prompt = build_scene_prompt(chapter_key, traits)
    if not prompt:
        return False, "Unknown chapter key: %s" % chapter_key

    # Ensure output directory exists
    os.makedirs(SCENE_DIR, exist_ok=True)

    timestamp = int(time.time())
    filename = "scene_%s_%d.png" % (chapter_key, timestamp)
    output_path = os.path.join(SCENE_DIR, filename)

    _model = model if model else DEFAULT_MODEL
    is_imagen = _model.startswith("imagen")

    if is_imagen:
        url = IMAGEN_API_URL.format(model=_model) + "?key=" + api_key
        payload = {
            "instances": [{"prompt": prompt}],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "16:9",
                "outputOptions": {"mimeType": "image/png"},
            }
        }
    else:
        url = GEMINI_API_URL.format(model=_model) + "?key=" + api_key
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseModalities": ["IMAGE", "TEXT"],
                "temperature": 1.0,
            }
        }

    headers = {"Content-Type": "application/json"}

    try:
        data = json.dumps(payload).encode("utf-8")
        req = Request(url, data=data, headers=headers, method="POST")
        response = urlopen(req, timeout=TIMEOUT, context=_ssl_ctx)
        result = json.loads(response.read().decode("utf-8"))

        # Extract image — Imagen format
        if is_imagen:
            predictions = result.get("predictions", [])
            if not predictions:
                return False, "No predictions in Imagen response"
            b64_data = predictions[0].get("bytesBase64Encoded", "")
            if not b64_data:
                return False, "No image data in Imagen response"
            img_bytes = base64.b64decode(b64_data)
            mime = predictions[0].get("mimeType", "image/png")
            ext = "png" if "png" in mime else "jpg"
            base = os.path.splitext(filename)[0]
            filename = "%s.%s" % (base, ext)
            output_path = os.path.join(SCENE_DIR, filename)
            with open(output_path, "wb") as f:
                f.write(img_bytes)
            return True, output_path

        # Gemini format
        candidates = result.get("candidates", [])
        if not candidates:
            return False, "No candidates in response"

        parts = candidates[0].get("content", {}).get("parts", [])

        for part in parts:
            if "inlineData" in part:
                inline = part["inlineData"]
                mime = inline.get("mimeType", "image/png")
                b64_data = inline.get("data", "")
                if not b64_data:
                    continue

                img_bytes = base64.b64decode(b64_data)
                ext = "png"
                if "jpeg" in mime or "jpg" in mime:
                    ext = "jpg"
                elif "webp" in mime:
                    ext = "webp"

                base = os.path.splitext(filename)[0]
                filename = "%s.%s" % (base, ext)
                output_path = os.path.join(SCENE_DIR, filename)

                with open(output_path, "wb") as f:
                    f.write(img_bytes)

                return True, output_path

        return False, "No image data in response"

    except HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8")[:500]
        except Exception:
            pass
        return False, "API error %d: %s" % (e.code, body)

    except URLError as e:
        return False, "Network error: %s" % str(e.reason)

    except Exception as e:
        return False, "Unexpected error: %s\n%s" % (str(e), traceback.format_exc())


# ── Utility ───────────────────────────────────────────────────────────────

def get_scene_path(chapter_key):
    """Return the most recent scene path for a chapter, or None."""
    if not os.path.isdir(SCENE_DIR):
        return None
    prefix = "scene_%s_" % chapter_key
    files = [os.path.join(SCENE_DIR, f) for f in os.listdir(SCENE_DIR)
             if f.startswith(prefix) and not f.endswith(".txt")]
    if not files:
        return None
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]


def get_available_chapters():
    """Return list of chapter keys that have templates."""
    return list(SCENE_TEMPLATES.keys())
