"""
Script to import problems from data.js into Supabase
"""
import json
import ast
import re
from app.database import get_supabase

def extract_problems_from_js(js_file_path):
    """Extract problems array from JavaScript file"""
    with open(js_file_path, 'r') as f:
        content = f.read()
    
    # Find the problems array
    match = re.search(r'const leetcodeProblems = \[(.*?)\];', content, re.DOTALL)
    if not match:
        raise ValueError("Could not find leetcodeProblems array")
    
    # Extract and parse the array
    array_content = match.group(1)
    
    # Parse each problem
    problems = []
    # Match each problem object
    pattern = r'\{[^}]*id:\s*(\d+),\s*number:\s*(\d+),\s*title:\s*"([^"]+)",\s*difficulty:\s*"([^"]+)",\s*topics:\s*(\[[^\]]+\]|[^,]+),\s*(?:subtopic:\s*"([^"]*)",\s*)?link:\s*"([^"]+)"\s*\}'
    
    # More flexible parsing
    for match in re.finditer(r'id:\s*(\d+).*?number:\s*(\d+).*?title:\s*"([^"]*)".*?difficulty:\s*"([^"]*)".*?topics:\s*(\[[^\]]+\]|\[[^\]]*\]|\'[^\']*\'|"[^"]*").*?(?:subtopic:\s*"([^"]*)").*?link:\s*"([^"]*)"', content, re.DOTALL):
        problems.append({
            'id': int(match.group(1)),
            'number': int(match.group(2)),
            'title': match.group(3),
            'difficulty': match.group(4),
            'topics': match.group(5),
            'subtopic': match.group(6),
            'link': match.group(7)
        })
    
    return problems

def import_problems():
    """Import problems to Supabase"""
    print("Importing problems from data.js...")
    
    # Read data.js
    problems_data = extract_problems_from_js('../data.js')
    
    # Clean and prepare data for Supabase
    import_data = []
    for problem in problems_data:
        # Parse topics (could be a string representation or list)
        topics = problem['topics']
        if isinstance(topics, str):
            # Try to parse as JSON/array string (handles single or double quotes)
            if topics.strip().startswith('['):
                try:
                    topics = json.loads(topics)
                except Exception:
                    try:
                        topics = ast.literal_eval(topics)
                    except Exception:
                        # Fallback: strip quotes and wrap
                        topics = [topics.strip().strip('"\'')]
            else:
                topics = [topics.strip().strip('"\'')]
        elif not isinstance(topics, list):
            topics = [str(topics)]
        
        import_data.append({
            'id': problem['id'],
            'number': problem['number'],
            'title': problem['title'],
            'difficulty': problem['difficulty'],
            'topics': topics,  # Supabase will handle JSON
            'link': problem['link'],
            'subtopic': problem.get('subtopic', '')
        })
    
    # Import to Supabase
    supabase = get_supabase()
    
    # Batch insert (Supabase allows inserting multiple rows)
    batch_size = 100
    for i in range(0, len(import_data), batch_size):
        batch = import_data[i:i + batch_size]
        print(f"Importing batch {i // batch_size + 1} ({len(batch)} problems)...")
        try:
            supabase.table("problems").insert(batch).execute()
            print(f"✓ Successfully imported batch {i // batch_size + 1}")
        except Exception as e:
            print(f"✗ Error importing batch {i // batch_size + 1}: {e}")
    
    print(f"\nImport complete! Total problems: {len(import_data)}")

if __name__ == "__main__":
    import_problems()

