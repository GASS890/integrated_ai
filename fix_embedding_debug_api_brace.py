from pathlib import Path

path = Path("main.py")
text = path.read_text(encoding="utf-8")

bad = '''    return {
        "query": req.query,
        "count": len(results),
        "results": results,
    }
    }
'''

good = '''    return {
        "query": req.query,
        "count": len(results),
        "results": results,
    }
'''

text = text.replace(bad, good)

path.write_text(text, encoding="utf-8")
print("extra brace removed.")
