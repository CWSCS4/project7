#!/usr/bin/env node
const fs = require('fs')

if (process.argv.length !== 3) throw new Error('Incorrect syntax. Use: ./compile-vm.js FILE[.asm]')

const DECREMENT_AND_LOAD_SP = [
	'@SP',
	'M=M-1',
	'A=M'
]
const POP_INTO_D = DECREMENT_AND_LOAD_SP.concat([
	'D=M'
])
const PUSH_FROM_D = [
	'@SP',
	'A=M',
	'M=D',
	'@SP',
	'M=M+1'
]
class AddInstruction {
	toHack() {
		return POP_INTO_D
			.concat(DECREMENT_AND_LOAD_SP)
			.concat([
				'D=M+D'
			])
			.concat(PUSH_FROM_D)
	}
}
class AndInstruction {
	toHack() {
		return POP_INTO_D
			.concat(DECREMENT_AND_LOAD_SP)
			.concat([
				'D=M&D'
			])
			.concat(PUSH_FROM_D)
	}
}
function comparisonInstructions(jmpTrue) {
	const jmpTrueLabel = jmpTrue + '_' + String(instructions.length) //guarantee no collisions
	const endLabel = 'END_' + jmpTrueLabel
	return POP_INTO_D.concat([
		'@SP',
		'M=M-1',
		'A=M',
		'D=M-D',
		'@' + jmpTrueLabel,
		'D;J' + jmpTrue,
		'D=0',
		'@' + endLabel,
		'0;JMP',
		'(' + jmpTrueLabel + ')',
		'D=-1',
		'(' + endLabel + ')',
		'@SP',
		'M=M+1',
		'A=M-1',
		'M=D'
	])
}
class GtInstruction {
	toHack() {
		return comparisonInstructions('GT')
	}
}
class EqInstruction {
	toHack() {
		return comparisonInstructions('EQ')
	}
}
class LtInstruction {
	toHack() {
		return comparisonInstructions('LT')
	}
}
class NegInstruction {
	toHack() {
		return DECREMENT_AND_LOAD_SP
			.concat([
				'D=-M'
			])
			.concat(PUSH_FROM_D)
	}
}
class NotInstruction {
	toHack() {
		return DECREMENT_AND_LOAD_SP
			.concat([
				'D=!M'
			])
			.concat(PUSH_FROM_D)
	}
}
class OrInstruction {
	toHack() {
		return POP_INTO_D
			.concat(DECREMENT_AND_LOAD_SP)
			.concat([
				'D=M|D'
			])
			.concat(PUSH_FROM_D)
	}
}
function getValueIntoD(positionArguments) {
	switch (positionArguments[0]) {
		case 'constant': {
			return [
				'@' + positionArguments[1],
				'D=A'
			]
			break
		}
		default: {
			throw new Error('Unknown segment: "' + positionArguments[0] + '"')
		}
	}
}
class PushInstruction {
	constructor(positionArguments) {
		this.instructions = getValueIntoD(positionArguments)
			.concat(PUSH_FROM_D)
	}
	toHack() {
		return this.instructions
	}
}
class SubInstruction {
	toHack() {
		return POP_INTO_D
			.concat(DECREMENT_AND_LOAD_SP)
			.concat([
				'D=M-D'
			])
			.concat(PUSH_FROM_D)
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
const ASM = '.asm'
const file = process.argv[2]
let rootFile
if (file.endsWith(VM)) rootFile = file.substring(0, file.length - VM.length)
else rootFile = file
const inStream = fs.createReadStream(rootFile + VM)
inStream.on('error', err => {
	throw new Error('Could not find file: ' + rootFile + VM)
})
const instructions = []
const EMPTY = /^\s*(?:\/\/.*)?$/
getLines(inStream, line => {
	line = line.trim()
	if (EMPTY.test(line)) return
	const commandArguments = line.split(' ')
	let instruction
	switch (commandArguments[0]) {
		case 'add': {
			instruction = new AddInstruction
			break
		}
		case 'and': {
			instruction = new AndInstruction
			break
		}
		case 'gt': {
			instruction = new GtInstruction
			break
		}
		case 'eq': {
			instruction = new EqInstruction
			break
		}
		case 'lt': {
			instruction = new LtInstruction
			break
		}
		case 'neg': {
			instruction = new NegInstruction
			break
		}
		case 'not': {
			instruction = new NotInstruction
			break
		}
		case 'or': {
			instruction = new OrInstruction
			break
		}
		case 'push': {
			const [_, ...positionArguments] = commandArguments
			instruction = new PushInstruction(positionArguments)
			break
		}
		case 'sub': {
			instruction = new SubInstruction
			break
		}
		default: {
			throw new Error('Unrecognized command in "' + line + '"')
		}
	}
	instructions.push(...instruction.toHack())
}, () => {
	const outStream = fs.createWriteStream(rootFile + ASM)
	for (const instruction of instructions) {
		outStream.write(instruction)
		outStream.write('\n')
	}
	outStream.end()
})