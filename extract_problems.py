#!/usr/bin/env python3
import re
import json
from bs4 import BeautifulSoup

# Read the HTML file
with open('Leetcode_problem_set.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

# Find all grid-group-title elements
groups = soup.find_all('div', class_='grid-group-title')
problems = []

problem_id = 1

for group in groups:
    group_title = group.find('span', class_='').text.strip()
    
    # Find the parent grid-group
    grid_group = group.find_parent('div', class_='grid-group')
    if not grid_group:
        continue
    
    # Find all subgroups
    subgroups = grid_group.find_all('div', class_='grid-subgroup')
    
    for subgroup in subgroups:
        subgroup_title = subgroup.find('span', class_='subgroup-title')
        if not subgroup_title:
            continue
        
        subgroup_name = subgroup_title.text.strip()
        
        # Find all problem rows in this subgroup
        problem_rows = subgroup.find_all('tr', class_='p-item')
        
        for row in problem_rows:
            # Extract problem details
            title_elem = row.find('div', class_='p-title')
            if not title_elem:
                continue
            
            title = title_elem.get('title', title_elem.text.strip())
            
            # Extract difficulty
            difficulty_elem = row.find('td', class_='p-difficulty')
            difficulty = 'Easy'  # default
            if difficulty_elem:
                difficulty_badge = difficulty_elem.find('span', class_='difficulty-hard')
                if difficulty_badge:
                    difficulty = 'Hard'
                else:
                    medium_badge = difficulty_elem.find('span', class_='difficulty-medium')
                    if medium_badge:
                        difficulty = 'Medium'
                    else:
                        easy_badge = difficulty_elem.find('span', class_='difficulty-easy')
                        if easy_badge:
                            difficulty = 'Easy'
            
            # Extract LeetCode link
            leetcode_link_elem = row.find('a', href=True)
            link = ''
            if leetcode_link_elem:
                link = leetcode_link_elem.get('href', '')
            
            # Extract problem number from title or link
            number = problem_id
            
            # Build the problem object
            problem = {
                'id': problem_id,
                'number': number,
                'title': title,
                'difficulty': difficulty,
                'topics': [group_title],
                'subtopic': subgroup_name,
                'link': link
            }
            
            problems.append(problem)
            problem_id += 1

# Output as JSON
output_js = 'const leetcodeProblems = ' + json.dumps(problems, indent=4) + ';\n'
print(output_js)
print(f"\nTotal problems: {len(problems)}")

