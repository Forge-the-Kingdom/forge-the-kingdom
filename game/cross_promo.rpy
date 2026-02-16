## =========================================================================
## CROSS-PROMOTION — Forge the Kingdom: Extraction RTS
## Shows a tasteful promo screen after credits
## Update the URL below when the real itch.io page is live
## =========================================================================

## The RTS itch.io URL — update this with the real link!
define EXTRACTION_RTS_URL = "https://YOURUSERNAME.itch.io/forge-the-kingdom-rts"

screen cross_promo_rts():
    modal True
    zorder 200

    frame:
        xfill True
        yfill True
        background "#0d0618ee"

        vbox:
            align (0.5, 0.5)
            spacing 16
            xmaximum 700

            text "⚔️" size 64 xalign 0.5
            null height 8

            text "{b}The kingdom is rebuilt.\nNow defend it.{/b}" size 28 color "#f1c40f" xalign 0.5 text_align 0.5
            null height 4

            text "Design units you're afraid to lose.\nSend them into hostile territory.\nExtract resources — or lose everything." size 18 color "#a89ab8" xalign 0.5 text_align 0.5 line_spacing 4
            null height 16

            text "{b}Forge the Kingdom: Extraction{/b}" size 22 color "#e8dff0" xalign 0.5
            text "An Extraction RTS — $5 on itch.io" size 16 color "#a89ab8" xalign 0.5
            null height 20

            hbox:
                xalign 0.5
                spacing 20

                textbutton "⚔️  Check It Out":
                    xsize 220
                    ysize 44
                    text_size 18
                    text_color "#1a0a2e"
                    text_bold True
                    background Frame(Solid("#f1c40f"), 0, 0)
                    hover_background Frame(Solid("#ffd866"), 0, 0)
                    action [OpenURL(EXTRACTION_RTS_URL), Return("opened")]

                textbutton "Maybe Later":
                    xsize 160
                    ysize 44
                    text_size 16
                    text_color "#a89ab8"
                    background Frame(Solid("#2a1245"), 0, 0)
                    hover_background Frame(Solid("#3a1a5e"), 0, 0)
                    action Return("skip")
