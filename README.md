# Reamp2CSV
Simple converter from RigExpert REAMP-file to csv-file.


simple REAMP logger file converter to CSV         Version 1.0     
                                                                  
(c) Dietmar Krause, DL2SBA 2026                   2026-02-20      
                                                                  
Usage                                                             
     python scriptName <parm1> <parm2> <parm3>                    
                                                                  
     parm1    locale used for number formatting                   
              'German' for ',' as decimal seperator               
              'US' for '.' as decimal seperator                   
     parm2    Input filename in *.reamp format                    
     parm3    Output filename in CSV-format                       
              Field seperator is ';'                              
              Field#                                              
              1   relative time in µs to start of recording       
              2   absolute time of recording in UTC               
                  the time is fully qualifier down to µs          
              3   first channel in file                           
              4   second channel in file (optional)               
              5   third channel in file (optional)                
                                                                  
              voltage data is written in mV                       
              current data is written in µA                       
                                                                  
 Restrictions:                                                    
     ChannelMap is not used                                       
                                                                  
 Import into Excel                                                
     The timestamp in the file is down to µs resolution.          
     Excel currently supports only ms resolution for timestamps   
     To see at least ms in the column, use the custom cell format 
               'TT.MM.JJJJ hh:mm:ss,000'                          
                                                                  
 Send comments and bug reports to 'labview@dl2sba.de'             
