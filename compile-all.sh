#!/bin/bash
for vm in */*/*.vm; do
	base=${vm/.vm/}
	echo Compiling $base
	./compile-vm.js $vm && Assembler.sh $base > /dev/null
done