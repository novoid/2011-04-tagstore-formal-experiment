#/bin/sh

NR_OF_TAGS_FILE_POSTFIX="a_t_number_of_tags.csv"
AVERAGE_NR_OF_TAGS_FILE_POSTFIX="a_t_average_number_of_tags.csv"
AVERAGE_NR_OF_TAGS_LIST="average_nr_of_tags_-_list.csv"
rm -f ${AVERAGE_NR_OF_TAGS_LIST}

## visits all TP-folders and 
## extracts number of tags per item and 
## calculates average number
for testperson in `find . -type d -name 'TP*'`; do

    cd ${testperson}

    nr_of_tags_file="${testperson}${NR_OF_TAGS_FILE_POSTFIX}"
    average_nr_of_tags_file="${testperson}${AVERAGE_NR_OF_TAGS_FILE_POSTFIX}"

    echo "generating \"${nr_of_tags_file}\" ..."
    ## get all lines with a "ta" command; ignore lines with comment; extract numbers
    grep " ta " ${testperson}a_t.txt | grep -v "#" | sed "s/.* ta //" > ${nr_of_tags_file}

    echo "generating \"${average_nr_of_tags_file}\" ..."
    awk '{ total += $1; count++ } END { print total/count }' \
	< ${nr_of_tags_file} \
	> ${average_nr_of_tags_file}

    echo "generating \"${AVERAGE_NR_OF_TAGS_LIST}\" ..."
    cat TP*a_t_average_number_of_tags.csv >> ../${AVERAGE_NR_OF_TAGS_LIST}

    cd ..
done

## re-collects all number of tags files
echo "generating \"${NR_OF_TAGS_FILE_POSTFIX}\" ..."
rm -f ${NR_OF_TAGS_FILE_POSTFIX}
find . -type f -name 'TP*a_t_number_of_tags.csv' -print0 | \
    xargs -I{} -0 cat  {} >> ${NR_OF_TAGS_FILE_POSTFIX}

echo "generating \"${AVERAGE_NR_OF_TAGS_FILE_POSTFIX}\" ..."
awk '{ total += $1; count++ } END { print total/count }' \
    < ${NR_OF_TAGS_FILE_POSTFIX} \
    > ${AVERAGE_NR_OF_TAGS_FILE_POSTFIX}

#end