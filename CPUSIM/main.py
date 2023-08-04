# GLOBAL
CPU_NAME = "NVARC_16_4"
SIM_VER = "1.0.0"
BANKS = 3
BANK_LEN = 2 ** 16

# LIBS
import dearpygui.dearpygui as dpg
import math
import time
from mybin import *
import charmap

# UTILS
def get_charmap(val):
    if val in charmap.charmap_rev.keys():
        return charmap.charmap_rev[val]
    else:
        return " "

# DPG SETUP
dpg.create_context()

with dpg.font_registry():
    with dpg.font("notomono.ttf", 13, default_font=True, tag="Default font") as f:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
    
dpg.bind_font("Default font")

dpg.create_viewport(title=f'CPUSIM GUI [CPU: {CPU_NAME}] [SIM VERSION: {SIM_VER}] [BANK: {BANK_LEN}B NUM: {BANKS}]')
dpg.setup_dearpygui()

# DPG MSG BOX
def show_info(title, message):
    with dpg.mutex():
        viewport_width = dpg.get_viewport_client_width()
        viewport_height = dpg.get_viewport_client_height()

        with dpg.window(label=title, modal=True) as modal_id:
            dpg.add_text(message)
    dpg.split_frame()
    width = dpg.get_item_width(modal_id)
    height = dpg.get_item_height(modal_id)
    dpg.set_item_pos(modal_id, [viewport_width // 2 - width // 2, viewport_height // 2 - height // 2])

# PREDEFINE VARS
ram = []

ram_editor_x = 10
ram_editor_y = 20
ram_editor_curr_bank = 0
ram_editor_scroll = 0
ram_editor_row_start = 20
ram_editor_cell_start_x = 100
ram_editor_cell_start_y = 140
ram_editor_cell_width = 30
ram_editor_cell_height = 20
ram_editor_max_addr = BANK_LEN
ram_editor_last_cell = (0, 0)
ram_editor_last_addr = 0
ram_editor_max_pages = 0

ram_dump_file = ""

clock_tps = 0
is_hlt = True
is_clock = False
instr_ptr = 0
instr_bank = 0
ram_bank = 0
ram_ptr = 0
last_instr = ""

reg_a = 0
reg_b = 0
reg_c = 0
cpu_carry = 0
cpu_exp = 0

ascii_monitor_bank = 1
ascii_monitor_x = 20
ascii_monitor_y = 20

# RAM FILLER
for i in range(BANKS):
    ram.append([ 0 for j in range(BANK_LEN) ])

# RAM UTILS
def read_ram(bank:int, ptr:int):
    if bank >= 0 and bank < BANKS and ptr >= 0 and ptr < BANK_LEN:
        return ram[bank][ptr]
    return 0

def write_ram(bank:int, ptr:int, value:int):
    global ram
    if bank >= 0 and bank < BANKS and ptr >= 0 and ptr < BANK_LEN and value >= 0 and value < 256:
        ram[bank][ptr] = value

# CPU
def cpu_next_instr_ptr():
    global instr_ptr
    instr_ptr, notgood = bin_16_sum(instr_ptr, 1)
    if notgood == 1:
        instr_ptr = 0
        hlt()

def clk():
    global instr_ptr
    global instr_bank
    global ram_ptr
    global ram_bank
    global ram
    global last_instr
    global cpu_carry
    global cpu_exp
    global reg_a
    global reg_b
    global reg_c
    if not is_hlt:
        curr_instr_val = read_ram(instr_bank, instr_ptr)
        if curr_instr_val == 1:
            # add
            last_instr = "ADD"
            reg_a, cpu_carry = bin_16_sum(reg_a, reg_b)
            cpu_next_instr_ptr()
        elif curr_instr_val == 2:
            # sub
            last_instr = "SUB"
            reg_a, cpu_carry = bin_16_sub(reg_a, reg_b)
            cpu_next_instr_ptr()
        elif curr_instr_val == 3:
            # lda
            last_instr = "LDA"
            write_ram(ram_bank, ram_ptr, reg_a)
            cpu_next_instr_ptr()
        elif curr_instr_val == 4:
            #ldb
            last_instr = "LDB"
            write_ram(ram_bank, ram_ptr, reg_b)
            cpu_next_instr_ptr()
        elif curr_instr_val == 5:
            #ldc
            last_instr = "LDC"
            write_ram(ram_bank, ram_ptr, reg_c)
            cpu_next_instr_ptr()
        elif curr_instr_val == 6:
            #ldwa
            last_instr = "LDWA"
            a, b = bin_16_8_split(reg_a)
            write_ram(ram_bank, ram_ptr, a)
            c, _ = bin_16_sum(ram_ptr, 1)
            write_ram(ram_bank, c, b)
            cpu_next_instr_ptr()
        elif curr_instr_val == 7:
            #ldwb
            last_instr = "LDWB"
            a, b = bin_16_8_split(reg_b)
            write_ram(ram_bank, ram_ptr, a)
            c, _ = bin_16_sum(ram_ptr, 1)
            write_ram(ram_bank, c, b)
            cpu_next_instr_ptr()
        elif curr_instr_val == 8:
            #ldwc
            last_instr = "LDWC"
            a, b = bin_16_8_split(reg_c)
            write_ram(ram_bank, ram_ptr, a)
            c, _ = bin_16_sum(ram_ptr, 1)
            write_ram(ram_bank, c, b)
            cpu_next_instr_ptr()
        elif curr_instr_val == 9:
            #wra
            last_instr = "WRA"
            reg_a = read_ram(ram_bank, ram_ptr)
            cpu_next_instr_ptr()
        elif curr_instr_val == 10:
            #wrb
            last_instr = "WRB"
            reg_b = read_ram(ram_bank, ram_ptr)
            cpu_next_instr_ptr()
        elif curr_instr_val == 11:
            #wrc
            last_instr = "WRC"
            reg_c = read_ram(ram_bank, ram_ptr)
            cpu_next_instr_ptr()
        elif curr_instr_val == 12:
            #wrwa
            last_instr = "WRWA"
            c, _ = bin_16_sum(ram_ptr, 1)
            reg_a =  bin_8_16_comp(read_ram(ram_bank, ram_ptr), read_ram(ram_bank, c))
            cpu_next_instr_ptr()
        elif curr_instr_val == 13:
            #wrwb
            last_instr = "WRWB"
            c, _ = bin_16_sum(ram_ptr, 1)
            reg_b = bin_8_16_comp(read_ram(ram_bank, ram_ptr), read_ram(ram_bank, c))
            cpu_next_instr_ptr()
        elif curr_instr_val == 14:
            #wrwc
            last_instr = "WRWC"
            c, _ = bin_16_sum(ram_ptr, 1)
            reg_c =  bin_8_16_comp(read_ram(ram_bank, ram_ptr), read_ram(ram_bank, c))
            cpu_next_instr_ptr()
        elif curr_instr_val == 15:
            #swab
            last_instr = "SWAB"
            reg_a, reg_b = reg_b, reg_a
            cpu_next_instr_ptr()
        elif curr_instr_val == 16:
            #swbc
            last_instr = "SWBC"
            reg_c, reg_b = reg_b, reg_c
            cpu_next_instr_ptr()
        elif curr_instr_val == 17:
            #swac
            last_instr = "SWAC"
            reg_a, reg_c = reg_c, reg_a
            cpu_next_instr_ptr()
        elif curr_instr_val == 18:
            #shla
            last_instr = "SHLA"
            reg_a = bin_16_shl(reg_a)
            cpu_next_instr_ptr()
        elif curr_instr_val == 19:
            #shlb
            last_instr = "SHLB"
            reg_b = bin_16_shl(reg_b)
            cpu_next_instr_ptr()
        elif curr_instr_val == 20:
            #shlc
            last_instr = "SHLC"
            reg_c = bin_16_shl(reg_c)
            cpu_next_instr_ptr()
        elif curr_instr_val == 21:
            #shra
            last_instr = "SHRA"
            reg_a = bin_16_shr(reg_a)
            cpu_next_instr_ptr()
        elif curr_instr_val == 22:
            #shrb
            last_instr = "SHRB"
            reg_b = bin_16_shr(reg_b)
            cpu_next_instr_ptr()
        elif curr_instr_val == 23:
            #shrc
            last_instr = "SHRC"
            reg_c = bin_16_shr(reg_c)
            cpu_next_instr_ptr()
        elif curr_instr_val == 24:
            #sta
            last_instr = "STA"
            cpu_next_instr_ptr()
            a = read_ram(instr_bank, instr_ptr)
            cpu_next_instr_ptr()
            b = read_ram(instr_bank, instr_ptr)
            reg_a = bin_8_16_comp(a, b)
            cpu_next_instr_ptr()
        elif curr_instr_val == 25:
            #stb
            last_instr = "STB"
            cpu_next_instr_ptr()
            a = read_ram(instr_bank, instr_ptr)
            cpu_next_instr_ptr()
            b = read_ram(instr_bank, instr_ptr)
            reg_b = bin_8_16_comp(a, b)
            cpu_next_instr_ptr()
        elif curr_instr_val == 26:
            #stc
            last_instr = "STC"
            cpu_next_instr_ptr()
            a = read_ram(instr_bank, instr_ptr)
            cpu_next_instr_ptr()
            b = read_ram(instr_bank, instr_ptr)
            reg_c = bin_8_16_comp(a, b)
            cpu_next_instr_ptr()
        elif curr_instr_val == 27:
            #mptr
            last_instr = "MPTR"
            ram_ptr = reg_a
            cpu_next_instr_ptr()
        elif curr_instr_val == 28:
            #bank
            last_instr = "BANK"
            ram_bank = reg_a
            cpu_next_instr_ptr()
        elif curr_instr_val == 29:
            #exp
            last_instr = "EXP"
            cpu_exp = reg_a
            cpu_next_instr_ptr()
        elif curr_instr_val == 30:
            #not
            last_instr = "NOT"
            reg_a = bin_not(reg_a)
            cpu_next_instr_ptr()
        elif curr_instr_val == 31:
            #and
            last_instr = "AND"
            reg_a = bin_and(reg_a, reg_b)
            cpu_next_instr_ptr()
        elif curr_instr_val == 32:
            #or
            last_instr = "OR"
            reg_a = bin_or(reg_a, reg_b)
            cpu_next_instr_ptr()
        elif curr_instr_val == 33:
            #xor
            last_instr = "XOR"
            reg_a = bin_xor(reg_a, reg_b)
        elif curr_instr_val == 34:
            cpu_next_instr_ptr()
            #jmp
            last_instr = "JMP"
            instr_ptr = ram_ptr
        elif curr_instr_val == 35:
            #jmpc
            last_instr = "JMPC"
            if cpu_carry == 1:
                instr_ptr = ram_ptr
            else:
                cpu_next_instr_ptr()
        elif curr_instr_val == 36:
            #jmpe
            last_instr = "JMPE"
            if reg_a == reg_b:
                instr_ptr = ram_ptr
            else:
                cpu_next_instr_ptr()
        elif curr_instr_val == 37:
            #jmpg
            last_instr = "JMPG"
            if reg_a > reg_b:
                instr_ptr = ram_ptr
            else:
                cpu_next_instr_ptr()
        elif curr_instr_val == 38:
            #jmpl
            last_instr = "JMPL"
            if reg_a < reg_b:
                instr_ptr = ram_ptr
            else:
                cpu_next_instr_ptr()
        elif curr_instr_val == 39:
            #jmpz
            last_instr = "JMPZ"
            if reg_a == 0:
                instr_ptr = ram_ptr
            else:
                cpu_next_instr_ptr()
        elif curr_instr_val == 40:
            #noc
            last_instr = "NOC"
            cpu_next_instr_ptr()
        elif curr_instr_val == 41:
            #ibnk
            last_instr = "IBNK"
            instr_bank = reg_a
            cpu_next_instr_ptr()
        elif curr_instr_val == 255:
            last_instr = "HLT"
            hlt()
            cpu_next_instr_ptr()
        else:
            last_instr = "-"
            cpu_next_instr_ptr()

# RAM EDITOR THEMES
with dpg.theme() as ram_editor_both_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Button, (189, 189, 47), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (145, 145, 36), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (163, 163, 41), category=dpg.mvThemeCat_Core)

with dpg.theme() as ram_editor_ram_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Button, (60, 186, 41), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (38, 117, 26), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (43, 133, 29), category=dpg.mvThemeCat_Core)

with dpg.theme() as ram_editor_instr_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Button, (41, 72, 186), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (29, 50, 130), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (34, 58, 148), category=dpg.mvThemeCat_Core)

# RAM EDITOR FUNCTIONS
def ram_editor_update_scrollbar():
    if ram_editor_scroll == 0:
        value = 0
    else:
        value = -(ram_editor_scroll / ram_editor_max_pages)
    dpg.set_value("ram_editor_scroller", value)

def ram_editor_scroll_1():
    global ram_editor_scroll
    ram_editor_scroll += 1
    if ram_editor_scroll > ram_editor_max_pages:
        ram_editor_scroll = ram_editor_max_pages
    ram_editor_update_scrollbar()

def ram_editor_scroll_10():
    global ram_editor_scroll
    ram_editor_scroll += 10
    if ram_editor_scroll > ram_editor_max_pages:
        ram_editor_scroll = ram_editor_max_pages
    ram_editor_update_scrollbar()

def ram_editor_scroll_100():
    global ram_editor_scroll
    ram_editor_scroll += 100
    if ram_editor_scroll > ram_editor_max_pages:
        ram_editor_scroll = ram_editor_max_pages
    ram_editor_update_scrollbar()

def ram_editor_scroll__1():
    global ram_editor_scroll
    ram_editor_scroll -= 1
    if ram_editor_scroll < 0:
        ram_editor_scroll = 0
    ram_editor_update_scrollbar()

def ram_editor_scroll__10():
    global ram_editor_scroll
    ram_editor_scroll -= 10
    if ram_editor_scroll < 0:
        ram_editor_scroll = 0
    ram_editor_update_scrollbar()

def ram_editor_scroll__100():
    global ram_editor_scroll
    ram_editor_scroll -= 100
    if ram_editor_scroll < 0:
        ram_editor_scroll = 0
    ram_editor_update_scrollbar()

def ram_editor_get_addr_for(x, y):
    global_offset = ram_editor_x * ram_editor_scroll
    local_offset = ram_editor_x * y + x
    return global_offset + local_offset

def ram_editor_goto():
    global ram_editor_last_addr
    global ram_editor_scroll

    addr = dpg.get_value("ram_editor_goto")
    ram_editor_last_addr = addr
    ram_editor_scroll = int(addr / ram_editor_x)
    if ram_editor_scroll > ram_editor_max_pages:
        ram_editor_scroll = ram_editor_max_pages
    ram_editor_update_scrollbar()

def ram_editor_get_start_end_addr(y):
    global_offset = ram_editor_x * ram_editor_scroll
    start = global_offset + ram_editor_x * y
    end = global_offset + ram_editor_x * y + ram_editor_x - 1
    max_addr = ram_editor_max_addr - 1
    if end > max_addr:
        end = max_addr
    return start, end

def ram_editor_callback(sender:str):
    global ram_editor_last_cell
    global ram_editor_last_addr

    s1 = sender.split("[")
    s2 = s1[1].split("]")
    s3 = s2[0]
    nums_s = s3.split(";")
    nums = (int(nums_s[0]), int(nums_s[1]))
    x = nums[0]
    y = nums[1]
    addr = ram_editor_get_addr_for(x, y)

    ram_editor_last_cell = nums
    ram_editor_last_addr = addr

def ram_editor_update_info():
    dpg.set_value("ram_editor_info", f"Скролл: {ram_editor_scroll} | Выбранная ячейка: X{ram_editor_last_cell[0]} Y{ram_editor_last_cell[1]} | Адрес: {ram_editor_last_addr}")

def ram_editor_scroller_callback(sender):
    global ram_editor_scroll
    ram_editor_scroll = round(-dpg.get_value(sender) * ram_editor_max_pages)

def ram_editor_change_x(sender):
    global ram_editor_x
    ram_editor_clear_group()
    ram_editor_x = dpg.get_value(sender)
    ram_editor_construct_group()

def ram_editor_change_y(sender):
    global ram_editor_y
    ram_editor_clear_group()
    ram_editor_y = dpg.get_value(sender)
    ram_editor_construct_group()

def ram_editor_change_bank(sender):
    global ram_editor_curr_bank
    ram_editor_curr_bank = int(dpg.get_value(sender).split(" ")[1])

def ram_editor_set_ram_value():
    global ram
    write_ram(ram_editor_curr_bank, ram_editor_last_addr, dpg.get_value("ram_editor_set_value"))

def ram_editor_construct_group():
    global ram_editor_x
    global ram_editor_y
    global ram_editor_max_pages
    global ram_editor_scroll

    start_x = ram_editor_cell_start_x
    start_y = ram_editor_cell_start_y

    for y in range(0, ram_editor_y):
        dpg.add_text("0-0", parent="ram_editor_group",
                        tag=f"ram_editor_row_{y}",
                        pos=(ram_editor_row_start, y * ram_editor_cell_height + start_y),
                        )
        for x in range(0, ram_editor_x):
            dpg.add_button(label="0", parent="ram_editor_group",
                        tag=f"ram_editor_cell_[{x};{y}]",
                        pos=(x * ram_editor_cell_width + start_x, y * ram_editor_cell_height + start_y),
                        width=ram_editor_cell_width - 1,
                        height=ram_editor_cell_height - 1,
                        callback=ram_editor_callback,
                        )
    
    ram_editor_max_pages = math.ceil(ram_editor_max_addr / ram_editor_x) - ram_editor_y
    ram_editor_scroll = 0
    dpg.set_value("ram_editor_scroller", 0)
    dpg.configure_item("ram_editor_scroller", height=ram_editor_y * ram_editor_cell_height, pos=(ram_editor_cell_width * ram_editor_x + start_x + 10, start_y))

def ram_editor_clear_group():
    global ram_editor_x
    global ram_editor_y

    for y in range(0, ram_editor_y):
        dpg.delete_item(f"ram_editor_row_{y}")
        for x in range(0, ram_editor_x):
            dpg.delete_item(f"ram_editor_cell_[{x};{y}]")

def ram_editor_set_data():
    for y in range(0, ram_editor_y):
        el1 = f"ram_editor_row_{y}"
        start, end = ram_editor_get_start_end_addr(y)
        try:
            dpg.set_value(el1, f"{start}-{end}")
        except Exception as e:
            #print(f"NOT FOUND ELEMENT {el1}")
            pass
        for x in range(0, ram_editor_x):
            el2 = f"ram_editor_cell_[{x};{y}]"
            try:
                addr = ram_editor_get_addr_for(x, y)
                dpg.configure_item(el2, label=ram[ram_editor_curr_bank][addr])
                dpg.configure_item(el2, enabled=True)
                if addr == instr_ptr and addr == ram_ptr and ram_bank == ram_editor_curr_bank and instr_bank == ram_editor_curr_bank:
                    dpg.bind_item_theme(el2, ram_editor_both_theme)
                elif addr == ram_ptr and ram_bank == ram_editor_curr_bank:
                    dpg.bind_item_theme(el2, ram_editor_ram_theme)
                elif addr == instr_ptr and instr_bank == ram_editor_curr_bank:
                    dpg.bind_item_theme(el2, ram_editor_instr_theme)
                else:
                    dpg.bind_item_theme(el2, dpg.theme())
            except Exception as e:
                try:
                    dpg.configure_item(el2, label="")
                    dpg.configure_item(el2, enabled=False)
                except Exception as e:
                    #print(f"NOT FOUND ELEMENT {el2}")
                    pass

# RAM DUMP FUNCTIONS
def ram_dump_file_selected(sender, app_data):
    global ram_dump_file
    try:
        temp_path = app_data["selections"][list(app_data["selections"].keys())[0]]
        with open(temp_path, "r", encoding="UTF-8") as f:
            f.read()
        # всё получилось
        ram_dump_file = temp_path
        dpg.set_value("ram_dump_file_text", ram_dump_file)
    except Exception as e:
        show_info("Ошибка!", f"Не удалось открыть файл:\n{e}")

def ram_dump_select_file():
    dpg.show_item("ram_dump_file_dialog")

def ram_dump_load_def():
    try:
        with open(ram_dump_file, "r") as f:
            ram_temp = []
            for bank in f.read().split(";"):
                temp_bank = []
                for val in bank.split(","):
                    temp_bank.append(val)
                ram_temp.append(temp_bank)

            for bank in range(len(ram_temp)):
                for addr in range(len(ram_temp[bank])):
                    write_ram(bank, addr, int(ram_temp[bank][addr]))
            show_info("Успех!", f"Дамп загружен!")
    except Exception as e:
        show_info("Ошибка!", f"Не удалось загрузить дамп:\n{e}")

def ram_dump_save_def():
    try:
        with open(ram_dump_file, "w") as f:
            a = []
            for i in ram:
                a.append(",".join([ str(j) for j in i ]))
            s = ";".join(a)
            f.write(s)
            show_info("Успех!", f"Дамп сохранён!")
    except Exception as e:
        show_info("Ошибка!", f"Не удалось сохранить дамп:\n{e}")

# CPU CON FUNCTIONS
def tps_change_callback(sender):
    global clock_tps
    clock_tps = dpg.get_value(sender)

def hlt():
    global is_hlt
    is_hlt = True

def unhlt():
    global is_hlt
    is_hlt = False

def start_clock():
    global is_clock
    is_clock = True

def stop_clock():
    global is_clock
    is_clock = False

def instr_ptr_change():
    global instr_ptr
    instr_ptr = dpg.get_value("instr_ptr_el")

def instr_bank_change():
    global instr_bank
    instr_bank = dpg.get_value("instr_bank_el")

def ram_ptr_change():
    global ram_ptr
    ram_ptr = dpg.get_value("ram_ptr_el")

def ram_bank_change():
    global ram_bank
    ram_bank = dpg.get_value("ram_bank_el")

def set_a_reg():
    global reg_a
    reg_a = dpg.get_value("reg_a_input")

def set_b_reg():
    global reg_b
    reg_b = dpg.get_value("reg_b_input")

def set_c_reg():
    global reg_c
    reg_c = dpg.get_value("reg_c_input")

def set_carry_on():
    global cpu_carry
    cpu_carry = 1

def set_carry_off():
    global cpu_carry
    cpu_carry = 0

def set_exp():
    global cpu_exp
    cpu_exp = dpg.get_value("exp_input")

# ASCII MONITOR
def ascii_monitor_change_bank(sender):
    global ascii_monitor_bank
    ascii_monitor_bank = int(dpg.get_value(sender).split(" ")[1])

def ascii_monitor_change_x(sender):
    global ascii_monitor_x
    ascii_monitor_x = dpg.get_value(sender)

def ascii_monitor_change_y(sender):
    global ascii_monitor_y
    ascii_monitor_y = dpg.get_value(sender)

def ascii_monitor_update():
    s = ""
    for y in range(ascii_monitor_y):
        for x in range(ascii_monitor_x):
            val = read_ram(ascii_monitor_bank, y * ascii_monitor_x + x)
            s += get_charmap(val)
        s += "\n"
    print(s)
    dpg.set_value("ascii_monitor_text", s)
        

# CPU CON
with dpg.window(label="Управление процессором", no_close=True):
    dpg.add_text("Работа:")
    # Работа
    with dpg.group(horizontal=True):
        dpg.add_button(label="остановить (HLT)", callback=hlt)
        dpg.add_button(label="продолжить (un HLT)", callback=unhlt)
    
    # Автотактирование
    dpg.add_text("Тактирование:")
    dpg.add_slider_int(label="Тактов в секунду", max_value=500, callback=tps_change_callback) # ТУТ РАЗГОН!!!111
    with dpg.group(horizontal=True):
        dpg.add_button(label="остановить авт.такт.", callback=stop_clock)
        dpg.add_button(label="запустить авт.такт.", callback=start_clock)
    dpg.add_button(label="Сделать такт", callback=clk)
    
    # ОЗУ
    dpg.add_text("ОЗУ:")
    with dpg.group(horizontal=True):
        dpg.add_button(label="Применить", callback=ram_ptr_change)
        dpg.add_input_int(label="Указатель ОЗУ", min_value=0, max_value=BANK_LEN - 1, min_clamped=True, max_clamped=True, tag="ram_ptr_el", width=100)
    with dpg.group(horizontal=True):
        dpg.add_button(label="Применить", callback=ram_bank_change)
        dpg.add_input_int(label="Банка ОЗУ", min_value=0, max_value=BANKS - 1, min_clamped=True, max_clamped=True, tag="ram_bank_el", width=100)

    # Инструкции
    dpg.add_text("Инструкции:")
    with dpg.group(horizontal=True):
        dpg.add_button(label="Применить", callback=instr_ptr_change)
        dpg.add_input_int(label="Указатель инструкций", min_value=0, max_value=BANK_LEN - 1, min_clamped=True, max_clamped=True, tag="instr_ptr_el", width=100)
    with dpg.group(horizontal=True):
        dpg.add_button(label="Применить", callback=instr_bank_change)
        dpg.add_input_int(label="Банка инструкций", min_value=0, max_value=BANKS - 1, min_clamped=True, max_clamped=True, tag="instr_bank_el", width=100)
    
    # Регистры
    dpg.add_text("Регистры:")
    with dpg.group(horizontal=True):
        dpg.add_button(label="Применить", callback=set_a_reg)
        dpg.add_input_int(label="A", min_value=0, max_value=2 ** 16 - 1, min_clamped=True, max_clamped=True, tag="reg_a_input", width=100)
    with dpg.group(horizontal=True):
        dpg.add_button(label="Применить", callback=set_b_reg)
        dpg.add_input_int(label="B", min_value=0, max_value=2 ** 16 - 1, min_clamped=True, max_clamped=True, tag="reg_b_input", width=100)
    with dpg.group(horizontal=True):
        dpg.add_button(label="Применить", callback=set_c_reg)
        dpg.add_input_int(label="C", min_value=0, max_value=2 ** 16 - 1, min_clamped=True, max_clamped=True, tag="reg_c_input", width=100)

    # Флаги
    dpg.add_text("Флаги:")
    with dpg.group(horizontal=True):
        dpg.add_button(label="Установ. carry", callback=set_carry_on)
        dpg.add_button(label="Сбросить carry", callback=set_carry_off)

    # Доп
    dpg.add_text("Доп:")
    with dpg.group(horizontal=True):
        dpg.add_button(label="Применить", callback=set_exp)
        dpg.add_input_int(label="EXP", min_value=0, max_value=2 ** 16 - 1, min_clamped=True, max_clamped=True, tag="exp_input", width=100)

# CPU STATUS
with dpg.window(label="Состояние процессора", no_close=True):
    dpg.add_text(tag="cpu_status")

# RAM EDITOR
with dpg.window(label="Редактор ОЗУ", no_close=True):
    with dpg.group(horizontal=True):
        dpg.add_slider_int(label="X", min_value=5, max_value=20, default_value=10, width=100, callback=ram_editor_change_x)
        dpg.add_slider_int(label="Y", min_value=10, max_value=40, default_value=20, width=100, callback=ram_editor_change_y)
    with dpg.group(horizontal=True):
        dpg.add_combo(items=[ f"Банка {i}" for i in range(0, BANKS) ], label="Банка ОЗУ", width=150, default_value="Банка 0", callback=ram_editor_change_bank)
    with dpg.group(horizontal=True):
        dpg.add_button(label="Установить", callback=ram_editor_set_ram_value)
        dpg.add_input_int(label="Значение", min_value=0, max_value=255, min_clamped=True, max_clamped=True, tag="ram_editor_set_value", width=100)
    dpg.add_text("", tag="ram_editor_info")
    with dpg.group(horizontal=True):
        dpg.add_group(tag="ram_editor_group")
        dpg.add_slider_float(vertical=True, tag="ram_editor_scroller", min_value=-1, max_value=0, callback=ram_editor_scroller_callback)
    ram_editor_construct_group()
    dpg.add_text("Скролл:")
    with dpg.group(horizontal=True):
        dpg.add_button(label="+1", callback=ram_editor_scroll_1)
        dpg.add_button(label="+10", callback=ram_editor_scroll_10)
        dpg.add_button(label="+100", callback=ram_editor_scroll_100)
    with dpg.group(horizontal=True):
        dpg.add_button(label="-1", callback=ram_editor_scroll__1)
        dpg.add_button(label="-10", callback=ram_editor_scroll__10)
        dpg.add_button(label="-100", callback=ram_editor_scroll__100)
    with dpg.group(horizontal=True):
        dpg.add_button(label="Пыерейти", callback=ram_editor_goto)
        dpg.add_input_int(label="Адрес", min_value=0, max_value=ram_editor_max_addr - 1, min_clamped=True, max_clamped=True, tag="ram_editor_goto", width=100)

# RAM DUMP
with dpg.file_dialog(
directory_selector=False, show=False, callback=ram_dump_file_selected,
tag="ram_dump_file_dialog",
width=700 ,height=400, default_path="."):
    dpg.add_file_extension(".*")

with dpg.window(label="Дамп ОЗУ", no_close=True):
    dpg.add_text("Файл")
    with dpg.group(horizontal=True):
        dpg.add_button(label="Выбрать", callback=ram_dump_select_file)
        dpg.add_text("Файл не выбран", tag="ram_dump_file_text")
    with dpg.group(horizontal=True):
        dpg.add_button(label="Загрузить [текст]", callback=ram_dump_load_def)
        dpg.add_button(label="Сохранить [текст]", callback=ram_dump_save_def)

with dpg.window(label="ASCII экран", no_close=True):
    with dpg.group(horizontal=True):
        dpg.add_combo(items=[ f"Банка {i}" for i in range(0, BANKS) ], label="Банка ОЗУ", width=150, default_value="Банка 0", callback=ascii_monitor_change_bank)
    with dpg.group(horizontal=True):
        dpg.add_input_int(label="X", min_value=20, max_value=200, default_value=20, min_clamped=True, max_clamped=True, width=100, callback=ascii_monitor_change_x)
        dpg.add_input_int(label="Y", min_value=20, max_value=200, default_value=20, min_clamped=True, max_clamped=True,  width=100, callback=ascii_monitor_change_y)
    dpg.add_text("", tag="ascii_monitor_text")

# SHOW STUFF
dpg.show_viewport()

# MAIN CYCLE
last_time = 0
while dpg.is_dearpygui_running():
    # CPU CLK
    if is_clock:
        if clock_tps and time.time() > last_time + (1 / clock_tps):
            clk()
            last_time = time.time()
    
    # CPU STATUS
    dpg.set_value("cpu_status", f"""Состояние: {"ОСТАНОВЛЕН" if is_hlt else "РАБОТАЕТ"}
Автотактирование: {clock_tps} Т/С - {"работает" if is_clock else "остановлен"}
==========
Адрес ОЗУ: {ram_ptr}
Банка ОЗУ: {ram_bank}
==========
Адрес инструкции: {instr_ptr}
Банка инструкций: {instr_bank}
==========
Последняя инструкция: {last_instr}
==========
Регистр A: {reg_a}
Регистр B: {reg_b}
Регистр C: {reg_c}
Флаг carry: {cpu_carry}
==========
EXP:
bin: {bin(cpu_exp)}
dec: {cpu_exp}
""")
    # RAM EDITOR UPDATE
    ram_editor_set_data()
    ram_editor_update_info()

    # ASCII MONITOR UPDATE
    ascii_monitor_update()

    # RENDER WINDOWS
    dpg.render_dearpygui_frame()

# ENDs
dpg.destroy_context()
