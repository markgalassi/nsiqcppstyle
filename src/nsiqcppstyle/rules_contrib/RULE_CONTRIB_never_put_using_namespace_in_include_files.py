"""
Do not allow "using namespace" at the top level in header files.
It's OK in .c* files.

== Violation in an include file ==

    #define "I am in a .h file"
    using namespace std;

== Good ==

    #define "I am in a .h file"
    void f() {
      using namespace std;
      cout << "dude\n";
    }

"""

from nsiqunittest.nsiqcppstyle_unittestbase import *
from nsiqcppstyle.nsiqcppstyle_rulehelper import *
import nsiqcppstyle.nsiqcppstyle_reporter as nsiqcppstyle_reporter
from nsiqcppstyle.nsiqcppstyle_rulemanager import get_ruleManager


def RunRule(lexer, file_basename, file_dirname):
    if lexer.filename[-2:] != '.h' and not lexer.filename[-4:] in ('.hpp', '.hxx'):
        console.Out.Verbose('hey, we are NOT in a .h file')
        return # get out non-header files: this rule does not apply there
    for lineno, line in enumerate(lexer.lines):
        console.Out.Verbose('line:', line)
        if Search("^using namespace", line):
            nsiqcppstyle_reporter.Error(DummyToken(
                lexer.filename, line, lineno, 0), __name__, 
                  'Never put "using namespace" at top level in include files')
    pass

get_ruleManager().AddFileStartRule(RunRule)

##########################################################################
# Unit Test
##########################################################################


class testRule(nct):
    def setUpRule(self):
        get_ruleManager().AddFunctionNameRule(RunRule)

    def test1(self):
        self.Analyze("thisfile.hpp", "int k() {%s};"
                     % ("void f\n{\n"
                        + "using namespace std;\n"
                        + "cout << 2.5 << '\\n'\n}\n"))
        self.ExpectSuccess(__name__)

    def test2(self):
        self.Analyze("thisfile.hpp", "int k() {%s};"
                     % ("using namespace std;\nvoid f\n{\n"
                        + "cout << 2.5 << '\\n'\n}\n"))
        self.ExpectError(__name__)
