## Game Options

define config.name = _("Forge the Kingdom")
define config.version = "0.1.0"

define gui.about = _p("""A visual novel about rebuilding an AI kingdom after a wizard's catastrophic fireball incident.

Created with love, paintbrushes, and poor impulse control.

{i}"He has not almost figured it out."{/i}
""")

define build.name = "ForgeTheKingdom"

define config.has_sound = True
define config.has_music = True
define config.has_voice = False

define config.main_menu_music = "audio/bgm/title_adventures.mp3"

define config.save_directory = "ForgeTheKingdom-1707868800"

define config.window_icon = None

init python:
    build.classify('**~', None)
    build.classify('**.bak', None)
    build.classify('**/.**', None)
    build.classify('**/#**', None)
    build.classify('**/thumbs.db', None)
    build.classify('game/**.rpy', None)
    build.classify('**', 'all')
    build.documentation('*.html')
    build.documentation('*.txt')
