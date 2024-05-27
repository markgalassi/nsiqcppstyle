"""
Do not indent statements inside of a namespace.

== Violation ==

namespace nsA{

  static int a = (3 + 2); <== Violation

void func1(int z, double x){}
  static int e;           <== Violation

  void func2(){           <== Violation
    ;
  }                       <== Violation

namespace nsB{int x; 
              int y;}
  int z;                  <== Violation

} /* nsA */

== Good ==

namespace nsC{
static int b =
  (2 + 3);

static int c = (1 + 
                1)
static int d =
    6;

typedef std::vector<
  int> marmot_t;

void func1(int z,
           double x){
}

int f[2][2] = {{1,1}
               {2,2}};

} /* nsC */
"""

from nsiqcppstyle_reporter import *
from nsiqcppstyle_rulemanager import *
from nsiqcppstyle_rulehelper import *
import re

# regex match for a completed statement (e.g. one ending in a semicolon or
# consisting of a '}' alone as at the end of a namespace or function).
statementRe = re.compile('(.*;|})\s*((/[*]|//).*)?')

# was the last line we processed complete?
lineComplete = True

def RunRule(lexer, line, lineno) :
    # print 'IN_FILE:', __file__, len(line), line
    global lineComplete

    t = lexer.GetCurToken()
    contextStack = t.contextStack

    # get list of tokens up to and including the current one.
    # print 'ABOUT: tokens'
    tokens = lexer.tokenlist[:lexer.tokenlist.index(t) + 1]
    # print 'TOKENS:', tokens
    #print contextStack.Peek().type, ":", lineComplete, ":", line

    # Only work in namespace scope
    if contextStack != None:
        the_peek = contextStack.Peek()
        if the_peek != None and contextStack.Peek().type == "NAMESPACE_BLOCK":
            # only check the rule if the last line was completed
            if lineComplete and line[0] == ' ':
                mess = "Indented namespace on line %d (%s)" %(lineno, line)
                nsiqcppstyle_reporter.Error(DummyToken(lexer.filename, line, 
                                                       lineno, 0), __name__, mess)
            lineComplete = (statementRe.match(line) is not None)
        else:
            # reset line state if we switch context
            lineComplete = True

ruleManager.AddLineRule(RunRule)

###########################################################################################
# Unit Test
###########################################################################################

from nsiqunittest.nsiqcppstyle_unittestbase import *

class testRule(nct):
    def setUpRule(self):
        ruleManager.AddRule(RunRule)
        
    def test1(self):
        self.Analyze("thisfile.c","""
namespace test {
  void function() {
  
  }
}
""")
        assert CheckErrorContent(__name__)
        
    def test2(self):
        self.Analyze("thisfile.c","""
namespace test1 {
  namespace test2 {
    void function() {
    
    }
  }
}
""")
        assert CheckErrorContent(__name__)
        
    def test3(self):
        self.Analyze("thisfile.c","""
namespace test1 {
namespace test2 {
void function() {

}
}
}
""")
        assert not CheckErrorContent(__name__)
        
    def test4(self):
        self.Analyze("thisfile.c","""
namespace test1 {
int v1 = 0;
namespace test2 {
void function() {

}
}
}
""")
