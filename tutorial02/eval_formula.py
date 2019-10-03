# author: Tan Wang Leng

# see commentary.txt for description of this program
import sys


# enum of modes
MODE_DEFINITION = 0
MODE_EVALUATE = 1
ACCEPTED_UNARY_OPERATORS = ['~']
ACCEPTED_BINARY_OPERATORS = ['^', 'V', '>', '-']


# ---- helper methods ----

def print_programmer_error(message):
    print('Programmer error: ' + message)


def print_answer(line_number, result):
    print('Answer (line ' + str(line_number) + '): ' + str(result))


def print_eval_error(message):
    print('Runtime error: ' + message)


def print_error_l(line_number, message):
    print('Error (line ' + str(line_number) + '): ' + message)


def print_error_lc(line_number, char_number, message):
    print('Error (line ' + str(line_number) + ', char ' + str(char_number) + '): ' + message)


# ---- abstract syntax tree classes ----

class AstNegate:
    def __init__(self, cform):
        self.cform = cform

    def evaluate(self, defined_cforms, truth_assignment):
        # TODO: Could have cached the answer! Useful if composite formula
        # appears more than once!
        return not self.cform.evaluate(defined_cforms, truth_assignment)


class AstAnd:
    def __init__(self, cform_left, cform_right):
        self.cform_left = cform_left
        self.cform_right = cform_right

    def evaluate(self, defined_cforms, truth_assignment):
        # TODO: Could have cached the answer! Useful if composite formula
        # appears more than once!
        left = self.cform_left.evaluate(defined_cforms, truth_assignment)
        right = self.cform_right.evaluate(defined_cforms, truth_assignment)
        return (left and right)


class AstOr:
    def __init__(self, cform_left, cform_right):
        self.cform_left = cform_left
        self.cform_right = cform_right

    def evaluate(self, defined_cforms, truth_assignment):
        # TODO: Could have cached the answer! Useful if composite formula
        # appears more than once!
        left = self.cform_left.evaluate(defined_cforms, truth_assignment)
        right = self.cform_right.evaluate(defined_cforms, truth_assignment)
        return (left or right)


class AstImplies:
    def __init__(self, cform_left, cform_right):
        self.cform_left = cform_left
        self.cform_right = cform_right

    def evaluate(self, defined_cforms, truth_assignment):
        # TODO: Could have cached the answer! Useful if composite formula
        # appears more than once!
        left = self.cform_left.evaluate(defined_cforms, truth_assignment)
        right = self.cform_right.evaluate(defined_cforms, truth_assignment)
        return ((not left) or right)


class AstIff:
    def __init__(self, cform_left, cform_right):
        self.cform_left = cform_left
        self.cform_right = cform_right

    def evaluate(self, defined_cforms, truth_assignment):
        # TODO: Could have cached the answer! Useful if composite formula
        # appears more than once!
        left = self.cform_left.evaluate(defined_cforms, truth_assignment)
        right = self.cform_right.evaluate(defined_cforms, truth_assignment)
        return ((left and right) or ((not left) and (not right)))


class AstCname:
    def __init__(self, cname):
        self.cname = cname

    def evaluate(self, defined_cforms, truth_assignment):
        if self.cname not in defined_cforms:
            # formula does not exist
            print_eval_error('Cannot find composite formula ' + str(self.cname) + '!')
            return False

        # TODO: Could have cached the answer! Useful if composite formula
        # appears more than once!
        return defined_cforms[self.cname].evaluate(defined_cforms, truth_assignment)


class AstPname:
    def __init__(self, pname):
        self.pname = int(pname)

    def evaluate(self, defined_cforms, truth_assignment):
        # remember that pname are 1-indexed
        if self.pname > len(truth_assignment) or self.pname < 1:
            # proposition does not exist
            print_eval_error('Cannot find truth value of proposition ' + str(self.pname) + '!')
            return False

        return truth_assignment[self.pname - 1]


# ---- main implementation code ----

# a composite formula can only be a lower-case alphabet
def is_cname(character):
    ascii_code = ord(character)
    return ascii_code >= ord('a') and ascii_code <= ord('z')


# an atomic proposition can only be a numeric number from 0 - 9
def is_pname(character):
    ascii_code = ord(character)
    return ascii_code >= ord('0') and ascii_code <= ord('9')


def is_unary_operator(character):
    return character in ACCEPTED_UNARY_OPERATORS


def is_binary_operator(character):
    return character in ACCEPTED_BINARY_OPERATORS


# evaluate a composite formula using the truth assignment given
# and print the answer
def do_evaluate(line_number, cform, defined_cforms, truth_assignment):
    answer = cform.evaluate(defined_cforms, truth_assignment)
    print_answer(line_number, answer)


# parse a line in the input as a truth assignment (this is a line
# that appears during 'mode eval')
#
# returns a truth assignment, or None if there's a parsing error
def parse_evaluate(line_number, line):
    result = [False] * len(line)

    for i in range(0, len(line)):
        if line[i] == '0':
            result[i] = False
        elif line[i] == '1':
            result[i] = True
        else:
            print_error_lc(line_number, i, 'Expected 0 or 1, found ' + str(result[i]))
            return None

    return result


# definition mode: parse cform
#
# returns the formula's abstract syntax tree itself + next_index,
# or None for parse error
def def_parse_cform(line_number, line, start_index):
    if is_pname(line[start_index]):
        return AstPname(line[start_index]), start_index + 1
    
    if is_cname(line[start_index]):
        return AstCname(line[start_index]), start_index + 1

    if line[start_index] == '(':
        start_index += 1

        if is_unary_operator(line[start_index]):
            op = line[start_index]
            op_index = start_index
            start_index += 1

            cform, start_index = def_parse_cform(line_number, line, start_index)
            
            if cform is None:
                print_error_lc(line_number, op_index + 1, 'Expected <cform>')
                return None, start_index

            if line[start_index] != ')':
                print_error_lc(line_number, start_index, 'Expected ")"')
            start_index += 1

            if op == '~':
                return AstNegate(cform), start_index
            else:
                # we forgot to code this operator???
                print_programmer_error('Don\'t know how to handle unary operator ' + op)
                return None, start_index
        else:
            # assume binary
            cform_current_index = start_index
            cform_left, start_index = def_parse_cform(line_number, line, start_index)

            if cform_left is None:
                print_error_lc(line_number, cform_current_index, 'Expected left <cform>')
                return None, start_index

            op = line[start_index]
            op_index = start_index
            start_index += 1

            if not is_binary_operator(op):
                print_error_lc(line_number, op_index, 'Expected <binary>')
                return None, start_index

            cform_current_index = start_index
            cform_right, start_index = def_parse_cform(line_number, line, start_index)
            
            if cform_right is None:
                print_error_lc(line_number, cform_current_index, 'Expected right <cform>')
                return None, start_index

            if line[start_index] != ')':
                print_error_lc(line_number, start_index, 'Expected ")"')
            start_index += 1

            if op == '^':
                return AstAnd(cform_left, cform_right), start_index
            elif op == 'V':
                return AstOr(cform_left, cform_right), start_index
            elif op == '>':
                return AstImplies(cform_left, cform_right), start_index
            elif op == '-':
                return AstIff(cform_left, cform_right), start_index
            else:
                # we forgot to code this operator???
                print_programmer_error('Don\'t know how to handle binary operator ' + op)
                return None, start_index


    # not well-defined
    print_error_lc(line_number, start_index, 'Expected <pname>, <cname> or "("')
    return None, start_index


# parse a line in the input as a composite formula definition
#
# returns the name of the composite formula + the formula's abstract
# syntax tree itself, i.e. (cname, cform). None for cform if there's
# a parsing error
def parse_definition(line_number, line):
    if len(line) < 3:
        print_error_l(line_number, 'Illegal syntax, expected: <cname> "=" <cform>')
        return '', None
    
    if not is_cname(line[0]):
        print_error_lc(line_number, 0, 'Expected <cname>')
        return '', None        

    cname = line[0]

    if line[1] != '=':
        print_error_lc(line_number, 1, 'Expected "="')
        return cname, None
    
    cform, next_index = def_parse_cform(line_number, line, 2)

    # check that we are not getting additional characters after
    # <cform>
    if next_index < len(line):
        print_error_lc(line_number, next_index, 'Unexpected trailing characters after <cform>')
    
    return cname, cform


# main entry point of program
def main():
    mode = MODE_DEFINITION

    line_number = 0

    defined_cforms = dict()
    last_defined_cform = None

    for line in sys.stdin:
        line_number += 1

        # purge newline
        line = line.replace('\r', '').replace('\n', '')

        # if mode statement, change mode
        if line.startswith('mode '):
            if line == 'mode def':
                mode = MODE_DEFINITION
            elif line == 'mode eval':
                mode = MODE_EVALUATE
            elif line == 'mode end':
                # end of file
                return
            else:
                print_error_l(line_number, 'Unknown mode "' + line + '"')
                return

        # input for a mode
        else:
            # mode def
            if mode == MODE_DEFINITION:
                cname, cform = parse_definition(line_number, line)

                if cform is None:
                    print_error_l(line_number, 'Parse error')
                    return

                defined_cforms[cname] = cform
                last_defined_cform = cform

            # mode eval
            elif mode == MODE_EVALUATE:
                if last_defined_cform == None:
                    print_error_l(line_number, 'No formula is defined yet, cannot evaluate!')
                    return

                truth_assignment = parse_evaluate(line_number, line)
                if truth_assignment == None:
                    print_error_l(line_number, 'Parse error')
                    return

                do_evaluate(line_number, last_defined_cform, defined_cforms, truth_assignment)

            # we forgot to code this mode???
            else:
                print_programmer_error('Mode ' + mode + ' is not being handled!')
                return


if __name__ == '__main__':
    main()
