# -----------------------------------------------------------------------------
# This file was developed by Juliano Vieira Martins.
# julianovmartins@gmail.com
# Creation Date: Sept/2023
# Updated Date: Oct/2023
# Version: 2.0.0
# Description: This is a test file for the Udacity project:
# "Adventure Game DECI - LVL 2".
# Copyright © 2023, Juliano Martins. All rights reserved.
# -----------------------------------------------------------------------------

import argparse
import ast
import io
import os
import re
import subprocess
import sys
import tokenize
import unittest

import pycodestyle

python_command = sys.executable


def msg_color(message, color):
    color_codes = {
        "red": "\033[1;91m",
        # "green": "\033[1;92m",
        "blue": "\033[1;94m",
        # "orange": "\033[1;93m",
        # "yellow": "\033[1;33m",
        # "purple": "\033[1;95m",
        # "cyan": "\033[1;96m",
        # "white": "\033[1;97m",
        "end": "\033[0m"
    }
    colored_message = (f"{color_codes.get(color, color_codes['end'])}"
                       f"{message}{color_codes['end']}")
    return colored_message


def remove_comments(source_code):
    """ Remove all comments from the code """

    io_obj = io.StringIO(source_code)
    out = []
    prev_tok_type = tokenize.INDENT
    last_lineno = -1
    last_col = 0

    for tok in tokenize.generate_tokens(io_obj.readline):
        token_type, token_string, start, end, line_text = tok
        start_line, start_col = start
        end_line, end_col = end

        # handle new line
        if start_line > last_lineno:
            last_col = 0

        # handle spaces
        if start_col > last_col:
            out.append(" " * (start_col - last_col))

        # skip comments
        if token_type == tokenize.COMMENT:
            pass
        elif token_type == tokenize.STRING:
            if prev_tok_type != tokenize.INDENT:
                if prev_tok_type != tokenize.NEWLINE:
                    if start_col > 0:
                        out.append(token_string)
        else:
            out.append(token_string)

        prev_tok_type = token_type
        last_col = end_col
        last_lineno = end_line

    return ''.join(out)


def check_pep8_compliance(file_target, errors):
    """
    This function serves to verify the compliance of a Python source file
    with the PEP 8 style guide."""

    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    style = pycodestyle.StyleGuide(show_source=False)
    result = style.check_files([file_target])
    sys.stdout = old_stdout
    if hasattr(result, '_deferred_print'):
        # noinspection PyProtectedMember
        for line, col, error_code, message in (item[:4] for item in
                                               result._deferred_print):
            if error_code in errors:
                return f"Line: {line}, Column: {col}: {message}"
    return None


class StudentFileDetector(ast.NodeVisitor):
    """
    This class extends the `ast.NodeVisitor` class from Python's Abstract
    Syntax Tree (AST) library. Its primary purpose is to perform static code
    analysis on a Python source file to identify and catalog various constructs
    and idioms used within the code. The class relies on the visitor pattern
    for traversal and analysis of AST nodes.
    """

    def __init__(self):
        self.stdout_write_statements = set()
        self.function_definitions = set()
        self.variable_assignments = set()
        self.function_with_input = set()
        self.function_with_while = set()
        self.function_names = set()
        self.recursive_calls = set()
        self.print_statements = set()

    @staticmethod
    def set_parents(tree):
        """
        Annotates each AST node in the tree with its corresponding parent node.
        """
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                child.parent = parent

    @staticmethod
    def find_parent_function(node):
        """
        Traverses the AST hierarchy in search of a parent "FunctionDef" node
        for a given node. Returns the name of the parent function if found;
        otherwise, returns None.
        """
        current = node
        while current:
            if isinstance(current, ast.FunctionDef):
                return current.name
            current = getattr(current, "parent", None)

    def visit_Call(self, node):
        """
        Visits "Call" nodes to identify instances where the "input()" function
        is invoked. Adds the name of the parent function to the
        "function_with_input" set if it exists.
        """
        if isinstance(node.func, ast.Name):
            if node.func.id == "input":
                parent_function = self.find_parent_function(node)
                if parent_function is not None:
                    self.function_with_input.add(parent_function)
            elif node.func.id == "print":
                parent_function = self.find_parent_function(node)
                if parent_function is not None:
                    self.print_statements.add((parent_function, node.lineno))
        elif isinstance(node.func, ast.Attribute):
            parent_function = self.find_parent_function(node)
            if node.func.attr == "write" and isinstance(
                    node.func.value, ast.Attribute
            ) and node.func.value.attr == 'stdout':
                if parent_function is not None:
                    self.stdout_write_statements.add(
                        (parent_function, node.lineno)
                    )

        self.generic_visit(node)

    def visit_Assign(self, node):
        """
        Visits "Assign" nodes to identify variable assignments. Adds a tuple
        of parent function name, variable name, and the node itself to the
        "variable_assignments" set.
        """
        parent_function = self.find_parent_function(node)
        parent_function = parent_function if parent_function \
            else "global_scope"
        for target in node.targets:
            if isinstance(target, ast.Name):
                variable_name = target.id
                self.variable_assignments.add(
                    (parent_function, variable_name, node))
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        """
        Visits "AugAssign" nodes to identify augmented assignments like "+=",
        "-=", etc. Adds a tuple of parent function name, variable name, and
        the node itself to the "variable_assignments" set.
        """
        parent_function = self.find_parent_function(node)
        parent_function = parent_function if parent_function \
            else "global_scope"
        if isinstance(node.target, ast.Name):
            variable_name = node.target.id
            self.variable_assignments.add(
                (parent_function, variable_name, node))
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """
        Visits "FunctionDef" nodes to identify function definitions, "while"
        loops, and recursive calls.Adds the function name to the
        "function_names" set. And if applicable, to "function_with_while" and
        "recursive_calls" sets.
        """
        function_name = node.name
        self.function_names.add(function_name)
        self.function_definitions.add((function_name, node))

        for sub_node in ast.walk(node):
            if isinstance(sub_node, ast.While):
                self.function_with_while.add(function_name)
            elif (isinstance(sub_node, ast.Call) and
                  isinstance(sub_node.func, ast.Name) and
                  sub_node.func.id == function_name):
                self.recursive_calls.add(function_name)
        self.generic_visit(node)


class SuppressTracebackTextTestResult(unittest.TextTestResult):
    """ The SuppressTracebackTextTestResult class is a subclass of unittest.
    TextTestResult, specifically tailored to suppress the display of
    traceback information in the test output.
    """
    separator1 = ''
    separator2 = ''
    separator3 = '=' * 70

    def getDescription(self, test):
        description = super().getDescription(test)
        match = re.search(r'(SubTest: [^]]+)', description)
        if match:
            return msg_color(match.group(1), "blue")
        return description

    def printErrorList(self, flavour, errors):
        for test, err in errors:
            self.stream.write(self.separator3)
            self.stream.write("\n")
            self.stream.write(self.getDescription(test))
            self.stream.write("\n")
            self.stream.write("%s" % err)
            self.stream.write("\n")
            self.stream.flush()

    @staticmethod
    def _exc_info_to_string(err, _):
        return f"{err[1]}"


class SuppressTracebackTextTestRunner(unittest.TextTestRunner):
    """ The SuppressTracebackTextTestRunner class is a subclass of unittest.
    TextTestRunner designed to utilize the custom result class
    SuppressTracebackTextTestResult. Its primary purpose is to execute test
    cases while suppressing traceback information in the test output.
    """
    resultclass = SuppressTracebackTextTestResult


class AdventureGameTests(unittest.TestCase):
    """ This class serves as a testing framework for evaluating
    functionalities associated with adventure games. """
    tree = None
    detector = None
    file_content = None
    longMessage = False

    def shortDescription(self):
        return None

    @classmethod
    def setUpClass(cls):
        """ A class method responsible for initializing class-level variables.
        It reads the content of the Python file under test, instantiates the
        StudentFileDetector, parses the content into an AST, and invokes the
        visit method from the detector."""

        # Setup for load file
        with open(file_name, "r") as f:
            cls.file_content = f.read()
        cls.detector = StudentFileDetector()
        cls.tree = ast.parse(cls.file_content)
        cls.detector.set_parents(cls.tree)
        cls.detector.visit(cls.tree)

    def test_output_to_console(self):
        """
        A unit test that verifies the presence of console outputs in the Python
        script, based on specific criteria. Utilizes the `print_statements`
        attribute of the `StudentFileDetector` class to ascertain the locations
        of `print()` statements.
        """
        subtest_message = "SubTest: Checking for output descriptions..."
        try:
            with self.subTest(subtest_message):
                # Check for print statements
                has_print_statements = any(
                    line for function, line in self.detector.print_statements)

                # Check for sys.stdout.write statements
                # This assumes that stdout_write_statements is an attribute
                # in StudentFileDetector
                has_stdout_write_statements = any(
                    line for function,
                    line in self.detector.stdout_write_statements)

                self.assertTrue(
                    has_print_statements or has_stdout_write_statements,
                    msg_color(
                        "Neither 'print()' nor 'sys.stdout.write()' "
                        "statement was found in the code.", "red")
                )
        except AssertionError as ae:
            self.fail(
                msg_color(f"Assertion error occurred: {ae}", "red")
            )
        except Exception as e:
            self.fail(
                msg_color(f"An unspecified exception occurred: {e}", "red")
            )

    def test_import_and_function_usage(self):
        """
        Verifies the importation of specific modules and the utilization of
        particular functions within a Python script. The method employs regular
        expressions to search for these elements in the content of the file.
        """
        subtest_message = "SubTest: Checking for import of 'time' module..."
        try:
            # Regular expressions to find import statements and function usage
            import_time_re = re.compile(
                r"^\s*import\s+(?:[\w, ]*,\s*)?time(?:\s*,\s*[\w, ]*)?$|^\s*"
                r"from\s+time\s+import\s+\w+",
                re.MULTILINE)
            import_random_re = re.compile(
                r"^\s*import\s+(?:[\w, ]*,\s*)?random(?:\s*,\s*[\w, ]*)?$|^\s*"
                r"from\s+random\s+import\s+\w+",
                re.MULTILINE)
            time_sleep_re = re.compile(r"(time\.sleep\()|(sleep\()",
                                       re.MULTILINE)
            random_function_re = re.compile(r"random\.\w+\(",
                                            re.MULTILINE)

            # SubTest for import of "time" module
            with self.subTest(subtest_message):

                self.assertTrue(
                    import_time_re.search(self.file_content),
                    msg_color("The 'time' module was not imported.", "red")
                )

            # SubTest for import of "random" module
            with self.subTest(
                    msg_color(
                        "SubTest: Checking import of 'random' module",
                        "blue")):
                self.assertTrue(
                    import_random_re.search(self.file_content),
                    msg_color("The 'random' module was not imported.",
                              "red")
                )

            # SubTest for usage of "time.sleep" function
            with self.subTest(
                    msg_color("SubTest: Checking usage of "
                              "'time.sleep' function", "blue")):
                self.assertTrue(
                    time_sleep_re.search(self.file_content),
                    msg_color("The 'time.sleep' function was not "
                              "used.", "red")
                )

                # SubTest for usage of any function from "random" module
                with self.subTest(
                        msg_color(
                            "SubTest: Checking usage of functions "
                            "from 'random' module", "blue")):
                    self.assertTrue(
                        random_function_re.search(self.file_content),
                        msg_color(
                            "No function from the 'random' module was used.",
                            "red")
                    )
        except AssertionError as ae:
            self.fail(
                msg_color(f"Assertion error occurred: {ae}", "red")
            )
        except Exception as e:
            self.fail(
                msg_color(f"An unspecified exception occurred: {e}", "red")
            )

    def test_interactive_elements(self):
        """
        Validates the presence of key interactive constructs such as "input",
        "if/elif/else", and "while" in the Python script. Regular expressions
        are employed to detect these constructs in the file content.
        """
        try:
            # Define regular expressions for the constructs
            input_re = re.compile(r"input\s?\(", re.MULTILINE)
            if_elif_else_re = re.compile(r"\bif\b|\belif\b|\belse\b",
                                         re.MULTILINE)
            while_re = re.compile(r"\bwhile\b", re.MULTILINE)

            constructs = [
                ("input", input_re),
                ("if/elif/else", if_elif_else_re),
                ("while", while_re)
            ]

            for name, regex in constructs:
                subtest_message = f"SubTest: Checking for usage of '{name}'..."
                with self.subTest(subtest_message):
                    count = len(regex.findall(self.file_content))
                    self.assertGreaterEqual(
                        count, 1,
                        msg_color(f"The statement '{name}' "
                                  f"was found {count} times in your code.",
                                  "red")
                    )
        except AssertionError as ae:
            self.fail(
                msg_color(f"Assertion error occurred: {ae}", "red")
            )
        except Exception as e:
            self.fail(
                msg_color(f"An unspecified exception occurred: {e}", "red")
            )

    def test_input_while_or_recursive(self):
        """
        Examines the functions in the Python script for the presence of
        "input()" calls, and verifies that these functions also include either
        a "while" loop or a recursive call. This is done to ensure that
        functions taking user input also include control flow mechanisms that
        can manage the input appropriately.
        """
        subtest_message = "SubTest: Checking for 'input()' validation..."
        try:
            functions_with_input = self.detector.function_with_input
            functions_with_while = self.detector.function_with_while
            functions_with_recursive_calls = self.detector.recursive_calls

            with self.subTest(subtest_message):
                for func in functions_with_input:
                    self.assertTrue(
                        func in functions_with_while or
                        func in functions_with_recursive_calls,
                        msg_color(
                            f"The function '{func}()' contains an 'input()' "
                            f"but lacks either a 'while' loop or a recursive "
                            f"call for itself.", "red"))
        except AssertionError as ae:
            self.fail(
                msg_color(f"Assertion error occurred: {ae}", "red")
            )
        except Exception as e:
            self.fail(
                msg_color(f"An unspecified exception occurred: {e}", "red")
            )

    def test_variable_for_score_exists(self):
        """
        Inspects the Python script for the presence of a variable that appears
        to maintain and update a game score. The method examines both regular
        assignment operations and augmented assignment operations
        (e.g., +=, -=) with respect to the variable. It specifically looks for
        binary operations involving addition or subtraction in the assignment.
        """
        subtest_message = "SubTest: Checking for the scoring system..."
        # Variable to hold whether the criteria are met
        criteria_met = False

        try:
            with self.subTest(subtest_message):
                for func_name, variable_name, node \
                        in self.detector.variable_assignments:
                    variable_name = variable_name.lower()
                    if "score" not in variable_name:
                        continue
                    if isinstance(node, ast.Assign):
                        if isinstance(node.value, ast.BinOp) and (
                                isinstance(node.value.op, ast.Add) or
                                isinstance(node.value.op, ast.Sub)):
                            criteria_met = True
                            break
                    elif isinstance(node, ast.AugAssign):
                        if isinstance(node.op, (ast.Add, ast.Sub)):
                            criteria_met = True
                            break

                    if criteria_met:
                        break

                self.assertTrue(criteria_met, msg_color(
                    "No variable found for maintaining and updating the game "
                    "score based on contextual analysis.", "red"))
        except AssertionError as ae:
            self.fail(
                msg_color(f"Assertion error occurred: {ae}", "red")
            )
        except Exception as e:
            self.fail(
                msg_color(f"An unspecified exception occurred: {e}", "red")
            )

    def test_function_definitions(self):
        """
        Conducts an assessment to ascertain the existence of a minimum of four
        function definitions within the code under examination. The method
        employs the Abstract Syntax Tree (AST) to identify said function
        definitions.
        """
        subtest_message = ("SubTest: Checking the existence of at "
                           "least four function definitions...")
        # Retrieve the set of function definitions from the AST detector
        function_definitions = self.detector.function_definitions
        try:
            # Assert that at least four function definitions exist
            with self.subTest(subtest_message):
                self.assertGreaterEqual(
                    len(function_definitions), 4,
                    msg_color(f"Only {len(function_definitions)} "
                              f"function definitions were found, at least "
                              f"four are required.", "red")
                )
        except AssertionError as ae:
            self.fail(
                msg_color(f"Assertion error occurred: {ae}", "red")
            )
        except Exception as e:
            self.fail(
                msg_color(f"An unspecified exception occurred: {e}", "red")
            )

    def test_pep8_compliance(self):
        """
        Executes a suite of subtests aimed at verifying the compliance of the
        code under scrutiny with the PEP8 style guidelines. Utilizes string
        manipulation and regular expression matching for the assessment of
        various aspects such as indentation, line length, and quoting
        conventions.
        """
        subtest_message = "SubTest: Checking for PEP8 compliance..."
        try:
            with self.subTest(subtest_message):

                # 1. 4 spaces per indentation level

                errors = ['E101', 'E111', 'E112', 'E113', 'E114', 'E115',
                          'E116', 'E117', 'E121', 'E122', 'E123', 'E124',
                          'E125', 'E126', 'E127', 'E128', 'E129', 'E131',
                          'E133', 'W191']

                result = check_pep8_compliance(file_name, errors)

                self.assertIsNone(
                    result, msg_color(
                        f"PEP8 errors found: {result}", "red"))

                lines = self.file_content.split("\n")

                single_quotes = []
                double_quotes = []

                for line_number, line in enumerate(lines, start=1):

                    # 2. Spaces are used, not tabs
                    self.assertFalse(
                        "\t" in line, msg_color(
                            f"Line {line_number}: Tab character "
                            f"detected.", "red"
                        )
                    )

                    # 3. Line length is less than 80 characters
                    self.assertLess(
                        len(line), 80, msg_color(
                            f"Line {line_number}: Exceeds 80 characters.",
                            "red"
                        )
                    )

                    # 4. import statements are on separate lines
                    self.assertFalse(
                        "," in line and line.lstrip().startswith("import "),
                        msg_color(f"Line {line_number}: Multiple "
                                  f"imports on one line.", "red"))

                    # 5. code uses single quotes or double quotes
                    # Keep track the type of string we are in
                    # (None, "'", or '"')
                    in_string = None
                    in_comment = False

                    for char in line:
                        # Detect if we are in a comment
                        if char == '#' and in_string is None:
                            in_comment = True

                        # Skip quote checks if in a comment
                        if in_comment:
                            continue

                        # This condition ensures we are not inside a
                        # single-quoted string
                        if char == '"' and in_string != "'":
                            if in_string == '"':
                                # We are closing a double-quoted string
                                in_string = None
                            else:
                                double_quotes.append(line_number)
                                # We are opening a double-quoted string
                                in_string = '"'
                        # This condition ensures we are not inside a
                        # double-quoted string
                        elif char == "'" and in_string != '"':
                            if in_string == "'":
                                # We are closing a single-quoted string
                                in_string = None
                            else:
                                single_quotes.append(line_number)
                                # We are opening a single-quoted string
                                in_string = "'"
                    # If both types of quotes are used for string delimiters,
                    # fail the test.
                    if single_quotes and double_quotes:
                        text = (f"Line {single_quotes[0]} and "
                                f"{double_quotes[0]}: Both single quotes "
                                f"(line {single_quotes[0]}) and double (line "
                                f"{double_quotes[0]}) quotes are used for "
                                f"string delimiters.")
                        self.fail(msg_color(text, "red"))

                    # 6. there are no trailing blank spaces
                    self.assertFalse(
                        len(line) != len(line.rstrip()), msg_color(
                            f"Line {line_number}: Trailing whitespace "
                            f"detected.", "red"))

                    # 7. function names use lower_case_with_underscores
                    if line.lstrip().startswith("def "):
                        func_name = line.lstrip()[4:].split("(")[0].strip()
                        self.assertTrue(
                            re.match("^[a-z_][a-z0-9_]*$", func_name),
                            msg_color(f"Line {line_number}: Function "
                                      f"name '{func_name}()' does not follow "
                                      f"PEP 8 naming conventions.",
                                      "red"))
        except AssertionError as ae:
            self.fail(
                msg_color(f"Assertion error occurred: {ae}", "red")
            )
        except Exception as e:
            self.fail(
                msg_color(f"An unspecified exception occurred: {e}", "red")
            )

    def test_function_comments(self):
        """
        Conducts a subtest to verify the presence of comments in proximity to
        function definitions. The subtest evaluates two criteria for each
        function: the presence of comments immediately above or below the
        function definition and the inclusion of a docstring within the
        function. The subtest employs the Abstract Syntax Tree (AST) to
        identify function definitions and the tokenize module to locate
        comments.
        """
        subtest_message = "SubTest: Checking for code comments..."
        try:
            with self.subTest(subtest_message):
                # Get the positions of function definitions in the AST
                function_positions = {node.lineno: node.name for (_, node) in
                                      self.detector.function_definitions}

                # Use the tokenize module to identify comments
                with tokenize.open(file_name) as f:
                    tokens = list(tokenize.generate_tokens(f.readline))

                for token_info in tokens:
                    lineno = token_info.start[0]

                    # If we encounter a line that contains a function
                    # definition in the AST
                    function_name = function_positions.get(lineno)

                    if function_name:
                        function_name = function_positions[lineno]

                        # Search for a comment immediately above, below,
                        # or in-line with the definition
                        comments_near_function = any(
                            t_type == tokenize.COMMENT and
                            (t_lineno == lineno - 1 or
                             t_lineno == lineno + 1 or t_lineno == lineno)
                            for t_info in tokens
                            for t_lineno in [t_info.start[0]]
                            for t_type in [t_info.type]
                        )

                        # Search for a docstring (triple-quoted comment)
                        # within the function
                        function_node = next(node for (_, node) in
                                             self.detector.function_definitions
                                             if node.name == function_name)
                        has_docstring = isinstance(function_node.body[0],
                                                   ast.Expr) and isinstance(
                            function_node.body[0].value, ast.Str)

                        # Test whether at least one of the two types of
                        # comments is present
                        self.assertTrue(
                            comments_near_function or has_docstring,
                            msg_color(f"The function '{function_name}()' "
                                      f"does not have enough comments for "
                                      f"description.", "red")
                        )
        except AssertionError as ae:
            self.fail(
                msg_color(f"Assertion error occurred: {ae}", "red")
            )
        except Exception as e:
            self.fail(
                msg_color(f"An unspecified exception occurred: {e}", "red")
            )

    def test_pycodestyle(self):
        """
        Executes a subtest utilizing the PycodeStyle tool to evaluate the
        code's adherence to PEP 8 style guidelines. The subtest invokes the
        PycodeStyle tool via a subprocess and parses its standard output to
        assert the absence of style issues. If the PycodeStyle tool is not
        installed, the test will gracefully fail with an appropriate message.
        """
        subtest_message = "SubTest: Running the PycodeStyle test..."
        if pycodestyle_run:
            try:
                with self.subTest(subtest_message):

                    result = subprocess.run(["pycodestyle", file_name], capture_output=True, text=True)

                    errors_and_warnings = result.stdout.split("\n")
                    for index, issue in enumerate(errors_and_warnings):
                        with self.subTest("SubTest: PyCodeStyle..."):
                            self.assertEqual(
                                issue, "",
                                msg_color(f"PycodeStyle fail: {issue}",
                                          "red"))
            except AssertionError as ae:
                self.fail(
                    msg_color(f"Assertion error occurred: {ae}", "red")
                )
            except Exception as e:
                self.fail(
                    msg_color(f"An unspecified exception occurred: {e}", "red")
                )
            except FileNotFoundError as fe:
                msg_color(f"An unspecified exception occurred: {fe}", "red")


if __name__ == "__main__":
    # Instantiate the argument parser
    parser = argparse.ArgumentParser(
        description="Run unit tests on a given student file."
    )

    # Define the "file" argument as a required positional argument
    parser.add_argument(
        "file",
        help="The name of the file to test."
    )

    parser.add_argument(
        "pycodestyle",
        help="Activate or deactivate pycodestyle check",
        type=bool,
        nargs="?",
        const=True,
        default=False
    )

    # Parse the arguments
    args = parser.parse_args()

    # Extract the file name from the parsed arguments
    file_name = args.file

    # Define whether pycodestyle will be executed or not
    pycodestyle_run = args.pycodestyle

    # Extract the file root and extension from the file name
    file_root, file_ext = os.path.splitext(file_name)

    # Validate that the file exists
    if not os.path.exists(file_name):
        print(f"The specified Python file {file_name} does not exist.")
        sys.exit(1)

    # Validate that the file is a Python file
    if file_ext != ".py":
        print("Please provide a Python file (.py) as an argument.")
        sys.exit(1)

    # Run unittest
    unittest.main(
        argv=["first-arg-is-ignored"],
        exit=False,
        testRunner=SuppressTracebackTextTestRunner(),
        buffer=None,
        verbosity=0,
    )
