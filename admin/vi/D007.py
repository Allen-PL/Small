# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) wxmall.janedao.cn
# Author：hyj
# Start  Date:  2019
##############################################################################


from imp import reload
from basic.publicw import DEBUG

if DEBUG=='1':
    import admin.vi.BASE_TPL
    reload(admin.vi.BASE_TPL)
from admin.vi.BASE_TPL             import cBASE_TPL

from admin.vi.mselect  import mselect_forM

class cD007(cBASE_TPL):

    def setClassName(self):

        self.dl_name = 'D007_dl'
        #self.inframe = 1


    def specialinit(self):
        self.navTitle = '投票管理'
        self.getBreadcrumb() #获取面包屑
        #self.isFile=1

    def goPartList(self):

        self.assign('NL',self.dl.GNL)
        PL,L = self.dl.mRight()
        self.assign('dataList',L)
        self.getPagination(PL)
        zszt = self.dl.GP('zszt','')
        istp = self.dl.GP('istp','')
        ft=self.dl.getmtcdata('RSXZT',zszt)
        self.assign('zszt',ft)
        self.assign('zsztval',zszt)
        s = self.runApp('D007_list.html')
        return s

    def initPagiUrl(self):
        zszt = self.REQUEST.get('zszt','')
        qqid = self.REQUEST.get('qqid','')
        url = self.sUrl
        if qqid:
            url += "&qqid=%s" % qqid
        if zszt:
            url += "&zszt=%s" % zszt
        return url

    def goPartLocalfrm(self):
        self.backurl = 'admin?viewid=D007'
        self.need_editor = 1
        self.initHiddenLocal()#初始隐藏域
        self.getBackBtn()
        sqqid = self.dl.GP('sqqid','')
        
        NL = [['编号','60px','center'],
              ['姓名','120px','center'],
              ['手机号','100px','center'],
              ['宣言','','center'],
              ['报名时间','140px','center'],
              ['操作','70px','center']
            ]
        self.assign('NL',NL)
        item,itemlist = self.dl.get_local_data(self.pk)
        #明细对象
        self.assign('item',item)
        self.assign('sqqid',sqqid)
        self.assign('itemlist',itemlist)


        s = self.runApp('D007_local.html')
        return s

    def goPartlotstop(self):
        L = self.dl.lotstop()
        return self.dl.json_encode(L)

    def goPartlotstar(self):
        L = self.dl.lotstar()
        return self.dl.json_encode(L)

