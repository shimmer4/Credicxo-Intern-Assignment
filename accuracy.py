import json

with open("data.json", 'r') as f:
    data = json.load(f)

correct = 0
wrong = 0

for product in data:
    error = data[product].get("error")

    if not error: correct = correct + 1
    if error == "some error occured while scraping.": wrong = wrong + 1

print(f"accuracy = {str((correct * 100) / (correct + wrong))[:5]} %")
print(f"successfully scraped {correct} products.")
print(f"couldnt scrape {wrong} products.")
