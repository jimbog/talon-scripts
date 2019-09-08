from talon.voice import Word, Context, Key, Rep, RepPhrase, Str, press
from talon import ctrl, clip
from talon_init import TALON_HOME, TALON_PLUGINS, TALON_USER
import string

# This section is the configuration for Emacs mode
from time import sleep
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

def toEmacsName(str):
    str = str.replace('C-', 'ctrl-')
    return str.replace('M-', 'alt-')
    
def enablePareditMode(m):    
    press('alt-x')
    sleep(0.1) # Time in seconds.
    text('enable-paredit-mode')

def defun(m):
    text("(defun  ())")
    sleep(0.1) # Time in seconds.
    press("esc 4 left")
    press("alt-p cmd-f11")
    
#emacsContext = Context("nomachine", app="NoMachine") #
emacsContext = Context("emacs") #
#emacsContext = Context("emacs", app="Emacs") #input
emacsContext.keymap({
    'close Emacs':  Key('ctrl-x ctrl-c'),
    'copy to mark':  Key('alt-w ctrl-u ctrl-space ctrl-u ctrl-space ctrl-y' ),
    
    'meta ex ': Key('alt-x'),  # mx,
    
    "cancel  Command": Key("ctrl-g"),
    "undo [it]": Key("ctrl-/"),
 
    "(repeat [it] | again)": Key("ctrl-x z"),
    "start macro": Key("f3"), # Key("ctrl-x e"),
    "(end | run) macro": Key("f4"), # Key("ctrl-x e"),
    
    # "(universal argument)": Key("ctrl-u"),
    "meta": Key("escape"), # useful for universal argument


    # files Commands
    'find file':  Key("ctrl-x ctrl-f"),
    '(find | open)  file (next | other) window':  Key("ctrl-x 4 ctrl-f"),
    'read only open file next window':  Key("ctrl-x 4 r"),
    "visit new file": Key('ctrl-x ctrl-c'),    
    'save [buffer to] file':  Key(toEmacsName('C-x C-s')),
    'write file':  Key(toEmacsName('C-x C-w')),
    
    'replace buffer with file':  Key(toEmacsName('C-x C-v')),
    '(insert file |  file into buffer)':  Key(toEmacsName('C-x i')),
        
    #  buffer commands
    "switch [to] buffer": Key('ctrl-x b'),
    "list [all] buffers": Key('ctrl-x ctrl-b'),
    " kill buffer": Key('ctrl-x k'),
    "switch to buffer other window": Key('ctrl-x 4 b'),
    "display buffer": Key('ctrl-x 4 ctrl-o'),

    
    # window commands
    'other window': Key('ctrl-x o'),
    "delete window": Key("ctrl-x 0"),
    "split window right": Key("ctrl-x 3"),
    "split window [below]": Key("ctrl-x 2"),
    " single window": Key("ctrl-x 1"),
    "read only": Key("ctrl-x ctrl-q"),
    "(window skinnier | shrink window horizontally)": Key("ctrl-x {"),
    "( window fatter| enlarge window horizontally)": Key("ctrl-x }"),
    'enlarge window': Key("ctrl-x ^"),
    
    # 
    "(just one space | single space)": Key("alt-space"),
    "(delete horizontal space | no room)": Key("alt-\\"),
    
    
    "apropos": Key("ctrl-h a"),
    

    # paredit stuff
    " slurp right": Key("ctrl-shift-0"),
    " slurp left": Key("ctrl-shift-9"),
    " raise it": Key("alt-s"),
    

    
    " show kill ring": [Key("ctrl-h v"), "kill-ring", Key("enter") ],
    "select [this] word": Key("esc f esc b ctrl-space alt-right"),
    "select inside parentheses": [Key("ctrl-r"), '(', Key("right"), Key("ctrl-space"), Key("ctrl-s"), ')', Key("left")],
    "copy [this] word": Key("esc f esc b ctrl-space alt-right alt-w"),
    
    "kill [this] word": Key("alt-left alt-d"),
    'zap character': Key("escape z"),
    'enable par edit': [Key("alt-x"), "enable-paredit-mode"],
    'transpose char': Key("ctrl-t"), #  transposes current char with the left one
    'transpose word': Key("alt-t"), #  transposes current word with the  right one
    
    
    #  region commands
    "(kill it | kill region)": Key("ctrl-w"),
    " append next kill": Key("alt-ctrl-w"),
    
    "(delete it | delete region)": [Key("alt-x"), "delete-region",Key("enter")],
    "(replace it | replace region)": [Key("alt-x"), "delete-region",Key("enter"), Key("ctrl-y")],
    
    
    "(copy it | kill ring save)": Key("alt-w"),
    " paste it | yank it ": Key("ctrl-y"),
    
    " front paste it | yank it ": Key("ctrl-u ctrl-y"),
    " (yank |  paste) pop": Key("alt-y"),

    
    " copy  paste": Key("alt-w ctrl-y"),
    'count  [words] region': Key("escape ="),
    'shell command on region': Key("escape |"), 

    #  line commands
    " (cut | kill) [whole] line ": Key("ctrl-a ctrl-k"),
    " (cut | kill) to end ": Key("ctrl-k"),
    "pre-kill line": Key("alt-0 ctrl-k"),
    "transpose lines ": Key("ctrl-x ctrl-t"),
    " delete line": Key("ctrl-a ctrl-k ctrl-k"),
    " copy line": Key("ctrl-a ctrl-@ ctrl-e  alt-w"),
    " copy to end": Key("ctrl-spc ctrl-e  alt-w"),
    
    "move [this] line to": Key("ctrl-a ctrl-@ ctrl-e  alt-w"),
    '(join lines | delete indentation)': Key("escape ^"),
    
    "([I] search | nerch)": Key("ctrl-s"),
    "((buy | pre-) search | berch)": Key("ctrl-r"),
    "(rejex I search | rejex nerch)": Key("escape ctrl-s"),
    "(rejex buy search | rejex berch)": Key("escape ctrl-r"),
    "(i word search | nerch word)": Key("alt-s w"),
    "(buy word search | berch word)": Key("alt-s w ctrl-r"),
    

    "rejex search replace ":  Key('escape ctrl-%'),
    'replace string': [Key('alt-x'), 'replace-string', Key('enter')],
    'replace regexp': [Key('alt-x'), 'replace-regexp', Key('enter')],
    
    

    "describe key": Key('ctrl-h k'),
    "cancel [Command]": Key("ctrl-g"),

    "kill back sentence": Key("ctrl-g"),
    
    # navigating
    "(line start | start off-line)": Key("ctrl-a"),
    "(line beginning | line begin)": Key("alt-m"),
    "(line  end | end of line)": Key("ctrl-e"),
    "previous line  | pre-line": Key("ctrl-p"),
    "next line": Key("ctrl-n"),
    "pre-word": Key("alt-b"),
    "pre-char ": Key("ctrl-b"),
    "nex word": Key("alt-f"),
    "next char": Key("ctrl-f"),
    "pre sentence": Key("alt-a"),
    "nex sentence": Key("alt-e"),
    "open line": Key("ctrl-o"),
    "scroll down": Key("ctrl-v"),
    "scroll up": Key("alt-v"),
    "scroll [down] other window": Key("escape ctrl-v"),
    "(recenter top bottom | line in middle)": Key("ctrl-l"),
    "(jump | go) [to] line": Key("escape g g"),    
    
    "(beginning of buffer |  buffer beginning)": Key("alt-<"),
    "(end of buffer |  buffer end)": Key("alt->"),

    # marking
    'mark it': Key("ctrl-space"),
    'mark word': Key("alt-@"),
    'jump mark': Key("ctrl-u ctrl-space"),
    'jump two mark': Key("ctrl-u ctrl-space ctrl-u ctrl-space"),
    'jump three mark': Key("ctrl-u ctrl-space ctrl-u ctrl-space ctrl-u ctrl-space"),
    "show mark ring": [Key("ctrl-h v"), "mark-ring", Key("enter") ],  
    'mark (flip | exchange)': Key("ctrl-x ctrl-x"), # useful to copy entire region without dragging the mouse
    

    #  help
    "describe key": Key("ctrl-h k"),
    "show key bindings": Key("ctrl-h b"),

    #  shell
    'a new shell':  [Key('alt-x'), "shell", Key('enter')],
    
    # javascript
 #   'funk': ['function (){\nreturn undefined\n}', Key("esc 2 up")],
#    'method': ['(){\nreturn undefined\n}', Key("up esc 4 left")],
    
    'class': ['class {\n}', Key("esc 3 left")],

    
    'switch buffer': [Key('ctrl-x'), Key('b')],
    'list buffers':  [Key('ctrl-x'), Key('ctrl-b')],

    'other window':  [Key('ctrl-x'), Key('o')],
    'kill window':  [Key('ctrl-x'), Key('0')],
    'single window':  [Key('ctrl-x'), Key('1')],
    'split window [vertically]':  [Key('ctrl-x'), Key('2')],
    'split window horizontally':  [Key('ctrl-x'), Key('3')],
    'help' : [Key('ctrl-h'), Key('ctrl-h')],
    'quit' : [Key('ctrl-g')],
    'kill buffer' : [Key('ctrl-x'), Key('k')],
    'open file' : [Key('ctrl-x'), Key('ctrl-f')],
    'save file' : [Key('ctrl-x'), Key('ctrl-s')],
    'save file as' : [Key('ctrl-x'), Key('ctrl-w')],   

    'move to the end of the line' : [Key('end')],
    'move up a page' : [Key('page up')],
    'move down a page' : [Key('page down')],
    'move to end of buffer' : [Key('alt-')],
    'kill region' : [Key('ctrl-w')],
    'kill line' : [Key('ctrl-k')],
    'ring save' : [Key('alt-w')],
    'yank here' : [Key('ctrl-y')],
    'yank pop' : [Key('alt-y')],
    'move to next item in the kill ring' : [Key('alt-Y')],

    'undo' : [Key('ctrl-_')],
    'buffer beginning' : [Key('home')],
    'move to the end of the line' : [Key('end')],
    'page up' : [Key('page up')],
    'page down' : [Key('page down')],
    'end of buffer' : [Key('alt->')],

    'query place' : [Key('alt-%')], # (‘space’ to replace, ‘n’ to skip, ‘!’ to replace all)
    
    'copy line below':  [Key('ctrl-a ctrl-space down alt-w ctrl-y')],
    'kill this line':  [Key('ctrl-a ctrl-space down ctrl-w')],

    #eshell commands
    'eshell': [Key('alt-x'), 'eshell'],    
    'mk dear': 'mkdir ',
    'change dear': 'cd ',
    'el-less': 'ls ',
    'touch': 'touch ',
    'pee double u dee': 'pwd',
    'erase-buffer': '(let ((inhibit-read-only t))    (erase-buffer))',


    
})

#  here ends the section is the configuration for Emacs mode


"""    
    #  Emacs lisp (elisp) and scheme stuff  
    "(evaluate | eval) it": Key("ctrl-x ctrl-e"),
    "(evaluate | eval) buffer": [Key("alt-x"), "eval-buffer", Key("enter")],
    "eval  whole buffer": [Key("ctrl-x"), Key("h"),
                           Key("ctrl-c"), Key("ctrl-r")],
    
    "eval sexper": Key("alt-:"),
    "set queue": ["(setq )", Key("left space")],
    " comment it": [";; "], #
    " nil": ["nil"], #
    
    "insert": ["(insert \"\")", Key("left left")],
    
    # "dee fun": ["(defun  ())", Key("esc 4 left"), Key("alt-p cmd-f11")],
    "dee fun": ["(define  ())", Key("esc 2 left"), Key("alt-p cmd-f11")],
    "defvar": ["(define  )", Key("left space"), Key("alt-p cmd-f11")],
    "prohgun": ["(progn )", Key("left")],
    "lambda": ["(lambda () )", Key("left left left")],
    " message": ['(message "")', Key("left left")],
    "let form": ["(let ())", Key("left left")],
    "if form": ["(if ())", Key("left left")],
    "if empty": ["(if (null? ))", Key("left left")],
    "check empty": ["(null? )", Key("left")],
    "empty list": ["'()"],
    "make list": ["(list )", Key("left")],
    ' Ellis T':  ["lst"],
    'equal pee':  ["(equal? )", Key("left")],
    ' condition':  ["(cond ())", Key("left left")],
    ' else':  ["(else ())", Key("left left")],
    'last exper': Key("alt-p"),
    'run scheme': [ Key("alt-x"), 'run-scheme'],
    
    "when form": ["(when ())", Key("left left")],
    "or form": ["(or ())", Key("left left")],
    "and form": ["(and ())", Key("left left")],
    "dotimes form": ["(dotimes (var upto))", Key("left enter")],
    "format form": ['(format " %s")', Key("alt-5 left")],
    "car": ['(car )', Key("left space")],
    "cons": ['(cons )', Key("left space")],
    "coodder": ['(cdr )', Key("left space")],
    "push": ['(push )', Key("left space")],    
    "mapcar": ['(mapcar )', Key("left space")],
    "while": ['(while () \n)', Key("left space")],
    "spinal fi": Key("alt-p cmd-f11"),    

    'scheme line new': '(newline)',
    'scheme display': ['(display )', Key("left")],
    'member':  ["(member )", Key("left")],
"""
