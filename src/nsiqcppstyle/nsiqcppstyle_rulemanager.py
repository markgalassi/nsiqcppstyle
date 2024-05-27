# Copyright (c) 2009 NHN Inc. All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#    * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#    * Neither the name of NHN Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import re
import sys
import importlib


if sys.version_info.minor < 9:
    from typing import Callable
else:
    from collections.abc import Callable

from nsiqcppstyle.nsiqcppstyle_outputer import get_consoleOutputer
console = get_consoleOutputer()
# from nsiqcppstyle.nsiqcppstyle_outputer import _consoleOutputer as console
from nsiqcppstyle.nsiqcppstyle_types import *
from nsiqcppstyle.nsiqcppstyle_util import *  # @UnusedWildImport

# global the_ruleManager
the_ruleManager = None

def set_ruleManager(rm):
    global the_ruleManager
    the_ruleManager = rm
    # print('SETTING: ruleManager to', the_ruleManager)

def get_ruleManager():
    global the_ruleManager
    # print('GETTING: ruleManager is', the_ruleManager)
    return the_ruleManager

class RuleManager:
    def __init__(self, runtimePath):
        # set_ruleManager(self)
        # print(f'INIT: RuleManager {the_ruleManager} - with runtimePath: {runtimePath}')
        self.availRuleNames = []
        # we need to find both builtin rules and contributed rules
        for rule_path in ["rules", "rules_contrib"]:
            basePath = os.path.join(runtimePath, rule_path)
            ruleFiles = os.listdir(basePath)
            rulePattern = re.compile(r"^(.*)\.py$")
            for eachRuleFile in ruleFiles:
                if os.path.isfile(os.path.join(basePath, eachRuleFile)):
                    ruleMatch = rulePattern.match(eachRuleFile)
                    if ruleMatch is not None and eachRuleFile.find("__init__") == -1:
                        ruleName = ruleMatch.group(1)
                        self.availRuleNames.append(ruleName)
        # print("FOUND_RULES:", self.availRuleNames)
        self.availRuleCount = len(self.availRuleNames)
        self.availRuleModules = {}
        self.loadedRule = []
        self.rules = []
        self.preprocessRules = []
        self.commentRules = []
        self.functionNameRules = []
        self.functionScopeRules = []
        self.typeNameRules = []
        self.typeScopeRules = []
        self.lineRules = []
        self.fileEndRules = []
        self.fileStartRules = []
        self.sessionEndRules = []
        self.sessionStartRules = []
        self.projectRules = []
        self.rollBackImporter = None

    #       self.LoadAllRules()

    def LoadRules(self, checkingRuleNames):
        """
        Load Rules. It resets rule before loading rules
        """
        self.ResetRules()
        self.ResetRegisteredRules()
        if self.rollBackImporter is not None:
            self.rollBackImporter.uninstall()

        self.rollBackImporter = RollbackImporter()
        console.Out.Ci(console.Separator)

        # print(f'  ABOUT: LoadRules self: {self} - dir: {dir(self)} - checkingRuleNames: {checkingRuleNames}')
        for ruleName in checkingRuleNames:
            # print('    ruleName:', ruleName)
            count = self.availRuleNames.count(ruleName)
            if count == 0:
                console.Out.Error("%s does not exist or incompatible." % ruleName)
                sys.exit(1)
                continue
            else:
                console.Out.Info("  - ", ruleName, "is applied.")
            try:
                if ruleName.startswith('RULE_CONTRIB_'):
                    # ruleModule = __import__("rules_contrib." + ruleName)
                    ruleModule = importlib.import_module("rules_contrib." + ruleName)
                else:
                    # ruleModule = __import__("rules." + ruleName)
                    ruleModule = importlib.import_module("rules." + ruleName)
                # print('JUST_LOADED_DICT:', ruleModule.__dict__.keys())
                # print('JUST_LOADED_RunRule:', ruleModule.RunRule)
            except Exception as err:
                print(f'*warning* - error when loading rule <{ruleName}> - err: {err=}, {type(err)=}')
                sys.exit(1)
            try:
                self.loadedRule.append(ruleModule)
            except:
                print(f'*error* - self.loadedRule.append(ruleModule.RunRule) - {ruleModule.RunRule}')
                exit(1)
            # # now add to the appropriate rule list according to the
            # # addition_type variable
            # print('ADDITION_TYPE:', dir(ruleModule))
            # print('ADDITION_TYPE:', ruleModule.__dict__.keys())
            # print('ADDITION_TYPE:', ruleModule.addition_type)
            # print('ADDITION_TYPE:', ruleModule.RunRule)
            # # now use the "addition_type" string from the module to
            # # form an instruction that we can eval()
            # func_to_eval = 'self.' + ruleModule.addition_type + '(ruleModule.RunRule)'
            # print('FUNC_TO_EVAL:', func_to_eval)
            # eval(func_to_eval)
            # if ruleModule.addition_type == 'AddFileStartRule':
            #     print(f'self.AddFileStartRule(ruleModule.RunRule)')
            #     self.AddFileStartRule(ruleModule.RunRule)
        if len(self.loadedRule) == 0:
            console.Out.Ci("  No Rule is specified. Please configure rules in filefilter.txt.")
        console.Out.Ci(console.Separator)

    def ResetRules(self):
        self.loadedRule = []

    ##########################################################################
    # Rule Runner
    ##########################################################################
    def RunPreprocessRule(self, lexer, contextStack):
        """Run rules which runs in the preprecessor blocks"""
        for preprocessRule in self.preprocessRules:
            data = lexer.Backup()
            preprocessRule(lexer, contextStack)
            lexer.Restore(data)

    def RunCommentRule(self, lexer, token):
        """Rule when a comment is encountered"""
        for eachCommentRule in self.commentRules:
            data = lexer.Backup()
            eachCommentRule(lexer, token)
            lexer.Restore(data)

    def RunFunctionNameRule(self, lexer, functionFullName, decl, contextStack, functionContext):
        """Run rules which runs on the function name"""
        for eachFunctionNameRule in self.functionNameRules:
            data = lexer.Backup()
            eachFunctionNameRule(lexer, functionFullName, decl, contextStack, functionContext)
            lexer.Restore(data)

    def RunFunctionScopeRule(self, lexer, contextStack):
        """Run rules which runs in the function blocks"""
        for eachFunctionScopeRule in self.functionScopeRules:
            data = lexer.Backup()
            eachFunctionScopeRule(lexer, contextStack)
            lexer.Restore(data)

    def RunTypeNameRule(self, lexer, typeName, typeFullName, decl, contextStack, typeContext):
        """Run rules which runs on the type names"""
        for typeNameRule in self.typeNameRules:
            data = lexer.Backup()
            typeNameRule(lexer, typeName, typeFullName, decl, contextStack, typeContext)
            lexer.Restore(data)

    def RunTypeScopeRule(self, lexer, contextStack):
        """Run rules which runs in the type blocks"""
        for typeScopeRule in self.typeScopeRules:
            data = lexer.Backup()
            typeScopeRule(lexer, contextStack)
            lexer.Restore(data)

    def RunRule(self, lexer, contextStack):
        """Run rules which runs in any tokens"""
        for rule in self.rules:
            data = lexer.Backup()
            rule(lexer, contextStack)
            lexer.Restore(data)

    def RunLineRule(self, lexer, line, lineno):
        """Run rules which runs in each lines."""
        # print(f'      IN_RunLineRule(): {len(self.lineRules)} {lexer} {line} {lineno}')
        for lineRule in self.lineRules:
            data = lexer.Backup()
            # print(f'        RUNLINERULE: {type(lineRule)} {lineRule.__name__} data: {data}')
            try:
                lineRule(lexer, line, lineno)
            except:
                print(f'*warning* - exception in lineRule <{lineRule.__name__}> - err: {err=}, {type(err)=}')
                sys.exit(1)
            lexer.Restore(data)

    def RunFileEndRule(self, lexer, filename, dirname):
        """Run rules which runs at the end of files."""
        for fileEndRule in self.fileEndRules:
            data = lexer.Backup()
            fileEndRule(lexer, filename, dirname)
            lexer.Restore(data)

    def RunFileStartRule(self, lexer, filename, dirname):
        """Run rules which runs at the start of files."""
        for fileStartRule in self.fileStartRules:
            data = lexer.Backup()
            fileStartRule(lexer, filename, dirname)
            lexer.Restore(data)

    def RunSessionEndRules(self):
        """Run rules which runs at the end of the script session."""
        for sessionEndRule in self.sessionEndRules:
            sessionEndRule()

    def RunSessionStartRules(self):
        """Run rules which runs at the start of the script session."""
        for sessionStartRule in self.sessionStartRules:
            sessionStartRule()

    def RunProjectRules(self, targetName):
        """Run rules which runs once a project."""
        for projectRule in self.projectRules:
            projectRule(targetName)

    ##########################################################################
    # Rule Resister Methods
    ##########################################################################

    def ResetRegisteredRules(self):
        """Reset all registered rules."""

        self.functionNameRules.clear()
        self.functionScopeRules.clear()
        self.lineRules.clear()
        self.rules.clear()
        self.typeNameRules.clear()
        self.typeScopeRules.clear()
        self.fileStartRules.clear()
        self.fileEndRules.clear()
        self.sessionStartRules.clear()
        self.sessionEndRules.clear()
        self.projectRules.clear()
        self.preprocessRules.clear()
        self.commentRules.clear()

    def AddPreprocessRule(self, user_function: Callable[[Lexer, ContextStack], None]):
        """Add rule which runs in preprocess statements"""
        self.preprocessRules.append(user_function)

    def AddCommentRule(self, user_function: Callable[[Lexer, Token], None]):
        """Add rule which runs when a comment is encountered"""
        self.commentRules.append(user_function)

    def AddFunctionScopeRule(self, user_function: Callable[[Lexer, ContextStack], None]):
        """Add rule which runs in function scope"""
        self.functionScopeRules.append(user_function)

    def AddFunctionNameRule(
        self,
        user_function: Callable[[Lexer, FullFunctionName, Declaration, ContextStack, Context], None],
    ):
        """Add rule on the function name place"""
        self.functionNameRules.append(user_function)

    def AddLineRule(self, user_function: Callable[[Lexer, LineText, LineNumber], None]):
        """Add rule on the each line"""
        import inspect
        # print('  FILE_FUNC:', __file__, inspect.currentframe().f_code.co_name)
        # print('  ADDED_FUNC:', user_function.__qualname__)
        # print('    ', len(self.lineRules), self.lineRules)
        self.lineRules.append(user_function)
        # print('    ', len(self.lineRules), self.lineRules)

    def AddRule(self, user_function: Callable[[Lexer, ContextStack], None]):
        """Add rule on any token"""
        self.rules.append(user_function)

    def AddTypeNameRule(
        self,
        user_function: Callable[[Lexer, TypeName, TypeFullName, Declaration, ContextStack, Context], None],
    ):
        """Add rule on any type (class / struct / union / namespace / enum)"""
        self.typeNameRules.append(user_function)

    def AddTypeScopeRule(self, user_function: Callable[[Lexer, ContextStack], None]):
        """Add rule when the token is within a type definition scope"""
        self.typeScopeRules.append(user_function)

    def AddFileEndRule(self, user_function: Callable[[Lexer, FileName, DirName], None]):
        """Add rule on the file end"""
        self.fileEndRules.append(user_function)

    def AddFileStartRule(self, user_function: Callable[[Lexer, FileName, DirName], None]):
        """Add rule on the file start"""
        self.fileStartRules.append(user_function)

    def AddSessionEndRule(self, user_function: Callable[[], None]):
        """
        Add rule on the session end.

        This rule is called when the script has finished processing all target files.
        It is called only once at the end of the script's run.
        """
        self.sessionEndRules.append(user_function)

    def AddSessionStartRule(self, user_function: Callable[[], None]):
        """
        Add rule on the session start

        This rule is called before the script begins processing the first target file.
        It is called only once at the start of the script's processing activities.
        """
        self.sessionStartRules.append(user_function)

    def AddProjectRules(self, user_function: Callable[[TargetDirectory], None]):
        """Add rule on the project"""
        self.projectRules.append(user_function)


class RollbackImporter:
    def __init__(self):
        """Creates an instance and installs as the global importer"""
        self.previousModules = sys.modules.copy()
        self.realImport = __builtins__["__import__"]
        __builtins__["__import__"] = self._import
        self.newModules = {}

    def _import(self, name, *args, **kwargs):
        result = self.realImport(name, *args, **kwargs)
        if name.find("rules") != -1:
            self.newModules[name] = 1
        return result

    def uninstall(self):
        for modname in self.newModules:
            if modname.find("rules") != -1 and modname not in self.previousModules:
                # Force reload when modname next imported
                del sys.modules[modname]
        __builtins__["__import__"] = self.realImport

# import traceback
# traceback.print_stack()
# runtimePath = GetRuntimePath()
# ruleManager = RuleManager(runtimePath)
# print('INIT_AND_RUN: ruleManager after:', ruleManager, 'runtimePath:', runtimePath , __file__)
# traceback.print_stack()
