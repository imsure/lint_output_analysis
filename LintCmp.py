#!/usr/bin/env python

import sys
from operator import itemgetter
import common as cmn
import os

class LintCmp(object):
    """
    This class is used to compare two lint output files.
    Only in charge of glue data together, handle the data
    to the 'LintAnalyzer' class.
    """
    def __init__(self, old_lintres, new_lintres):
        self.ores = old_lintres
        self.nres = new_lintres

    def cmp_msg_cnt_by_type(self):
        mc_old = self.ores.get_msg_count_prob_by_type()
        mc_new = self.nres.get_msg_count_prob_by_type()

        cmp_type = []
        for i in range(0, len(mc_old)):
            mtype = mc_old[i][0]
            cnt_old = mc_old[i][1]
            cnt_new = mc_new[i][1]
            diff = cnt_old - cnt_new
            cmp_type.append((mtype, cnt_old, cnt_new, diff))

        return cmp_type

    def cmp_msg_total(self):
        told = self.ores.get_total()
        tnew = self.nres.get_total()
        return told, tnew, float(told-tnew)/told

    def report_msgtypes(self, cmp_type, told, tnew, rate):
        print '+' * 40
        print 'Lint comparison report.'
        print '+' * 40

        print
        print 'Message Type'.ljust(18),
        print 'ID Range'.ljust(12),
        print 'Old Count'.ljust(12),
        print 'New Count'.ljust(12),
        print 'Difference(Old - New)'.ljust(15)
        print '-' * 80
        for mtype, oc, nc, diff in cmp_type:
            mrange = cmn.getRangeOfMsgType(mtype) 
            print str(mtype).ljust(18),
            print (str(mrange[0])+' ~ '+str(mrange[1]-1)).ljust(12),
            print str(oc).ljust(12), str(nc).ljust(12),
            print str(diff).ljust(15)

        print '-' * 80
        print 'Old Total:', told
        print 'New Total:', tnew
        print 'Total Messages number decreased:', told-tnew
        if rate >= 0:
            print 'Total Message dropped by', '{0:.1f}%'.format(rate*100)
        else:
            print 'Total Message increased by', '{0:.1f}%'.format(-rate*100)
        print

    def report_msgids(self, comb_id_cnt):
        """
        comb_id_cnt: [message_id, old_count, new_count]
        """
        print
        print 'Message ID'.ljust(12),
        print 'Old Count'.ljust(10),
        print 'New Count'.ljust(10),
        print 'Difference(old-new)'
        print '-' * 55
        for m, oc, nc in comb_id_cnt:
            print str(m).ljust(12),
            print str(oc).ljust(10), str(nc).ljust(10),
            print oc-nc
        print '-' * 55
        print

    def report_file_by_id(self, msgids):
        print '\nComparsion by message ID.'
        for msgid in msgids:
            print '\nMessage ID:', msgid
            print
            print 'File Name'.ljust(50),
            print 'Old Count'.ljust(10),
            print 'New Count'.ljust(10),
            print 'Difference(Old - New)'
            print '-' * 95

            fcnt_o = []
            flist_o = []
            if self.ores.has_msg(msgid):
                hlist, clist = self.ores.get_flist_by_id(msgid)
                fcnt_o = hlist + clist
                flist_o = [f for f, c in fcnt_o]
                
            fcnt_n = []
            flist_n = []
            if self.nres.has_msg(msgid):
                hlist, clist = self.nres.get_flist_by_id(msgid)
                fcnt_n = hlist + clist
                flist_n = [f for f, c in fcnt_n]

            same_fs = set(flist_o).intersection(flist_n)
            diff_o2n = set(flist_o) - set(flist_n)
            diff_n2o = set(flist_n) - set(flist_o)

            comb = []
            for f in same_fs:
                index_o = flist_o.index(f)
                index_n = flist_n.index(f)
                comb.append((f, fcnt_o[index_o][1], fcnt_n[index_n][1]))

            for f in diff_o2n:
                index_o = flist_o.index(f)
                comb.append((f, fcnt_o[index_o][1], 0))

            for f in diff_n2o:
                index_n = flist_n.index(f)
                comb.append((f, 0, fcnt_n[index_n][1]))

            for f, oc, nc in comb:
                print f.ljust(50),
                print str(oc).ljust(10),
                print str(nc).ljust(10),
                print (oc-nc)
                    
            print

    def report(self, mtypes=['Syntax_Errors', 'Warnings']):
        cmp_type = self.cmp_msg_cnt_by_type()
        told, tnew, rate = self.cmp_msg_total()
                
        old_stdout = sys.stdout
        fn = 'comparison_report_'+self.ores.get_fname_suffix()+\
            '_'+self.nres.get_fname_suffix()+'.txt'
        sys.stdout = open(os.path.join('./report', fn), 'w')

        self.report_msgtypes(cmp_type, told, tnew, rate)

        print 'Detailed comparsion of a specific message type.\n'
        for mtype in mtypes:
            print '*' * 30
            print 'Message Type:', mtype
            print '*' * 30
            print
            idcnt_o = self.ores.get_msgid_count_prob_by_type(mtype)
            ids_o = [v[0] for v in idcnt_o]
            idcnt_n = self.nres.get_msgid_count_prob_by_type(mtype)
            ids_n = [v[0] for v in idcnt_n]

            ## IDs that old result have but new result doesn't,
            ## that is, messages that we have cleared out.
            diff_o2n = set(ids_o) - set(ids_n)

            ## IDs that new result has but old result doesn't,
            ## that is, messages that we have introduced.
            diff_n2o = set(ids_n) - set(ids_o)

            same_ids = set(ids_o).intersection(set(ids_n))

            comb = []
            if diff_o2n == set([]): ## No message gone.
                print 'No old messages have been cleared out.\n'
            else:
                print 'Old new Messages have been cleared out.',
                print 'They are:', str(list(diff_o2n)).strip('[]')
                
            if diff_n2o == set([]): ## No message introduced.
                print 'No message have been introduced.'
            else:
                print 'New messages have been introduce.',
                print 'They are:', str(list(diff_n2o)).strip('[]')

            for m in same_ids:
                index_o = ids_o.index(m)
                index_n = ids_n.index(m)
                comb.append((m, idcnt_o[index_o][1], idcnt_n[index_n][1]))

            for m in diff_o2n:
                index_o = ids_o.index(m)
                comb.append((m, idcnt_o[index_o][1], 0))

            for m in diff_n2o:
                index_n = ids_n.index(m)
                comb.append((m, 0, idcnt_n[index_n][1]))

            comb.sort(key=itemgetter(0))
            self.report_msgids(comb)
            self.report_file_by_id([m for m,oc,nc in comb])

        sys.stdout = old_stdout
        print '\nComprasion report %s has been generated.' % (fn)
        print

        
