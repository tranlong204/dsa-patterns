#!/usr/bin/env python3
import re

with open('Leetcode_problem_set.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find all problem entries with their context
# Look for patterns like: grid-group-title -> subgroup -> problems
output = []

# Split by grid-groups
groups = re.split(r'<div class="grid-group', html)

for i, group in enumerate(groups[1:], 1):  # Skip first split
    # Find category name
    cat_match = re.search(r'<span class="">(.*?)</span>', group)
    if not cat_match:
        continue
    category = cat_match.group(1).strip()
    
    # Find all problem rows in this group
    problems = re.findall(r'<tr class="p-item">.*?</tr>', group, re.DOTALL)
    
    for row in problems:
        # Get title
        title_match = re.search(r'title="([^"]+)"', row)
        if not title_match or 'alt=' in row or 'title=' not in row.split('p-title')[0]:
            title_match = re.search(r'<div class="p-title"[^>]*title="([^"]+)"', row)
            if not title_match:
                continue
        
        title = title_match.group(1)
        
        # Skip if it's metadata
        if title in ['Mark as solved', 'Problem', 'Difficulty', 'Practice', 'Solution', 'Revision']:
            continue
        
        # Get difficulty
        difficulty = 'Easy'
        if 'difficulty-hard' in row:
            difficulty = 'Hard'
        elif 'difficulty-medium' in row:
            difficulty = 'Medium'
        
        # Get link
        link_match = re.search(r'href="(https://[^"]+)"', row)
        link = link_match.group(1) if link_match else ""
        
        # Determine subcategory by checking context
        subgroup_match = re.search(r'<span class="subgroup-title">(.*?)</span>', group[:group.find(row)])
        subtopic = subgroup_match.group(1).strip() if subgroup_match else ""
        
        output.append({
            'category': category,
            'subtopic': subtopic,
            'title': title,
            'difficulty': difficulty,
            'link': link
        })

# Output JavaScript
print("const leetcodeProblems = [")
for idx, p in enumerate(output):
    print(f"    {{ id: {idx+1}, number: {idx+1}, title: \"{p['title']}\", difficulty: \"{p['difficulty']}\", topics: [\"{p['category']}\"], link: \"{p['link']}\" }}{',' if idx < len(output) - 1 else ''}")

print("];")
print(f"\n// Extracted {len(output)} problems")

