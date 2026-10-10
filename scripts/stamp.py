#!/usr/bin/env python3
"""Stamp HTML files with <meta name="build" content="<hash>"> so the cloud
editor can tell page versions apart. Usage: python3 stamp.py file.html [...]"""
import hashlib, pathlib, re, sys

for name in sys.argv[1:]:
    p = pathlib.Path(name)
    html = re.sub(r'<meta name="build" content="[^"]*">\n?', '', p.read_text())
    markup = re.sub(r'<(script|style)\b.*?</\1>', '', html, flags=re.S)  # page structure only
    build = hashlib.sha1(markup.encode()).hexdigest()[:10]
    html = html.replace('<meta charset="UTF-8">', f'<meta charset="UTF-8">\n<meta name="build" content="{build}">', 1)
    p.write_text(html)
    print(build, name)
