fo = open('css_js/ui.css','r+')
fo.seek(77, 1)


ip = "192.168.221.171"

number = 15 - len(ip)

if number != 0:
	for x in range(0,number):
		ip = ip + " "

fo.write(ip)