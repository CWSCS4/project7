#!/usr/bin/env node
const fs = require('fs')
const path = require('path')

if (process.argv.length !== 3) throw new Error('Incorrect syntax. Use: ./compile-vm.js FILE[.asm]')

const DECREMENT_AND_LOAD_SP = [
	'@SP',
	'AM=M-1'
]
const POP_INTO_D = DECREMENT_AND_LOAD_SP
	.concat(['D=M'])
const PUSH_FROM_D = [
	'@SP',
	'M=M+1',
	'A=M-1',
	'M=D'
]
const ADD_INSTRUCTION = POP_INTO_D
	.concat(DECREMENT_AND_LOAD_SP)
	.concat(['D=M+D'])
	.concat(PUSH_FROM_D)
class AddInstruction {
	toHack() {
		return ADD_INSTRUCTION
	}
}
const AND_INSTRUCTION = POP_INTO_D
	.concat(DECREMENT_AND_LOAD_SP)
	.concat(['D=M&D'])
	.concat(PUSH_FROM_D)
class AndInstruction {
	toHack() {
		return AND_INSTRUCTION
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
			'(' + endLabel + ')'
		])
		.concat(PUSH_FROM_D)
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
const NEG_INSTRUCTION = DECREMENT_AND_LOAD_SP
	.concat(['D=-M'])
	.concat(PUSH_FROM_D)
class NegInstruction {
	toHack() {
		return NEG_INSTRUCTION
	}
}
const NOT_INSTRUCTION = DECREMENT_AND_LOAD_SP
	.concat(['D=!M'])
	.concat(PUSH_FROM_D)
class NotInstruction {
	toHack() {
		return NOT_INSTRUCTION
	}
}
const OR_INSTRUCTION = POP_INTO_D
	.concat(DECREMENT_AND_LOAD_SP)
	.concat(['D=M|D'])
	.concat(PUSH_FROM_D)
class OrInstruction {
	toHack() {
		return OR_INSTRUCTION
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
const TEMP_SEGMENT_OFFSET = 5
function getPositionIntoD({positionArguments, className}) {
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
		case 'static': {
			return [
				'@' + className + '.' + offset,
				'D=A'
			]
		}
		case 'temp': {
			return [
				'@' + String(TEMP_SEGMENT_OFFSET + Number(offset)),
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
	constructor({positionArguments, className}) {
		this.instructions = getPositionIntoD({positionArguments, className})
			.concat([
				'@R15',
				'M=D'
				
			])
			.concat(POP_INTO_D)
			.concat([
				'@R15',
				'A=M',
				'M=D'
			])
	}
	toHack() {
		return this.instructions
	}
}
function getValueIntoD({positionArguments, className}) {
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
			const intoDInstructions = getPositionIntoD({positionArguments, className})
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
	constructor({positionArguments, className}) {
		this.instructions = getValueIntoD({positionArguments, className})
			.concat(PUSH_FROM_D)
	}
	toHack() {
		return this.instructions
	}
}
const SUB_INSTRUCTION = POP_INTO_D
	.concat(DECREMENT_AND_LOAD_SP)
	.concat(['D=M-D'])
	.concat(PUSH_FROM_D)
class SubInstruction {
	toHack() {
		return SUB_INSTRUCTION
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
const rootFile = file.substring(0, file.length - VM.length)
const inStream = fs.createReadStream(file)
inStream.on('error', err => {
	throw new Error('Could not find file: ' + file)
})
const fullFile = path.resolve(rootFile)
const className = fullFile.substring(fullFile.lastIndexOf(path.sep) + 1)
const outStream = fs.createWriteStream(rootFile + ASM)
const EMPTY_LINE = /^\s*(?:\/\/.*)?$/
getLines(inStream, line => {
	line = line.trim()
	if (EMPTY_LINE.test(line)) return
	const commandArguments = line.split(' ')
	const [command, ...positionArguments] = commandArguments
	let instruction
	switch (command) {
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
			instruction = new PopInstruction({positionArguments, className})
			break
		}
		case 'push': {
			instruction = new PushInstruction({positionArguments, className})
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
}, () => outStream.end())