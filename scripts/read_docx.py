#!/usr/bin/env python3
"""Print the text of a .docx (paragraphs in order, tables as rows), no extra packages needed.

Usage: python3 read_docx.py <form.docx>
List items are prefixed with "• ", table rows with " | " between cells.
"""
import sys
import xml.etree.ElementTree as ET
import zipfile

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

with zipfile.ZipFile(sys.argv[1]) as z:
    body = ET.fromstring(z.read("word/document.xml")).find(W + "body")


def text_of(node):
    return "".join(t.text or "" for t in node.iter(W + "t"))


for el in body:
    if el.tag == W + "p":
        t = text_of(el)
        if t.strip():
            bullet = "• " if el.find(f"{W}pPr/{W}numPr") is not None else ""
            print(bullet + t)
    elif el.tag == W + "tbl":
        for row in el.iter(W + "tr"):
            print(" | ".join(text_of(cell) for cell in row.findall(W + "tc")))
        print()
