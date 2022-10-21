#!/bin/bash

> test_eeprom.log

while true
do
	dd if=/dev/random of=rand bs=1k count=16 >> test_eeprom.log 2>&1
	md5orig=$(md5sum rand | cut -d ' ' -f 1)

	python ../examples/file2eeprom.py -k 128 -f rand -p 64 -r 47 >> test_eeprom.log
	python ../examples/eeprom2file.py -k 128 -f rand2.bin >> test_eeprom.log

	md5eeprom=$(md5sum rand2.bin | cut -d ' ' -f 1)

	if [ $md5eeprom == $md5orig ]
	then
		echo "Ok"
	else
		echo "Fail"
		exit
	fi

done
