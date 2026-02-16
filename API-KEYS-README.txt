╔══════════════════════════════════════════════════════════════╗
║        FORGE THE KINGDOM — Setup Instructions                 ║
╚══════════════════════════════════════════════════════════════╝

This game has two paths:

  🎮 "Play the Story" — Experience the visual novel with
     AI-generated portraits and scenes. Requires a Gemini key.

  🏰 "Forge a REAL Kingdom" — Play the story AND install a
     fully-featured AI Kingdom on your machine with autonomous
     agents, security systems, and more. Requires BOTH keys.


STEP 1: Get Your API Keys
─────────────────────────

  Google Gemini (REQUIRED — powers all image generation):
    → https://aistudio.google.com/apikey
    → Sign in with Google → "Create API Key" → Copy it
    → FREE tier: 250 images/day — more than enough
    → Cost: $0

  Anthropic Claude (REQUIRED for "Forge a REAL Kingdom"):
    → TWO ways to get a key:
    
    Option A: Claude Pro/Max subscription (recommended if you already have one)
      → https://claude.ai → Settings → API Keys → Create Key → Copy it
      → Works with Pro ($20/mo) or Max ($100/mo) subscriptions
    
    Option B: Pay-as-you-go API account
      → https://console.anthropic.com/
      → Sign up → Set up billing → API Keys → Create Key → Copy it
      → Cost: ~$3/MTok input, ~$15/MTok output (you control spend)
      → Recommended: Set a monthly spending limit in Settings
    
    → Both key types work — they start with "sk-ant-"
    → If you only want to play the story, you can skip this


STEP 2: Add Keys to the Config File
────────────────────────────────────
  Open this file in any text editor (Notepad, TextEdit, etc.):

    game/api-keys.conf

  Paste your keys after the = sign:

    GEMINI_API_KEY=paste-your-gemini-key-here
    ANTHROPIC_API_KEY=paste-your-anthropic-key-here

  Save the file. That's it.


STEP 3: Launch the Game
───────────────────────
  Windows:  Double-click ForgeTheKingdom.exe
  Mac:      Double-click ForgeTheKingdom.app
  Linux:    Run ./ForgeTheKingdom.sh


WHAT YOU GET (Forge a REAL Kingdom path)
────────────────────────────────────────
  By the end of the story, your machine will have:

  • OpenClaw — AI agent orchestration platform
  • 12 autonomous AI agents — each with their own personality,
    workspace, and capabilities
  • The Articles of Cooperation — a governance framework for
    human-AI collaboration
  • Security systems (Knights & Watchtowers)
  • A Discord server with agent presence (optional)
  • Automated monitoring, daily briefings, and more

  Everything runs locally on YOUR machine. You own it all.


SECURITY
────────
  • Your keys stay on YOUR computer — never sent anywhere
    except directly to the API services (Anthropic/Google)
  • Never share the api-keys.conf file
  • Never post your keys online
  • To revoke access, delete api-keys.conf or regenerate
    your keys at the provider's console
  • Set spending limits on your Anthropic account:
    https://console.anthropic.com/settings/limits


TROUBLESHOOTING
───────────────
  "No portraits/scenes generating"
    → Check that api-keys.conf has your Gemini key filled in
    → Make sure there are no extra spaces around the key

  "Kingdom installation failed"
    → Check that your Anthropic key is valid and has billing set up
    → Make sure you have Node.js installed (https://nodejs.org)
    → Check your internet connection during installation

  "Key not working"
    → Verify at https://aistudio.google.com/apikey (Gemini)
    → Verify at https://console.anthropic.com/settings (Anthropic)

  The story mode works with ONLY a Gemini key.
  The full Kingdom requires both keys + Node.js.


Questions? Join us: https://discord.gg/VvemtKmE
