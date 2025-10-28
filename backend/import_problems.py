"""
Script to import problems from data.js to Supabase
This script reads the JavaScript file and imports all problems.
"""
import sys
import re
import json
import os
from pathlib import Path

# Add parent directory to path to import data.js
sys.path.append('..')

# Try to import the leetcodeProblems from data.js
# We'll parse it manually since it's JavaScript

def parse_data_js(file_path):
    """Parse the data.js file and extract problems"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    problems = []
    
    # Find all problem entries
    pattern = r'\{ id: (\d+), number: (\d+), title: "([^"]+)", difficulty: "([^"]+)", topics: (\[[^\]]+\]|\'[^\']+\'), (?:subtopic: "([^"]*)", )?link: "([^"]+)" \}'
    
    for match in re.finditer(pattern, content):
        problem_id = int(match.group(1))
        number = int(match.group(2))
        title = match.group(3)
        difficulty = match.group(4)
        topics_str = match.group(5)
        subtopic = match.group(6) if match.group(6) else None
        link = match.group(7)
        
        # Parse topics
        topics = []
        if topics_str.startswith('['):
            # JSON array format
            topics = json.loads(topics_str.replace("'", '"'))
        elif topics_str.startswith("'") or topics_str.startswith('"'):
            topics = [topics_str.strip("'\"")]
        
        problems.append({
            'id': problem_id,
            'number': number,
            'title': title,
            'difficulty': difficulty,
            'topics': topics,
            'link': link,
            'subtopic': subtopic
        })
    
    return problems

def import_to_supabase(problems):
    """Import problems to Supabase"""
    from dotenv import load_dotenv
    from app.database import get_supabase
    
    load_dotenv()
    
    supabase = get_supabase()
    
    # Batch insert
    batch_size = 50
    total = len(problems)
    
    print(f"Importing {total} problems to Supabase...")
    print("=" * 60)
    
    for i in range(0, total, batch_size):
        batch = problems[i:i + batch_size]
        print(f"\nImporting batch {i // batch_size + 1} (problems {i+1} to {min(i+batch_size, total)})...")
        
        try:
            # Format the batch data
            formatted_batch = []
            for p in batch:
                formatted_batch.append({
                    'id': p['id'],
                    'number': p['number'],
                    'title': p['title'],
                    'difficulty': p['difficulty'],
                    'topics': p['topics'],  # Will be converted to JSONB
                    'link': p['link'],
                    'subtopic': p['subtopic'] or None
                })
            
            response = supabase.table("problems").insert(formatted_batch).execute()
            print(f"✓ Successfully imported {len(batch)} problems")
            
        except Exception as e:
            print(f"✗ Error importing batch: {e}")
            print(f"  Retrying individual inserts...")
            for p in batch:
                try:
                    supabase.table("problems").insert({
                        'id': p['id'],
                        'number': p['number'],
                        'title': p['title'],
                        'difficulty': p['difficulty'],
                        'topics': p['topics'],
                        'link': p['link'],
                        'subtopic': p['subtopic'] or None
                    }).execute()
                except Exception as err:
                    print(f"  ✗ Failed to import problem {p['id']}: {err}")
    
    print("\n" + "=" * 60)
    print(f"Import complete! Total problems imported: {total}")

if __name__ == "__main__":
    # Read data.js from parent directory
    data_js_path = Path(__file__).parent.parent / "data.js"
    
    if not data_js_path.exists():
        print(f"Error: data.js not found at {data_js_path}")
        print("Please make sure data.js exists in the parent directory")
        sys.exit(1)
    
    print("Parsing data.js...")
    problems = parse_data_js(data_js_path)
    print(f"Found {len(problems)} problems")
    
    print("\nImporting to Supabase...")
    import_to_supabase(problems)

