"""
Do not write over 80 columns per a line.
This rule doesn't recognize tabs. It only think each character as 1 column.

== Violation ==

    int HEEEEEEEEEEEEEEEEEEELLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO = 1;
    <== Violation. Too long

== Good ==

    int K; <== OK. It's short.
"""
from nsiqcppstyle_reporter import Error, DummyToken
from nsiqcppstyle.nsiqcppstyle_rulemanager import get_ruleManager
from nsiqunittest.nsiqcppstyle_unittestbase import *

def RunRule(lexer, line, lineno):
    if len(line) > 80:
        Error(
            DummyToken(lexer.filename, line, lineno, 0),
            __name__,
            "Lines should very rarely be longer than 80 characters",
        )
    else:
        # print(f'ALL_OK: LINE_LESS_THAN_80_CHARS <{line}>')
        pass

get_ruleManager().AddLineRule(RunRule)



###########################################################################################
# Unit Test
###########################################################################################

from nsiqunittest.nsiqcppstyle_unittestbase import *
class testRule(nct):
    def setUpRule(self):
        get_ruleManager().AddLineRule(RunRule)
    def test1(self):
        self.Analyze("test/thisFile.c",
"""
void function(int k, int j, int pp)
{
%s
}
""" % ("d"*81))
        assert CheckErrorContent(__name__)
    def test2(self):
        self.Analyze("test/thisFile.c",
"""
void function(int k, int j, int pp)
{
%s
%s
}
""" % ("d"*79, " "*90))
        assert not CheckErrorContent(__name__)
