"""
misra.py is used to parse and categorize messages
related with different misra rules. The message ID
is 960, since most misra related messages fall under
message 960, we only concern about message 960.
"""

import os
import re
import operator
import sys

def parseline(line):
    m = re.search(r'(/\w+)+\.[ch]', line)
    if m != None:
        fname = re.search(r'/\w+\.[ch]', m.group()).group()
            
    m = re.search(r':(\d+):', line)
    if m != None:
        lnum = m.group(1)

    m = re.search(r'\d{1,2}\.\d{1,2}', line)
    if m != None:
        rule = m.group()

    m = re.search(r',.*', line)
    if m != None:
        desc = m.group()

    return rule, fname[1:], lnum, desc[2:]

def misra(lines):
    """
    'lines' is a list of line containning a mirsa message.
    """
    rules = {}
    for line in lines:
        rule, fname, lnum, desc = parseline(line)
        if not rules.has_key(rule):
            rules[rule] = {}
        if not rules[rule].has_key(fname):
            rules[rule][fname] = []

        rules[rule][fname].append((lnum, desc))
        
    display(rules)


def display(rules):
    """
    'rules' is a dict that maps each misra rule# to a dict
    that maps each file name to a list of (line#, description) tuples.
    """
    rule_count = []
    total = 0
    for rule, d in rules.items():
        count = 0
        for k in d.keys():
            count += len(d[k])

        rule_count.append((rule, count))
        total += count

    while True:
        print '\nMISRA Rule List:\n'
        print 'Index'.ljust(7),
        print 'Rule Number'.ljust(12),
        print 'Count'.ljust(10)
        print '-' * 27

        index = 0
        rule_count = sorted(rule_count, key=operator.itemgetter(1))
        for rule, count in rule_count:
            print ('['+str(index)+']').ljust(7),
            print rule.ljust(12),
            print str(count).ljust(10)
            index += 1

        print '-' * 27
        print 'Total:', total
        print

        # Wait for user input.
        print 'Enter the index number or type q to quit.\n'
        user_input = raw_input('Enter index or quit: ')
        if user_input == 'q':
            break
        else:
            try:
                user_input = int(user_input)
            except ValueError:
                print 'Please enter an integer!\n'
                continue

        try:
            rule = rule_count[user_input][0]
        except IndexError:
            print 'Please enter a valid index!\n'
            continue

        # Get a dict that maps file name to (line#, description)
        # sequence for a specific rule.
        files = rules[rule]

        counts = []
        for f, seq in files.items():
            counts.append((f, len(seq)))

        counts.sort(key=operator.itemgetter(1))

        while True:
            print '\nMISRA Rule: ', rule
            print 'Index'.ljust(7),
            print 'File Name'.ljust(40),
            print 'Count'.ljust(10)
            print '-' * 55

            for i, (f, num) in enumerate(counts):
                print ('['+str(i)+']').ljust(7),               
                print f.ljust(40),
                print str(num).ljust(10)

            # Wait for user input.
            print '\nEnter the index number or type q to quit.\n'
            user_input = raw_input('Enter index or quit: ')
            if user_input == 'q':
                break
            else:
                try:
                    user_input = int(user_input)
                except ValueError:
                    print 'Please enter an integer!\n'
                    continue

            details = []
            try:
                details = files[counts[user_input][0]]
            except IndexError:
                print 'Please enter an valid index!\n'
                continue

            print '\nFile: ', counts[user_input][0]
            print
            for lnum, desc in sorted(details, key=operator.itemgetter(0)):
                print lnum, '==>', desc

                              
def main():
    fname = sys.argv[1]
    f = open(os.path.join('/home/sd/workspace/hwd/build/dp600/hwd', fname), 'r')
    lines = []
    for line in f.readlines():
        if line.endswith('[PC-Lint 960]\n'):
            lines.append(line)

    misra(lines)

    
if __name__ == '__main__':
    main()

