#!/usr/bin/env python3
"""Render the Adv360 ZMK keymap as a single self-contained HTML page.

Usage: gen_keymap.py            writes keymap-viewer/keymap.html
Reads: config/adv360.keymap (layer include order), config/layers/*.dtsi,
       config/macros.dtsi (display names), config/info.json (geometry).
python3 stdlib only. Ported from ~/workspace/projects/corne_4_1/gen_keymap.py.
"""
import html
import json
import os
import re
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CONFIG = os.path.join(ROOT, "config")
U = 56  # px per key unit

# ---------------------------------------------------------------- geometry
# Thumb clusters, measured from assets/key-positions.png (the definitive
# diagram): position -> (center_x, center_y, w, h, rotation_deg), key units.
# info.json's thumb pivots put the clusters too far inboard, so override them.
THUMBS = {
    35: (7.00, 5.00, 1, 1, 15), 36: (7.97, 5.25, 1, 1, 15),
    52: (7.70, 6.20, 1, 1, 15), 67: (7.46, 7.18, 1, 1, 15),
    66: (6.64, 6.44, 1, 2, 15), 65: (5.67, 6.17, 1, 2, 15),
    37: (9.90, 5.25, 1, 1, -15), 38: (10.90, 5.00, 1, 1, -15),
    53: (10.20, 6.20, 1, 1, -15), 68: (10.40, 7.18, 1, 1, -15),
    69: (11.30, 6.44, 1, 2, -15), 70: (12.20, 6.17, 1, 2, -15),
}


# Stock Kinesis keycap legends for the six inner-column keys. Kinesis docs refer to
# these ("Mod + Hotkey 1 = left bootloader"), so show them as a corner badge on every
# layer. Verified against the user manual: Hotkey 1/3 = bootloader L/R (pos 20/21),
# Hotkey 4 = battery (pos 39).
STOCK_CAPS = {6: "Kp", 7: "Mod", 20: "①", 34: "②", 21: "③", 39: "④"}


def load_geometry():
    """-> list indexed by ZMK position 0..75 of (x, y, w, h, rotation_deg).
    Main keys come from config/info.json (listed in position order); rotation
    is about the key's own center."""
    info = json.load(open(os.path.join(CONFIG, "info.json")))
    keys = info["layouts"]["LAYOUT"]["layout"]
    geo = []
    for pos, k in enumerate(keys):
        if pos in THUMBS:
            cx, cy, w, h, r = THUMBS[pos]
            geo.append((cx - w / 2, cy - h / 2, w, h, r))
        else:
            geo.append((k["x"], k["y"], k.get("w", 1), k.get("h", 1), 0))
    return geo


# ---------------------------------------------------------------- parsing
def strip_comments(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return re.sub(r"//[^\n]*", "", s)


def parse_layers():
    """-> [(display_name, [binding, ...] * 76)] in layer-index order."""
    src = strip_comments(open(os.path.join(CONFIG, "adv360.keymap")).read())
    layers = []
    for inc in re.findall(r'#include\s+"(layers/[^"]+\.dtsi)"', src):
        text = strip_comments(open(os.path.join(CONFIG, inc)).read())
        m = re.search(r'display-name\s*=\s*"([^"]*)"', text)
        name = m.group(1) if m else os.path.basename(inc)[:-5]
        m = re.search(r"bindings\s*=\s*<(.*?)>\s*;", text, re.S)
        toks = m.group(1).split()
        binds, cur = [], None
        for t in toks:
            if t.startswith("&"):
                if cur:
                    binds.append(cur)
                cur = [t[1:]]
            else:
                cur.append(t)
        if cur:
            binds.append(cur)
        layers.append((name, binds))
    return layers


def parse_macro_names():
    """behavior node name -> display-name, from macros.dtsi."""
    text = strip_comments(open(os.path.join(CONFIG, "macros.dtsi")).read())
    names = {}
    for m in re.finditer(r"^\s*(\w+):\s*\w+\s*\{(.*?)^\s*\};", text, re.S | re.M):
        d = re.search(r'display-name\s*=\s*"([^"]*)"', m.group(2))
        if d:
            names[m.group(1)] = d.group(1)
    return names


# ---------------------------------------------------------------- legends
PLAIN = {
    "EQUAL": "=", "MINUS": "-", "BSPC": "Bksp", "BACKSPACE": "Bksp", "TAB": "Tab",
    "ESC": "Esc", "ESCAPE": "Esc", "SQT": "'", "APOS": "'", "GRAVE": "`",
    "PSCRN": "PrtSc", "LEFT": "←", "RIGHT": "→", "UP": "↑", "DOWN": "↓",
    "LEFT_ARROW": "←", "RIGHT_ARROW": "→", "UP_ARROW": "↑", "DOWN_ARROW": "↓",
    "HOME": "Home", "END": "End", "PG_UP": "PgUp", "PG_DN": "PgDn",
    "ENTER": "Enter", "RET": "Enter", "SPACE": "Space", "DEL": "Del", "DELETE": "Del",
    "LBKT": "[", "RBKT": "]", "LBRC": "{", "RBRC": "}", "COMMA": ",", "DOT": ".",
    "PERIOD": ".", "FSLH": "/", "SLASH": "/", "BSLH": "\\", "BACKSLASH": "\\",
    "SEMI": ";", "SEMICOLON": ";", "COLON": ":", "DQT": '"',
    "EXCL": "!", "AT": "@", "HASH": "#", "DOLLAR": "$", "DLLR": "$", "PERCENT": "%",
    "PRCNT": "%", "CARET": "^", "AMPS": "&", "STAR": "*", "ASTRK": "*",
    "LPAR": "(", "RPAR": ")", "UNDERSCORE": "_", "UNDER": "_", "PLUS": "+",
    "LT": "<", "GT": ">", "QMARK": "?", "QUESTION": "?", "PIPE": "|", "TILDE": "~",
    "CAPS": "Caps", "CAPSLOCK": "Caps",
    "LSHFT": "Shift", "LSHIFT": "Shift", "RSHFT": "Shift", "RSHIFT": "Shift",
    "LCTRL": "Ctrl", "RCTRL": "Ctrl", "LALT": "Opt", "RALT": "Opt",
    "LGUI": "Cmd", "RGUI": "Cmd", "LCMD": "Cmd", "RCMD": "Cmd",
    "C_VOL_UP": "Vol+", "C_VOL_DN": "Vol−", "C_MUTE": "Mute", "C_PP": "⏯",
    "C_NEXT": "⏭", "C_PREV": "⏮",
    "KP_NUM": "Num", "KP_NUMLOCK": "Num", "KP_EQUAL": "=", "KP_DIVIDE": "/",
    "KP_SLASH": "/", "KP_MULTIPLY": "*", "KP_ASTERISK": "*", "KP_MINUS": "-",
    "KP_PLUS": "+", "KP_ENTER": "Enter", "KP_DOT": ".", "KP_COMMA": ",",
}
SHIFTED = {"N1": "!", "N2": "@", "N3": "#", "N4": "$", "N5": "%", "N6": "^",
           "N7": "&", "N8": "*", "N9": "(", "N0": ")", "GRAVE": "~", "MINUS": "_",
           "EQUAL": "+", "LBKT": "{", "RBKT": "}", "BSLH": "|", "SEMI": ":",
           "SQT": '"', "COMMA": "<", "DOT": ">", "FSLH": "?"}
MODSYM = {"LALT": "⌥", "RALT": "⌥", "LCTRL": "⌃", "RCTRL": "⌃",
          "LGUI": "⌘", "RGUI": "⌘", "LSHFT": "⇧", "RSHFT": "⇧",
          "LCMD": "⌘", "RCMD": "⌘"}
MODFN = {"LS": "⇧", "RS": "⇧", "LC": "⌃", "RC": "⌃", "LA": "⌥", "RA": "⌥",
         "LG": "⌘", "RG": "⌘"}


def keycode(kc):
    """ZMK keycode (possibly wrapped in LS()/LC()/...) -> label."""
    m = re.fullmatch(r"(L[SCAG]|R[SCAG])\((.*)\)", kc)
    if m:
        mod, inner = m.group(1), m.group(2)
        if mod in ("LS", "RS") and not re.fullmatch(r"[LR][SCAG]\(.*\)", inner):
            if inner in SHIFTED:
                return SHIFTED[inner]
            if len(inner) == 1 and inner.isalpha():
                return inner
        return MODFN[mod] + keycode(inner)
    m = re.fullmatch(r"(?:N|NUMBER_|KP_N|KP_NUMBER_)(\d)", kc)
    if m:
        return m.group(1)
    m = re.fullmatch(r"F(\d{1,2})", kc)
    if m:
        return kc
    if kc in PLAIN:
        return PLAIN[kc]
    if len(kc) == 1:
        return kc
    return kc.replace("_", " ").title()


def make_legend(layer_names, macro_names):
    def lname(n):
        return layer_names[int(n)] if int(n) < len(layer_names) else f"L{n}"

    def legend(b):
        """binding token list -> (tap_label, hold_label or None)"""
        beh, args = b[0], b[1:]
        if beh in ("trans", "none"):
            return ("", None)
        if beh == "kp":
            return (keycode(args[0]), None)
        if beh == "mo":
            return (lname(args[0]), "hold")
        if beh == "tog":
            return (lname(args[0]), "toggle")
        if beh == "to":
            return (lname(args[0]), "to")
        if beh == "lt":
            return (keycode(args[1]), lname(args[0]))
        if beh == "mt":
            return (keycode(args[1]), MODSYM.get(args[0], args[0]))
        if beh in ("hm_l", "hm_r"):
            return (keycode(args[1]), MODSYM.get(args[0], args[0]))
        if beh in ("shift_const_l", "shift_const_r"):
            return (lname(args[1]) + " word", MODSYM.get(args[0], args[0]))
        if beh == "voiceink_all":
            return ("Voice", "PTT · 2× Hist")
        if beh == "bt":
            if args[0] == "BT_CLR":
                return ("BT Clr", None)
            m = re.fullmatch(r"BT_SEL", args[0])
            if m:
                return (f"BT {args[1]}", None)
            return (args[0].replace("BT_", "BT "), None)
        if beh == "bootloader":
            return ("Boot", None)
        if beh == "studio_unlock":
            return ("Studio", None)
        if beh == "macro_ver":
            return ("Version", None)
        if beh == "stp":
            return ("Batt", None)
        if beh == "bl":
            return ({"BL_TOG": "BL ⏻", "BL_INC": "BL +", "BL_DEC": "BL −"}
                    .get(args[0], args[0]), None)
        if beh == "rgb_ug":
            return ({"RGB_TOG": "RGB ⏻"}.get(args[0], args[0].replace("RGB_", "RGB ")), None)
        if beh == "mkp":
            return ({"LCLK": "L Click", "RCLK": "R Click", "MCLK": "M Click"}
                    .get(args[0], args[0]), None)
        if beh in macro_names:
            return (macro_names[beh].replace("Windows ", "Win ").replace("Mac ", ""), None)
        return (beh.replace("_", " ").title(), None)
    return legend


def layer_trigger(b):
    """-> (layer_index, how) if this binding activates a layer, else None."""
    beh, args = b[0], b[1:]
    if beh in ("mo", "lt") and args:
        return (int(args[0]), "hold")
    if beh == "tog" and args:
        return (int(args[0]), "toggle")
    if beh == "to" and args:
        return (int(args[0]), "switch to")
    if beh in ("shift_const_l", "shift_const_r") and len(args) > 1:
        return (int(args[1]), "tap")
    return None


# our keycode names -> JS KeyboardEvent.code values (for live highlighting)
JSCODE = {
    "SPACE": "Space", "ENTER": "Enter", "RET": "Enter", "BSPC": "Backspace",
    "BACKSPACE": "Backspace", "ESC": "Escape", "ESCAPE": "Escape", "TAB": "Tab",
    "DEL": "Delete", "DELETE": "Delete", "GRAVE": "Backquote", "MINUS": "Minus",
    "EQUAL": "Equal", "LBKT": "BracketLeft", "RBKT": "BracketRight",
    "BSLH": "Backslash", "SEMI": "Semicolon", "SQT": "Quote", "COMMA": "Comma",
    "DOT": "Period", "FSLH": "Slash", "LEFT": "ArrowLeft", "DOWN": "ArrowDown",
    "UP": "ArrowUp", "RIGHT": "ArrowRight", "HOME": "Home", "END": "End",
    "PG_UP": "PageUp", "PG_DN": "PageDown", "CAPS": "CapsLock", "PSCRN": "PrintScreen",
    "LSHFT": "ShiftLeft", "RSHFT": "ShiftRight", "LCTRL": "ControlLeft",
    "RCTRL": "ControlRight", "LALT": "AltLeft", "RALT": "AltRight",
    "LGUI": "MetaLeft", "RGUI": "MetaRight",
    "C_VOL_UP": "AudioVolumeUp", "C_VOL_DN": "AudioVolumeDown", "C_MUTE": "AudioVolumeMute",
    "KP_NUM": "NumLock", "KP_EQUAL": "NumpadEqual", "KP_DIVIDE": "NumpadDivide",
    "KP_MULTIPLY": "NumpadMultiply", "KP_MINUS": "NumpadSubtract", "KP_PLUS": "NumpadAdd",
    "KP_ENTER": "NumpadEnter", "KP_DOT": "NumpadDecimal",
}


def jscodes(b):
    beh, args = b[0], b[1:]
    codes = []
    kc = None
    if beh == "kp":
        kc = args[0]
    elif beh in ("hm_l", "hm_r", "mt"):
        codes.append(JSCODE.get(args[0], ""))
        kc = args[1]
    elif beh == "lt":
        kc = args[1]
    elif beh in ("shift_const_l", "shift_const_r"):
        codes.append(JSCODE.get(args[0], ""))
    if kc:
        m = re.fullmatch(r"(?:L[SCAG]|R[SCAG])\((.*)\)", kc)
        while m:
            kc = m.group(1)
            m = re.fullmatch(r"(?:L[SCAG]|R[SCAG])\((.*)\)", kc)
        if len(kc) == 1 and kc.isalpha():
            codes.append("Key" + kc)
        elif re.fullmatch(r"N\d", kc):
            codes.append("Digit" + kc[1])
        elif re.fullmatch(r"KP_N\d", kc):
            codes.append("Numpad" + kc[4])
        elif re.fullmatch(r"F\d{1,2}", kc):
            codes.append(kc)
        elif kc in JSCODE:
            codes.append(JSCODE[kc])
    return [c for c in codes if c]


# ---------------------------------------------------------------- render
def render_board(geo, layers, idx, legend):
    base, layer = layers[0][1], layers[idx][1]
    keys = []
    for pos, (x, y, w, h, r) in enumerate(geo):
        b = layer[pos]
        tap, hold = legend(b)
        cls, src = "key", b
        if idx != 0 and b[0] == "trans":
            tap, hold = legend(base[pos])
            src = base[pos]
            cls += " ghost"
        elif idx != 0 and b[0] != "none":
            cls += " active"
        if not tap and not hold:
            cls += " dead"
        trig = layer_trigger(base[pos])
        if idx != 0 and trig and trig[0] == idx:
            cls += " held"
            tap, hold = "◉ " + trig[1], None
        style = (f"left:{x*U:.0f}px;top:{y*U:.0f}px;width:{w*U-6:.0f}px;"
                 f"height:{h*U-6:.0f}px")
        if r:
            style += f";transform:rotate({r}deg)"
        hold_div = f'<div class="hold">{html.escape(hold)}</div>' if hold else ""
        cap = f'<div class="cap">{STOCK_CAPS[pos]}</div>' if pos in STOCK_CAPS else ""
        codes = " ".join(jscodes(src))
        keys.append(f'<div class="{cls}" data-pos="{pos}" data-codes="{codes}" '
                    f'style="{style}" title="{html.escape(" ".join(b))}">{cap}'
                    f'<div class="tap">{html.escape(tap)}</div>{hold_div}</div>')
    return f'<div class="board">{"".join(keys)}</div>'


def render_positions(geo, layers, legend):
    """Pseudo-layer: ZMK key position number on every key, base legend below."""
    base = layers[0][1]
    keys = []
    for pos, (x, y, w, h, r) in enumerate(geo):
        tap = legend(base[pos])[0]
        style = (f"left:{x*U:.0f}px;top:{y*U:.0f}px;width:{w*U-6:.0f}px;"
                 f"height:{h*U-6:.0f}px")
        if r:
            style += f";transform:rotate({r}deg)"
        cap = f'<div class="cap">{STOCK_CAPS[pos]}</div>' if pos in STOCK_CAPS else ""
        keys.append(f'<div class="key posn" data-pos="{pos}" style="{style}">{cap}'
                    f'<div class="tap">{pos}</div>'
                    f'<div class="hold">{html.escape(tap)}</div></div>')
    return f'<div class="board">{"".join(keys)}</div>'


def main():
    geo = load_geometry()
    layers = parse_layers()
    for name, binds in layers:
        if len(binds) != len(geo):
            sys.exit(f"layer {name}: {len(binds)} bindings, expected {len(geo)}")
    layer_names = [n for n, _ in layers]
    legend = make_legend(layer_names, parse_macro_names())
    N = len(layers)

    total_w = max(x + w for x, _, w, *_ in geo)
    total_h = max(y + h for _, y, _, h, *_ in geo) + 0.35  # rotated thumbs hang low

    def trigger_note(i):
        if i == 0:
            return ""
        for pos, b in enumerate(layers[0][1]):
            trig = layer_trigger(b)
            if trig and trig[0] == i:
                return f" &middot; {trig[1]} the amber key (pos {pos})"
        return " &middot; no trigger on the base layer"

    tabs = "".join(
        f'<span class="tab" data-i="{i}" onclick="show({i})">{i+1} {html.escape(n)}</span>'
        for i, n in enumerate(layer_names))
    tabs += f'<span class="tab" data-i="{N}" onclick="show({N})">{N+1} positions</span>'
    body = "".join(
        f'<section class="panel" id="p{i}"><h2>{html.escape(n)}{trigger_note(i)}</h2>'
        f"{render_board(geo, layers, i, legend)}</section>"
        for i, n in enumerate(layer_names))
    body += (f'<section class="panel" id="p{N}"><h2>positions &middot; '
             f'ZMK key numbers, for talking about the keymap</h2>'
             f"{render_positions(geo, layers, legend)}</section>")
    N += 1  # the positions pseudo-layer is the last panel

    page = f"""<!doctype html><meta charset="utf-8">
<title>Adv360 keymap</title>
<style>
  body {{ background:#111418; color:#e6e6e6; font:14px -apple-system, sans-serif;
         margin:0; display:flex; flex-direction:column; align-items:center;
         padding:10px 14px 6px; user-select:none; }}
  nav {{ display:flex; gap:8px; margin-bottom:2px; }}
  .tab {{ padding:3px 12px; border-radius:6px; color:#7a8494; font-size:13px;
          cursor:pointer; border:1px solid transparent; }}
  .tab.on {{ color:#e8b750; border-color:#4a4434; background:#221f18; }}
  .panel {{ display:none; }}
  .panel.on {{ display:block; }}
  h2 {{ font-size:14px; font-weight:600; color:#9aa4b2; margin:8px 0 2px;
        text-align:center; }}
  .board {{ position:relative; width:{total_w*U:.0f}px; height:{total_h*U:.0f}px; }}
  .key {{ position:absolute; background:#1d2229; border:1px solid #333a45;
          border-radius:7px; display:flex; flex-direction:column;
          align-items:center; justify-content:center; gap:1px; text-align:center;
          overflow:hidden; }}
  .tap {{ font-size:15px; line-height:1.1; }}
  .hold {{ font-size:10px; color:#7fb069; }}
  .cap {{ position:absolute; top:1px; right:4px; font-size:10px; color:#8a6d2f; }}
  .dead .cap, .ghost .cap {{ color:#c9a45c; }}
  .ghost {{ opacity:.32; }}
  .active {{ background:#24313f; border-color:#3e5871; }}
  .active .tap {{ color:#8ecbff; }}
  .dead {{ opacity:.28; }}
  .dead:has(.cap) {{ opacity:.6; }}
  .held {{ background:#3a2f1d; border-color:#8a6d2f; opacity:1; }}
  .held .tap {{ color:#e8b750; font-size:11px; }}
  .posn .tap {{ color:#e8b750; font-size:16px; font-weight:600; }}
  .posn .hold {{ color:#7a8494; }}
  .press {{ background:#e8b750 !important; border-color:#ffd98a !important; opacity:1 !important; }}
  .press .tap, .press .hold {{ color:#1a1509 !important; }}
  footer {{ color:#555e6a; font-size:11px; margin-top:2px; }}
</style>
<nav>{tabs}</nav>
{body}
<footer>1-{N} / arrows / space switch &middot; 0 or P = positions &middot; Esc or Q closes &middot;
adv360.keymap &middot; {datetime.now():%Y-%m-%d %H:%M}</footer>
<script>
  const N = {N};
  let cur = 0;
  function show(i) {{
    cur = (i + N) % N;
    document.querySelectorAll(".panel").forEach((p, j) =>
      p.classList.toggle("on", j === cur));
    document.querySelectorAll(".tab").forEach((t, j) =>
      t.classList.toggle("on", j === cur));
  }}
  function fit() {{
    document.body.style.zoom = Math.min(1, innerWidth / {total_w*U+40:.0f},
                                        innerHeight / {total_h*U+120:.0f});
  }}
  addEventListener("resize", fit); fit();

  // Live key highlighting: light the key that produced this event on the
  // current panel; if it only exists on another panel, follow it there.
  const panels = [...document.querySelectorAll(".panel")];
  function matches(i, code) {{
    return panels[i].querySelectorAll(`[data-codes~="${{code}}"]`);
  }}
  addEventListener("keydown", e => {{
    if (e.key === "Escape" || e.key === "q") {{ window.close(); return; }}
    if (e.key >= "1" && e.key <= "9" && +e.key <= N) {{ show(+e.key - 1); return; }}
    if (e.key === "0" || e.key === "p") {{ show(N - 1); return; }}
    if (e.key === "ArrowRight" || e.key === " ") {{ show(cur + 1); return; }}
    if (e.key === "ArrowLeft") {{ show(cur - 1); return; }}
    e.preventDefault();
    let hits = matches(cur, e.code);
    if (!hits.length) {{
      for (let i = 0; i < N; i++) {{
        if (i !== cur && matches(i, e.code).length) {{
          show(i); hits = matches(i, e.code); break;
        }}
      }}
    }}
    hits.forEach(k => k.classList.add("press"));
  }});
  addEventListener("keyup", e => {{
    panels.forEach(p => p.querySelectorAll(`[data-codes~="${{e.code}}"]`)
      .forEach(k => k.classList.remove("press")));
  }});
  addEventListener("blur", () =>
    document.querySelectorAll(".press").forEach(k => k.classList.remove("press")));
  show(parseInt(location.hash.slice(1)) - 1 || 0);
</script>
"""
    out = os.path.join(HERE, "keymap.html")
    with open(out, "w") as f:
        f.write(page)
    print(out)


if __name__ == "__main__":
    main()
