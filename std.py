from talon.voice import Word, Context, Key, Rep, RepPhrase, Str, press
from talon import app, ctrl, clip, ui
from talon_init import TALON_HOME, TALON_PLUGINS, TALON_USER
import string
import time

apps = {}

def switch_app(m):
    name = str(m._words[1])
    full = apps.get(name)
    if not full: return
    for app in ui.apps():
        if app.name == full:
            app.focus()
            # TODO: replace sleep with a check to see when it is in foreground
            time.sleep(0.25)
            break

ctx = Context('switcher')
keymap = {
    'open {switcher.apps}': switch_app,
}
ctx.keymap(keymap)

def update_lists():
    global apps
    new = {}
    for app in ui.apps():
        if app.background and not app.windows():
            continue
        words = app.name.split(' ')
        for word in words:
            if word and not word in new:
                new[word] = app.name
        new[app.name] = app.name
    if set(new.keys()) == set(apps.keys()):
        return
    ctx.set_list('apps', new.keys())
    apps = new

def ui_event(event, arg):
    update_lists()

ui.register('', ui_event)
update_lists()

numberStrings = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
numberDict = {val: i for i,val in enumerate(numberStrings) }

arg = 1
def retrieveArg():
    global arg
    print('arg is: ' + str(arg))
    return arg
def assignToArg(n):
  print(n.dgndictation[0]._words[0])
  return numberDict[n.dgndictation[0]._words[0]]
  def b(dictation):
    global arg
    arg = n
    print('arg is now ' + str(n))
  return b

# cleans up some Dragon output from <dgndictation>
mapping = {
    'semicolon': ';',
    'new-line': '\n',
    'new-paragraph': '\n\n',
}
# used for auto-spacing
punctuation = set('.,-!?')

def parse_word(word):
    word = str(word).lstrip('\\').split('\\', 1)[0]
    word = mapping.get(word, word)
    return word

def join_words(words, sep=' '):
    out = ''
    for i, word in enumerate(words):
        if i > 0 and word not in punctuation:
            out += sep
        out += word
    return out

def parse_words(m):
    return list(map(parse_word, m.dgndictation[0]._words))

def insert(s):
    Str(s)(None)

def text(m):
    insert(join_words(parse_words(m)).lower())

def sentence_text(m):
    text = join_words(parse_words(m)).lower()
    insert(text.capitalize())

def word(m):
    text = join_words(list(map(parse_word, m.dgnwords[0]._words)))
    insert(text.lower())

def surround(by):
    def func(i, word, last):
        if i == 0: word = by + word
        if last: word += by
        return word
    return func

def rot13(i, word, _):
    out = ''
    for c in word.lower():
        if c in string.ascii_lowercase:
            c = chr((((ord(c) - ord('a')) + 13) % 26) + ord('a'))
        out += c
    return out

formatters = {
#    'dunder': (True,  lambda i, word, _: '__%s__' % word if i == 0 else word),
    'camel':  (True,  lambda i, word, _: word if i == 0 else word.capitalize()),
    'title':  (True, lambda i, word, _: word.capitalize()),
    'pascal':  (True, lambda i, word, _: word.capitalize()),
    'snake':  (True,  lambda i, word, _: word if i == 0 else '_'+word),
    'smash':  (True,  lambda i, word, _: word),
    # spinal or kebab?
    'spinal':  (True,  lambda i, word, _: word if i == 0 else '-'+word),
    'pointy':  (True,  lambda i, word, _: word if i == 0 else '.'+word),
    # 'sentence':  (False, lambda i, word, _: word.capitalize() if i == 0 else word),
#     'title':  (False, lambda i, word, _: word.capitalize()),
    'allcaps': (False, lambda i, word, _: word.upper()),
    'dubstring': (False, surround('"')),
    'string': (False, surround("'")),
    'padded': (False, surround(" ")),
    'rot-thirteen':  (False, rot13),
}

def FormatText(m):
    fmt = []
    
    for w in m._words:
        if isinstance(w, Word):
            fmt.append(w.word)
    words = parse_words(m)
    """
    try:
        words = parse_words(m)
    except AttributeError:
        with clip.capture() as s:
            press('cmd-c')
        words = s.get().split(' ')
        if not words:
            return
    """
    tmp = []
    spaces = True
    for i, word in enumerate(words):
        word = parse_word(word)
        for name in reversed(fmt):
            smash, func = formatters[name]
            word = func(i, word, i == len(words)-1)
            spaces = spaces and not smash
        tmp.append(word)
    words = tmp

    sep = ' '
    if not spaces:
        sep = ''
    Str(sep.join(words))(None)

def copy_bundle(m):
    bundle = ui.active_app().bundle
    clip.set(bundle)
    app.notify('Copied app bundle', body='{}'.format(bundle))

ctx = Context('input')
ctx.keymap({
    'say <dgndictation> [over]': text,

    'sentence <dgndictation> [over]': sentence_text,
    'comma <dgndictation> [over]': [', ', text],
    'period <dgndictation> [over]': ['. ', sentence_text],
    'more <dgndictation> [over]': [' ', text],
    'word <dgnwords>': word,

    '(%s)+ [<dgndictation>]' % (' | '.join(formatters)): FormatText,

    # more keys and modifier keys are defined in basic_keys.py

    'slap': [Key('ctrl-e enter')],
    'question [mark]': '?',
    'tilde': '~',
    '(bang | exclamation point)': '!',
    'dollar sign': '$',
    'downscore | lodash': '_',
    'colon': ':',
    '(paren | left paren)': '(', '(rparen | are paren)': ')',
    '(brace | left brace)': '{', '(rbrace | are brace)': '}',
    '(angle | left angle | less than)': '<', '(rangle | are angle | greater than)': '>',

    'asterisk': '*',
    'pounder': '#',
    'percent sign': '%',
    'caret': '^',
    'at sign': '@',
    'ampersand': '&',
    'pipe': '|',

    '(dubquote | double quote)': '"',
    'triple quote': "'''",

    # 'cd': 'cd ',
    # 'cd talon home': 'cd {}'.format(TALON_HOME),
    # 'cd talon user': 'cd {}'.format(TALON_USER),
    # 'cd talon plugins': 'cd {}'.format(TALON_PLUGINS),

    'run make (durr | dear)': 'mkdir ',
    'run get': 'git ',
    'run get (R M | remove)': 'git rm ',
    'run get add': 'git add ',
    'run get bisect': 'git bisect ',
    'run get branch': 'git branch ',
    'run get checkout': 'git checkout ',
    'run get clone': 'git clone ',
    'run get commit': 'git commit ',
    'run get diff': 'git diff ',
    'run get fetch': 'git fetch ',
    'run get grep': 'git grep ',
    'run get in it': 'git init ',
    'run get log': 'git log ',
    'run get merge': 'git merge ',
    'run get move': 'git mv ',
    'run get pull': 'git pull ',
    'run get push': 'git push ',
    'run get rebase': 'git rebase ',
    'run get reset': 'git reset ',
    'run get show': 'git show ',
    'run get status': 'git status ',
    'run get tag': 'git tag ',
    'run (them | vim)': 'vim ',
    'run L S': 'ls\n',
    'dot pie': '.py',
    'run make': 'make\n',
    'run jobs': 'jobs\n',

    'const': 'const ',

    'tip pent': 'int ',
    'tip char': 'char ',
    'tip byte': 'byte ',
    'tip pent 64': 'int64_t ',
    'tip you went 64': 'uint64_t ',
    'tip pent 32': 'int32_t ',
    'tip you went 32': 'uint32_t ',
    'tip pent 16': 'int16_t ',
    'tip you went 16': 'uint16_t ',
    'tip pent 8': 'int8_t ',
    'tip you went 8': 'uint8_t ',
    'tip size': 'size_t',
    'tip float': 'float ',
    'tip double': 'double ',

    'args': ['()', Key('left')],
    'block': [' {}', Key('left enter enter up tab')],
    'empty array': '[]',
    'empty dict': '{}',

    'state (def | deaf | deft)': 'def ',
    'state else if': 'elif ',
    'state if': 'if ',
    'state else if': [' else if ()', Key('left')],
    'state while': ['while ()', Key('left')],
    'state for': ['for ()', Key('left')],
    'state for': 'for ',
    'state switch': ['switch ()', Key('left')],
    'state case': ['case \nbreak;', Key('up')],
    'state goto': 'goto ',
    'state import': 'import ',
    'state class': 'class ',

    'state include': '#include ',
    'state include system': ['#include <>', Key('left')],
    'state include local': ['#include ""', Key('left')],
    'state type deaf': 'typedef ',
    'state type deaf struct': ['typedef struct {\n\n};', Key('up'), '\t'],

    'comment see': '// ',
    'comment py': '# ',

    'word queue': 'queue',
    'word eye': 'eye',
    'word bson': 'bson',
    'word iter': 'iter',
    'word no': 'NULL',
    'word cmd': 'cmd',
    'word dup': 'dup',
    'word streak': ['streq()', Key('left')],
    'word printf': 'printf',
    'word (dickt | dictionary)': 'dict',
    'word shell': 'shell',

    'word lunixbochs': 'lunixbochs',
    'word talon': 'talon',
    'word Point2d': 'Point2d',
    'word Point3d': 'Point3d',
    'title Point': 'Point',
    'word angle': 'angle',

    'dunder in it': '__init__',
    'self taught': 'self.',
    'dickt in it': ['{}', Key('left')],
    'list in it': ['[]', Key('left')],
    'string utf8': "'utf8'",
    'state past': 'pass',

    'plus': '+',
    'doubledash': '--',
#    'arrow': '->',
    'par pair': '()', #'call': '()',
    'indirect': '&',
    'dereference': '*',
    'op (minus | subtract)': ' - ',
    'op (plus | add)': ' + ',
    'op (times | multiply)': ' * ',
    'op divide': ' / ',
    'op mod': ' % ',
    '[op] (minus | subtract) equals': ' -= ',
    '[op] (plus | add) equals': ' += ',
    '[op] (times | multiply) equals': ' *= ',
    '[op] divide equals': ' /= ',
    '[op] mod equals': ' %= ',

    '(op | is) greater [than]': ' > ',
    '(op | is) less [than]': ' < ',
    '(op | is) equal': ' == ',
    '(op | is) not equal': ' != ',
    '(op | is) greater [than] or equal': ' >= ',
    '(op | is) less [than] or equal': ' <= ',
    '(op (power | exponent) | to the power [of])': ' ** ',
    'op and': ' && ',
    'op or': ' || ',
    '[op] (logical | bitwise) and': ' & ',
    '[op] (logical | bitwise) or': ' | ',
    '(op | logical | bitwise) (ex | exclusive) or': ' ^ ',
    '[(op | logical | bitwise)] (left shift | shift left)': ' << ',
    '[(op | logical | bitwise)] (right shift | shift right)': ' >> ',
    '(op | logical | bitwise) and equals': ' &= ',
    '(op | logical | bitwise) or equals': ' |= ',
    '(op | logical | bitwise) (ex | exclusive) or equals': ' ^= ',
    '[(op | logical | bitwise)] (left shift | shift left) equals': ' <<= ',
    '[(op | logical | bitwise)] (right shift | shift right) equals': ' >>= ',


    'kill inside': [Key('alt-x'),'kill-inside', Key('enter')],

    'shebang bash': '#!/bin/bash -u\n',
    #my commands
    'mission': Key('ctrl-shift-up'),
    'spotlight <dgndictation> ': [Key('cmd-space'), text],
    'spot': Key('cmd-space'), #'more <dgndictation> [over]': [' ', text],
    'leave': Key('escape'),
    'boom': Key('enter'),
    'turnover': Key('cmd-tab'),
    'twist': Key('cmd-~'),
    'copy': Key('cmd-c'),
    'paste': Key('cmd-v'),
    'cut it': Key('cmd-x'),
    'close it': Key('cmd-w'),
    'scratch | undo [it]': Key('cmd-z'),
    'redo': Key('cmd-shift-z'),
    'preserve': Key('cmd-s'), 
    'new win': Key('cmd-n'),
    'nex win': Key('cmd-`'),
    'last window': Key('cmd-shift-`'),
    'last app': Key('cmd-shift-tab'),
    'next tab': Key('ctrl-tab'),
    'pre tab': Key('ctrl-shift-tab'),
    'new tab': Key('cmd-t'),
    'close tab': Key('cmd-w'),
    'reload': Key('cmd-r'),
    'last tab': Key('ctrl-shift-tab'),
    'kill line': Key('ctrl-k'),
    'cancel it': Key('ctrl-g'), #'more <dgndictation> [over]': [' ', text],
    'find here': Key('cmd-f'),
    'see ex': Key('ctrl-x'),
    'altex': Key('alt-x'), #'more <dgndictation> [over]': [' ', text],
    'see ey | line start': Key('ctrl-a'),
    'see bee': Key('ctrl-b'),
    'see see': Key('ctrl-c'),
    'cd | kill char': Key('ctrl-d'),
    'see end | line end': Key('ctrl-e'),
    'see firm': Key('ctrl-f'),
    'see good': Key('ctrl-g'),
    'see age': Key('ctrl-h'),
    'see eye': Key('ctrl-i'),
    'see jay': Key('ctrl-j'),
    'see kay': Key('ctrl-k'),
    'see luke': Key('ctrl-l'),
    'see made': Key('ctrl-m'),
    'see nex': Key('ctrl-n'),
    'see oh': Key('ctrl-o'),
    'see pee': Key('ctrl-p'),
    'see cue': Key('ctrl-q'),
    'see are | berch': Key('ctrl-r'),
    'nerch | search': Key('ctrl-s'),
    'see tea': Key('ctrl-t'),
    'see you': Key('ctrl-u'),
    'see vest': Key('ctrl-v'),
    'see whale': Key('ctrl-w'),
    'see yankee': Key('ctrl-y'),
    'see zulu': Key('ctrl-z'),
    'see space | set mark': Key('ctrl-space'),
    
    'sentence start': Key('alt-a'),
    'word back | meta bee': Key('alt-b'),
    'meta cap | cap word': Key('alt-c'),
    'alt dee | aldi | kill word': Key('alt-d'),
    'alt-back | kill pre-word': Key('alt-backspace'),
    'sentence end | alt end': Key('alt-e'),
    'next word  | alteff': Key('alt-f'),
    'alt good': Key('alt-g'),
    'alt age': Key('alt-h'),
    'alt eye': Key('alt-i'),
    'alt jay': Key('alt-j'),
    'alt kay': Key('alt-k'),
    'alt luke': Key('alt-l'),
    'alt made': Key('alt-m'),
    'alt nex': Key('alt-n'),
    'alt oh': Key('alt-o'),
    'alt pee': Key('alt-p'),
    'alt cue': Key('alt-q'),
    'berch | backsearch': Key('alt-r'),
    'alt ess': Key('alt-s'),
    'alt tea': Key('alt-t'),
    'flip it | alt tab': Key('alt-tab'),
    'alt you': Key('alt-u'),
    'alt vest': Key('alt-v'),
    'alt whale | ring save': Key('alt-w'),

    'nex dex': Key('ctrl-right'),
    'desktop back': Key('ctrl-left'),

    'links | display links | show [THEM] links': 'f',#[Key('ctrl-x'),Key('ctrl-f')],

    'click': lambda _: ctrl.mouse_click(button=0, hold=16000),
    'are click': lambda _: ctrl.mouse_click(button=1, hold=16000),
    'word menu': lambda _: [
        ctrl.mouse_click(button=0, hold=16000),
        ctrl.mouse_click(button=0, hold=16000),
        ctrl.mouse_click(button=1, hold=16000),
    ],

    'emacs':'emacs ',
    'node':'node ',
#    'code':'code ',
    'cat':'cat ',
    'chrome':'chrome',
    'return':'return',
    'pseudo-':'sudo ',
    'docker':'docker',
    'aws':'aws',
    'func':'func',

    

    
    'up': Key('up'),
    'down': Key('down'),
    'left': Key('left'),
    'right': Key('right'),
    
    'select all': Key('cmd-a'),


    'next space': Key('cmd-alt-ctrl-right'),
    'last space': Key('cmd-alt-ctrl-left'),

    'scroll down': [Key('down')] * 30,
    'scroll up': [Key('up')] * 30,

    'lift <dgndictation>': lambda n: [ctrl.key_press('up') for i in range(numberDict[n.dgndictation[0]._words[0]])] ,
    'hinder <dgndictation>': lambda n: [ctrl.key_press('down') for i in range(numberDict[n.dgndictation[0]._words[0]])] ,

    'copy active bundle': copy_bundle,
})


alpha_alt = 'aim bat chain drum each fox good harp india jury cake look made neat odd pure queen rule sun trap urine vest whale plex yard zulu'.split()
#alpha_alt = 'air bat cap drum each fine gust harp sit jury crunch look made near odd pit quench red sun trap urge vest whale plex yank zip'.split()
#alpha_alt = 'alpha bravo chain delta echo foxy golf hotel india juliet kilo Lima mikey nova oyster Paris queen ricky sierra tango urinal victor whiskey xray yankee sooloo'.split()
f_keys = {f'F {i}': f'f{i}' for i in range(1, 13)}
# arrows are separated because 'up' has a high false positive rate
arrows = ['left', 'right', 'up', 'down']
simple_keys = [
    'tab', 'escape', 'enter', 'space',
    # 'home', #It interferes with boom
    'pageup', 'pagedown', 'end',
]
alternate_keys = {
    'deal': 'backspace',
    'forward delete': 'delete',
    'play': 'space',
}
symbols = {
    'back tick': '`',
    'comma': ',',
    'period': '.',
    'semi': ';', 'semicolon': ';',
    'quote': "'",
    'L square': '[', 'left square': '[', 'square': '[',
    'R square': ']', 'right square': ']',
    'forward slash': '/', 'slash': '/',
    'backslash': '\\',
    'minus': '-',
    'dash': '-',
    'equals': '=',
}
modifiers = {
    'command': 'cmd',
    'control': 'ctrl',
    'shift': 'shift',
    'alt': 'alt',
    'option': 'alt',
}

alphabet = dict(zip(alpha_alt, string.ascii_lowercase))
#digits = {str(i): str(i) for i in range(10)}
digits = {'num' + str(i): str(i) for i in range(9)}#{

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
        return [modifiers[mod] for mod in m['basic_keys.modifiers']]
    except KeyError:
        return []

def get_keys(m):
    groups = ['basic_keys.keys', 'basic_keys.arrows', 'basic_keys.digits', 'basic_keys.alphabet']
    for group in groups:
        try:
            return [keymap[k] for k in m[group]]
        except KeyError: pass
    return []

def uppercase_letters(m):
    insert(''.join(get_keys(m)).upper())

def press_keys(m):
    mods = get_modifiers(m)
    keys = get_keys(m)
    if mods:
        press('-'.join(mods + [keys[0]]))
        keys = keys[1:]
    for k in keys:
        press(k)

ctx = Context('basic_keys')
ctx.keymap({
    '(uppercase | ship) {basic_keys.alphabet}+ [(lowercase | sunk)]': uppercase_letters,
    '{basic_keys.modifiers}* {basic_keys.alphabet}+': press_keys,
    '{basic_keys.modifiers}* {basic_keys.digits}+': press_keys,
    '{basic_keys.modifiers}* {basic_keys.keys}+': press_keys,
    '(go | {basic_keys.modifiers}+) {basic_keys.arrows}+': press_keys,
})
ctx.set_list('alphabet', alphabet.keys())
ctx.set_list('arrows', arrows.keys())
ctx.set_list('digits', digits.keys())
ctx.set_list('keys', keys.keys())
ctx.set_list('modifiers', modifiers.keys())


import time

from talon import ctrl
from talon import tap
from talon.audio import noise
from talon.track.geom import Point2d

class NoiseModel:
    def __init__(self):
        self.hiss_start = 0
        self.hiss_last = 0
        self.button = 0
        self.mouse_origin = Point2d(0, 0)
        self.mouse_last = Point2d(0, 0)
        self.dragging = False

        tap.register(tap.MMOVE, self.on_move)
        noise.register('noise', self.on_noise)

    def on_move(self, typ, e):
        if typ != tap.MMOVE: return
        self.mouse_last = pos = Point2d(e.x, e.y)
        if self.hiss_start and not self.dragging:
            if (pos - self.mouse_origin).len() > 10:
                self.dragging = True
                self.button = 0
                x, y = self.mouse_origin.x, self.mouse_origin.y
                ctrl.mouse(x, y)
                ctrl.mouse_click(x, y, button=0, down=True)

    def on_noise(self, noise):
        now = time.time()
        if noise == 'pop':
            ctrl.mouse_click(button=0, hold=16000)
        elif noise == 'hiss_start':
            if now - self.hiss_last < 0.25:
                ctrl.mouse_click(button=self.button, down=True)
                self.hiss_last = now
                self.dragging = True
            else:
                self.mouse_origin = self.mouse_last
            self.hiss_start = now
        elif noise == 'hiss_end':
            if self.dragging:
                ctrl.mouse_click(button=self.button, up=True)
                self.dragging = False
            else:
                duration = time.time() - self.hiss_start
                if duration > 0.5:
                    self.button = 1
                    ctrl.mouse_click(button=1)
                    self.hiss_last = now
                elif duration > 0.2:
                    self.button = 0
                    ctrl.mouse_click(button=0)
                    self.hiss_last = now
            self.hiss_start = 0

model = NoiseModel()




# from talon.voice import Word, Context, Key, Rep, RepPhrase, Str, press
# from talon import ctrl, clip
# from talon_init import TALON_HOME, TALON_PLUGINS, TALON_USER
# import string

# alpha_alt = 'Air bat Charlie Delta echo firm golf hotel India Juliet cake look Mike needle Oprah pure cute romeo saas Trap urine Victor wink Xray yell zulu'.split()

# # NATO
# # alpha_alt = 'Alpha Bravo Charlie Delta Echo Foxtrot Golf Hotel India Juliet Kilo Lima Mike November Oscar Papa Quebec Romeo Sierra Tango Uniform Victor Whiskey Xray Yankee Zulu'.split()
# # alpha_alt = 'air bat cap die each fail gone harm sit jury crash look mad near odd pit quest red sun trap urge vest whale box yes zip'.split()
# alnum = list(zip(alpha_alt, string.ascii_lowercase)) + [(str(i), str(i)) for i in range(0, 10)]

# alpha = {}
# alpha.update(dict(alnum))
# alpha.update({'ship %s' % word: letter for word, letter in zip(alpha_alt, string.ascii_uppercase)})

# alpha.update({'control %s' % k: Key('ctrl-%s' % v) for k, v in alnum})
# alpha.update({'command %s' % k: Key('cmd-%s' % v) for k, v in alnum})
# alpha.update({'command shift %s' % k: Key('ctrl-shift-%s' % v) for k, v in alnum})
# alpha.update({'alt %s' % k: Key('alt-%s' % v) for k, v in alnum})

# mapping = {
#     'semicolon': ';',
#     'new-line': '\n',
#     'new-paragraph': '\n\n',
# }
# punctuation = set('.,-!?')

# def parse_word(word):
#     word = str(word).lstrip('\\').split('\\', 1)[0]
#     word = mapping.get(word, word)
#     return word

# def join_words(words, sep=' '):
#     out = ''
#     for i, word in enumerate(words):
#         if i > 0 and word not in punctuation:
#             out += sep
#         out += word
#     return out

# def parse_words(m):
#     return list(map(parse_word, m.dgndictation[0]._words))

# def insert(s):
#     Str(s)(None)

# def text(m):
#     insert(join_words(parse_words(m)).lower())

# def sentence_text(m):
#     text = join_words(parse_words(m)).lower()
#     insert(text.capitalize())

# def word(m):
#     text = join_words(list(map(parse_word, m.dgnwords[0]._words)))
#     insert(text.lower())

# def surround(by):
#     def func(i, word, last):
#         if i == 0: word = by + word
#         if last: word += by
#         return word
#     return func

# def rot13(i, word, _):
#     out = ''
#     for c in word.lower():
#         if c in string.ascii_lowercase:
#             c = chr((((ord(c) - ord('a')) + 13) % 26) + ord('a'))
#         out += c
#     return out

# def dunder(i, word, _): return  '__%s__' % word if i == 0 else word
# def camel(i, word, _): return  word if i == 0 else word.capitalize()
# def snake(i, word, _): return  word if i == 0 else '_'+word
# def smash(i, word, _): return  word
# def lispee(i, word, _): return  word if i == 0 else '-'+word
# def sentence(i, word, _): return  word.capitalize() if i == 0 else word
# def title(i, word, _): return  word.capitalize()
# def allcaps(i, word, _): return  word.upper()


# ctx = Context('input')

# keymap = {}
# keymap.update(alpha)
# keymap.update({
#     #  these are general commands
#     # these command controls mac os x
#     "(Mission control | Sean Kohn)": Key("cmd-up"),
#     "(flip it)": Key("cmd-tab"),
#     "(app Windows)": Key("ctrl-down"),
#     "(flip app )": Key("cmd-`"),
#     " (show | hide) dock": Key("cmd-alt-d"),
#     " spotlight": Key("cmd-space"),
#     "copy": Key("cmd-c"),
#     "paste": Key("cmd-v"),
    

#     '(dictate | phrase) <dgndictation> [over]': text, # 'litter' stands for literally

#     'sentence <dgndictation> over': sentence_text,
#     'comma <dgndictation> [over]': [', ', text],
#     'period <dgndictation> [over]': ['. ', sentence_text],
#     'more <dgndictation> [over]': [' ', text],
#     'word <dgnwords>': word,

#     'tab it':   Key('tab'),
#     'left':  Key('left'),
#     'right': Key('right'),
#     'up':    Key('up'),
#     'down':  Key('down'),

#     'delete': Key('backspace'),

#     'slap': [Key('cmd-right enter')],
#     '(enter |  boom)': Key('enter'),
#     'escape': Key('esc'),
#     'question [mark]': '?',
#     'tilde': '~',
#     '(bang | exclamation point)': '!',
#     'dollar [sign]': '$',
#     'downscore': '_',
#     '(semi | semicolon)': ';',
#     'colon': ':',
#     '(square | left square [bracket])': '[', '(rsquare | are square | right square [bracket])': ']',
#     '(paren | left paren)': '(', '(rparen | are paren | right paren)': ')',
#     '(brace | left brace)': '{', '(rbrace | are brace | right brace)': '}',
#     '(angle | left angle | less than)': '<', '(rangle | are angle | right angle | greater than)': '>',

#     '(star | asterisk)': '*',
#     '(pound | hash [sign] | octo | thorpe | number sign)': '#',
#     'percent [sign]': '%',
#     'caret': '^',
#     'at sign': '@',
#     '(and sign | ampersand | amper)': '&',
#     'pipe': '|',

#     '(dubquote | double quote)': '"',
#     'quote': "'",
#     'triple quote': "'''",
#     '(dot | period)': '.',
#     'comma': ',',
#     'space': ' ',
#     '[forward] slash': '/',
#     'backslash': '\\',

#     '(dot dot | dotdot)': '..',
#     'cd': 'cd ',

#     'args': ['()', Key('left')],
#     'index': ['[]', Key('left')],
#     'block': [' {}', Key('left enter enter up tab')],
#     'empty array': '[]',
#     'empty dict': '{}',

#     'state (def | deaf | deft)': 'def ',
#     'state else if': 'elif ',
#     'state if': 'if ',
#     'state else if': [' else if ()', Key('left')],
#     'state while': ['while ()', Key('left')],
#     'state for': ['for ()', Key('left')],
#     'state for': 'for ',
#     'state switch': ['switch ()', Key('left')],
#     'state case': ['case \nbreak;', Key('up')],
#     'state goto': 'goto ',
#     'state import': 'import ',
#     'state class': 'class ',

#     'state include': '#include ',
#     'state include system': ['#include <>', Key('left')],
#     'state include local': ['#include ""', Key('left')],
#     'state type deaf': 'typedef ',
#     'state type deaf struct': ['typedef struct {\n\n};', Key('up'), '\t'],

#     'comment see': '// ',
#     'comment py': '# ',

#     'word queue': 'queue',
#     'word eye': 'eye',
#     'word bson': 'bson',
#     'word iter': 'iter',
#     'word no': 'NULL',
#     'word cmd': 'cmd',
#     'word dup': 'dup',
#     'word streak': ['streq()', Key('left')],
#     'word printf': 'printf',
#     'word (dickt | dictionary)': 'dict',
#     'word shell': 'shell',

#     'word lunixbochs': 'lunixbochs',
#     'word talon': 'talon',
#     'word Point2d': 'Point2d',
#     'word Point3d': 'Point3d',
#     'title Point': 'Point',
#     'word angle': 'angle',

#     'dunder in it': '__init__',
#     'self taught': 'self.',
#     'dickt in it': ['{}', Key('left')],
#     'list in it': ['[]', Key('left')],
#     'string utf8': "'utf8'",
#     'state past': 'pass',

#     'equals': '=',
#     '(minus | dash)': '-',
#     'plus': '+',
#     'arrow': '->',
#     'call': '()',
#     'indirect': '&',
#     'dereference': '*',
#     '(op equals | assign)': ' = ',
#     'op (minus | subtract)': ' - ',
#     'op (plus | add)': ' + ',
#     'op (times | multiply)': ' * ',
#     'op divide': ' / ',
#     'op mod': ' % ',
#     '[op] (minus | subtract) equals': ' -= ',
#     '[op] (plus | add) equals': ' += ',
#     '[op] (times | multiply) equals': ' *= ',
#     '[op] divide equals': ' /= ',
#     '[op] mod equals': ' %= ',

#     '(op | is) greater [than]': ' > ',
#     '(op | is) less [than]': ' < ',
#     '(op | is) equal': ' == ',
#     '(op | is) not equal': ' != ',
#     '(op | is) greater [than] or equal': ' >= ',
#     '(op | is) less [than] or equal': ' <= ',
#     '(op (power | exponent) | to the power [of])': ' ** ',
#     'op and': ' && ',
#     'op or': ' || ',
#     '[op] (logical | bitwise) and': ' & ',
#     '[op] (logical | bitwise) or': ' | ',
#     '(op | logical | bitwise) (ex | exclusive) or': ' ^ ',
#     '[(op | logical | bitwise)] (left shift | shift left)': ' << ',
#     '[(op | logical | bitwise)] (right shift | shift right)': ' >> ',
#     '(op | logical | bitwise) and equals': ' &= ',
#     '(op | logical | bitwise) or equals': ' |= ',
#     '(op | logical | bitwise) (ex | exclusive) or equals': ' ^= ',
#     '[(op | logical | bitwise)] (left shift | shift left) equals': ' <<= ',
#     '[(op | logical | bitwise)] (right shift | shift right) equals': ' >>= ',

# })
# ctx.keymap(keymap)





# #  here starts the section is the configuration for browser mode

# def address_bar(m):    
#     press('cmd-l')
#     sleep(0.1) # Time in seconds.
#     text(m)

# browserContext = Context("browser", app='Safari' )

# browserContext.keymap({
#     'search bar  <dgndictation> over ': address_bar,
#     'address bar':  Key('cmd-l'),
#     'close tab ': Key('cmd-w'),
#     'New tab ': Key('cmd-t'),
#     'find ': Key('cmd-f'),
#     ' back ': Key('cmd-['),
#     'forward': Key('cmd-]'),
# })

# #  here ends the section is the configuration for browser mode


# #  here starts the section is the configuration for terminal mode

# terminalContext = Context("terminal", app='Terminal' )

# terminalContext.keymap({
#     'clear ': Key('cmd-k'),
# })

# #  here ends the section is the configuration for terminal mode
