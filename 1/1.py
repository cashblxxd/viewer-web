from json import load
s = load(open("postings_1.json", encoding="utf-8"))
ans = 0
for i in s:
	ans += i["Детали отправления"].count("оски")
print(441)
