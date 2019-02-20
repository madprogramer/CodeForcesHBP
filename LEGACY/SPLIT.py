import re
#Adapted From: https://stackoverflow.com/a/3801846/2089784
def SPLIT(s):
    regex = []

    # Match a whole word:
    regex += [r'\w+']

    # Chinese Characters
    regex += [r'[\u4e00-\ufaff]']
    
    #Thai Characters
    #regex += [r'[\u0e00–\u0e7f]']

    # Match one of anything else, except for spaces:
    regex += [r'[^\s]']

    regex = "|".join(regex)
    r = re.compile(regex)

    return r.findall(s)