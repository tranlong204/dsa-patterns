#!/usr/bin/env python3
import re

with open('Leetcode_problem_set.html', 'r', encoding='utf-8') as f:
    content = f.read()

output = []
id_counter = 1

# Extract problem titles, difficulties, and links
# Pattern: p-title followed by difficulty and link
rows = re.findall(r'<tr class="p-item">.*?</tr>', content, re.DOTALL)

current_category = ""
current_subcategory = ""

for row in rows:
    # Extract title
    title_match = re.search(r'<div class="p-title" title="([^"]+)"', row)
    if not title_match:
        continue
    
    title = title_match.group(1)
    
    # Extract difficulty
    if 'difficulty-hard' in row:
        difficulty = 'Hard'
    elif 'difficulty-medium' in row:
        difficulty = 'Medium'
    else:
        difficulty = 'Easy'
    
    # Extract link
    link_match = re.search(r'href="(https://leetcode\.com/problems/[^"]*)"', row)
    link = link_match.group(1) if link_match else ""
    
    # Extract number from link
    number_match = re.search(r'/problems/([^/]+)/', link)
    number_str = number_match.group(1).replace('-', ' ') if number_match else str(id_counter)
    
    # Use the ID as number for now
    number = id_counter
    
    # Extract category - find the nearest grid-group-title
    # This is complex, so we'll use a placeholder for now
    topic = "Arrays"  # Will be updated
    
    output.append({
        'id': id_counter,
        'number': number,
        'title': title,
        'difficulty': difficulty,
        'topics': [topic],
        'link': link if link else f"https://leetcode.com/problems/{title.lower().replace(' ', '-')}/"
    })
    
    id_counter += 1

# Output as JavaScript
print("const leetcodeProblems = [")
for i, p in enumerate(output):
    print(f"    {{ id: {p['id']}, number: {p['number']}, title: \"{p['title']}\", difficulty: \"{p['difficulty']}\", topics: [\"{p['topics'][0]}\"], link: \"{p['link']}\" }}{',' if i < len(output) - 1 else ''}")

print("];")

