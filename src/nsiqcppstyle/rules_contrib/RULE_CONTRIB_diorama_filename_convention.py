"""
Do not use the special characters in a filename.
Only alphabets, numbers and underbars can be used for a filename.

== Vilolation ==

    /testdir/test-1.c <== Violation. - is used.

== Good ==

    testdir/test.c
    testdir1/test_1.c 
    /testdir/test-1.c  - is used.
"""
import nsiqcppstyle.nsiqcppstyle_reporter as nsiqcppstyle_reporter
from nsiqcppstyle.nsiqcppstyle_rulemanager import get_ruleManager
import nsiqcppstyle.nsiqcppstyle_checker as nsiqcppstyle_checker
def RunRule(lexer, filename, dirname) :
    if not Match(r"^[\-_A-Za-z0-9\.]*$", filename) :
        nsiqcppstyle_reporter.Error(DummyToken(lexer.filename, "", 0, 0), __name__,
          'Do not use special characters in file name (%s).' % filename)

get_ruleManager().AddFileStartRule(RunRule)






###########################################################################################
# Unit Test
###########################################################################################

from nsiqunittest.nsiqcppstyle_unittestbase import *
class testRule(nct):
    def setUpRule(self):
        get_ruleManager().AddFileStartRule(RunRule)
    
    def test1(self):
        self.Analyze("test2/!thisfile22.c", "")
        assert CheckErrorContent(__name__)
    
    def test2(self):
        self.Analyze("test/this-file.c", "")
        self.Analyze("test/thisfile.c", "")
        self.Analyze("test/thisfile.h", "")
        assert not CheckErrorContent(__name__)
