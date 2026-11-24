#!/usr/bin/env python3
"""Render the 23 November 2026 front page of THE WORLD as a 1024x1024 PNG.

Headlines and figures follow the story list in README.md, checked against
live news on the morning of 24 November 2026 (Beijing time). The only
picture is the pre-generated hero illustration in assets/; every word on
the page is drawn here with PIL. No network access, no secrets.
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
HERO_PATH = os.path.join(
    HERE,
    "assets",
    "media-generation-hero-nvidia-return-0-d0d7d3f6-8196-428c-a4bb-95e34c3cd7d9.webp",
)
OUT_PATH = os.path.join(HERE, "entry.png")

SIZE = 1024
MARGIN = 40
CONTENT = SIZE - 2 * MARGIN
MAX_BYTES = 1_000_000

PAPER = (247, 241, 229)
INK = (17, 17, 17)
GREY = (68, 60, 52)
CRIMSON = (143, 29, 29)
DEEP_BLUE = (27, 42, 74)
WHITE = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/liberation/"


def fnt(filename, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, filename), size)


def serif_bold(size):
    return fnt("LiberationSerif-Bold.ttf", size)


def serif_plain(size):
    return fnt("LiberationSerif-Regular.ttf", size)


def serif_italic(size):
    return fnt("LiberationSerif-Italic.ttf", size)


def sans_bold(size):
    return fnt("LiberationSans-Bold.ttf", size)


def fit_font(draw, text, filename, start_size, max_width):
    size = start_size
    while size > 10:
        candidate = fnt(filename, size)
        if draw.textlength(text, font=candidate) <= max_width:
            return candidate
        size -= 2
    return fnt(filename, 10)


def wrap_lines(draw, text, font, max_width):
    lines, current = [], ""
    for word in text.split():
        attempt = (current + " " + word).strip()
        if not current or draw.textlength(attempt, font=font) <= max_width:
            current = attempt
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


class Page:
    def __init__(self):
        self.sheet = Image.new("RGB", (SIZE, SIZE), PAPER)
        self.draw = ImageDraw.Draw(self.sheet)
        self.y = 22

    def text_width(self, text, font):
        return self.draw.textlength(text, font=font)

    def centred(self, y, text, font, fill=INK):
        self.draw.text(
            (SIZE // 2 - self.text_width(text, font) / 2, y),
            text, font=font, fill=fill,
        )

    def spaced(self, y, text, font, gap, fill=INK):
        widths = [self.draw.textlength(ch, font=font) for ch in text]
        total = sum(widths) + gap * (len(text) - 1)
        x = SIZE // 2 - total / 2
        for ch, w in zip(text, widths):
            self.draw.text((x, y), ch, font=font, fill=fill)
            x += w + gap

    def hline(self, y, weight, x0=MARGIN, x1=SIZE - MARGIN):
        self.draw.line([(x0, y), (x1, y)], fill=INK, width=weight)

    def masthead(self):
        self.spaced(self.y, "ONE DAY · ONE PAGE", sans_bold(15), 6, GREY)
        self.y += 30
        title = fit_font(
            self.draw, "THE WORLD", "LiberationSerif-Bold.ttf", 118, CONTENT)
        self.centred(self.y - 14, "THE WORLD", title)
        self.y += 98
        self.hline(self.y, 3)
        self.y += 5
        self.hline(self.y, 1)
        self.y += 12
        self.centred(
            self.y, "MONDAY,  23 NOVEMBER 2026", serif_bold(30), CRIMSON)
        self.y += 42
        self.hline(self.y, 1)
        self.y += 14

    def lead(self):
        headline = "HUANG IS BACK — NVIDIA SOARS 31%"
        head_font = fit_font(
            self.draw, headline, "LiberationSerif-Bold.ttf", 56, CONTENT)
        self.centred(self.y, headline, head_font)
        self.y += 56
        deck = ("Eleven days after he resigned, the board reinstates Jensen "
                "Huang as chief executive — shares end up 31.5%, their best "
                "day since 2003, as the S&P 500 jumps 4.7%")
        deck_font = serif_plain(22)
        for line in wrap_lines(self.draw, deck, deck_font, CONTENT - 40):
            self.centred(self.y, line, deck_font)
            self.y += 26
        self.y += 8

    def hero(self):
        photo = Image.open(HERO_PATH).convert("RGB")
        ratio = CONTENT / 140
        sw, sh = photo.size
        if sw / sh > ratio:
            nw = int(sh * ratio)
            left = (sw - nw) // 2
            photo = photo.crop((left, 0, left + nw, sh))
        else:
            nh = int(sw / ratio)
            top = (sh - nh) // 2
            photo = photo.crop((0, top, sw, top + nh))
        photo = photo.resize((CONTENT, 140), Image.LANCZOS)
        self.sheet.paste(photo, (MARGIN, self.y))
        self.draw.rectangle(
            [MARGIN, self.y, SIZE - MARGIN, self.y + 140],
            outline=INK, width=1)
        self.y += 140 + 8
        self.draw.text(
            (MARGIN, self.y),
            "A chipmaker rises again: Nvidia gains $952 billion in a day as "
            "its founder returns. (Illustration)",
            font=serif_italic(16), fill=GREY)
        self.y += 14

    def ticker(self):
        height = 36
        self.draw.rectangle(
            [MARGIN, self.y, SIZE - MARGIN, self.y + height], fill=DEEP_BLUE)
        tick = ("DYMER: 11 KILLED  ·  BENGHAZI: RUSSIAN WARSHIP SUNK  ·  "
                "INDIA PLEDGES $1.62BN TO NEPAL")
        tick_font = fit_font(
            self.draw, tick, "LiberationSans-Bold.ttf", 19, CONTENT - 16)
        self.centred(self.y + 8, tick, tick_font, WHITE)
        self.y += height + 6

    def one_story(self, x, top, width, item):
        yy = top
        self.draw.text((x, yy), item["kicker"], font=sans_bold(15), fill=CRIMSON)
        yy += 22
        head_font = serif_bold(25)
        for line in wrap_lines(self.draw, item["headline"], head_font, width):
            self.draw.text((x, yy), line, font=head_font, fill=INK)
            yy += 28
        yy += 2
        body_font = serif_plain(17)
        for line in wrap_lines(self.draw, item["body"], body_font, width):
            self.draw.text((x, yy), line, font=body_font, fill=INK)
            yy += 21
        return yy + 10

    def grid(self):
        gutter = 30
        col = (CONTENT - gutter) // 2
        left_x = MARGIN
        right_x = MARGIN + col + gutter
        top = self.y

        left_column = [
            {"kicker": "UKRAINE",
             "headline": "Dymer toll rises to 11; boy pulled alive",
             "body": "Rescuers raise the toll from a Russian drone strike on "
                     "a five-storey block: a boy of 7 and a woman of 79 are "
                     "pulled alive from the rubble; Kyiv region mourns."},
            {"kicker": "LIBYA",
             "headline": "Ukraine sinks Russian corvette in Benghazi",
             "body": "Seven sea drones sink the corvette Merkury and destroy "
                     "a Ka-27 helicopter; the cargo ship Angara is hit too — "
                     "the war reaches 2,400 km from the front."},
            {"kicker": "GULF",
             "headline": "Iran says it downed a US drone",
             "body": "Tehran claims its army shot down a US LUCAS drone east "
                     "of the Strait of Hormuz and vows \"all available means\" "
                     "against the US naval blockade."},
        ]
        right_column = [
            {"kicker": "NEPAL",
             "headline": "India pledges $1.62bn to rebuild",
             "body": "Modi announces the package after talks with PM Balendra "
                     "Shah; August's glacier flood killed about 1,500 people "
                     "and left 5,200 missing."},
            {"kicker": "WASHINGTON",
             "headline": "Democrats' House haul hits 258 seats",
             "body": "Their largest majority since 1992, after Chuck Hubbard "
                     "beats Virginia Foxx in North Carolina — a gain of 44 "
                     "seats in the midterm sweep."},
            {"kicker": "MARKETS",
             "headline": "Nikkei falls over 5% as Wall Street rebounds",
             "body": "Japan's Nikkei drops more than 5% in Asian trading "
                     "while US stocks surge on the Nvidia news; the Nasdaq "
                     "ends up 6.5%."},
        ]
        yy = top
        for item in left_column:
            yy = self.one_story(left_x, yy, col, item)
        left_end = yy
        yy = top
        for item in right_column:
            yy = self.one_story(right_x, yy, col, item)
        right_end = yy
        mid = MARGIN + col + gutter // 2
        self.draw.line(
            [(mid, top), (mid, max(left_end, right_end) - 12)],
            fill=INK, width=1)
        self.y = max(left_end, right_end) + 2

    def footer(self):
        self.hline(self.y, 1)
        self.y += 10
        also = ("ALSO:   'Chapo Isidro' captured in Sinaloa  ·  EU proposes "
                "22nd sanctions package on Russia  ·  Trump calls Putin 'my "
                "friend' after Shenzhen summit")
        also_font = sans_bold(16)
        for line in wrap_lines(self.draw, also, also_font, CONTENT):
            self.centred(self.y, line, also_font)
            self.y += 22
        self.y += 2
        self.centred(
            self.y,
            "Every story above was reported on "
            "Monday 23 November 2026.",
            serif_italic(15), GREY)
        self.y += 16

    def save(self):
        assert self.y <= SIZE, f"page overflowed: cursor at {self.y}"
        self.sheet.save(OUT_PATH, format="PNG", optimize=True)
        size = os.path.getsize(OUT_PATH)
        print(f"wrote {OUT_PATH}: {SIZE}x{SIZE}, {size} bytes, "
              f"cursor ended at y={self.y}")
        if size >= MAX_BYTES:
            raise SystemExit(
                f"entry.png is {size} bytes, over the 1 MiB limit")


def main():
    page = Page()
    page.masthead()
    page.lead()
    page.hero()
    page.ticker()
    page.grid()
    page.footer()
    page.save()


if __name__ == "__main__":
    main()
