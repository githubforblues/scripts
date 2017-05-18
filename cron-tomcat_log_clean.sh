#!/bin/bash
#

PATH="./logs/server.log."
SIZE=10

NUM=`/bin/ls -l $PATH* | /usr/bin/wc -l | /usr/bin/tail -n 1`
if [ $SIZE -lt $NUM ];then
let NUM=$NUM-$SIZE
	for i in `/bin/ls -l -t $PATH* | /usr/bin/tail -n $NUM | /bin/awk '{print $NF}'`;do
		/bin/rm -f $i
	done
fi

