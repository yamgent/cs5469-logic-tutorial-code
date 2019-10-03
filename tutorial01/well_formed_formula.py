# author: Tan Wang Leng

# check whether expression is a well-formed formula
#
# each character in expression is either one of these (no spaces allowed):
#   - propositions: A, B, C, ..., Z
#   - unary connectives: ~ (neg)
#   - binary connectives: ^ (and), v (or), > (implies), - (iff)
#   - parenthesis must be used for composite formulas
#
# examples of well-formed & malformed formulas:
#   - ((~(AvB))^C)
#   - ((~A)>BvC)
#
import sys


# a character is a proposition if it is 
# between 'A' to 'Z' inclusive
def is_proposition(character):
    ascii_code = ord(character)
    return ascii_code >= ord('A') and ascii_code <= ord('Z')


# get the character at a particular index
# return '' if index out of range
def char_at(formula, index):
    if index >= len(formula):
        return ''
    return formula[index]


# consume as much symbols as possible, returns
# the index of the next symbol that was not
# consumed by this algorithm
def parse_greedy(formula, start_index):
    first_char = char_at(formula, start_index)

    # composite
    if first_char == '(':
        second_char = char_at(formula, start_index + 1)
        # unary
        if second_char == '~':
            end_index = parse_greedy(formula, start_index + 2)
            if end_index == -1:
                print('Error: Expected formula at ' + str(start_index + 2))
                return -1
            last_char = char_at(formula, end_index)
            if last_char != ')':
                print('Error: Expected ")" at ' + str(end_index))
                return -1
            return end_index + 1
        # binary
        else:
            end_index_one = parse_greedy(formula, start_index + 1)
            if end_index_one == -1:
                print('Error: Expected formula at ' + str(start_index + 1))
                return -1

            connective = char_at(formula, end_index_one)
            supported_connectives = { '^', 'v', '>', '-' }
            if connective not in supported_connectives:
                print('Error: Unsupported connective "' + connective + 
                    '" at ' + str(start_index + 1))
                return -1

            end_index_two = parse_greedy(formula, end_index_one + 1)
            if end_index_two == -1:
                print('Error: Expected formula at ' + str(end_index_one + 1))
                return -1
            
            last_char = char_at(formula, end_index_two)
            if last_char != ')':
                print('Error: Expected ")" at ' + str(end_index_two))
                return -1
            return end_index_two + 1

    # atomic
    elif is_proposition(first_char):
        return start_index + 1
    else:
        print('Error: Unexpected token "' + first_char + 
            '" at ' + str(start_index))
        return -1


def main():
    for line in sys.stdin:
        # purge newline
        line = line.replace('\r', '').replace('\n', '')

        print('--------------------')
        print('Expression: ' + line)

        end_index = parse_greedy(line, 0)
        well_formed = end_index == len(line)

        if well_formed:
            print('WELL-FORMED')
        else:
            if end_index == -1:
                print('Error: There were some syntax errors')
            elif end_index < len(line):
                print('Error: Additional token after ' + str(end_index))
            else:
                print('Error: Programming/parser error. end_index ' 
                + '> len(line) at ' + str(end_index))
            
            print('MALFORMED')


if __name__ == '__main__':
    main()
