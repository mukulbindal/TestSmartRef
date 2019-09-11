def isprime(n):
	i=2
	while(i*i<=n):
		if n%i==0:
			return False
		i+=1
	return True
l=[]
for i in range(2,8001):
	if isprime(i):
		l.append(i)

print(len(l))