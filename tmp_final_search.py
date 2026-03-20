import os

def search_files(directory, query):
    results = []
    for root, dirs, files in os.walk(directory):
        if '.git' in dirs:
            dirs.remove('.git')
        if 'node_modules' in dirs:
            dirs.remove('node_modules')
        if 'venv' in dirs:
            dirs.remove('venv')
            
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if query in content:
                        results.append(file_path)
            except Exception:
                pass
    return results

query = "transfer_method"
results = search_files(r"c:\Users\hoang\Downloads\Web Technology\Oldshop-Ecommecre", query)
for res in results:
    print(res)

if not results:
    print("No results found for:", query)
    # Try searching for just "transfer"
    query2 = "transfer"
    results2 = search_files(r"c:\Users\hoang\Downloads\Web Technology\Oldshop-Ecommecre", query2)
    print("\nResults for 'transfer':")
    for res in results2:
        print(res)
