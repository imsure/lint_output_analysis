Lint Output Analysis
====================

Author: Shuo Yang

Email: imsure95@gmail.com

Description
====================

A python tool for indexing, retrieving the output of Flexelint and gathering statistics of the output and generate report.
It also allows you to compare different outputs.

Lint output is in the following format:

/path/to/source/code/xxx.c:146: Note: Violates MISRA 2004 Advisory Rule 19.13, '#/##' operator used in macro: '_READLOGFILE_INIT'  [PC-Lint 961]

Example of part of report:

++++++++++++++++++++++++++++++++++++++++
Lint comparison report.
++++++++++++++++++++++++++++++++++++++++

Message Type       ID Range     Old Count    New Count    Difference(Old - New)
--------------------------------------------------------------------------------
Warnings           400 ~ 699    2586         786          1800           
Syntax_Errors      1 ~ 199      817          5            812            
Internal_Errors    200 ~ 299    0            0            0              
Informational      700 ~ 899    3095         1629         1466           
Fatal_Errors       300 ~ 399    0            0            0              
Elective_Notes     900 ~ 999    15882        8787         7095           
--------------------------------------------------------------------------------
Old Total: 22380
New Total: 11207
Total Messages number decreased: 11173
Total Message dropped by 49.9%


How To Use
============
run:

python UI.py -h

to see the instructions.