# This file is part of the Frescobaldi project, http://www.frescobaldi.org/
#
# Copyright (c) 2008, 2009, 2010 by Wilbert Berendsen
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# See http://www.gnu.org/licenses/ for more information.

from __future__ import unicode_literals

"""
Parses and tokenizes Texinfo input, recognizing LilyPond in Texinfo.
"""

from . import (
    Token,
    Leaver,
    Space,
    CommentBase,
    EscapeBase,
    Parser,
    FallthroughParser,
)


class Comment(CommentBase):
    pass


class LineComment(Comment):
    rx = r"@c\b.*$"


class BlockCommentStart(Comment):
    rx = r"@ignore\b"
    def changeState(self, state):
        state.enter(CommentParser)
        
        
class BlockCommentEnd(Comment, Leaver):
    rx = r"@end\s+ignore\b"


class Attribute(Token):
    pass


class Keyword(Token):
    rx = r"@[a-zA-Z]+"


class Block(Token):
    pass


class BlockStart(Block):
    rx = r"@[a-zA-Z]+\{"
    def changeState(self, state):
        state.enter(BlockParser)


class BlockEnd(Block, Leaver):
    rx = r"\}"


class EscapeChar(EscapeBase):
    rx = r"@[@{}]"
    

class Accent(EscapeChar):
    rx = "@['\"',=^`~](\\{[a-zA-Z]\\}|[a-zA-Z]\\b)"


class Verbatim(Token):
    pass


class VerbatimStart(Keyword):
    rx = r"@verbatim\b"
    def changeState(self, state):
        state.enter(VerbatimParser)


class VerbatimEnd(Keyword, Leaver):
    rx = r"@end\s+verbatim\b"
    
    
class LilyPondBlockStart(Block):
    rx = r"@lilypond(?=(\[[a-zA-Z,=0-9\\\s]+\])?\{)"
    def changeState(self, state):
        state.enter(LilyPondBlockAttrParser)


class LilyPondBlockStartBrace(Block):
    rx = r"\{"
    def changeState(self, state):
        state.replace(LilyPondBlockParser)


class LilyPondBlockEnd(Block, Leaver):
    rx = r"\}"
    
    
class LilyPondEnvStart(Keyword):
    rx = r"@lilypond\b"
    def changeState(self, state):
        state.enter(LilyPondEnvAttrParser)
    
    
class LilyPondEnvEnd(Keyword, Leaver):
    rx = r"@end\s+lilypond\b"


class LilyPondFileStart(Block):
    rx = r"@lilypondfile\b"
    def changeState(self, state):
        state.enter(LilyPondFileParser)


class LilyPondFileStartBrace(Block):
    rx = r"\{"
    def changeState(self, state):
        state.replace(BlockParser)


class LilyPondAttrStart(Attribute):
    rx = r"\["
    def changeState(self, state):
        state.enter(LilyPondAttrParser)
    
    
class LilyPondAttrEnd(Attribute, Leaver):
    rx = r"\]"


# Parsers:

class TexinfoParser(Parser):
    items = (
        LineComment,
        BlockCommentStart,
        Accent,
        EscapeChar,
        LilyPondBlockStart,
        LilyPondEnvStart,
        LilyPondFileStart,
        BlockStart,
        VerbatimStart,
        Keyword,
    )


class CommentParser(Parser):
    default = Comment
    items = (
        BlockCommentEnd,
    )


class BlockParser(Parser):
    items = (
        BlockEnd,
        Accent,
        EscapeChar,
        BlockStart,
        Keyword,
    )


class VerbatimParser(Parser):
    default = Verbatim
    items = (
        VerbatimEnd,
    )


class LilyPondBlockAttrParser(Parser):
    items = (
        LilyPondAttrStart,
        LilyPondBlockStartBrace,
    )


class LilyPondEnvAttrParser(FallthroughParser):
    items = (
        LilyPondAttrStart,
    )
    def fallthrough(self, state):
        state.replace(LilyPondEnvParser)


class LilyPondAttrParser(Parser):
    default = Attribute
    items = (
        LilyPondAttrEnd,
    )


class LilyPondFileParser(Parser):
    items = (
        LilyPondAttrStart,
        LilyPondFileStartBrace,
    )


import lilypond

class LilyPondBlockParser(lilypond.LilyPondParserGlobal):
    items = (
        LilyPondBlockEnd,
    ) + lilypond.LilyPondParserGlobal.items


class LilyPondEnvParser(lilypond.LilyPondParserGlobal):
    items = (
        LilyPondEnvEnd,
    ) + lilypond.LilyPondParserGlobal.items
    
