"""
Portrait Generator — Forge the Kingdom
Calls Gemini's image generation API to create custom character portraits.
Merith paints your portrait. Results may vary. He's trying his best.

Usage (from Ren'Py):
    import portrait_generator as pg
    success, path = pg.generate_portrait(traits, api_key)
"""

import os
import json
import base64
import time
import traceback

# Use urllib since requests may not be available in Ren'Py's Python
try:
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError
    import ssl
    # Ren'Py's bundled Python may not have system CA certs
    try:
        _ssl_ctx = ssl.create_default_context()
        # Test if default context works by checking it has CA certs
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

GEMINI_MODEL = "gemini-2.0-flash-exp-image-generation"
GEMINI_MODEL_25 = "gemini-2.5-flash-image"
IMAGEN_MODEL = "imagen-4.0-generate-001"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
IMAGEN_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:predict"
PORTRAIT_DIR = os.path.join(os.path.dirname(__file__), "images", "char", "custom")
TIMEOUT = 60  # seconds

# ── Trait Definitions ─────────────────────────────────────────────────────

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

# ── Prompt Builder ────────────────────────────────────────────────────────

def build_prompt(traits):
    """
    Build a Gemini image generation prompt from character traits.

    traits: dict with keys:
        - description: str (free text from player — the wild card)
        - background: str (warrior/scholar/rogue/mystic)
        - build: str (imposing/average/slight)
        - augmentation: str (organic/cybernetic/psychic)
        - ruler_name: str
    """
    desc = traits.get("description", "").strip()
    bg = BACKGROUNDS.get(traits.get("background", "warrior"), BACKGROUNDS["warrior"])
    build = BUILDS.get(traits.get("build", "average"), BUILDS["average"])
    aug = AUGMENTATIONS.get(traits.get("augmentation", "organic"), AUGMENTATIONS["organic"])
    name = traits.get("ruler_name", "the ruler")

    # Core prompt — Merith's painting style
    prompt = (
        f"Create a fantasy portrait painting in rich oil paint style. "
        f"This is a royal portrait of {name}, the new ruler of the Forge Kingdom. "
        f"Painted by a wizard named Merith who accidentally turns all his spells into art. "
        f"\n\n"
        f"Subject description: {desc}\n" if desc else ""
    )

    prompt += (
        f"Character archetype: {bg}. "
        f"Physical build: {build}. "
        f"Special traits: {aug}. "
        f"\n\n"
        f"Art style: Oil painting with visible brushstrokes, warm firelight and purple magical ambiance, "
        f"ornate golden frame border, medieval fantasy aesthetic with a hint of steampunk. "
        f"The portrait should look like it belongs in a castle gallery. "
        f"Dramatic lighting from the left. Rich colors — deep purples, warm golds, ember oranges. "
        f"The subject should look regal but approachable, like someone you'd follow into battle "
        f"or trust with your kingdom's API keys. "
        f"Portrait orientation, head and upper body, facing slightly left. "
        f"Resolution: high quality, detailed."
    )

    return prompt


# ── API Call ──────────────────────────────────────────────────────────────

def generate_portrait(traits, api_key, filename=None, model=None):
    """
    Generate a portrait using Gemini's image generation.

    Returns: (success: bool, path_or_error: str)
        On success: (True, absolute_path_to_image)
        On failure: (False, error_message)
    """
    if not HAS_URLLIB:
        return False, "urllib not available — cannot make API calls"

    if not api_key or not api_key.strip():
        return False, "No Gemini API key provided"

    # Ensure output directory exists
    os.makedirs(PORTRAIT_DIR, exist_ok=True)

    # Build filename
    if not filename:
        timestamp = int(time.time())
        filename = f"portrait_{timestamp}.png"

    output_path = os.path.join(PORTRAIT_DIR, filename)

    # Build the prompt
    prompt = build_prompt(traits)

    # Build API request
    _model = model if model else GEMINI_MODEL_25
    is_imagen = _model.startswith("imagen")

    if is_imagen:
        url = IMAGEN_API_URL.format(model=_model) + f"?key={api_key}"
        payload = {
            "instances": [
                {"prompt": prompt}
            ],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "3:4",
                "outputOptions": {"mimeType": "image/png"},
            }
        }
    else:
        url = GEMINI_API_URL.format(model=_model) + f"?key={api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "responseModalities": ["IMAGE", "TEXT"],
                "temperature": 1.0,
            }
        }

    headers = {
        "Content-Type": "application/json",
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = Request(url, data=data, headers=headers, method="POST")
        response = urlopen(req, timeout=TIMEOUT, context=_ssl_ctx)
        result = json.loads(response.read().decode("utf-8"))

        # Extract image from response — Imagen uses different format
        if is_imagen:
            predictions = result.get("predictions", [])
            if not predictions:
                return False, "No predictions in Imagen response"
            b64_data = predictions[0].get("bytesBase64Encoded", "")
            mime = predictions[0].get("mimeType", "image/png")
            if not b64_data:
                return False, "No image data in Imagen response"
            img_bytes = base64.b64decode(b64_data)
            ext = "png" if "png" in mime else "jpg"
            base = os.path.splitext(filename)[0]
            filename = f"{base}.{ext}"
            output_path = os.path.join(PORTRAIT_DIR, filename)
            with open(output_path, "wb") as f:
                f.write(img_bytes)
            return True, output_path

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

                # Decode and save
                img_bytes = base64.b64decode(b64_data)

                # Determine extension from mime
                ext = "png"
                if "jpeg" in mime or "jpg" in mime:
                    ext = "jpg"
                elif "webp" in mime:
                    ext = "webp"

                # Update filename with correct extension
                base = os.path.splitext(filename)[0]
                filename = f"{base}.{ext}"
                output_path = os.path.join(PORTRAIT_DIR, filename)

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
        return False, f"API error {e.code}: {body}"

    except URLError as e:
        return False, f"Network error: {e.reason}"

    except Exception as e:
        return False, f"Unexpected error: {str(e)}\n{traceback.format_exc()}"


# ── Key Detection ─────────────────────────────────────────────────────────

def _read_api_keys_conf():
    """Read api-keys.conf from the game directory. Returns dict of key=value pairs."""
    keys = {}
    # Look for api-keys.conf relative to this file (in game/ directory)
    conf_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "api-keys.conf"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "api-keys.conf"),
    ]
    for conf_path in conf_paths:
        try:
            with open(conf_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        v = v.strip()
                        if v:
                            keys[k.strip()] = v
        except Exception:
            pass
    return keys


def find_gemini_key():
    """
    Try to find a Gemini API key from various sources.
    Returns key string or None.
    """
    # Check api-keys.conf first (user-facing config file)
    conf = _read_api_keys_conf()
    if conf.get("GEMINI_API_KEY"):
        return conf["GEMINI_API_KEY"]

    # Check environment
    for env_var in ["GEMINI_API_KEY", "GOOGLE_API_KEY"]:
        key = os.environ.get(env_var)
        if key:
            return key

    # Check OpenClaw auth profiles
    auth_paths = [
        os.path.expanduser("~/.openclaw/auth-profiles.json"),
        os.path.expanduser("~/.openclaw/agents/wizard/workspace/../auth-profiles.json"),
    ]

    for path in auth_paths:
        try:
            with open(path, "r") as f:
                profiles = json.load(f)
            for profile in profiles if isinstance(profiles, list) else [profiles]:
                if isinstance(profile, dict):
                    if "gemini" in str(profile.get("name", "")).lower() or \
                       "google" in str(profile.get("name", "")).lower():
                        key = profile.get("key") or profile.get("apiKey") or profile.get("token")
                        if key:
                            return key
        except Exception:
            pass

    # Check ~/.gemini/settings.json
    gemini_settings = os.path.expanduser("~/.gemini/settings.json")
    try:
        with open(gemini_settings, "r") as f:
            data = json.load(f)
        key = data.get("GEMINI_API_KEY")
        if key:
            return key
    except Exception:
        pass

    # Check for key file
    key_path = os.path.expanduser("~/.forge-kingdom/gemini_key")
    try:
        with open(key_path, "r") as f:
            key = f.read().strip()
        if key:
            return key
    except Exception:
        pass

    return None


def validate_key_quick(api_key):
    """Quick validation — just checks if the key format looks right."""
    if not api_key:
        return False
    key = api_key.strip()
    # Gemini keys are typically 39 chars starting with AI
    return len(key) > 20


# ── Utility ───────────────────────────────────────────────────────────────

def get_custom_portrait_path():
    """Return the most recent custom portrait path, or None."""
    if not os.path.isdir(PORTRAIT_DIR):
        return None

    files = []
    for f in os.listdir(PORTRAIT_DIR):
        if f.startswith("portrait_") and not f.endswith(".txt"):
            files.append(os.path.join(PORTRAIT_DIR, f))

    if not files:
        return None

    # Return most recent
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]


def get_relative_portrait_path():
    """Return the portrait path relative to the game directory (for Ren'Py)."""
    full = get_custom_portrait_path()
    if not full:
        return None

    game_dir = os.path.dirname(__file__)
    try:
        rel = os.path.relpath(full, game_dir)
        return rel
    except ValueError:
        return full
