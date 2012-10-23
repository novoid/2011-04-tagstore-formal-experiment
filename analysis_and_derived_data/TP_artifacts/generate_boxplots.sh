#!/bin/sh

R < generate_boxplots.R --no-save

## optional step: cropping the pdf output files
for file in *boxplot*orig.pdf; do
    pdfcrop $file
done
for file in *boxplot*orig-crop.pdf; do
    newname=`echo $file | sed 's/_orig-/_/'`
    echo "renaming \"$file\"  ->  \"$newname\""
    mv "${file}" "${newname}"
done

## remove the originals, keeping the cropped versions:
rm *boxplot*orig.pdf

#end