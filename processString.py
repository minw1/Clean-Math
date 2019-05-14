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

def process_brackets(input_str):
    output_str = input_str

    # Determine if brackets are correct
    b_crct = True
    b_ref = [0]*len(output_str)
	
    

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
