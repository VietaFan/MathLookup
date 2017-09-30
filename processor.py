def parseContent(line):
    try:
        pieces = line.strip().split()
        lineType = pieces[0]
        i = 0
        while i < len(lineType) and lineType[i].isalpha():
            i += 1
        remainder = ' '.join(pieces[1:])
        typeName = lineType[:i].lower()
        pos = remainder.index(':')
        if '(' in remainder:
            pos = remainder.index('(')
        objName = remainder[:pos]
        return typeName, objName.lower().strip()
    except:
        return None, None

class MathNotes:
    ''' A class that models a file with math notes as a sort of filesystem,
    allowing you to easily view the structure and find specific definitions and theorems.'''
    def __init__(self, lines, chunkSize = 1000):
        self.lines = []
        for line in lines:
            if line.strip() == '':
                continue
            self.lines.append(line.strip('\n'))
        self.chunkSize = chunkSize
        N = len(self.lines)
        depth = []
        # get indent width of each line
        for line in self.lines:
            d = 0
            for c in line:
                if c == ' ':
                    d += 1
                elif c == '\t':
                    d += 4
                else:
                    break
            depth.append(d)
        self.end = {}
        self.parent = {-1: -1}
        self.roots = []
        # get the successor of each line (e.g. the line
        # immediately following the end of the block starting at line)
        # and the line starting the section containing each line
        stack = []
        for i in range(N):
            while len(stack) > 0 and depth[stack[-1]] >= depth[i]:
                self.end[stack.pop()] = i
            if len(stack):
                self.parent[i] = stack[-1]
            else:
                self.parent[i] = -1
                self.roots.append(i)
            stack.append(i)
        for x in stack:
            self.end[x] = N
        # create a list of children of each node
        self.children = {}
        for i in range(N):
            if self.parent[i] not in self.children:
                self.children[self.parent[i]] = []
            self.children[self.parent[i]].append(i)
        self.children[-1] = self.roots
        # find sections, definitions, and theorems
        self.secLines = []
        self.defLines = []
        self.thmLines = []
        self.sections = {}
        self.defs = {}
        self.thms = {}
        for i in range(N):
            first, name = parseContent(self.lines[i])
            if first in {'section', 'sec'}:
                self.secLines.append(i)
                self.sections[name] = i
            elif first in {'definition', 'def'}:
                self.defLines.append(i)
                self.defs[name] = i
            elif first in {'theorem', 'thm', 'lemma', 'proposition', 'prop'}:
                self.thmLines.append(i)
                self.thms[name] = i

    def getLine(self, thing):
        ''' Returns the line in the notes where thing is covered.
        If thing is not found, it will return None. '''
        thing = thing.strip().lower()
        if thing in self.sections:
            return self.sections[thing]
        elif thing in self.defs:
            return self.defs[thing]
        elif thing in self.thms:
            return self.thms[thing]
        else:
            return None

    def showLines(self, L):
        ''' Prints the block of the notes starting at the current line,
        at a reasonable rate so that the user can see them.'''
        pos = 0
        while pos < len(L):
            for i in range(min(len(L)-pos, self.chunkSize)):
                print(L[pos])
                pos += 1
            if pos == len(L):
                break
            response = input()
            if response[0] == 'q':
                break
            
    def showBlock(self, lineNum):
        self.showLines(self.lines[lineNum:self.end[lineNum]])

    def showChildren(self, lineNum):
        self.showLines(['(%s) ' % (i) + self.lines[self.children[lineNum][i]] for i in range(len(self.children[lineNum]))])


def prompt(mathNotes):
    pos = -1
    while True:
        cmd = input('>').strip()
        line = mathNotes.getLine(cmd.lower())
        if line != None:
            mathNotes.showBlock(line)
            continue
        cmd = cmd.split()
        first = cmd[0].lower()
        if first == 'ls':
            mathNotes.showChildren(pos)
        elif first == 'cd':
            if cmd[1] == '..':
                pos = mathNotes.parent[pos]
                continue
            n = int(cmd[1])
            if n >= len(mathNotes.children[pos]):
                continue
            pos = mathNotes.children[pos][n]
        elif first == 'all':
            if pos == -1:
                mathNotes.showLines(mathNotes.lines)
            else:
                mathNotes.showBlock(pos)
        elif first == 'quit':
            break
    
def readNotes(filename):
    file = open(filename)
    notes = MathNotes(file.readlines())
    file.close()
    return notes

notes = readNotes('linalg.txt')
prompt(notes)
