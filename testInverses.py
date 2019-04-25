import plyParser as pprs 
import expToStr as xptos


def is_inverse(stri):
	ex = pprs.get_exp(stri)
	st2 = xptos.expToStr(ex)
	print(st2)
	return st2==stri

while True:
   print(is_inverse(input(">>> ")))



