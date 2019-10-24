#!/bin/bash

echo "
\documentclass[]{standalone}

\usepackage[english]{babel}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{xspace}
\usepackage{booktabs}
\usepackage{xcolor}
\usepackage{tikz}

\usepackage{qcircuit}


\usepackage{hyperref}
\hypersetup{
	pdflang=en,
	colorlinks=true,
	%filecolor=magenta,      
	%urlcolor=cyan,
	allcolors=blue,
	linkcolor=blue,
	bookmarksnumbered=true
}


\title{stuff}
\author{jsk}
\date{\today}

\setlength\parindent{0pt}

\begin{document} " > texpix_tmp.tex

filenames=$1
outputname=$2

echo "filenames=" $filenames
echo "outputname=" $outputname

for file in $filenames ; do
	echo "\includegraphics[width=0.25\textwidth]{$file}" >> texpix_tmp.tex
done

echo "\end{document}" >> texpix_tmp.tex



pdflatex texpix_tmp.tex

mv texpix_tmp.pdf $outputname
rm texpix_tmp.tex
