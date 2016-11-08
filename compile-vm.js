#!/usr/bin/env node
const fs = require('fs')

if (process.argv.length !== 3) throw new Error('Incorrect syntax. Use: ./compile-vm.js FILE[.asm]')

const DECREMENT_AND_LOAD_SP = [
	'@SP',
	'AM=M-1'
]
const POP_INTO_D = DECREMENT_AND_LOAD_SP
	.concat(['D=M'])
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
			.concat(['D=M+D'])
			.concat(PUSH_FROM_D)
	}
}
class AndInstruction {
	toHack() {
		return POP_INTO_D
			.concat(DECREMENT_AND_LOAD_SP)
			.concat(['D=M&D'])
			.concat(PUSH_FROM_D)
	}
}
let comparisonLabelID = 0
function comparisonInstructions(jmpTrue) {
	const jmpTrueLabel = jmpTrue + '_' + String(comparisonLabelID++) //guarantee no collisions
	const endLabel = 'END_' + jmpTrueLabel
	return POP_INTO_D
		.concat([
			'@SP',
			'AM=M-1',
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
			.concat(['D=-M'])
			.concat(PUSH_FROM_D)
	}
}
class NotInstruction {
	toHack() {
		return DECREMENT_AND_LOAD_SP
			.concat(['D=!M'])
			.concat(PUSH_FROM_D)
	}
}
class OrInstruction {
	toHack() {
		return POP_INTO_D
			.concat(DECREMENT_AND_LOAD_SP)
			.concat(['D=M|D'])
			.concat(PUSH_FROM_D)
	}
}
function getVariableSegmentStartIntoD(segment) {
	let segmentStartPointer
	switch (segment) {
		case 'argument': {
			segmentStartPointer = '@ARG'
			break
		}
		case 'local': {
			segmentStartPointer = '@LCL'
			break
		}
		case 'this': {
			segmentStartPointer = '@THIS'
			break
		}
		case 'that': {
			segmentStartPointer = '@THAT'
			break
		}
		default: {
			throw new Error('Segment "' + segment + '" is not a variable segment')
		}
	}
	return [
		segmentStartPointer,
		'D=M'
	]
}
function getFixedSegmentStart(segment) {
	switch (segment) {
		case 'static': {
			return 16
			break
		}
		case 'temp': {
			return 5
			break
		}
		default: {
			throw new Error('Segment "' + segment + '" is not a fixed segment')
		}
	}
}
function getPositionIntoD(positionArguments) {
	const [segment, offset] = positionArguments
	switch (segment) {
		case 'argument':
		case 'local':
		case 'this':
		case 'that': {
			return getVariableSegmentStartIntoD(segment)
				.concat([
					'@' + offset,
					'D=D+A'
				])
		}
		case 'static':
		case 'temp': {
			return [
				'@' + String(getFixedSegmentStart(segment) + Number(offset)),
				'D=A'
			]
		}
		case 'pointer': {
			let position
			switch (offset) {
				case '0': {
					position = '@THIS'
					break
				}
				case '1': {
					position = '@THAT'
					break
				}
				default: {
					throw new Error('Unknown pointer offset: ' + offset)
				}
			}
			return [
				position,
				'D=A'
			]
		}
		default: {
			throw new Error('Unknown segment: "' + segment + '"')
		}
	}
}
class PopInstruction {
	constructor(positionArguments) {
		this.instructions = POP_INTO_D
			.concat([
				'@R14',
				'M=D'
			])
			.concat(getPositionIntoD(positionArguments))
			.concat([
				'@R15',
				'M=D',
				'@R14',
				'D=M',
				'@R15',
				'A=M',
				'M=D'
			])
	}
	toHack() {
		return this.instructions
	}
}
function getValueIntoD(positionArguments) {
	const [segment, offset] = positionArguments
	switch (segment) {
		case 'constant': {
			return [
				'@' + offset,
				'D=A'
			]
			break
		}
		case 'argument':
		case 'local':
		case 'static':
		case 'this':
		case 'that':
		case 'pointer':
		case 'temp': {
			const intoDInstructions = getPositionIntoD(positionArguments)
			const lastInstruction = intoDInstructions[intoDInstructions.length - 1]
			if (lastInstruction === 'D=A') intoDInstructions.pop()
			else intoDInstructions[intoDInstructions.length - 1] = lastInstruction.replace('D=', 'A=')
			intoDInstructions.push('D=M')
			return intoDInstructions
		}
		default: {
			throw new Error('Unknown segment: "' + segment + '"')
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
			.concat(['D=M-D'])
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
const outStream = fs.createWriteStream(rootFile + ASM)
const EMPTY_LINE = /^\s*(?:\/\/.*)?$/
getLines(inStream, line => {
	line = line.trim()
	if (EMPTY_LINE.test(line)) return
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
		case 'pop': {
			const [_, ...positionArguments] = commandArguments
			instruction = new PopInstruction(positionArguments)
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
	for (const line of instruction.toHack()) {
		outStream.write(line)
		outStream.write('\n')
	}
}, () => {
	outStream.end()
})