#!/usr/bin/env python

from LintResult import LintResult
import common as cmn
from LintCmp import LintCmp
import os

class UI(object):

    def __init__(self):
        self.features = ['Query by message ID',
                         'Query by file name']

        try:
            os.mkdir('./report')
        except OSError:
            pass

    def print_msg_cnt_prob_by_type(self, total, raw_msg_cnt_prob):
        print '\nLint Messages counts and probabilities by message type:'

        print '\nMessage Type'.ljust(25),
        print 'Count'.ljust(9),
        print 'Probability'.ljust(15)
        print '-' * 46
        for index, (msgtype, cnt, prob) in enumerate(raw_msg_cnt_prob):
            print '[%d]' % (index), str(msgtype).ljust(20),
            print str(cnt).ljust(9),
            print '{0:.1f}%'.format(float(prob) * 100).ljust(15)

        print '-' * 46
        print 'Total:', total
        print

    def show_msgtype_and_get_type(self, lintres):
        """
        """
        total = lintres.get_total()
        msg_cnt_by_type = lintres.get_msg_count_prob_by_type()

        self.print_msg_cnt_prob_by_type(total, msg_cnt_by_type)

        print 'To look up a specific type of message',
        print 'enter the index number in the [].',
        print 'Or type \'q\' to quit.\n'        

        user_input = raw_input('Enter index or quit: ')
        if user_input != 'q':
            ## convert index to message type
            try:
                user_input = msg_cnt_by_type[int(user_input)][0]
            except:
                print 'Wrong index!\n'
                return ''
                
        return user_input

    def print_msgid_cnt_prob_by_type(self, mid_cnt_prob, mtype):
        mrange = cmn.getRangeOfMsgType(mtype)
        print '\nMessage Type:', mtype, '\tRange of ID:', mrange[0], 'to', mrange[1]-1
        print 'IDs found:\n'
        print 'Message ID'.ljust(12),
        print 'Count'.ljust(7),
        print 'Probability'.ljust(15)
        print '-' * 32
        for (msgid, cnt, prob) in mid_cnt_prob:
            print str(msgid).ljust(12), str(cnt).ljust(7),
            print '{0:.3f}%'.format(prob * 100).ljust(15)

        print '-' * 32
        print 'Number of distinct IDs:', (len(mid_cnt_prob))
        print
        
    def print_flist_by_id(self, msgid, hlist, clist):
        findex = 0
        print
        print ''.rjust(25), 'Message ID:', msgid
        print 'File Name'.ljust(56), 'Count'
        print '-' * 65
        
        for f, cnt in hlist:
            print '[%d]' % (findex),
            print '{0:48} ==> {1:3d}'.format(f, cnt)
            findex += 1
            
        for f, cnt in clist:
            print '[%d]' % (findex),
            print '{0:48} ==> {1:3d}'.format(f, cnt)
            findex += 1

    def show_msgids_by_type_and_get_a_msgid(self, res, mtype):
        mid_cnt_prob = res.get_msgid_count_prob_by_type(mtype)
        self.print_msgid_cnt_prob_by_type(mid_cnt_prob, mtype)

        print 'Enter a message ID you want to look for or type \'q\' to quit.\n'
        return raw_input('Enter message ID or quit: ')

    def show_flist_by_msgid_and_get_a_file(self, res, msgid):
        try:
            hlist, clist = res.get_flist_by_id(msgid)
        except:
            return ''

        self.print_flist_by_id(msgid, hlist, clist)

        print '\nEnter an index of file you want to look for or type \'q\' to quit.\n'
        user_input = \
            raw_input('Enter index of file or quit: ')
        if user_input != 'q':
            ## Need to convert index to the real file name here.
            try:
                index = int(user_input)
            except:
                return ''
            if index >= len(hlist):
                try:
                    user_input = clist[index-len(hlist)][0]
                except:
                    print 'Wrong index!\n'
                    return ''
            else:
                try:
                    user_input = hlist[index][0]
                except:
                    print 'Wrong index!\n'
                    return ''
                    
        return user_input

    def print_file_info(self, fname, finfo):
        print '\nFile Name:', fname
        print 'Line number'.ljust(16), 'Description'
        print '-' * 75
        for (linenum, desc) in finfo:
            print '{0:11d} ==>'.format(linenum),
            print desc[0 : 50]
            times = 1 + len(desc) / 50
            for x in range(1, times):
                print ''.rjust(16), desc[x*50 : (x+1)*50]
            print

    def generate_report(self, lintres):
        self.generate_report_by_type(lintres, 'Syntax_Errors')
        self.generate_report_by_type(lintres, 'Warnings')

    def generate_report_by_type(self, lintres, mtype):
        import sys
        old_stdout = sys.stdout
        fname = 'report_'+lintres.get_fname_suffix()+'_'+mtype+'.txt'
        sys.stdout = open(os.path.join('./report', fname), 'w')

        msg_range = cmn.getRangeOfMsgType(mtype)
        print '+' * 50
        print 'Lint Report for DP600 Project.'
        print 'Message Type: %s. Range of Message ID:(%d~%d)' % (mtype, msg_range[0], msg_range[1])
        print '+' * 50
        
        self.print_msg_cnt_prob_by_type(lintres.get_total(),
                                        lintres.get_msg_count_prob_by_type())

        mid_cnt_prob = lintres.get_msgid_count_prob_by_type(mtype)
        self.print_msgid_cnt_prob_by_type(mid_cnt_prob, mtype)

        mids = [mid for mid, cnt, prob in mid_cnt_prob]
        for mid in mids:
            hlist, clist = lintres.get_flist_by_id(mid)
            self.print_flist_by_id(mid, hlist, clist)
            
            for (hfile, cnt) in hlist:
                hinfo = lintres.get_info_by_id_and_file(mid, hfile)
                self.print_file_info(hfile, hinfo)
                
            for (cfile, cnt) in clist:
                cinfo = lintres.get_info_by_id_and_file(mid, cfile)
                self.print_file_info(cfile, cinfo)            

        print >> sys.stderr, '\nReport %s generated for %s.\n' % (fname, mtype)
        sys.stdout = old_stdout

    def show_feature_list(self):
        print '\nFeature List:\n'
        for index, feature in enumerate(self.features):
            print '[%d] %s' % (index, feature)

        print '\nEnter an index to select the type of query or type \'q\' to quit.\n'
        user_input = \
            raw_input('Enter index of feature or quit: ')
        if user_input != 'q':
            ## Need to convert index to the real file name here.
            try:
                return int(user_input)
            except:
                print 'Wrong index!\n'

        return user_input


    def start_query_by_id(self, lintres):
        while True:
            ## This is the second level of user interface.
            ## Show count and prob of each message type
            ## and let user select a specific type or quit.
            user_input = self.show_msgtype_and_get_type(lintres)
            if user_input == 'q':
                print
                break
            elif user_input == '':
                continue

            mtype = user_input

            while True:
                ## This is the second level of user interface.
                ## Show message id and its count and prob of a user
                ## specified message type and get a message id from user.
                user_input = self.show_msgids_by_type_and_get_a_msgid(lintres, mtype)
                if user_input == 'q':
                    break
                try:
                    msg_id = int(user_input)
                except:
                    print 'Wrong index!\n'
                    continue
                
                while True:
                    user_input = self.show_flist_by_msgid_and_get_a_file(lintres, msg_id)
                    if user_input == 'q':
                        break
                    elif user_input == '':
                        print 'Wrong message ID!'
                        break

                    fname = user_input
                    finfo = lintres.get_info_by_id_and_file(msg_id, fname)
                    self.print_file_info(fname, finfo)            

    def show_filetypes_and_get_type(self, lintres):
        print '\nFile Types:\n'
        for index, ftype in enumerate(cmn.fileTypes):
            print '[%d] %s' % (index, ftype)

        print '\nEnter an index to select the type of file or type \'q\' to quit.\n'
        user_input = raw_input('Enter index of file type or quit: ')
        if user_input != 'q':
            try:
                return int(user_input)
            except:
                print 'Wrong index!\n'

        return user_input

    def show_files_and_get_fname(self, lintres, ftype):
        print
        files = lintres.get_files_by_type(ftype)
        index = 0
        for fs in zip(files[0::2], files[1::2]):
            print '[%d]' % (index),
            print '{0:48}'.format(fs[0]),
            print '[%d]' % (index+1),
            print '{0:48}'.format(fs[1])
            index += 2

        if len(files) % 2 != 0:
            print '[%d]' % (index),
            print '{0:48}'.format(files[index])

        print '\nEnter an index to select the file name or type \'q\' to quit.\n'
        user_input = raw_input('Enter index of file name or quit: ')
        if user_input != 'q':
            try:
                return files[int(user_input)]
            except:
                print 'Wrong index!\n'
                return ''

        return user_input

    def show_cnt_and_linenums_and_get_linenum(self, lintres, fname):
        mtype2cnt, total, lnum2msgcnt = lintres.get_cnt_linenums_by_fname(fname)

        print '\nFile Name:', fname
        print
        for mtype in mtype2cnt.keys():
            print mtype.ljust(15),
        print 'Total'.ljust(10)
        print '-' * 70
        
        for val in mtype2cnt.values():
            print str(val).ljust(15),
        print str(total).ljust(10)

        print
        print 'Line Number'.ljust(12),
        print 'Message Count'
        print '-' * 30
        for (lnum, cnt) in lnum2msgcnt:
            print str(lnum).ljust(5), '=====>', cnt

        return raw_input('\nEnter \'q\' to quit or \'c\' to continue: ')


    def start_query_by_file(self, lintres):
        while True:
            user_input = self.show_filetypes_and_get_type(lintres)
            
            if user_input == 'q':
                break
            try:
                ftype = cmn.fileTypes[user_input]
            except:
                print 'Wrong index!\n'
                continue

            while True:
                user_input = self.show_files_and_get_fname(lintres, ftype)
                if user_input == 'q':
                    break
                elif user_input == '':
                    continue

                fname = user_input
                try:
                    user_input = self.show_cnt_and_linenums_and_get_linenum(lintres, fname)
                except:
                    print 'Wrong index\n'
                    continue

                if user_input == 'q':
                    break
                if user_input == 'c':
                    continue

                
    def start(self, lintres):
        """
        Start point of User Interface.
        """
        while True:
            ## First let user choose a feature they want to use.
            user_input = self.show_feature_list()
            if user_input == 'q':
                print
                break

            if user_input == 0:
                self.start_query_by_id(lintres)
            elif user_input == 1:
                self.start_query_by_file(lintres)
            else:
                print 'Please enter a valid index number! Try again.'                
                

def main():
    from optparse import OptionParser
    
    parser = OptionParser(usage="usage: %prog [options]",
                          version="%prog 1.0")

    parser.add_option("-b", "--build_path",
                      action="store", # optional because action defaults to "store"
                      dest="bpath",
                      type="string",
                      default="/home/sd/workspace/hwd/build/dp600/hwd/",
                      help="Specifiy where lint output file is. Default is /home/sd/workspace/hwd/build/dp600/hwd/")
    
    parser.add_option("-s", "--src_path",
                      action="store", # optional because action defaults to "store"
                      dest="spath",
                      type="string",
                      default="/home/sd/workspace/hwd/dp6xx_src/",
                      help="Specifiy where source files are. Default is /home/sd/workspace/hwd/dp6xx_src/.")

    parser.add_option("-o", "--old",
                      action="store",
                      dest="old_file",
                      default=None,
                      type="string",
                      help="Specifiy an old lint output file. Default is None.")
    
    parser.add_option("-n", "--new",
                      action="store", # optional because action defaults to "store"
                      dest="new_file",
                      type="string",
                      default="lint.origout",
                      help="Specifiy a new lint output file, use lint.orgi_out as default if not specified.")
    
    (options, args) = parser.parse_args()

    if len(args) >= 1:
        parser.error("No arguments needed!")

    cmn.build_path = options.bpath
    cmn.src_path = options.spath

    nres = LintResult(options.new_file, cmn.build_path)
    nres.process()

    if options.old_file is not None:
        ores = LintResult(options.old_file, cmn.build_path)
        ores.process()
        lintcmp = LintCmp(ores, nres)
        lintcmp.report()

    ui = UI()
    ui.generate_report(nres)
    ui.start(nres)


if __name__ == '__main__':
    main()


