"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # This will hold our 256 bytes of memory
        self.ram = [0] * 256

        # This will hold out 8 general purpose registers
        self.reg = [0] * 8

        # This is our program counter. It holds the address of the currently executing instruction
        self.pc = 0

        self.SP = self.reg[7]

        self.ir = 0

        self.flag = 0B00000000

        self.branch_table = {
            0b10000010: self.LDI,
            0b01000111: self.PRN,
            0b00000001: self.HLT,
            0b10100000: self.ADD,
            0b10100010: self.MUL,
            0b01000101: self.PUSH,
            0b01000110: self.POP,
            0b00010001: self.RET,
            0b01010000: self.CALL,
            0b01010100: self.JMP,
            0b01010101: self.JEQ,
            0b01010110: self.JNE
        }

    def ram_read(self, MAR):
        # Memory Address Register (MAR)
        # MAR contains the address that is being read
        return self.ram[MAR]

    def ram_write(self, MAR, MDA):
        # MDR contains the data that was read or the data to write.
        # Memory Data Register (MDR)
        # Memory Address Register (MAR)
        # MAR contains the address that is being read or written to

        self.ram[MAR] = MDA
        return self.ram[MAR]

    def load(self, prog_path):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]
        program = []
        with open(prog_path) as f:
            for line in f:
                comment_split = line.split('#')
                n = comment_split[0].strip()

                if n == '':
                    continue

                x = int(n, 2)
                program.append(x)

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
            # added the option for multiplication
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] < self.reg[reg_b]:
                self.flag = 0b00000100
            if self.reg[reg_a] > self.reg[reg_b]:
                self.flag = 0b00000010
            if self.reg[reg_a] == self.reg[reg_b]:
                self.flag = 0b00000001
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def HLT(self):
        self.running = False

    def LDI(self):
        address = self.ram_read(self.pc + 1)
        value = self.ram_read(self.pc + 2)
        self.reg[address] = value

    def PRN(self):
        address = self.ram_read(self.pc + 1)
        value = self.reg[address]
        print(value)

    def ADD(self):
        operandA = self.ram_read(self.pc + 1)
        operandB = self.ram_read(self.pc + 2)
        self.alu('ADD', operandA, operandB)

    def MUL(self):
        operandA = self.ram_read(self.pc + 1)
        operandB = self.ram_read(self.pc + 2)
        self.alu('MUL', operandA, operandB)

    def PUSH(self):
        self.sp -= 1
        address = self.ram[self.pc + 1]
        value = self.reg[address]
        self.ram[self.sp] = value

    def POP(self):
        address = self.ram[self.pc + 1]
        value = self.ram[self.sp]
        self.reg[address] = value
        self.sp += 1

    def CALL(self):
        self.sp -= 1
        self.ram[self.sp] = self.pc + 2
        regis = self.ram[self.pc + 1]
        self.pc = self.reg[regis]

    def RET(self):
        self.pc = self.ram[self.sp]
        self.sp += 1

    def CMP(self):
        op_a = self.ram_read(self.pc + 1)
        op_b = self.ram_read(self.pc + 2)
        self.alu("CMP", op_a, op_b)
        self.pc += 3

    def JMP(self):
        # get address from register
        reg_num = self.ram_read(self.pc + 1)
        # set pc to address
        self.pc = self.reg[reg_num]

    def JEQ(self):
        if self.flag == 0b00000001:
            reg_num = self.ram_read(self.pc + 1)
            self.pc = self.reg[reg_num]
        else:
            self.pc += 2

    def JNE(self):
        if self.flag != 0b00000001:
            reg_num = self.ram_read(self.pc + 1)
            self.pc = self.reg[reg_num]
        else:
            self.pc += 2

    def run(self):
        """Run the CPU."""

        self.running = True
        while self.running:
            ir = self.ram_read(self.pc)

            if ir in self.branch_table:
                self.branch_table[ir]()
                operands = (ir & 0b11000000) >> 6
                param = (ir & 0b00010000) >> 4

                if not param:
                    self.pc += operands + 1

            else:
                self.running = False
                print(f"Terminated due to bad input. {ir} at {self.pc}")
