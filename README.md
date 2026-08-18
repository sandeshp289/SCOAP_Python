# SCOAP_Python

Description:

SCOAP and Probability-based Testability Analysis in Python

Code I:

Files:

    scoap.py                                       : Python code

    s27.lev                                        : Input circuit file (for e.g. s1423) in lev format

    s27.(none/clk/clk_rst).(combo/seq/prob).scoap  : Output file (containing testability values for all gates)
    
                                                     (none: without clk/rst consideration, 
                                                         
                                                     clk: with clk consideration, 
                                                          
                                                     clk_rst: with both clk and rst consideration)

                                                     (combo: combinational SCOAP-based controllability and observability computation, 
                                                         
                                                      seq: sequential SCOAP-based controllability and observability computation, 
                                                          
                                                      prob: Combinational Probability-based controllability and observability computation)                                                       


    s27.(none/clk/clk_rst).seq.csv                  : Output file (File containing testability values for all flip-flops in CSV format)
    
Execution:

    python scoap.py s27 (none/clk/clk_rst)
    
Codes II, III and IV:

Files:

    scoap_feature1.py, scoap_feature2.py, scoap_feature3.py  : Python codes

    s27.lev                                                  : Input circuit file (for e.g. s1423) in lev format

    s27.(none/clk/clk_rst).(combo/seq/prob).scoap            : Output file (containing testability values for all gates)
    
    s27.(none/clk/clk_rst).feature.seq.csv                   : Output file (File containing additional feature values for all flip-flops in CSV format)
    
 
Execution:

    python scoap_feature(1/2/3).py s27 (none/clk/rst) (NFI) (NFO)

    where NFI: # of gates in fan-in of flip-flop
    
          NFO: # gates in fanout of flip-flop
    
    
