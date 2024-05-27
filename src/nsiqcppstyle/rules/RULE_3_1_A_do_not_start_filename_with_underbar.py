"""
Do not start the file name with underbars.

== Violation ==

    _a.c <== Error
    _bsds.h <== Error

== Good ==
    a.c
    BdSc.h

"""
from nsiqcppstyle_reporter import Error, DummyToken
from nsiqcppstyle.nsiqcppstyle_rulemanager import get_ruleManager
from nsiqunittest.nsiqcppstyle_unittestbase import *


def RunRule(lexer, filename, dirname):
    if filename.startswith("_"):
        nsiqcppstyle_reporter.Error(
            nsiqcppstyle_reporter.DummyToken(lexer.filename, "", 0, 0),
            __name__,
            "File name(%s) should not start with underbar." % filename,
        )


get_ruleManager().AddFileStartRule(RunRule)

##########################################################################
# Unit Test
##########################################################################


class testRule(nct):
    def setUpRule(self):
        get_ruleManager().AddFileStartRule(RunRule)

    def test1(self):
        self.Analyze("_thisfile.c", "")
        self.ExpectError(__name__)

    def test2(self):
        self.Analyze("thi_sfile.c", "")
        self.ExpectSuccess(__name__)
