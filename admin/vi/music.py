# -*- coding: utf-8 -*-


from imp import reload
from admin.vi import WxApi
reload(WxApi)

class cmusic(WxApi.cWxApi):
    
    def setClassName(self):
        #设定要实例的 BIZ类和TPL类，为空则继承基类，可以能过判断part的值来设置不同的类名
        self.dl_name = 'music_dl'

    def specialinit(self):
        self.navTitle = '音乐回复'
        self.getBreadcrumb() #获取面包屑

    #管理公众号
    def goPartList(self):
        keyword = self.dl.GP('keyword','')
        status = self.dl.GP('status','1')
        pagesize = 5
        condition = " module = 'music'"
        sUrl = 'admin?viewid=music'
        param = {}
        childsql = "SELECT  id FROM ims_rule where %s" % (condition)
        if keyword : 
            condition += "  AND name LIKE '%%%s%%'" % keyword
            childsql += "  AND name LIKE '%%%s%%'" % keyword
            param['keyword'] = keyword
        if status : 
            condition += "  AND status = '%s'" % status
            childsql += "  AND status = '%s'" % status
            param['status'] = status
        childsql+="limit %s"%((self.pageNo - 1) * pagesize)
        

        sql = "SELECT * FROM ims_rule WHERE %s and id not in (%s) ORDER BY status DESC, displayorder DESC, id ASC limit %s" % (condition,childsql,pagesize)

        L,t = self.dl.db.fetchall(sql) 
        total = self.dl.db.fetchcolumn("select count(*) from ims_rule  where %s" % condition)
        html_pager = self.pagination(total,self.pageNo,pagesize,sUrl)
        self.assign('html_pager',html_pager)
        for i in range(len(L)):
            kws,total = self.dl.db.fetchall("SELECT * FROM ims_rule_keyword WHERE rid = '%s'"%L[i].get('id',''))
            L[i]['keywords'] = kws
        self.assign({
            'status':status,'keyword':keyword , 'list' : L , 'site_url':self.objHandle.environ.get('HTTP_HOST')
        })
        return self.runApp('rule_music.html')

    def goPartLocalform(self):
        rule = {'rule':{},'keyword':{}}
        reply = ''
        keyword = ''
        id = self.dl.GP('id','')
        if id:
            rule['rule'] = self.dl.db.fetch("SELECT * FROM ims_rule WHERE id = '%s'"%id)
            if not rule['rule'] :
                return self.mScriptMsg('抱歉，您操作的规则不在存或是已经被删除！',[['admin?viewid=music','返回列表']])
            rule['keyword'],total = self.dl.db.fetchall("SELECT * FROM ims_rule_keyword WHERE rid = '%s'"%id)
            keyword_array = []
            for kw in rule['keyword']:
                if kw.get('type') != 1:
                    continue
                keyword_array.append(kw.get('content',''))
            keyword = ','.join('%s'%kw for kw in keyword_array)
            reply = self.dl.db.fetch("select title as bt,description,url as baselink,hqurl from ims_music_reply where rid = '%s'" % id)
        self.assign('rule',rule['rule'])
        self.assign('keyword',keyword)
        self.assign('specialkeyword',rule['keyword'])
        self.assign('reply',reply)

        return self.runApp('rule_music_post.html')

    def goPartDelete(self):
        dR=self.delete_data()
        R=dR['R']
        if str(R)=='1':    #错误
            s=self.mScriptMsg(dR['MSG'])
        else:
            url  ='?viewid=%s&pageNo=%s'%(self.viewid , self.pageNo)
            
            url+=self.getAddUrlStrA()
            s=self.mScriptMsg('数据删除成功',[[url,'返回列表']],'success')
        return s 
        
    def delete_data(self):
        dR = {'R':'','MSG':""}
        self.dl.db.query("delete from ims_rule where id = '%s'"%self.pk)
        self.dl.db.query("delete from ims_rule_keyword where rid = '%s'"%self.pk)
        self.dl.db.query("delete from ims_stat_rule where rid = '%s'"%self.pk)
        self.dl.db.query("delete from ims_stat_keyword where rid = '%s'"%self.pk)
        return dR

    def goPartWelcome(self):
        id = self.dl.GP('id','')
        weid = self.weid
        content = self.dl.db.fetchcolumn("select content from ims_music_reply where rid = '%s'" % id)
        self.dl.db.query("update ims_wechats set welcome = '%s' where weid = '%s'" % (content , weid))
        return self.dl.oFunc.json_encode({'error':0})

    def goPartDefault(self):
        id = self.dl.GP('id','')
        weid = self.weid
        content = self.dl.db.fetchcolumn("select content from ims_music_reply where rid = '%s'" % id)
        self.dl.db.query("update ims_wechats set defaults= '%s' where weid = '%s'" % (content , weid))
        return self.dl.oFunc.json_encode({'error':0})


    def goPartPost(self):
        pk = self.dl.GP('pk','')
        data = {'weid':self.weid,'cid':self.dl.usr_id,'displayorder':0}
        data['name'] = self.dl.GP('name','')
        data['status'] = self.dl.GP('status','0')
        data['module'] = self.dl.GP('module','')
        keywords = self.dl.GP('keywords','')
        title = self.dl.GP('title','')
        description = self.dl.GP('description','')
        baselink = self.dl.GP('baselink','')
        hqurl = self.dl.GP('hqurl','')
        if pk == "":
            self.dl.db.insert("ims_rule",data)
            pk = self.dl.db.insertid()
            
        else:
            rule = self.dl.db.fetch("select id from ims_rule where weid = '%s' and id = '%s'" % (self.weid , pk))
            if not rule:
                url  ='admin?viewid=music'
                return self.mScriptMsg('该规则不存在或已被删除了',[[url,'返回列表']],'error')
            self.dl.db.update("ims_rule",data," id='%s'" % pk)
            
        reply = self.dl.db.fetch("select * from ims_music_reply where rid = '%s'" % pk)
        if reply:
            self.dl.db.update('ims_music_reply',{'title':title,'description':description,'url':baselink,'hqurl':hqurl}," rid='%s'" % pk)
        else:
            self.dl.db.insert('ims_music_reply',{'rid':pk,'title':title,'description':description,'url':baselink,'hqurl':hqurl})
        #更新，添加，删除关键字
        if pk:
            sql = "DELETE FROM ims_rule_keyword WHERE [rid]='%s' AND weid='%s'" % (pk,self.weid)
            self.dl.db.query(sql)
            rows = []
            
            kwds = keywords.split(",")
            keywordname = self.objHandle.values.getlist('keywordname')
            keywordvalue = self.objHandle.values.getlist('keywordvalue')
            for i in range(len(keywordname)):
                rowtpl = {
                    'rid' : pk , 'weid' : self.weid , 'module':data['module'],'status':data['status'],'displayorder':0
                }
                kn = keywordname[i]
                kv = keywordvalue[i]
                rowtpl['content'] = kn
                rowtpl['type'] = kv
                rows.append(rowtpl)
            for kw in kwds:
                rowtpl = {
                    'rid' : pk , 'weid' : self.weid , 'module':data['module'],'status':data['status'],'displayorder':0
                }
                rowtpl['content'] = kw
                rowtpl['type'] = 1
                rows.append(rowtpl)
            for rule_keyword in rows:
                self.dl.db.insert("ims_rule_keyword",rule_keyword)
            return self.mScriptMsg('规则操作成功！',[['admin?viewid=music&part=localform&id=%s' % pk,'返回']],'success')
        else:
            return self.mScriptMsg('规则操作失败, 请联系网站管理员！')



