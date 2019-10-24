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
\setlength\parindent{0pt}

\begin{document}
\begin{tabular}{c}" > tmp.tex


for div in 0 1 2 ; do
	for rand in 0 1 ; do
		for rc in 0 1 ; do
			if [ $rc == 1 ] && [ $div == 0 ] ; then
			       continue
		        fi
	                if [ $rc == 1 ] && [ $div == 1 ] ; then
                               continue
                        fi
		
			files=""
			for steps in 1 2 4 8 ; do
				file=input_division_${div}_randomize_${rand}_steps_${steps}_randomize_components_${rc}.pdf
				files="$files $file"
			done
			echo "files so far="$files
			bash make_single_column.sh "$files" col_d_${div}_r_${rand}_rc_${rc}_steps_1_2_4_8.pdf
			if [ $div == 2 ] ; then
				echo "\$ H = e^{i\frac{H_0}{2}}e{i\frac{H_1}{2}} \$, randomize=$rand, trotter steps = 1 (2), 2 (4), 4 (8), 8 (16) \\\\" >> tmp.tex
			else
				echo "\$ H = e^{iH_{${div}}} \$, randomize=$rand, trotter steps = 1, 2, 4, 8 \\\\" >> tmp.tex
			fi
			echo "\includegraphics[width=1.0\textwidth]{col_d_${div}_r_${rand}_rc_${rc}_steps_1_2_4_8.pdf} \\\\" >> tmp.tex 
		done
	done
done

echo "\end{tabular}" >> tmp.tex
echo "\end{document}" >> tmp.tex

pdflatex tmp.tex
mv tmp.tex figure.tex
mv tmp.pdf figure.pdf

