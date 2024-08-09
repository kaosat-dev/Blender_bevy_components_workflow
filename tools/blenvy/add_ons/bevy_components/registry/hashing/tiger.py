import struct
from .sboxes import t1, t2, t3, t4

def tiger_round(abc, order, x, mul):
	abc[order[2]] ^= x
	abc[order[2]] &= 0xffffffffffffffff
	abc[order[0]] -= t1[((abc[order[2]]) >> (0*8))&0xFF] ^ t2[((abc[order[2]]) >> ( 2*8)) & 0xFF] ^ t3[((abc[order[2]]) >> (4*8))&0xFF] ^ t4[((abc[order[2]]) >> ( 6*8)) & 0xFF]
	abc[order[1]] += t4[((abc[order[2]]) >> (1*8))&0xFF] ^ t3[((abc[order[2]]) >> ( 3*8)) & 0xFF] ^ t2[((abc[order[2]]) >> (5*8))&0xFF] ^ t1[((abc[order[2]]) >> ( 7*8)) & 0xFF]
	abc[order[1]] *= mul
	abc[order[0]] &= 0xffffffffffffffff
	abc[order[1]] &= 0xffffffffffffffff
	abc[order[2]] &= 0xffffffffffffffff
	return abc
	
def tiger_pass(abc, mul, mystr):
	abc = tiger_round(abc, (0, 1, 2), mystr[0], mul)
	abc = tiger_round(abc, (1, 2, 0), mystr[1], mul)
	abc = tiger_round(abc, (2, 0, 1), mystr[2], mul)
	abc = tiger_round(abc, (0, 1, 2), mystr[3], mul)
	abc = tiger_round(abc, (1, 2, 0), mystr[4], mul)
	abc = tiger_round(abc, (2, 0, 1), mystr[5], mul)
	abc = tiger_round(abc, (0, 1, 2), mystr[6], mul)
	abc = tiger_round(abc, (1, 2, 0), mystr[7], mul)
	return abc

def tiger_compress(string, res):
	a = aa = res[0]
	b = bb = res[1]
	c = cc = res[2]
	
	x = []
	for i in range(8):
		x.append(int.from_bytes(string[i*8:i*8+8], byteorder='little'))
		
	allf = 0xFFFFFFFFFFFFFFFF
	for i in range(0, 3):
		if i != 0:
			x[0] = (x[0] - (x[7] ^ 0xA5A5A5A5A5A5A5A5)&allf ) & allf
			x[1] ^= x[0]
			x[2] = (x[2] + x[1]) & allf
			x[3] = (x[3] - (x[2] ^ (~x[1]&allf) << 19)&allf) & allf
			x[4] ^= x[3]
			x[5] = (x[5] + x[4]) & allf
			x[6] = (x[6] - (x[5] ^ (~x[4]&allf) >> 23)&allf) & allf
			x[7] ^= x[6]
			x[0] = (x[0] + x[7]) & allf
			x[1] = (x[1] - (x[0] ^ (~x[7]&allf) << 19)&allf) & allf
			x[2] ^= x[1]
			x[3] = (x[3] + x[2]) & allf
			x[4] = (x[4] - (x[3] ^ (~x[2]&allf) >> 23)&allf) & allf
			x[5] ^= x[4] 
			x[6] = (x[6] + x[5]) & allf
			x[7] = (x[7] - (x[6] ^ 0x0123456789ABCDEF)&allf ) & allf
			
		if i == 0:
			a, b, c = tiger_pass([a, b, c],5, x)
		elif i == 1:
			a, b, c = tiger_pass([a, b, c],7, x)
		else:
			a, b, c = tiger_pass([a, b, c],9, x)
		a, b, c = c, a, b
	res[0] = a^aa
	res[1] = (b - bb) & allf
	res[2] = (c + cc) & allf
	
def hash(string):
	string = bytearray(string.encode())
	i = 0

	res = [0x0123456789ABCDEF, 0xFEDCBA9876543210, 0xF096A5B4C3B2E187]
	offset = 0
	length = len(string)
	while i < length-63:
		tiger_compress( string[i:i+64], res )
		i += 64
	temp = string[i:]
	j = len(temp)
	temp.append(1)
	j += 1

	while j&7 != 0:
		temp.append(0)
		j += 1

	if j > 56:
		while j < 64:
			temp.append(0)
			j += 1
		tiger_compress(temp, res)
		j = 0

	# make the first 56 bytes 0
	temp.extend([0 for i in range(0, 56-j)])
	while j < 56:
		temp[j] = 0
		j += 1
	while len(temp) > 56:
		temp.pop(56)
	temp.extend(struct.pack('<Q', length<<3))
	tiger_compress(temp, res)

	res = list(map(lambda x: int.from_bytes(x.to_bytes(8, byteorder='big'), byteorder='little'), res))
	return "%016X%016X%016X" % (res[0], res[1], res[2])