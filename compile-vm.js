#!/usr/bin/env node
const fs = require('fs')

if (process.argv.length !== 3) throw new Error('Incorrect syntax. Use: ./compile-vm.js FILE[.asm]')

class EqInstruction {
	toString() {
		const eqLabel = 'EQ_' + String(instructions.length)
		const endLabel = 'END_' + eqLabel
		return [
			'@SP',
			'M=M-1',
			'A=M',
			'D=M',
			'@SP',
			'M=M-1',
			'A=M',
			'D=D-M',
			'@' + eqLabel,
			'D;JEQ',
			'D=0',
			'@' + endLabel,
			'0;JMP',
			'(' + eqLabel + ')',
			'D=1',
			'(' + endLabel + ')',
			'@SP',
			'M=M+1',
			'A=M-1',
			'M=D'
		]
	}
}
function getR15Instructions(positionArguments) {
	switch (positionArguments[0]) {
		default: {
			throw new Error('Unknown segment: "' + positionArguments[0] + '"')
		}
	}
}
class PushInstruction {
	constructor(positionArguments) {
		this.r15Instructions = getR15Instructions(positionArguments)
	}
}

function getLines(stream, lineCallback, endCallback) {
	let residual = ''
	stream.on('data', chunk => {
		chunk = chunk.toString()
		let lastConsumed = 0
		for (let i = 0; i < chunk.length; i++) {
			if (chunk[i] === '\n') {
				lineCallback(residual + chunk.substring(lastConsumed, i))
				residual = ''
				lastConsumed = i + 1
			}
		}
		residual += chunk.substring(lastConsumed)
	})
	stream.on('end', () => {
		lineCallback(residual)
		endCallback()
	})
}

const VM = '.vm'
const HACK = '.hack'
const file = process.argv[2]
let rootFile
if (file.endsWith(VM)) rootFile = file.substring(0, file.length - VM.length)
else rootFile = file
const inStream = fs.createReadStream(rootFile + VM)
inStream.on('error', err => {
	throw new Error('Could not find file: ' + rootFile + VM)
})
const INITIALIZE_INSTRUCTIONS = [
	'@256',
	'D=A',
	'@SP',
	'M=D'
]
const instructions = []
const EMPTY = /^\s*(?:\/\/.*)?$/
getLines(inStream, line => {
	line = line.trim()
	if (EMPTY.test(line)) return
	const commandArguments = line.split(' ')
	let instruction
	switch (commandArguments[0]) {
		case 'eq': {
			instruction = new EqInstruction
			break
		}
		case 'push': {
			const [_, ...positionArguments] = commandArguments
			instruction = new PushInstruction(positionArguments)
			break
		}
		default: {
			throw new Error('Unrecognized command in "' + line + '"')
		}
	}
	for (const hackInstruction of instruction.toHack()) instructions.push(hackInstruction)
}, () => {
	const outStream = fs.createWriteStream(rootFile + HACK)
	for (const instructionSet of [INITIALIZE_INSTRUCTIONS, instructions]) {
		for (const instruction of instructionSet) {
			outStream.write(instruction)
			outStream.write('\n')
		}
	}
	outStream.end()
})