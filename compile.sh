#!/bin/bash

# Main file name (without extension)
MAIN="main"

echo "Compiling $MAIN.tex..."

# First pass
pdflatex -interaction=nonstopmode $MAIN.tex

# BibTeX
bibtex $MAIN.aux

# Second pass
pdflatex -interaction=nonstopmode $MAIN.tex

# Third pass (to fix references and TOC)
pdflatex -interaction=nonstopmode $MAIN.tex

echo "Compilation finished. Result: $MAIN.pdf"
