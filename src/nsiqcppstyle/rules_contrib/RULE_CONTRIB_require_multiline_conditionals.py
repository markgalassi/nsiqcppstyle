"""
Conditionals should be multiline, LH bracket on same line, brackets aligned, .


== Violation ==

    void function() 
    {
        if (k) { do something; } <== Violation. it should be multiline
        if (k)
        { <== Violation. left bracket should be on same line as condition
         do something; } <== Violation. right bracket should be aligned
        if     (k) { <== Violation. spacing  should be 'if (k)'
        }
    }

== Good ==
    
    void function() {
        if (k) { <== OK
        } else { <== OK
        }
        if(k) { <== OK
        }
    }
"""

from nsiqcppstyle_rulehelper import  *
from nsiqcppstyle_reporter import *
from nsiqcppstyle_rulemanager import *

def RunRule(lexer, contextStack) :
    t = lexer.GetCurToken()
    if t.type in ("IF", "WHILE") :
        spaces = 0
        t2 = lexer.GetNextToken(False, True, True)
        if t2 != None and t2.type == "SPACE" and len(t2.value) > 1:
            nsiqcppstyle_reporter.Error(t2, __name__, "Too much spacing in conditional '%s%s('." % (t.value, t2.value))

        t3 = lexer.GetNextTokenInType("LBRACE", False, True)
        if t3 != None:
            if t.lineno != t3.lineno:
                nsiqcppstyle_reporter.Error(t3, __name__, "Left brace must be on the same line as the conditional keyword '%s'. " % t.value)
            t4 = lexer.GetNextMatchingToken(False)
            prevToken = lexer.GetPrevTokenSkipWhiteSpaceAndCommentAndPreprocess()
            if t4 != None and prevToken != None and \
                    prevToken.lineno == t4.lineno :
                nsiqcppstyle_reporter.Error(t4, __name__, "The closing brace ('%s') for conditionals should be located alone in a line ('%s')" % (t4.value, prevToken.value))
            if t4.lineno != t.lineno and GetRealColumn(t4) != GetRealColumn(t) :
                nsiqcppstyle_reporter.Error(t4, __name__, "The closing brace should be located in same column as the keyword '%s'" % t.value)

ruleManager.AddFunctionScopeRule(RunRule)







###########################################################################################
# Unit Test
###########################################################################################

from nsiqunittest.nsiqcppstyle_unittestbase import *
class testRule(nct):
    def setUpRule(self):
        ruleManager.AddFunctionScopeRule(RunRule)
    def test1(self):
        self.Analyze("test/thisFile.c", 
"""
void function(int k, int j, int pp)
{
    if (AA == D)
    {
    }
}
""")
        assert CheckErrorContent(__name__)    
    def test2(self):
        self.Analyze("test/thisFile.c", 
"""
void function(int k, int j, int pp)
{
    if (AA == D) { }
}
""")
        assert CheckErrorContent(__name__)    
    def test3(self):
        self.Analyze("test/thisFile.c", 
"""
void function(int k, int j, int pp)
{
    while (AA == D) {
      something(); }
}
""")
        assert CheckErrorContent(__name__)    
    def test4(self):
        self.Analyze("test/thisFile.c", 
"""
void function(int k, int j, int pp)
{
    if    (AA == D)    {
    }
}
""")
        assert CheckErrorContent(__name__)    
    def test5(self):
        self.Analyze("test/thisFile.c", 
"""
void function(int k, int j, int pp)
{
    if (AA == D)    {
           }
}
""")
        assert CheckErrorContent(__name__)    
    def test6(self):
        self.Analyze("test/thisFile.c", 
"""
void F() {
    if(k) {
    }
}
""")
        assert not CheckErrorContent(__name__)    
