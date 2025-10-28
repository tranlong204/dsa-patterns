#!/usr/bin/env python3
import re
import json

# Read the HTML file
with open('Leetcode_problem_set.html', 'r', encoding='utf-8') as f:
    content = f.read()

problems = []
problem_id = 1

# Find all grid-groups
grid_group_pattern = r'<div class="grid-group view-grid">(.*?)</div></div></div></div>'
grid_groups = re.findall(grid_group_pattern, content, re.DOTALL)

for group_html in grid_groups:
    # Get the category name
    category_match = re.search(r'<span class="">(.*?)</span>', group_html)
    if not category_match:
        continue
    category = category_match.group(1).strip()
    
    # Find all subgroups
    subgroup_pattern = r'<div class="grid-subgroup.*?</div></div></div>'
    subgroups = re.findall(subgroup_pattern, group_html, re.DOTALL)
    
    for subgroup_html in subgroups:
        # Get subgroup name
        subgroup_match = re.search(r'<span class="subgroup-title">(.*?)</span>', subgroup_html)
        if not subgroup_match:
            # Sometimes there's no subgroup
            subgroup_name = ""
        else:
            subgroup_name = subgroup_match.group(1).strip()
        
        # Find all problem rows
        problem_pattern = r'<tr class="p-item">(.*?)</tr>'
        problem_rows = re.findall(problem_pattern, subgroup_html, re.DOTALL)
        
        for row_html in problem_rows:
            # Extract title
            title_match = re.search(r'<div class="p-title" title="(.*?)"', row_html)
            if not title_match:
                continue
            title = title_match.group(1).strip()
            
            # Extract difficulty
            difficulty = 'Easy'
            if 'difficulty-hard' in row_html:
                difficulty = 'Hard'
            elif 'difficulty-medium' in row_html:
                difficulty = 'Medium'
            else:
                difficulty = 'Easy'
            
            # Extract link
            link_match = re.search(r'href="(https://leetcode.com/problems/[^"]*)"', row_html)
            link = link_match.group(1) if link_match else ""
            
            # Extract problem number if available
            number = problem_id
            
            problem = {
                'id': problem_id,
                'number': number,
                'title': title,
                'difficulty': difficulty,
                'topics': [category],
                'link': link,
                'subtopic': subgroup_name if subgroup_name else category
            }
            
            problems.append(problem)
            problem_id += 1

# Generate the JavaScript output
print("const leetcodeProblems = [")
for i, p in enumerate(problems):
    print(f"    {{ id: {p['id']}, number: {p['number']}, title: \"{p['title']}\", difficulty: \"{p['difficulty']}\", topics: [\"{p['topics'][0]}\"], link: \"{p['link']}\" }}", end="")
    if i < len(problems) - 1:
        print(",")
    else:
        print()

print("];")
print(f"\n// Total: {len(problems)} problems extracted")

