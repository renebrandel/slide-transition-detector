#!/bin/bash

while [[ $# -gt 1 ]];
do
    key="$1"
    case $key in 
        -p|--prefix)
            PREFIX="$2"
            shift
            ;;
        -f|--filetype)
            FILETYPE="$2"
            shift
            ;;
        -o|--output)
            OUTPUT="$2"
            shift
            ;;
        -i|--index)
            INDEX="$2"
            shift
            ;;
        *)
        ;;
    esac
    shift
done
FILETYPE=".$FILETYPE"


TMP=/tmp/$$/
mkdir $TMP

TMPCOUNTER=/tmp/$$.tmp
echo $INDEX > $TMPCOUNTER


while [ true ]; do
    COUNTER=$(($(cat $TMPCOUNTER)+1))
    echo $PREFIX$COUNTER$FILETYPE
    if [ ! -f $PREFIX$COUNTER$FILETYPE ]; then
        break
    fi
    RAND=$(shuf -i 1-40 -n 1)
    ffmpeg -loop 1 -f image2 -vframes 100 -i $PREFIX$COUNTER$FILETYPE -vcodec libx264 -b 800k -t $RAND $TMP$COUNTER.mp4
    echo $COUNTER > $TMPCOUNTER
done
LENGTH=$(($(cat $TMPCOUNTER)))
VIDEO_LOC=videos/loc.txt
VIDEOS=""
for i in $(seq 1 $LENGTH);
do
    VIDEOS="$VIDEOS$TMP$i.mp4 "
done    
echo $VIDEOS

mencoder -oac copy -ovc copy -idx -o $OUTPUT.mp4 $VIDEOS

rm -rf $TMP
unlink $TMPCOUNTER
