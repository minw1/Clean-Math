import plyParser as pprs 
import expToStr as xptos
import re

def process_string(input_str):
    output_str = input_str
    #Remove illegal characters
    illegal_chars = ['!', '@', '#', '$', '%', '&', '_', '\\', ':', ';', '\"', '\'', '?', '>', '<', ',', '=']
    idx = 0
    while idx < len(output_str):
        if output_str[idx] in illegal_chars:
            output_str = output_str[:idx] + output_str[idx+1:]
        else:
            idx += 1

    #Replace multiplication operators with unicode version
    output_str = output_str.replace('*', '\u00B7')

    #Insert implicit multiplication
    output_str = re.sub('(?<=\w|\))(?=\|?\()|(?<=\))(?=\|?\w)|(?<=\d|[a-zA-Z])(?=\|?[a-zA-Z])|(?<=[a-zA-Z])(?=\|?\d)', '*', output_str)
	
   #Close unclosed parentheses (with shadow parens)
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
    output_str = extr_lprns*"\u2985" + output_str + "\u2986"*extr_rprns
	
    #Add brackets for division operands
	
    return output_str



def is_inverse(stri):
	ex = pprs.get_exp(stri)
	st2 = xptos.expToStr(process_string(ex))
	print(st2)
	return st2==stri

#while True:
 #  print(is_inverse(input(">>> ")))



