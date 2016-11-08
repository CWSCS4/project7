#!/bin/bash
for vm in */*/*.vm; do
	base=${vm/.vm/}
	echo Compiling $base
	./compile-vm.js $base && Assembler.sh $base > /dev/null
done