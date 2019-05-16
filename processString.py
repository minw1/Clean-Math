import re

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

    print("Left Index: " + str(l_idx) + "\nRight Index: " + str(r_idx))
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
def place_bracket(input_str, b_ref, b_missing, op_indices, id, idx, add_idx, b_left):
    b_char = '}'
    if b_left:
        b_char = '{'
        
    # Place bracket and edit references to it
    output_str = input_str
    output_str = output_str[:idx] + b_char + output_str[idx:]
    b_missing[i][add_idx] = False
    b_ref = b_ref[:idx] + [id] + b_ref[idx:]
    for j in range(0, len(op_indices)):
        if op_indices[j] > idx:
            op_indices[j] += 1
        for j in range(idx, len(b_ref)):
            if b_ref[j] >= idx+1:
                b_ref[j] += 1
    return (output_str, b_ref, b_missing, op_indices)

def process_brackets(input_str):
    output_str = input_str

    # Determine if brackets are correct
    b_crct = True
    b_ref = [0]*len(output_str)
    b_missing = [[False, False, False, False]]*len(output_str)
    op_indices = []
    for m in re.finditer('\^|\/'):
        op_indices.append(m.start())
    
    #  Search for missing brackets
    for i in op_indices:
        id = i+1
        if output_str[i] == '^':
            b_found = False
            b_shift = 1
            b_depth = -1
            while not b_found:
                if i+b_shift => len(output_str):
                    b_found = True
                    b_crct = False
                elif output_str[i+b_shift] == '}':
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
                    if output_str[i+b_shift] == '{' or output_str[i+b_shift] == '^':
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
            elif i+2 <= len(output_str) and output_str[i+1] == '|' and output_str[i+2] == '{':
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
                        if output_str[i+b_shift] == '^':
                            b_depth += 1
                        elif output_str[i+b_shift] == '}':
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
                        if output_str[i+b_shift] == '^' or output_str[i+b_shift] == '{':
                            b_depth += -1
                        b_shift += 1
    
    #  Search for and eliminate extra brackets
    for i in range(0, len(output_str)):
        if (output_str[i] == '{' or output_str[i] == '}') and b_ref[i] == 0:
            b_ref[i] = -1
    for i in range(0, len(output_str)):
        if i >= len(b_ref):
            break
        elif b_ref == -1:
            for j in range(0, len(op_indices)):
                if op_indices[j] > i:
                    op_indices[j] -= 1
            for j in range(i, len(b_ref)):
                if b_ref[j] > i+1:
                    b_ref[j] -= 1
            b_ref = b_ref[0, i] + b_ref[i+1, len(output_str)-1]
            b_missing = b_missing[0, i] + b_missing[i+1, len(output_str)-1]
            output_str = output_str[0:i] + output_str[i+1, len(output_str)-1]
    
    # If brackets are incorrect, correct them
    i = 0
    while not b_crct:
        if i >= len(output_str):
            b_crct = True
        elif b_missing[i] != [False, False, False, False]:
            # If it's an exponent, close bracket
            if output_str[i] == '^':
                # Find location at which to place bracket
                l_found = False
                l_shift = 1
                b_depth = -1
                while not l_found:
                    if i+l_shift => len(output_str):
                        l_found = True
                    elif output_str[i+l_shift] == '}':
                        if b_depth == -1:
                            l_found = True
                        else:
                            b_depth += 1
                    elif output_str[i+l_shift] == '{' or output_str[i+l_shift] == '^':
                        b_depth += -1
                        l_shift += 1
                    elif b_depth != -1:
                        l_shift += 1
                    elif re.search(r'[0-9a-zA-Z\|]', output_str[i]) != None:
                        l_shift += 1
                    else:
                        l_found = True
                
                # Place bracket and edit references
                id = i+1
                idx = i+l_shift
                add_idx = 0
                b_left = False
                updated_info = place_bracket(output_str, b_ref, b_missing, op_indices, id, idx, add_idx, b_left)
                output_str = updated_info[0]
                b_ref = updated_info[1]
                b_missing = updated_info[2]
                op_indices = updated_info[3]
                
                # Advance index
                i += 1
            # If it's a fraction, close brackets
            elif output_str[i] == '/':
                # (Open and)+ close left brackets
                #  If left opening bracket is missing, place it (note: this is not the first bracket in the fraction)
                if b_missing[i][1]:
                    # Place bracket and edit references
                    id = i+1
                    idx = i-1
                    add_idx = 1
                    b_left = False
                    updated_info = place_bracket(output_str, b_ref, b_missing, op_indices, id, idx, add_idx, b_left)
                    output_str = updated_info[0]
                    b_ref = updated_info[1]
                    b_missing = updated_info[2]
                    op_indices = updated_info[3]
                #  If left closing bracket is missing, place it
                if b_missing[i][0]:
                    # Search for index at which to place bracket
                    # Place bracket and edit references
                    
                #  If right opening bracket is missing, place it
                if b_missing[i][2]:
                    # Place bracket and edit references
                    id = i+1
                    idx = i+1
                    add_idx = 2
                    b_left = True
                    updated_info = place_bracket(output_str, b_ref, b_missing, op_indices, id, idx, add_idx, b_left)
                    output_str = updated_info[0]
                    b_ref = updated_info[1]
                    b_missing = updated_info[2]
                    op_indices = updated_info[3]
                
                #  If right closing bracket is missing, place it
                if b_missing[i][4]:
                    # Search for index at which to place bracket
                    # Place bracket and edit references

def process_string(input_str):
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

    #Add brackets for division operands

    if("|" in output_str):
    #Edit cursor index
        index = output_str.index("|")
    else:
        index = -1
    return (output_str, index)
