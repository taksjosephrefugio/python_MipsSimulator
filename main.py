# This program is a MIPS simulator
# This program takes in a machine code written in Hexadecimal and simulate MIPS based on said machine code
# At the end of the program, this should give a summary of values held in the registers and in the Memory Address Array
# Code Written for: ECE-366 Spring 2019, UIC, Prof. Wenjing Rao
# Code Written by: Tak's Joseph Refugio, J.B. Ruutelmann, Rohith 'Fortnight' Roy
# Code Written on: February 2019

# takes in a number n and returns an array of zeroes with size n
def InitZero(n):
    a = []              # temp array
    i = 0
    while i < n:
        a.append(0)     # populate temp array w/ zeroes
        i += 1
    return a            

######################
# GLOBAL VARIABLES ###
######################
# Registers
pc = 0                                  # stores pc count in int
reg = InitZero(17);                     # stores int values for $8-$23
MemoryArray = InitZero(501)             # 501 Memory Addresses: 0x2000-0x3000
Hex_Machine_Array = []                  # a string array of machine code hex values that needed to be read in later
Bin_Machine_Array = []                  # int-wise same as hex but is now stored as binary string
HamWt_Array = []                        # stores the hamming weight for S0 - S15
ProcessState = 'ON'                     # tells whether to keep going or end the processing
curr_int_str = "error"                  # holds the string eq   uivalent of the current instruction
instr_count = 0                         # holds the instruction count

# reads input.txt as source
def ReadFile():
    global Hex_Machine_Array

    File = open("input.txt", "r")                        # opening the file
    Hex_Machine_Array = File.read().splitlines()        # reading line-by-line
    codeCount = len(Hex_Machine_Array)
    tempString = " "

    for i in range(codeCount):
        tempString = Hex_Machine_Array[i] 
        Hex_Machine_Array[i] = tempString[2:10]

    codeCount = len(Hex_Machine_Array)

    for i in range(codeCount):
        temp = format(int(Hex_Machine_Array[i], 16), "032b")
        Bin_Machine_Array.append(temp) 

# prints the contents of memory
def PrintMemory():
    x = 8192;   #integer version of 0x2000
    
    y = 0;  #border trigger
    z = 0;  #trigger for printing top/bottom borders
    
    for i in range( len(MemoryArray) ):
        if (MemoryArray[i] != 0):
            if(not z):  #if there is a value in memory
                print("####################################################")
                print('\t\t\t\t\t\t\t| M E M O R Y      |\n')
                z+=1
            print("# Address: ", hex(x), "| Value:", MemoryArray[i], " #"); y+=1;
            
        x+=4
       
    if(z):
        print("\n")

    if(not y):
        print("###################")
        print("# Memory is empty #");
        print("###################")

# prints the contents of memory
def PrintRegisters():
    count = 0
    print("---------------------------------")
    print("\t\t\t\t\t\t\t| R E G I S T E R S |     \n")
    for i in range(17):
        if i is 0:
            if reg[i] is not 0:
                print("| $" +str(i)+" = " +str(reg[i])+" |")
                count = count + 1
        else:
            if reg[i] is not 0:
                print("| $" +str(i+7)+" = " +str(reg[i])+ "  |")
                count = count + 1
    if count == 0:
        print("All Registers Have No Values")

    print ("| PC = " + str(pc) + " |")

# prints the seeds values
def PrintSeeds():
    print("******************************************************")
    print("\t\t\t\t\t\t\t| S E E D S |        \n")
    i = 4                                       # starting at 0x2010
    while i < 20:       #S0 - S15
        print("* S" + str(i-4) + "\t= " + str(MemoryArray[i]))
        i += 1

# prints the average of the seeds values
def PrintAverage():
    global avg
    i = 4
    seed_sum = 0
    while i < 20:
        seed_sum += MemoryArray[i]
        i += 1

    avg = seed_sum / 4
    MemoryArray[3] = avg                        # store avg in Mem[0x200c]
    print("Seed Sum:\t\t" + str(seed_sum))
    print("Seed Average:\t\t" + str(MemoryArray[3]))

# # prints the hamming weight
def PrintHamW():
    one_ctr = 0
    for i in range(16):                         # iterate through all seeds
        test_num = MemoryArray[i + 4]           # test each seeds
        test_str = format(test_num, '032b')
        for j in range(32):                     # count no. of '1' for each seeds
            if test_str[j] == '1':
                one_ctr += 1
        HamWt_Array.append(one_ctr)             # populating HamWt_Array
        one_ctr = 0                             # reset one_ctr for next seed

    # calculate average hamming weight
    sum_hamwt = 0
    for i in range(16):
        sum_hamwt += HamWt_Array[i]
    avg_hamwt = sum_hamwt / 16
    MemoryArray[0] = avg_hamwt
    print("Average Hamming Weight:\t" + str(avg_hamwt))

# print the instruction count
def PrintInstrCnt():
    global instr_count
    print('Instruction Count:\t' + str(instr_count))

# takes an actual register name (i.e. if $8 then int_reg = 8) and returns an index to be usable in reg[] array
def GiveMeRegIndex(int_reg):
    if int_reg == 0:
        index = 0                   # for $0
    else:
        index = int_reg - 7         # reg array starts for $8
    return index

# input: int; return: binary string format of the 2s Comp
def TwosComp_16(int_num):
    bin_num = format(int_num,'016b')
    
    hex_mask = '0xFFFF'
    bin_mask = format(int(hex_mask,16), '016b')
    
    int_flip = int(bin_num,2) ^ int(bin_mask,2)
    bin_flip = format(int_flip, '016b')
    add_one = int(bin_flip,2) + 1
    result = format(add_one, '016b')
    return result

# input: int; return: binary string format of the 2s Comp
def TwosComp_32(int_num):
    bin_num = format(int_num,'032b')
    
    hex_mask = '0xFFFFFFFF'
    bin_mask = format(int(hex_mask,16), '032b')
    
    int_flip = int(bin_num,2) ^ int(bin_mask,2)
    bin_flip = format(int_flip, '032b')
    add_one = int(bin_flip,2) + 1
    result = format(add_one, '032b')
    return result

# takes pc_count (a multiple of 4) and converts it to usable index integers (0, 1, 2, ...)
def pc2Index(pc_count):
    return pc_count/4

# takes an integer representing a memory address and converts it to usable index integers (0, 1, 2, ...)
def MemAdd2Index(int_MemAdd):
    int_base_memory = int('0x00002000', 16)
    return (int_MemAdd - int_base_memory)/4

# does MIPS calculation depending on input binary
def Decoder(curr_bin):
    global ProcessState
    global curr_int_str
    global pc

    if curr_bin[0:32] == "00010000000000001111111111111111": # END Instruction
        ProcessState = 'OFF'
        curr_int_str = ("beq $0, $0, end")


    ############################################# START OF R-TYPES  #############################################
    elif curr_bin[0:6] == "000000" and curr_bin[26:32] == "100000":   # ADD
        int_rs = int(curr_bin[6:11],2)
        int_rt = int(curr_bin[11:16],2)
        int_rd = int(curr_bin[16:21],2)

        rs = GiveMeRegIndex(int_rs)
        rt = GiveMeRegIndex(int_rt)
        rd = GiveMeRegIndex(int_rd)
        reg[rd] = reg[rs] + reg[rt]

        #updating string
        curr_int_str = ("add $" + str(int_rd) + ", $" + str(int_rs) + ", $" + str(int_rt))
        pc += 4

    elif curr_bin[0:6] == "000000" and curr_bin[26:32] == "100001":   # ADDU
        int_rs = int(curr_bin[6:11],2)
        int_rt = int(curr_bin[11:16],2)
        int_rd = int(curr_bin[16:21],2)

        rs = GiveMeRegIndex(int_rs)
        rt = GiveMeRegIndex(int_rt)
        rd = GiveMeRegIndex(int_rd)
        
        reg[rd] = reg[rs] + reg[rt]

        #updating string
        curr_int_str = ("addu $" + str(int_rd) + ", $" + str(int_rs) + ", $" + str(int_rt))
        pc += 4

    elif curr_bin[0:6] == "000000" and curr_bin[26:32] == "100010":    # SUB
        int_rs = int(curr_bin[6:11],2)
        int_rt = int(curr_bin[11:16],2)
        int_rd = int(curr_bin[16:21],2)

        rs = GiveMeRegIndex(int_rs)
        rt = GiveMeRegIndex(int_rt)
        rd = GiveMeRegIndex(int_rd)
        reg[rd] = reg[rs] - reg[rt] 
        
        #updating string
        curr_int_str = ("sub $" + str(int_rd) + ", $" + str(int_rs) + ", $" + str(int_rt))
        pc += 4

    elif curr_bin[0:6] == "000000" and curr_bin[26:32] == "100101":   # OR
        int_rs = int(curr_bin[6:11],2)
        int_rt = int(curr_bin[11:16],2)
        int_rd = int(curr_bin[16:21],2)

        rs = GiveMeRegIndex(int_rs)
        rt = GiveMeRegIndex(int_rt)
        rd = GiveMeRegIndex(int_rd)
        reg[rd] = reg[rs] | reg[rt]

        curr_int_str = ("or $" + str(int_rd) + ", $" + str(int_rs) + ", $" + str(int_rt)) 
        pc += 4

    elif curr_bin[0:6] == "000000" and curr_bin[26:32] == "100110":   # XOR
        int_rs = int(curr_bin[6:11],2)
        int_rt = int(curr_bin[11:16],2)
        int_rd = int(curr_bin[16:21],2)

        rs = GiveMeRegIndex(int_rs)
        rt = GiveMeRegIndex(int_rt)
        rd = GiveMeRegIndex(int_rd)
        reg[rd] = reg[rs] ^ reg[rt]

        #updating string
        curr_int_str = ("xor $" + str(int_rd) + ", $" + str(int_rs) + ", $" + str(int_rt))
        pc += 4

    elif curr_bin[0:6] == "000000" and curr_bin[26:32] == "100100":   # AND
        int_rs = int(curr_bin[6:11],2)
        int_rt = int(curr_bin[11:16],2)
        int_rd = int(curr_bin[16:21],2)

        rs = GiveMeRegIndex(int_rs)
        rt = GiveMeRegIndex(int_rt)
        rd = GiveMeRegIndex(int_rd)
        reg[rd] = reg[rs] & reg[rt]

        #updating string
        curr_int_str = ("and $" + str(int_rd) + ", $" + str(int_rs) + ", $" + str(int_rt))
        pc += 4

    elif curr_bin[0:6] == "000000" and curr_bin[26:32] == "000000":   # SLL
        #int_rs = int(curr_bin[6:11],2)  #dont care
        int_rt = int(curr_bin[11:16],2) #source
        int_rd = int(curr_bin[16:21],2) #dest
        shift = int(curr_bin[21:26],2) #shift amt
        
        #rs = GiveMeRegIndex(int_rs)
        rt = GiveMeRegIndex(int_rt)
        rd = GiveMeRegIndex(int_rd)
        reg[rd] = reg[rt] << (shift)

        #updating string
        curr_int_str = ("sll $" + str(int_rd) + ", $" + str(int_rt) + ", " + str(shift))
        pc += 4

    elif curr_bin[0:6] == "000000" and curr_bin[26:32] == "000010":   # SRL
        #int_rs = int(curr_bin[6:11],2)  #dont care
        int_rt = int(curr_bin[11:16],2) #source
        int_rd = int(curr_bin[16:21],2) #dest
        shift = int(curr_bin[21:26],2) #shift amt
        
        #rs = GiveMeRegIndex(int_rs)
        rt = GiveMeRegIndex(int_rt)
        rd = GiveMeRegIndex(int_rd)
        reg[rd] = reg[rt] >> (shift)

        #updating string
        curr_int_str = ("srl $" + str(int_rd) + ", $" + str(int_rt) + ", " + str(shift))
        pc += 4

    elif curr_bin[0:6] == "000000" and curr_bin[26:32] == "101010":   # SLT
        int_rs = int(curr_bin[6:11],2)  
        int_rt = int(curr_bin[11:16],2) 
        int_rd = int(curr_bin[16:21],2)
        
        rs = GiveMeRegIndex(int_rs)
        rt = GiveMeRegIndex(int_rt)
        rd = GiveMeRegIndex(int_rd)
        
        if reg[rs] < reg[rt]:
            reg[rd] = 1
        else:
            reg[rd] = 0

        #updating string
        curr_int_str = ("slt $" + str(int_rd) + ", $" + str(int_rs) + ", $" + str(int_rt))
        pc += 4
    

    ############################################# START OF I-TYPES  #############################################
    elif curr_bin[0:6] == "001000":                                                             # ADDI
        int_rs = int(curr_bin[6:11],2)
        int_rt = int(curr_bin[11:16],2)
        imm = int(curr_bin[16:32],2)

        if curr_bin[16] == '1':
            imm_2s_comp = TwosComp_16(imm)
            imm = -int(imm_2s_comp,2)

        rs = GiveMeRegIndex(int_rs)
        rt = GiveMeRegIndex(int_rt)
        reg[rt] = reg[rs] + imm

        #updating string
        curr_int_str = ("addi $" + str(int_rt) + ", $" + str(int_rs) + ", " + str(imm))
        pc += 4

    elif curr_bin[0:6] == "001100":                                                             # ANDI
        int_rs = int(curr_bin[6:11],2)
        int_rt = int(curr_bin[11:16],2)
        imm = int(curr_bin[16:32],2)
        
        rs = GiveMeRegIndex(int_rs)
        rt = GiveMeRegIndex(int_rt)
        reg[rt] = reg[rs] & imm

        #updating string
        curr_int_str = ("andi $" + str(int_rt) + ", $" + str(int_rs) + ", " + str(imm))
        pc += 4

    elif curr_bin[0:6] == "001101":                                                             # ORI
        int_rs = int(curr_bin[6:11],2)
        int_rt = int(curr_bin[11:16],2)
        imm = int(curr_bin[16:32],2)

        rs = GiveMeRegIndex(int_rs)
        rt = GiveMeRegIndex(int_rt)
        reg[rt] = reg[rs] | imm

        #updating string
        curr_int_str = ("ori $" + str(int_rt) + ", $" + str(int_rs) + ", " + str(imm))
        pc += 4

    elif curr_bin[0:6] == "000100":                                                             # BEQ
        int_rs = int(curr_bin[6:11],2)
        int_rt = int(curr_bin[11:16],2)
        bin_imm = curr_bin[16:32]     

        rs = GiveMeRegIndex(int_rs)
        rt = GiveMeRegIndex(int_rt)

        pc += 4       
        fin_int_imm = int(bin_imm,2)
        if reg[rs] == reg[rt]:
            if curr_bin[16] == '1':                 # if imm is a negative
                int_imm = int(bin_imm,2)
                bin_2s_comp = TwosComp_16(int_imm)
                fin_int_imm = -int(bin_2s_comp,2)
            else:                                   # if imm is positive
                fin_int_imm = int(bin_imm,2)
            pc += (fin_int_imm * 4)
        curr_int_str = ("beq $" + str(int_rt) + ", $" + str(int_rs) + ", " + str(int(bin_imm,2)))

    elif curr_bin[0:6] == "000101":                                                             # BNE
        int_rs = int(curr_bin[6:11],2)
        int_rt = int(curr_bin[11:16],2)
        bin_imm = curr_bin[16:32]     

        rs = GiveMeRegIndex(int_rs)
        rt = GiveMeRegIndex(int_rt)

        pc += 4
        fin_int_imm = int(bin_imm,2)
        if reg[rs] != reg[rt]:
            if curr_bin[16] == '1':                 # if imm is a negative             
                int_imm = int(bin_imm,2)
                bin_2s_comp = TwosComp_16(int_imm)
                fin_int_imm = -int(bin_2s_comp,2)
            else:                                   # if imm is positive
                fin_int_imm = int(bin_imm,2)
            pc += (fin_int_imm * 4)
        curr_int_str = ("bne $" + str(int_rt) + ", $" + str(int_rs) + ", " + str(fin_int_imm))

    elif curr_bin[0:6] == "101011":                                                             # SW
        int_rs = int(curr_bin[6:11],2)
        int_rt = int(curr_bin[11:16],2)
        int_imm = int(curr_bin[16:32],2)

        rs = GiveMeRegIndex(int_rs)
        rt = GiveMeRegIndex(int_rt)

        if curr_bin[16] == '1':
            bin_2s_comp = TwosComp_16(int_imm)
            int_imm = -int(bin_2s_comp,2)

        int_target_mem = reg[rs] + int_imm
        target_index = MemAdd2Index(int_target_mem)
        MemoryArray[target_index] = reg[rt]

        pc += 4
        curr_int_str = ("sw $" + str(int_rt) + ", " + str(int_imm) + "($" + str(int_rs) + ")")

    elif curr_bin[0:6] == "100011":                                                             # LW
        int_rs = int(curr_bin[6:11],2)
        int_rt = int(curr_bin[11:16],2)
        int_imm = int(curr_bin[16:32],2)

        rs = GiveMeRegIndex(int_rs)
        rt = GiveMeRegIndex(int_rt)

        if curr_bin[16] == '1':
            bin_2s_comp = TwosComp_16(int_imm)
            int_imm = -int(bin_2s_comp,2)

        int_target_mem = reg[rs] + int_imm
        target_index = MemAdd2Index(int_target_mem)
        reg[rt] = MemoryArray[target_index]

        pc += 4
        curr_int_str = ("lw $" + str(int_rt) + ", " + str(int_imm) + "($" + str(int_rs) + ")")

    ############################################# START OF J-TYPE  #############################################
    elif curr_bin[0:6] == "000010":             # JUMP
        
        bin_imm = curr_bin[6:32] 
        imm_sign = curr_bin[6]

        pc += 4
        
        if(imm_sign == '1'):            #immediate is negative
            imm =TwosComp_26(bin_imm)   #convert integer->two's comp-> integer with correct sign
                    
        else:                   #immediate is positive
                imm = int(bin_imm,2)    #convert to integer
            
        pc += (imm*4)
        curr_int_str = ("jump", imm)
        print("curr_bin is", curr_bin, "imm_sign is", imm_sign)

# MAIN FUNCTION
def main():
    ReadFile()
    print(Hex_Machine_Array)
    print(Bin_Machine_Array)

    global instr_count
    while ProcessState == 'ON':
        i = pc2Index(pc)
        Decoder(Bin_Machine_Array[i])
        instr_count += 1
    
    if ProcessState == 'OFF':
        print('\n\n\n')
        print("//////////////////////////////////////////////////////////////////////////")
        print("//////////////////////// F I N A L  R E S U L T //////////////////////////")
        print("//////////////////////////////////////////////////////////////////////////")
        print('\n')
        PrintSeeds()
        PrintAverage()
        PrintHamW()
        PrintInstrCnt()
        PrintRegisters()
        PrintMemory()

# These next lines are necessary in Python in order for the Python interpreter to call the main function. 
if __name__ == "__main__":
    main()