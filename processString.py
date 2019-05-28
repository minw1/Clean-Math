import re
import string
admissible = [str(i) for i in range(10)]+list(string.ascii_lowercase)+list(string.ascii_uppercase)+['|','^']

def process_shadow_parens(input_str):
    output_str = input_str
    #Remove superfluous shadow parens and close unclosed parentheses (with shadow parens)
    # Find shadow-paren edges of string
    l_idx = 0
    l_add = True
    while l_add:
        if l_idx + 1 > len(output_str):
            l_add = False
        elif output_str[l_idx] == '\u2985':
            l_idx += 1
        else:
            l_add = False

    r_idx = len(output_str)-1
    r_add = True
    while r_add:
        if r_idx - 1 < l_idx:
            r_add = False
        elif output_str[r_idx] == '\u2986':
            r_idx -= 1
        else:
            r_add = False

    #print("Left Index: " + str(l_idx) + "\nRight Index: " + str(r_idx))
    # Turn shadow parens contained within the string (and not adjacent to parens) into actual parens
    for i in range(l_idx, r_idx+1):
        if output_str[i] == '\u2985':
            replace = True
            if i != r_idx and output_str[i+1] == '(':
                replace = False
            elif i != l_idx and output_str[i-1] == '(':
                replace = False
            if replace:
                output_str = output_str[:i] + '(' + output_str[i+1:]
        elif output_str[i] == '\u2986':
            replace = True
            if i != r_idx and output_str[i+1] == ')':
                replace = False
            elif i != l_idx and output_str[i-1] == ')':
                replace = False
            if replace:
                output_str = output_str[:i] + ')' + output_str[i+1:]

    # Refresh shadow parens, maintaining cursor position
    c_dist = (None, 0)
    if '|' in output_str[:l_idx]:
        c_dist = ('L', output_str[:l_idx].index('|'))
    elif '|' in output_str[r_idx+1:]:
        c_dist = ('R', len(output_str)-1 - output_str.index('|'))
    
    output_str = output_str[l_idx:r_idx+1]
    #  Remove shadow parens
    output_str = output_str.replace('\u2985', '').replace('\u2986', '')
    #  Figure out how many new shadow parens to add
    extr_lprns = 0
    extr_rprns = 0
    for i in range(0, len(output_str)):
        if output_str[i] == "(":
            extr_rprns += 1
        elif output_str[i] == ")":
            if extr_rprns > 0:
                extr_rprns -= 1
            else:
                extr_lprns += 1
    # Add new shadow parens
    output_str = extr_lprns * "\u2985" + output_str + "\u2986" * extr_rprns
    # Add cursor back in
    if c_dist[0] == 'L':
        output_str = output_str[:c_dist[1]] + '|' + output_str[c_dist[1]:]
    elif c_dist[0] == 'R':
        output_str = output_str[:len(output_str)-c_dist[1]] + '|' + output_str[len(output_str)-c_dist[1]:]
    
    return output_str

# Place a bracket in a string (note: this only makes sense in reference to process_brackets
def place_bracket(input_str, b_ref, b_missing, op_indices, i, id, idx, add_idx, b_left):
    b_char = '}'
    if b_left:
        b_char = '{'
        
    # Place bracket and edit references to it
    output_str = input_str
    output_str = output_str[:idx] + b_char + output_str[idx:]
    b_missing[i][add_idx] = False
    b_missing = b_missing[:idx]+[[False,False,False,False]]+b_missing[idx:]
    b_ref = b_ref[:idx] + [id] + b_ref[idx:]
    for j in range(0, len(op_indices)):
        if op_indices[j] > idx:
            op_indices[j] += 1
        for j in range(idx, len(b_ref)):
            if b_ref[j] >= idx+1:
                b_ref[j] += 1
    return (output_str, b_ref, b_missing, op_indices)

def add_close_brack(input_str, b_depth=0, p_depth=0):
    '''takes a string without an opening bracket and adds a closing bracket at the first place it should be'''
    if len(input_str) == 0:
        return '}'
    first_char = input_str[0]
    if first_char in ('(','\u2985'):
        return first_char+add_close_brack(input_str[1:],b_depth,p_depth+1)
    if first_char in (')','\u2986'):
        if p_depth == 1:
            return first_char+'}'+input_str[1:]
        elif p_depth == 0:
            return '}'+input_str
        else:
            return first_char+add_close_brack(input_str[1:],b_depth,p_depth-1)
    if first_char == '{':
        return first_char+add_close_brack(input_str[1:],b_depth+1,p_depth)
    if first_char == '}':
        if b_depth == 1:
            return first_char+'}'+input_str[1:]
        elif b_depth == 0:
            return '}'+input_str
        else:
            return first_char+add_close_brack(input_str[1:],b_depth-1,p_depth)
    if first_char in admissible:
        return first_char+add_close_brack(input_str[1:],b_depth,p_depth)
    return '}'+input_str

def robust_reverse(input_str):
    rev = input_str[::-1]
    chars = ''
    for char in rev:
        if char == ')': chars+='('
        elif char == '(': chars+=')'
        elif char == '\u2985': chars+='\u2986'
        elif char == '\u2986': chars+='\u2985'
        elif char == '}': chars+='{'
        elif char == '{': chars+='}'
        else: chars += char
    return chars

def add_close_brack_reverse(input_str, b_depth=0, p_depth=0):
    rev = robust_reverse(input_str)
    bracked = add_close_brack(rev, b_depth, p_depth)
    return robust_reverse(bracked)
    
    
def process_brackets(input_str):
    print('input_str to pbrack',input_str)
    output_str = input_str

    # Determine if brackets are correct
    b_crct = True
    b_ref = [0]*len(output_str)
    b_missing = [[False, False, False, False] for counter in range(len(output_str))]
    op_indices = []
    for m in re.finditer('\^|\/', output_str):
        op_indices.append(m.start())
    
    #  Search for missing brackets
    for i in op_indices:
        id = i+1
        if output_str[i] == '^':
            #Check for right-adjacent bracket
            if i+1 < len(output_str) and output_str[i+1] == '{': # Checks for right-adjacent bracket
                if b_ref[i+1] == 0:
                    b_ref[i+1] == id
                else:
                    b_crct = False
                    b_missing[i][0] = True
                    b_missing[i][1] = True
            elif i+2 < len(output_str) and output_str[i+1] == '|' and output_str[i+2] == '{':
                if b_ref[i+2] == 0:
                    b_ref[i+2] == id
                else:
                    b_crct = False
                    b_missing[i][0] = True
                    b_missing[i][1] = True
            else:
                b_missing[i][0] = True
                b_missing[i][1] = True

            if not b_missing[i][0]:
                b_found = False
                b_shift = 1
                b_depth = -1
                while not b_found:
                    
                    if i+b_shift >= len(output_str):
                        b_found = True
                        b_crct = False
                        b_missing[i][0] = True
                    elif output_str[i+b_shift] == '}':
                        if b_depth == -1:
                            b_found = True
                            if b_ref[i+b_shift] == 0:
                                b_ref[i+b_shift] = id
                        else:
                            b_depth += 1
                    else:
                        if output_str[i+b_shift] == '{':
                            b_depth += -1
                        b_shift += 1
                        
        elif output_str[i] == '/':
            # Check if adjacent brackets are missing
            if i-1 >= 0 and output_str[i-1] == '}': # Checks for left-adjacent bracket
                if b_ref[i-1] == 0:
                    b_ref[i-1] == id
                else:
                    b_crct = False
                    b_missing[i][0] = True
                    b_missing[i][1] = True
            elif i-2 >=0 and output_str[i-1] == '|' and output_str[i-2] == '}':
                if b_ref[i-2] == 0:
                    b_ref[i-2] == id
                else:
                    b_crct = False
                    b_missing[i][0] = True
                    b_missing[i][1] = True
            else:
                b_missing[i][0] = True
                b_missing[i][1] = True
            
            if i+1 < len(output_str) and output_str[i+1] == '{': # Checks for right-adjacent bracket
                if b_ref[i+1] == 0:
                    b_ref[i+1] == id
                else:
                    b_crct = False
                    b_missing[i][2] = True
                    b_missing[i][3] = True
            elif i+2 < len(output_str) and output_str[i+1] == '|' and output_str[i+2] == '{':
                if b_ref[i+2] == 0:
                    b_ref[i+2] == id
                else:
                    b_crct = False
                    b_missing[i][2] = True
                    b_missing[i][3] = True
            else:
                b_missing[i][2] = True
                b_missing[i][3] = True
            
            # If the left-adjacent bracket isn't missing, search for closing bracket
            if not b_missing[i][1]:
                b_found = False
                b_shift = -2
                b_depth = -1
                while not b_found:
                    if i+b_shift < 0:
                        b_found = True
                        b_crct = False
                        b_missing[i][0] = True
                    elif output_str[i+b_shift] == '{':
                        if b_depth == -1:
                            b_found = True
                            if b_ref[i+b_shift] == 0:
                                b_ref[i+b_shift] = id
                            else:
                                b_crct = False
                                b_missing[i][0] = True
                        else:
                            b_depth += 1
                    else:
                        if output_str[i+b_shift] == '}':
                            b_depth += -1
                        b_shift -= 1
            # If the right-adjacent bracket isn't missing, search for closing bracket
            if not b_missing[i][2]:
                b_found = False
                b_shift = 2
                b_depth = -1
                while not b_found:
                    if i+b_shift >= len(output_str):
                        b_found = True
                        b_crct = False
                        b_missing[i][3] = True
                    elif output_str[i+b_shift] == '}':
                        if b_depth == -1:
                            b_found = True
                            if b_ref[i+b_shift] == 0:
                                b_ref[i+b_shift] = id
                            else:
                                b_crct = False
                                b_missing[i][3] = True
                        else:
                            b_depth += 1
                    else:
                        if output_str[i+b_shift] == '{':
                            b_depth += -1
                        b_shift += 1

    #Determine what index to fix
    op_idx = [i for i in range(len(b_missing)) if b_missing[i] != [False,False,False,False]]
    if op_idx == []: return output_str
    op_idx = op_idx[0]
    if output_str[op_idx] == '^':
        end_part = output_str[op_idx+1:]
        new_str = output_str[:op_idx+1]
        if b_missing[0]: new_str += '{'
        else: end_part = end_part[1:]
        new_str += add_close_brack(end_part)
        return process_brackets(new_str)
        
    elif output_str[op_idx] == '/':
        brack_miss = b_missing[op_idx]
        
        start_part = output_str[:op_idx]
        end_part = output_str[op_idx+1:]

        if not b_missing[1]: start_part = start_part[:-1]
        if not b_missing[2]: end_part = end_part[1:]
            
        new_str = add_close_brack_reverse(start_part)+'}/{'+add_close_brack(end_part)
        return process_brackets(new_str)
    
    return output_str

def process_string(input_str):
    print('processing',input_str)
    output_str = input_str
    #Remove illegal characters
    illegal_chars = ['!', '@', '#', '$', '%', '&', '_', '\\', ':', ';', '\"', '\'', '?', '>', '<', ',', '=']
    str_idx = 0
    while str_idx < len(output_str):
        if output_str[str_idx] in illegal_chars:
            output_str = output_str[:str_idx] + output_str[str_idx+1:]
        else:
            str_idx += 1

    #Replace multiplication operators with unicode version
    output_str = output_str.replace('*', '\u00B7')

    #Process shadow parens
    output_str = process_shadow_parens(output_str)

    #Remove extraneous {}
    output_str = output_str.replace('{}', '')

    #Add brackets for division and exponentiation operands
    output_str = process_brackets(output_str)
    
    if("|" in output_str):
    #Edit cursor index
        index = output_str.index("|")
    else:
        index = -1
    print('output',output_str)
    return (output_str, index)

z=process_brackets
v=z('1+2^|')
print(v)
