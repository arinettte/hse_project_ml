n = int(input())
lst = list(map(int,input().split()))
lst.sort()
mem = [10**9 for i in range(n)]
mem[0] = 0
mem[1] = lst[1] - lst[0]
mem[2] = lst[2] - lst[0]
for i in range(3,n):
    mem[i]  = min(mem[i-2] + lst[i] -lst[i-1],mem[i-1] +  lst[i] -lst[i-1])
print(mem)