cnt = 0
b = 1
for a in range(1,5):
	for c in range(1,10):
		if b< (a-1)*(c-1):
			print(a,b,c)
			cnt+=1
print(cnt)