import re, cgi
#Adapted From: https://stackoverflow.com/a/19730306/2089784
def CLEAN(mess):
	tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')
	no_tags = tag_re.sub('', mess)
	ready = cgi.escape(no_tags)
	return ready