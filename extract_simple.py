#!/usr/bin/env python3
import re

# Read the HTML file
with open('Leetcode_problem_set.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all group titles
group_pattern = r'<div class="grid-group-title.*?<span class="">(.*?)</span>'
groups = re.findall(group_pattern, content)

# Find problem rows with their details
problem_pattern = r'<div class="p-title" title="(.*?)".*?</div>.*?data-value="(Hard|Medium|Easy)".*?href="(.*?)"'
problems_data = re.findall(problem_pattern, content, re.DOTALL)

print(f"Found {len(groups)} categories")
print(f"Found {len(problems_data)} problems")

# Print first few for debugging
print("\nFirst 5 problems:")
for i, (title, diff, link) in enumerate(problems_data[:5]):
    print(f"{i+1}. {title} [{diff}]")

