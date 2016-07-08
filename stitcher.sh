#!/bin/bash


PREFIX="slides/"
FILETYPE=".jpg"

TMP=/tmp/$$/
mkdir $TMP

TMPCOUNTER=/tmp/$$.tmp
echo -1 > $TMPCOUNTER


while [ true ]; do
    COUNTER=$(($(cat $TMPCOUNTER)+1))
    if [ ! -f $PREFIX$COUNTER$FILETYPE ]; then
        break
    fi
    RANDOM=$(shuf -i 1-40 -n 1)
    ffmpeg -loop 1 -f image2 -vframes 100 -i $PREFIX$COUNTER$FILETYPE -vcodec libx264 -t $RANDOM "$TMP$COUNTER.mp4"
    echo $COUNTER > $TMPCOUNTER
done
LENGTH=$(($(cat $TMPCOUNTER)))
VIDEOS=""
for i in $(seq 0 $LENGTH);
do
    echo $i
    VIDEOS="$VIDEOS $TMP$i.mp4 "
done    
echo $VIDEOS

mencoder -oac copy -ovc copy -idx -o $OUTPUT.mp4 $VIDEOS

rm -rf $TMP
unlink $TMPCOUNTER
