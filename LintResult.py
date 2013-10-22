#!/usr/bin/env python

"""
Module for gathering and processing file output by Lint.
It will be used by 'LintAnalysis' module.
"""

import os
import re
import bisect
from operator import itemgetter
import common as cmn

class LintMsg(object):
    """
    class LintMsg represents a detailed lint message
    identified by a unique messge ID. It contains the
    collection of records that correspond to the message.

    Data Structure:
    1. 'type2file'
       A dict mapping type of file to a file list.
       The file List is sorted by file name for easy lookup.
       'c' -> [1.c, 2.c, 3.c, ...]
       'h' -> [1.h, 2.h, 3.h, ...]
    2. file2info
       A dict mapping file name to a list of (line#, desc) tuples.
       This List is sorted by line#.
       '1.c' -> [(1, xxx), (2, yyy), ...]
       '1.h' -> [(1, xxx), (2, yyy), ...]
       ......
    3. file2msg_count
       A dict mapping file name to the number of message it has.
    4. 'id'
       message id
    5. 'total'
       total count of the message.

    Methods used internally:
    1. update_total(self)
    2. add_record(self, ftype, fname, line_num, desc)

    Methods used as interface.
    (but only for class 'LintResult'. We'll let 'LintResult'
    exports interface of 'LintMsg' to other modules.):
    1. get_total(self)
    2. get_flist_by_type(self, ftype)
    3. get_info_by_type(self, fname)
    """
    def __init__(self, msg_id):
        self.id = msg_id
        self.total = 0
        ## Map file type of a list of files.
        self.type2file = {}
        self.type2file['h'] = []
        self.type2file['c'] = []

        ## Map file to a list of (line_num, desc)
        self.file2info = {}
        ## Map file to a the total message count it gets.
        self.file2msg_count = {}

    def update_total(self):
        self.total += 1

    def add_record(self, ftype, fname, line_num, desc):
        """
        Add a record. Record should be sorted by the file name.

        'record' is a (file_type, file_name, line#, description) tuple
        represents detailed information belongs to a given message.
        """
        if ftype == 'h': # header file
            ## each key value relates to a list of
            ## (file_name, line#, description) tuples.
            if fname not in self.type2file['h']:
                bisect.insort(self.type2file['h'], fname)
        else: # c file
            if fname not in self.type2file['c']:
                bisect.insort(self.type2file['c'], fname)

        if not self.file2info.has_key(fname):
            self.file2info[fname] = [(line_num, desc)]
        else:
            self.file2info[fname].append((line_num, desc))
            
        self.file2msg_count[fname] = \
            self.file2msg_count.get(fname, 0) + 1

        self.update_total()

    def get_total(self):
        """
        Return total count of the message.
        """
        return self.total

    def get_linenums_by_file(self, fname):
        return [num for (num, info) in sorted(self.file2info[fname], key=itemgetter(0))]

    def get_file_linenum(self):
        hlist = self.type2file.get('h')
        clist = self.type2file.get('c')

        fn2lnums = {}
        for fname in hlist:
            fn2lnums[fname] = self.get_linenums_by_file(fname)

        for fname in clist:
            fn2lnums[fname] = self.get_linenums_by_file(fname)

        return fn2lnums

    def get_flist_by_type(self, ftype):
        """
        Return [(file, message_count)] in which all file
        has the type 'ftype'. List is sorted by file name.
        """
        try:
            flist = self.type2file.get(ftype)
        except KeyError:
            print 'Invalid Key for type2file!!!'

        return [(fname, self.file2msg_count[fname]) for fname in flist]

    def get_info_by_file(self, fname):
        """
        Return list:
        [line_num, description]:sorted by line_num
        """
        return sorted(self.file2info[fname],
                      key=lambda a : a[0])

class File(object):
    def __init__(self, fname):
        self.fname = fname
        self.line2msg = {}
        self.total_msg = 0
        self.mtype2cnt = {}

    def add_record(self, msgid, linenum, mtype):
        self.mtype2cnt[mtype] = self.mtype2cnt.get(mtype, 0) + 1
        self.total_msg += 1
        self.line2msg[linenum] = self.line2msg.get(linenum, 0) + 1

    def get_cnt_by_mtype(self):
        return self.mtype2cnt

    def get_total(self):
        return self.total_msg

    def get_linenums(self):
        return sorted(self.line2msg.iteritems(), key=itemgetter(0))

class LintResult(object):
    """
    class LintResult represents the result generated
    by analyzing the output file after running 'make run_lint'.

    This class is an aggregation of the class 'LintMsg'.

    Data structure:
    1. msg_count_by_type:
    2. total_msg_num:
    3. messages:
       A collection of class LintMsg.

    Methods used internally:
    1. init_msg_type_count(self)
    2. count_msg_by_type(self)
    3. parse_line(self, line)
    4. classify_msg_by_id(self)

    Methods used as interface to other modules:
    1. get_total(self)
    2. get_msg_count_by_type(self)
    3. get_msgid_and_count(self)
    4. get_msg_by_id(self, msgid)
    5. prcess(self)
    """
    def __init__(self, fname, path):
        try:
            self.fobj = open(os.path.join(path, fname), 'r')
        except IOError:
            print 'failed to open file %s at %s' % (fname, path)

        self.fname = fname
        self.content = self.fobj.read()
        self.msg_count_by_type = {}
        self.total_msg_num = 0
        ## Map message ID to 'LintMsg' object.
        self.messages = {}
        self.id_count_prob = []
        self.files = {}

    ## Internal methods

    def init_msg_type_count(self):
        """
        Initialize each message type count by zero.
        """
        for key in cmn.getMsgTypes():
            self.msg_count_by_type[key] = 0

    def count_msg_by_type(self):
        """
        Count how many times each message types occurs
        for statistic analysis purpose.

        Message type has been defined in 'common' module.
        """
        self.init_msg_type_count()
        patobj = re.compile(cmn.lint_msg_pat)
        ## Find all matches matching pattern '[PC-Lint xxx]'.
        matches = patobj.findall(self.content)
        ## Get all message number from matching strings.
        msg_ids = map(cmn.toInt, matches)
        self.total_msg_num = len(msg_ids)

        ## Compute count for each message type.
        for msgid in msg_ids:
            self.msg_count_by_type[cmn.getMsgTypeByID(msgid)] += 1

    def parse_line(self, line):
        """
        Parse a line that contains a valid lint message.
        """
        ## maxsplit is two, thus 'elems' will have
        ## at most three elements.
        elems = line.split(':', 2)
        
        if elems[0].endswith('.c'):
            ftype = 'c' # c source file            
        else: ## include .inl file.
            ftype = 'h' # header file

        fname = elems[0][len(cmn.src_path):]
        line_num = elems[1]
        desc = elems[2]

        return (ftype, str(fname), int(line_num), desc)

    def classify_msg_by_id(self):
        """
        Classfiy messages by their unique ID. This method
        will generate a collection of 'LintMsg' objects which
        can guide us to modify the code and perform statistical analysis.
        """
        lines = self.content.split('\n')
        for line in lines:
            m = re.search(cmn.lint_msg_pat, line)
            if m: ## found a match
                msg_id = cmn.toInt(m.group(0))
                if not self.messages.has_key(msg_id):
                    ## If this the first time identifing the
                    ## message id, create a 'LintMsg' object for it.
                    self.messages[msg_id] = LintMsg(msg_id)

                ftype, fname, line_num, desc = self.parse_line(line)
                self.messages[msg_id].add_record(ftype, fname,
                                                 line_num, desc)

                if not self.files.has_key(fname):
                    self.files[fname] = File(fname)
                self.files[fname].add_record(msg_id, line_num,
                                             cmn.getMsgTypeByID(msg_id))
                   

    def count_prob_forall_messages(self):
        """
        Return each message id, its count and prob.
        Sort by count number by decending order.
        """
        idcnt = [(mid, msg.get_total()) for mid, msg in self.messages.iteritems()]
        sorted_idcnt = sorted(idcnt, key=lambda (k, v) : v, reverse=True)

        self.id_count_prob = \
            [(mid, cnt, float(cnt)/self.total_msg_num) for mid, cnt in sorted_idcnt]

        return self.id_count_prob

    ## End of internal methods.


    ## Misc Interface

    def has_msg(self, msgid):
        return self.messages.has_key(msgid)

    def get_fname_suffix(self):
        """
        Return file name in which lint result is stored.
        """
        return self.fname.split('.')[1]

    def get_total(self):
        """
        Return the number of messages.
        """
        return self.total_msg_num

    ## End of misc interface.

    ## Interface for querying messages by type.
    
    def get_msg_count_prob_by_type(self):
        """
        Return [message_type, count, prob] sorted by count in decending order.
        """
        mtypecnt = sorted(self.msg_count_by_type.iteritems(),
                        key=lambda (k, v) : k, reverse=True)
        return [(t, c, float(c)/self.total_msg_num) for t,c in mtypecnt]

    def get_msgid_count_prob_by_type(self, mtype):
        """
        Return [message_id, count, prob] sorted by message_id
        for a given message type 'mtype'.
        """
        mids = []
        id_cnt_prob = []
        mrange = cmn.getRangeOfMsgType(mtype)

        for mid in self.messages.keys():
            if mid in range(mrange[0], mrange[1]):
                mids.append(mid)

        return sorted([(mid, c, p) for mid, c, p in self.id_count_prob if mid in mids],
                      key=itemgetter(0))
               
    ## End of Interface for querying messages by type.

    ## Interface for querying messages by message id.
    def get_flist_by_id(self, msgid):
        """
        Return all header files and c source files
        containing a given message id 'msgid'.
        """
        hlist = self.messages[msgid].get_flist_by_type('h')
        clist = self.messages[msgid].get_flist_by_type('c')
        return (hlist, clist)

    def get_info_by_id_and_file(self, msgid, fname):
        """
        Return detailed information of a file 'fname' containing
        message whose id is 'msgid'.
        """
        return self.messages[msgid].get_info_by_file(fname)

    def get_file_linenum_by_id(self, msgid):
        return self.messages[msgid].get_file_linenum()

    ## End of Interface for querying messages by message id.

    ## Interface for querying message, line number by file.

    def get_files_by_type(self, ftype):
        find_c_file = lambda f : f.endswith('.c')
        find_h_file = lambda f : f.endswith('.h') or f.endswith('inl')

        if ftype == 'c':
            files = filter(find_c_file, self.files.keys())
        else:
            files = filter(find_h_file, self.files.keys())

        files.sort()
        return files

    def get_cnt_linenums_by_fname(self, fname):
        f = self.files[fname]
        
        mtype2cnt = f.get_cnt_by_mtype()
        total = f.get_total()
        linenums = f.get_linenums()
        return mtype2cnt, total, linenums


    ## End of interface for file.

    def process(self):
        """
        A wrapper method for internal processing.
        Must be called first.
        """
        self.count_msg_by_type()
        self.classify_msg_by_id()
        self.count_prob_forall_messages()
    
        
def main():
    lintres = LintResult()
    lintres.process()

    hlist, clist = lintres.get_flist_by_id(18)
    #print hlist
    #print clist
    #print lintres.get_info_by_id_and_file(18, hlist[0][0])

if __name__ == '__main__':
    main()
