import sys
import os

code = []

try:
    with open(sys.argv[1], "r", encoding="UTF-8") as f:
        content = f.readlines()
except Exception as e:
    print("No file!")
    quit()

lines = []

for i in content:
    lines.append(i.strip())

nc_lines = []
for i in lines:
    if len(i) > 0:
        if i[0] != "#":
            nc_lines.append(i)

vars = {}

ncv_lines = []

code.append("DATA:")

for i in nc_lines:
    try:
        if i.split(" ")[0].lower() == "int":
            name = i.split(" ")[1]
            vars[name] = f"&{name}"
            code.append( f"&{ name } { int( i.split( ' ' )[2] ) }" )
        elif i.split(" ")[0].lower() == "str":
            name = i.split(" ")[1]
            vars[name] = f"&{name}"
            code.append( f'&{ name } "{ " ".join(i.split( " " )[2:] ) }"' )
        else:
            ncv_lines.append(i)
    except Exception as e:
        print(f"Error on line: {i}")
        quit()

size = 0

code.append("TEXT:")

for i in ncv_lines:
    #code.append(f"-- {i}")
    #code.append(f"STA 0")
    #code.append(f"STB 0")
    #code.append(f"STC 0")
    try:
        # ПРИСВАЕВАНИЕ
        if len(i.split("=")) == 2:
            s1 = i.split("=")
            p1 = s1[0].strip()
            p2 = s1[1].strip()
            if p1[0] == "$":
                set_to_name = p1[1:]
                if set_to_name in vars.keys():
                    set_to_addr = vars[set_to_name]
                    code.append(f"STC {set_to_addr}")
                    if len(p2.split("+")) == 2:
                        s2 = p2.split("+")
                        op1 = s2[0].strip()
                        op2 = s2[1].strip()
                        if len(op2) > 1 and op2[0] == "$":
                            op2_name = op2[1:]
                            if op2_name in vars.keys():
                                op2_addr = vars[op2_name]
                                code.append(f"STA {op2_addr}")
                                code.append(f"MPTR")
                                code.append(f"WRWB")
                            else:
                                print(f"Error on line: {i}")
                                quit()
                        else:
                            code.append(f"STB {op2}")
                        
                        if len(op1) > 1 and op1[0] == "$":
                            op1_name = op1[1:]
                            if op1_name in vars.keys():
                                op1_addr = vars[op1_name]
                                code.append(f"STA {op1_addr}")
                                code.append(f"MPTR")
                                code.append(f"WRWA")
                            else:
                                print(f"Error on line: {i}")
                                quit()
                        else:
                            code.append(f"STA {op1}")
                        code.append(f"SWAC")
                        code.append(f"MPTR")
                        code.append(f"SWAC")
                        code.append(f"ADD")
                        code.append(f"LDWA")
                        
                    elif len(p2.split("-")) == 2:
                        s2 = p2.split("+")
                        op1 = s2[0].strip()
                        op2 = s2[1].strip()
                        if len(op2) > 1 and op2[0] == "$":
                            op2_name = p2[1:]
                            if op2_name in vars.keys():
                                op2_addr = vars[op2_name]
                                code.append(f"STA {op2_addr}")
                                code.append(f"MPTR")
                                code.append(f"WRWB")
                            else:
                                print(f"Error on line: {i}")
                                quit()
                        else:
                            code.append(f"STB {op2}")
                        
                        if len(op1) > 1 and op1[0] == "$":
                            op1_name = p1[1:]
                            if op1_name in vars.keys():
                                op1_addr = vars[op1_name]
                                code.append(f"STA {op1_addr}")
                                code.append(f"MPTR")
                                code.append(f"WRWA")
                            else:
                                print(f"Error on line: {i}")
                                quit()
                        else:
                            code.append(f"STA {op1}")
                        code.append(f"SWAC")
                        code.append(f"MPTR")
                        code.append(f"SWAC")
                        code.append(f"SUB")
                        code.append(f"LDWA")
                    else:
                        if len(p2) > 1 and p2[0] == "$":
                            p2_name = p2[1:]
                            if p2_name in vars.keys():
                                p2_addr = vars[p2_name]
                                code.append(f"STA {p2_addr}")
                                code.append(f"MPTR")
                                code.append(f"WRWA")
                            else:
                                print(f"Error on line: {i}")
                                quit()
                        else:
                            code.append(f"STA {p2}")
                        code.append(f"SWAC")
                        code.append(f"MPTR")
                        code.append(f"SWAC")
                        code.append(f"LDWA")
                else:
                    print(f"Error on line: {i}")
                    quit()
            else:
                print(f"Error on line: {i}")
                quit()
        # ПОИНТЕРЫ
        elif len(i) > 1 and i[0] == "&":
            code.append(i)
        elif len(i.split(",")) == 3:
            s1 = i.split(",")
            s2 = s1[0].split(":")
            p1 = s2[0].strip()
            p2 = s2[1].strip()
            p3 = s1[1].strip()
            p4 = s1[2].strip()
            print(p1, p2, p3, p4)
            # СЛОЖНЫЕ УСЛОВИЯ
            if p1.lower() in ["jmpe", "jmpl", "jmpg"]:
                code.append(f"STC {p4}")
                op1 = p2
                op2 = p3
                op3 = p4
                if len(op2) > 1 and op2[0] == "$":
                    op2_name = op2[1:]
                    if op2_name in vars.keys():
                        op2_addr = vars[op2_name]
                        code.append(f"STA {op2_addr}")
                        code.append(f"MPTR")
                        code.append(f"WRWB")
                    else:
                        print(f"Error on line: {i}")
                        quit()
                else:
                    code.append(f"STB {op2}")
                
                if len(op1) > 1 and op1[0] == "$":
                    op1_name = op1[1:]
                    if op1_name in vars.keys():
                        op1_addr = vars[op1_name]
                        code.append(f"STA {op1_addr}")
                        code.append(f"MPTR")
                        code.append(f"WRWA")
                    else:
                        print(f"Error on line: {i}")
                        quit()
                else:
                    code.append(f"STA {op1}")
                
                code.append(f"SWAC")
                code.append(f"MPTR")
                code.append(f"SWAC")
                code.append(f"{p1}")
            # WRITE TO ADDR
            elif p1 == "write_to_addr":
                op1 = p2
                op2 = p3
                op3 = p4
                if len(op1) > 1 and op1[0] == "$":
                    op1_name = op1[1:]
                    if op1_name in vars.keys():
                        op1_addr = vars[op1_name]
                        code.append(f"STA {op1_addr}")
                        code.append(f"MPTR")
                        code.append(f"WRWB")
                    else:
                        print(f"Error on line: {i}")
                        quit()
                else:
                    code.append(f"STB {op1}")
                
                if len(op2) > 1 and op2[0] == "$":
                    op2_name = op2[1:]
                    if op2_name in vars.keys():
                        op2_addr = vars[op2_name]
                        code.append(f"STA {op2_addr}")
                        code.append(f"MPTR")
                        code.append(f"WRWC")
                    else:
                        print(f"Error on line: {i}")
                        quit()
                else:
                    code.append(f"STC {op2}")
                
                if len(op3) > 1 and op3[0] == "$":
                    op3_name = op3[1:]
                    if op3_name in vars.keys():
                        op3_addr = vars[op3_name]
                        code.append(f"STA {op3_addr}")
                        code.append(f"MPTR")
                        code.append(f"WRWA")
                    else:
                        print(f"Error on line: {i}")
                        quit()
                else:
                    code.append(f"STA {op2}")
                
                code.append("SWAB")
                code.append("BANK")
                code.append("SWAB")
                code.append("SWAC")
                code.append("MPTR")
                code.append("SWAC")
                code.append("LDWA")
                code.append(f"STA 0")
                code.append(f"BANK")
            # WRITE TO ADDR 8
            elif p1 == "write_to_addr_8":
                op1 = p2
                op2 = p3
                op3 = p4
                if len(op1) > 1 and op1[0] == "$":
                    op1_name = op1[1:]
                    if op1_name in vars.keys():
                        op1_addr = vars[op1_name]
                        code.append(f"STA {op1_addr}")
                        code.append(f"MPTR")
                        code.append(f"WRWB")
                    else:
                        print(f"Error on line: {i}")
                        quit()
                else:
                    code.append(f"STB {op1}")
                
                if len(op2) > 1 and op2[0] == "$":
                    op2_name = op2[1:]
                    if op2_name in vars.keys():
                        op2_addr = vars[op2_name]
                        code.append(f"STA {op2_addr}")
                        code.append(f"MPTR")
                        code.append(f"WRWC")
                    else:
                        print(f"Error on line: {i}")
                        quit()
                else:
                    code.append(f"STC {op2}")
                
                if len(op3) > 1 and op3[0] == "$":
                    op3_name = op3[1:]
                    if op3_name in vars.keys():
                        op3_addr = vars[op3_name]
                        code.append(f"STA {op3_addr}")
                        code.append(f"MPTR")
                        code.append(f"WRWA")
                    else:
                        print(f"Error on line: {i}")
                        quit()
                else:
                    code.append(f"STA {op2}")
                
                code.append("SWAB")
                code.append("BANK")
                code.append("SWAB")
                code.append("SWAC")
                code.append("MPTR")
                code.append("SWAC")
                code.append("LDA")
                code.append(f"STA 0")
                code.append(f"BANK")
            # READ FROM ADDR
            elif p1 == "read_from_addr":
                op1 = p2
                op2 = p3
                op3 = p4
                if len(op1) > 1 and op1[0] == "$":
                    op1_name = op1[1:]
                    if op1_name in vars.keys():
                        code.append(f"STA {op1_addr}")
                        code.append(f"MPTR")
                        code.append(f"WRWB")
                    else:
                        print(f"Error on line: {i}")
                        quit()
                else:
                    code.append(f"STB {p2}")
                
                if len(op2) > 1 and op2[0] == "$":
                    op2_name = op2[1:]
                    if op2_name in vars.keys():
                        op2_addr = vars[op2_name]
                        code.append(f"STA {op2_addr}")
                        code.append(f"MPTR")
                        code.append(f"WRWC")
                    else:
                        print(f"Error on line: {i}")
                        quit()
                else:
                    code.append(f"STC {p3}")
                
                if len(op3) > 1 and op3[0] == "$":
                    op3_name = op3[1:]
                    if op3_name in vars.keys():
                        op3_addr = vars[op3_name]
                        stuff = f"STA {op3_addr}"
                    else:
                        print(f"Error on line: {i}")
                        quit()
                else:
                    stuff = f"STA {p4}"

                code.append(f"SWAB")
                code.append(f"BANK")
                code.append(f"SWAB")
                code.append(f"SWAC")
                code.append(f"MPTR")
                code.append(f"SWAC")
                code.append(f"WRWB")
                code.append(f"STA 0")
                code.append(f"BANK")
                code.append(stuff)
                code.append(f"MPTR")
                code.append(f"LDWB")
            # READ FROM ADDR 8
            elif p1 == "read_from_addr_8":
                op1 = p2
                op2 = p3
                op3 = p4
                if len(op1) > 1 and op1[0] == "$":
                    op1_name = op1[1:]
                    if op1_name in vars.keys():
                        code.append(f"STA {op1_addr}")
                        code.append(f"MPTR")
                        code.append(f"WRWB")
                    else:
                        print(f"Error on line: {i}")
                        quit()
                else:
                    code.append(f"STB {p2}")
                
                if len(op2) > 1 and op2[0] == "$":
                    op2_name = op2[1:]
                    if op2_name in vars.keys():
                        op2_addr = vars[op2_name]
                        code.append(f"STA {op2_addr}")
                        code.append(f"MPTR")
                        code.append(f"WRWC")
                    else:
                        print(f"Error on line: {i}")
                        quit()
                else:
                    code.append(f"STC {p3}")
                
                if len(op3) > 1 and op3[0] == "$":
                    op3_name = op3[1:]
                    if op3_name in vars.keys():
                        op3_addr = vars[op3_name]
                        stuff = f"STA {op3_addr}"
                    else:
                        print(f"Error on line: {i}")
                        quit()
                else:
                    stuff = f"STA {p4}"

                code.append(f"SWAB")
                code.append(f"BANK")
                code.append(f"SWAB")
                code.append(f"SWAC")
                code.append(f"MPTR")
                code.append(f"SWAC")
                code.append(f"WRB")
                code.append(f"STA 0")
                code.append(f"BANK")
                code.append(stuff)
                code.append(f"MPTR")
                code.append(f"LDWB")
        elif i.lower() == "hlt":
            code.append("HLT")
        else:
            print(f"Error on line: {i}")
            quit()
    except Exception as e:
        print(f"Error on line: {i}")
        quit()

path = os.getcwd()

with open(f"{path}\\NVASMT\\temp.txt", "w") as f:
    f.write("\n".join(code))

os.system(f"""python "{path}\\NVASMT\\ASM\\main.py" "{path}\\NVASMT\\temp.txt\"""")

