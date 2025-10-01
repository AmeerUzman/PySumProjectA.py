#Part A
#non negetive number adder
nums = (3, -2, 7, 0, -9, 5)
total = 0
for x in nums:
    if x >= 0:
        total = total + x 
    else:
        continue
print ("Sum of non‑negatives:", total)

# vowel counter
s = ("Hello, CS class 103!").lower()
vowels = ("aeiou")
total_vowels = 0
for x in s:
    if x in vowels:
        total_vowels = total_vowels + 1
    else:
        continue
print("Vowel count:", total_vowels)
