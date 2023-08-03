VARS:
    test_var1 1
    test_var2 123
TEXT:
    -- ПРЕИНИТ
    STA &sumptr
    MPTR
    STA 0
    STB $test_var1
    SWAC
    &sumptr
    -- ГОТОВИМ ВСЁ К ADD
    SWAC -- test comment
    STB $test_var1
    ADD
    -- ГОТОВИМ ВСЁ К JMPL
    STB $test_var2
    SWAC
    JMPL
    -- КОНЕЦ
    SWAC
    EXP
    NOC
    NOC
    NOC
    HLT