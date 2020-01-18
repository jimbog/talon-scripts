from talon import app
from talon.voice import Context, Str, press
import string
alpha_alt = ('aim bat chain drop each fine go harp inner'
    ' join cake look mark next odd put Quick rule subs til'
    ' uke viz word plex yank theta').split(' ')

f_keys = {f"F {i}": f"f{i}" for i in range(1, 13)}
# arrows are separated because 'up' has a high false positive rate
arrows = ["left", "right", "up", "down"]
simple_keys = ["tab", "escape", "enter", "space", "pageup", "pagedown"]
alternate_keys = {"delete": "backspace", "forward delete": "delete", "trim": "backspace"}
symbols = {
    "back tick": "`",
    "comma": ",",
    "point": ".",
    "period": ".",
    "semi": ";",
    "semicolon": ";",
    "quote": "'",
    "L square": "[",
    "left square": "[",
    "square": "[",
    "R square": "]",
    "right square": "]",
    "forward slash": "/",
    "slash": "/",
    "backslash": "\\",
    "minus": "-",
    "dash": "-",
    "equals": "=",
    'quotation': "'",
    'plus': '+',
    'question': '?',
    'tilde': '~',
    'bang': '!', 'exclamation point': '!', 
    'Money': '$',
    'down score': '_', 'under score': '_',
    'colon': ':',
    'paren': '(', 'L paren': '(', 'left paren': '(',
    'R paren': ')', 'right paren': ')',
    'brace': '{', 'left brace': '{',
    'R brace': '}', 'right brace': '}',
    'angle': '<', 'left angle': '<', 'less than': '<',
    'rangle': '>', 'R angle': '>', 'right angle': '>', 'greater than': '>',
    'asterisk': '*',
    'pound': '#', 'hash': '#', 'hash sign': '#', 'number sign': '#',
    'percent': '%', 'percent sign': '%',
    'caret': '^',
    'at sign': '@',
    'and sign': '&', 'ampersand': '&',
    'pipe': '|',
    'dubquote': '"', 'double quote': '"',
}
modifiers = {
    "control": "ctrl",
    "troll": "ctrl",
    "shift": "shift",
    "alt": "alt",
}
if app.platform == "mac":
    modifiers["command"] = "cmd"
    modifiers["option"] = "alt"
elif app.platform == "windows":
    modifiers["windows"] = "win"
elif app.platform == "linux":
    modifiers["super"] = "super"

alphabet = dict(zip(alpha_alt, string.ascii_lowercase))
digits = {
    "a zero":  "0",
    "a one":   "1",
    "a two":   "2",
    "a three": "3",
    "a four":  "4",
    "a five":  "5",
    "a six":   "6",
    "a seven": "7",
    "an eight": "8",
    "a nine":  "9",
}

simple_keys = {k: k for k in simple_keys}
arrows = {k: k for k in arrows}
keys = {}
keys.update(f_keys)
keys.update(simple_keys)
keys.update(alternate_keys)
keys.update(symbols)

# map alnum and keys separately so engine gives priority to letter/number repeats
keymap = keys.copy()
keymap.update(arrows)
keymap.update(alphabet)
keymap.update(digits)


def insert(s):
    Str(s)(None)


def get_modifiers(m):
    try:
        return [modifiers[mod] for mod in m["modifiers_list"]]
    except KeyError:
        return []


def get_keys(m):
    groups = ["keys_list", "arrows_list", "digits_list", "alphabet_list"]
    for group in groups:
        try:
            return [keymap[k] for k in m[group]]
        except KeyError:
            pass
    return []


def uppercase_letters(m):
    insert("".join(get_keys(m)).upper())


def press_keys(m):
    mods = get_modifiers(m)
    keys = get_keys(m)
    if mods:
        press("-".join(mods + [keys[0]]))
        keys = keys[1:]
    for k in keys:
        press(k)


ctx = Context("basic")
ctx.keymap(
    {
        "(upper | ship | big) {basic.alphabet}+ [(lowercase | sunk)]": uppercase_letters,
        "{basic.modifiers}* {basic.alphabet}+": press_keys,
        "{basic.modifiers}* {basic.digits}+": press_keys,
        "{basic.modifiers}* {basic.keys}+": press_keys,
        "(go | {basic.modifiers}+) {basic.arrows}+": press_keys,
        "preserve": lambda _: press("ctrl-s"),
        'leave': lambda m: press('escape'),
        'play': lambda m: press('space'),
        'boom': lambda m: press('enter'),
        'turnover': lambda m: press('alt-tab'),
        'move back': lambda m: press('alt-left'),
        'Move forward': lambda m: press('alt-right'),
        'uncomment': lambda m: press('ctrl-/'),
        'copy': lambda m: press('ctrl-c'),
        'paste it': lambda m: press('ctrl-v'),
        'cut it': lambda m: press('ctrl-x'),
        'close it': lambda m: press('ctrl-w'),
        'scratch | undo [it]': lambda m: press('ctrl-z'),
        'redo [it]': lambda m: press('ctrl-shift-z'),
        'new win': lambda m: press('ctrl-n'),
        'nex win': lambda m: press('ctrl-`'),
        'next tab': lambda m: press('ctrl-tab'),
        'pre tab': lambda m: press('ctrl-shift-tab'),
        'new tab': lambda m: press('ctrl-t'),
        'close tab': lambda m: press('ctrl-w'),
        'reload': lambda m: press('ctrl-r'),
        # 'cancel it': lambda m: press('ctrl-g'), #'more <dgndictation> [over]': [' ', text],
        'find here': lambda m: press('ctrl-f'),
        # emacs bindings
        'line start': lambda m: press('ctrl-a'),
        'line end': lambda m: press('ctrl-e'),
        'kill line': lambda m: press('ctrl-k'),
        'slap': lambda m: press('ctrl-e enter'),
    }
)
ctx.set_list("alphabet", alphabet.keys())
ctx.set_list("arrows", arrows.keys())
ctx.set_list("digits", digits.keys())
ctx.set_list("keys", keys.keys())
ctx.set_list("modifiers", modifiers.keys())
