from mybin import *
import sys
import charmap

# GLOBAL
INSTR_LEN_3 = {"sta": 24, "stb": 25, "stc": 26}
INSTR_LEN_1 = {"add": 1, "sub": 2,
               "lda": 3, "ldb": 4, "ldc": 5,
               "ldwa": 6, "ldwb": 7, "ldwc": 8,
               "wra": 9, "wrb": 10, "wrc": 11,
               "wrwa": 12, "wrwb": 13, "wrwc": 14,
               "swab": 15, "swbc": 16, "swac": 17,
               "shla": 18, "shlb": 19, "shlc": 20,
               "shra": 21, "shrb": 22, "shrc": 23,
               "mptr": 27, "bank": 28, "exp": 29, "ibnk": 41,
               "not": 30, "and": 31, "or": 32, "xor": 33,
               "jmp": 34, "jmpc": 35, "jmpe": 36, "jmpg": 37, "jmpl": 38, "jmpz": 39,
               "noc": 40, "hlt": 255}

# FUNCTIONS
def get_is_start(a:str, b:str):
    return len(a) <= len(b) and b[0:len(a)] == a

def get_is_start_array(a:list, b:str):
    for i in a:
        if get_is_start(a, i): return True
    return False

def get_instr_len(l):
    for i in INSTR_LEN_1:
        if l == i: return 1
    for i in INSTR_LEN_3:
        if get_is_start(i + " ", l): return 3
    return 0

def get_charmap(a):
    try:
        return charmap.charmap[a]
    except Exception as e:
        return 0

# RESULT
result = []

# POINTERS AND VARS
ptrs = {}
vars = {}

# GET FILE
try:
    with open(sys.argv[1], "r", encoding="UTF-8") as f:
        content = f.readlines()
except Exception as e:
    print(f"no file! {e}")
    quit()

# GET MODE LINES
vars_lines = []
text_lines = []
data_lines = []
mode = ""

for i in content:
    ls = i.strip()
    lsl = ls.lower()
    if lsl == "vars:":
        mode = "vars"
        continue
    if lsl == "text:":
        mode = "text"
        continue
    if lsl == "data:":
        mode = "data"
        continue

    if mode == "vars":
        vars_lines.append(ls)
    if mode == "text":
        text_lines.append(ls)
    if mode == "data":
        data_lines.append(ls)

# REMOVE COMMENTS
nc_vars = []
nc_text = []
nc_data = []

for i in vars_lines:
    l = i.split("--")[0].strip()
    if l != "":
        nc_vars.append(l)

for i in text_lines:
    l = i.split("--")[0].strip()
    if l != "":
        nc_text.append(l)

for i in data_lines:
    l = i.split("--")[0].strip()
    if l != "":
        nc_data.append(l)

# GET VARS
for i in nc_vars:
    try:
        a = i.split(" ")
        vars[a[0]] = int(a[-1])
    except Exception as e:
        print("failed to parse vars")
        quit()

# GET POINTERS AND SET DATA BYTES
size = 0
f_text = []

for i in nc_text:
    n = get_instr_len(i.lower())
    if get_is_start("&", i):
        ptrs[i[1:]] = size
    elif n > 0:
        size += n
        f_text.append(i)
    else:
        print(f"error on text line: {i}")
        quit()

text_size = size
data_bytes = []

for i in nc_data:
    try:
        a = i.split(" ")
        val = a[1:]
        name = a[0]
        if name[0] == "&":
            name = name[1:]
        else:
            print(f"error on data line: {i}")
            quit()
        
        val = " ".join(val)
        if val[0] == '"' and val[-1] == '"':
            val = val[1:-1]
            val1 = list(bin_16_8_split(len(val)))
            data_bytes += val1
            for i in val:
                if i in charmap.charmap.keys():
                    data_bytes.append(charmap.charmap[i])
                else:
                    data_bytes.append(0)
            allsize = len(val) + 2
            size += allsize
            ptrs[name] = size - allsize
        else:
            val = bin_16_8_split(int(val))
            size += 2
            data_bytes += val
            ptrs[name] = size - 2
    except Exception as e:
        print(f"error on data line: {i} {e}")
        quit()

# SET TEXT BYTES
text_bytes = []

for i in f_text:
    try:
        n = get_instr_len(i.lower())
        if n == 1:
            text_bytes.append(INSTR_LEN_1[i.lower()])
        elif n == 3:
            text_bytes.append(INSTR_LEN_3[i.split(" ")[0].lower()])
            a = i.split(" ")[1]
            if get_is_start("#fmem", a):
                text_bytes += list(bin_16_8_split(size + int(a[5:])))
            elif get_is_start("$", a):
                text_bytes += list(bin_16_8_split(vars[a[1:]]))
            elif get_is_start("&", a):
                text_bytes += list(bin_16_8_split(ptrs[a[1:]]))
            else:
                text_bytes += bin_16_8_split(int(a))
        else:
            print(f"error on text line: {i}")
            quit()
    except Exception as e:
        print(f"error on text line: {i} {e}")
        quit()

result += text_bytes
result += data_bytes

with open("build.txt", "w") as f:
    f.write(",".join([ str(i) for i in result ]))

print(f"""Размер: {size} байт
Размер TEXT: {text_size} байт
Размер DATA: {size - text_size} байт""")