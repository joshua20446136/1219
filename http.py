'''
Created on 2021年12月16日
@author: Joshua
'''

import requests
import re
import datetime
from urllib.parse import urlencode
import json


def GetHtml(url,get_parameters):        
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'}
    req = requests.get(url, params=get_parameters,headers=headers)
    if req.status_code != 200:
        try:
            req.raise_for_status()
        except requests.exceptions.RequestException as ex:
            return None, "Status Code : " + str(ex)
    result = req.text
    error = "Page Error"
    return (result, error)



# 采集接口地址 
url = "https://i.maoyan.com/ajax/moreCinemas"
# 采集接口地址 参数
params = {'movieId' : 0, 'limit' : 20,'cityId' : 451, 'offset' : 0 }
# 测试地址 是否正确
# url_addr = url + '?' + urlencode(params)
# print(url_addr)
# 设置初始区域 总条数 为 -1 
total = -1
# 循环取页面数据
while True:
    # 数据转JSON格式
    json_txt  =  json.loads(  GetHtml(url,params)[0] )
    # 设置区域总条数 数据,当前区域只有第一次时设置 
    if total < 0 :
        total = json_txt['cinemas']['paging']['total']

    # 取前当页面limit大小数据
    for num in range(params['limit']):
        total = total - 1
        print("num: %d " % num)
        print( json_txt['cinemas']['cinemas'][num]['nm'] )
        print( json_txt['cinemas']['cinemas'][num]['addr'] )

        # print( 'total:%d' ,total )
        # 判断当前页面最后一条数据
        if( 0 == total):
             break
    # print(json_txt['cinemas']['paging']['hasMore'])
    # 判断是否是最后一条数据 及 最后一页面  结束采集
    if( 0 == total and False == json_txt['cinemas']['paging']['hasMore'] ):
        print('当前区域数据采集结束 标志信息 total:%d , hasMore:%s' % ( total , json_txt['cinemas']['paging']['hasMore'] ))
        # 重置 初始区域 总条数 为 -1 
        total = -1
        break
    # 翻页 +1
    params['offset'] = params['offset'] + params['limit']

# 翻页结束标记 及 总条数
print( json_txt['cinemas']['paging']['hasMore'])
print( total )



# if __name__ == '__main__':








class Collect(object):
    '''
    classdocs
    '''


    def __init__(self,building,parames):
        '''
        params
        Constructor
        '''
        self.Building = building
        self.Url = parames['url']
        self.PayLoad = parames['payload']
        self.StartPage = 0
        self.EndPage = 0
        self.BuildingUrl = list()
        
    def Sendemail(self,title):
        email = Send_Email()
        fc_date = datetime.date.today().strftime('%Y%m%d')
        email.Send(fc_date + title,fc_date + title)
    
    def GetEndPage(self,html):
        reinfo = re.findall("<a href=\"/project/page_(\d+)\?dc=88c9fcce-72a7-4ccf-8565-5406111509b3\">尾页<\/a>",html)
        #reinfo = re.findall("<a href=\"/project\?dc=88c9fcce-72a7-4ccf-8565-5406111509b3&amp;page=(\d+)\">尾页<\/a>",html)
        return reinfo[0]
    
    def GetBuildAddressUrl(self,html):
        reinfo = re.findall('<ul id="project_list">(.*?)<\/ul>',html,re.S)
        self.BuildingUrl += re.findall('<a href=\"/project/Details/(.*?)\">(.*?)<\/a></b>',html)
    
    def GetBuildContent(self,contenturl):
        print(len(self.BuildingUrl))
        for i in range(0,len(self.BuildingUrl)):
        #for i in range(0,1):  
            #print(self.BuildingUrl[i][1])             
            #项目首页
            url = contenturl[0] + self.BuildingUrl[i][0]
            print(url)
            try:
                html,error = self.GetHtml(url,None)
            except BaseException as e:
                print(e)
                print('Error:%s' % error)
            #推广名    ,住宅备案均价, 项目地址
            aliasname = re.findall('<small class=\"color--grey\">推广名：(.*?)<\/small>', html)[0]
            try:
                avgprice = re.findall('<big class="color--red bold fs24" style="vertical-align: -1px;">\s+(.*?)\s+</big>', html)[0]+'元/㎡'
            except:
                avgprice = '//'
            pjaddress = re.findall('<span class="bold">项目地址：</span><span title="(.*?)">', html)[0]
            
            #实时数据
            url = contenturl[1] + self.BuildingUrl[i][0]
            try:
                html,error = self.GetHtml(url,None)
            except BaseException as e:
                print(e)
                print('Error:%s' % error)

            #已售面积、已售套数、当前可售面积、当前可售套数
            soldarea = re.findall('<big>(.*?)<\/big><small>已售面积<\/small>', html)[0]
            soldcycle = re.findall('<big>(.*?)<\/big><small>已售套数<\/small>', html)[0]
            caarea = re.findall('<big>(.*?)<\/big><small>当前可售面积<\/small>', html)[0]
            cacycle = re.findall('<big>(.*?)<\/big><small>当前可售套数<\/small>', html)[0]
            
            
            #项目首页
            setattr(self.Building,'fcname',self.BuildingUrl[i][1])
            setattr(self.Building,'aliasname',aliasname)
            setattr(self.Building,'avgprice',avgprice)
            setattr(self.Building,'pjaddress',pjaddress)
            #实时数据
            setattr(self.Building,'soldarea',soldarea)
            setattr(self.Building,'soldcycle',soldcycle)            
            setattr(self.Building,'caarea',caarea)
            setattr(self.Building,'cacycle',cacycle)
            print(i)
            
            self.Building.save()           
        pass
    
    def GetBuildAddressUrls(self):        
        while True:
            self.StartPage += 1
            page = self.StartPage
            try:
                html,error = self.GetHtml(self.Url+str(page), self.PayLoad)
            except BaseException as e:
                print(e)
                print('Error:%s' % error)
                print('Error:%s' % e)
                break 
            
            self.GetBuildAddressUrl(html)
            
            if 0 == self.EndPage:
                try:
                    self.EndPage = int(self.GetEndPage(html))
                except Exception as e:
                    print(e)
                    print('Error-e:%s' % e)
                    break            
            if page >= self.EndPage:
                break
        return self
        pass
    
    def GetHtml(self,url,get_parameters):        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'}
        req = requests.get(url, params=get_parameters,headers=headers)
        if req.status_code != 200:
            try:
                req.raise_for_status()
            except requests.exceptions.RequestException as ex:
                return None, "Status Code : " + str(ex)
        result = req.text
        error = "Page Error"
        return (result, error)