import requests
from bs4 import BeautifulSoup
import re

import datetime as dt
from urllib.request import urlopen
import numpy as np
import pandas as pd

daylist = []
TAlist = []
RNlist = []
SNlist = []

firstday = dt.datetime(2021,1,1)
now = dt.datetime.now()
daylist.append(firstday.strftime("%Y%m%d"))
for i in range(0, (now-firstday).days) :
    daylist.append((firstday + dt.timedelta(days = i+1)).strftime("%Y%m%d"))

for day in daylist :
    domain = "https://apihub.kma.go.kr/api/typ01/url/kma_sfcdd.php?tm={0}&stn=0&help=1&authKey=Oe59BoxnQP-ufQaMZxD_-Q".format(day)
    with urlopen(domain) as f:
        lines = f.readlines()
        lines = lines[65:]
        del lines[-1]
        TAsum = 0
        RNsum = 0
        SNsum = 0
        for itr in lines :
            itr = str(itr)
            flg = 0
            idx = 0

            for i in itr :
                idx += 1
                if i == ',' :
                    flg += 1
                if flg == 10 :
                    TAidx_start = idx + 1
                if flg == 11 :
                    TAidx_end = idx
                if flg == 38 :
                    RNidx_start = idx + 1
                if flg == 39 :
                    RNidx_end = idx
                if flg == 47 :
                    SNidx_start = idx + 1
                if flg == 48 :
                    SNidx_end = idx
            TAsum += float(itr[TAidx_start : TAidx_end])
            if float(itr[RNidx_start : RNidx_end]) > 0 :
                RNsum += float(itr[RNidx_start : RNidx_end])
            if float(itr[SNidx_start : SNidx_end]) > 0 :
                SNsum += float(itr[SNidx_start : SNidx_end])
        TAmean = TAsum/len(lines)
        RNmean = RNsum/len(lines)
        SNmean = SNsum/len(lines)
        TAlist.append(TAmean)
        RNlist.append(RNmean)
        SNlist.append(SNmean)
        
weather_dic = {
    'day' : daylist,
    'Temperature' : TAlist,
    'Rainfall' : RNlist,
    'Snowfall' : SNlist
}
weather_df = pd.DataFrame(weather_dic)
weather_df


warmlist = ['드라마', 'R&B/소울', '발라드', '팝', '캐롤']
excitinglist = ['댄스', '락', '일렉트로니카', '트로트', '팝']
wetlist = ['드라마', 'R&B/소울', '발라드', '인디']
solitarylist = ['발라드', '인디', '블루스/포크']
bouncelist = ['댄스', '일렉트로니카', '랩/힙합', '트로트']
etclist = ['그외장르', '한국영화', '월드뮤직']
ignorelist = ['OST', 'POP', '가요', '전체']

header = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}

def countgen(day) :
    warm_cnt = 0
    exciting_cnt = 0
    wet_cnt = 0
    solitary_cnt = 0
    bounce_cnt = 0
    etc_cnt = 0
    genrelist = []
    
    for i in range(1, 5) :
        url = 'https://www.genie.co.kr/chart/top200?ditc=D&ymd={0}&hh=06&rtm=N&pg={1}'.format(day, i)
        data = requests.get(url, headers = header)
        soup = BeautifulSoup(data.text, 'html.parser')
        trs = soup.select('#body-content > div.newest-list > div > table > tbody > tr')
        for tr in trs:
            a_tag = tr.select_one('td.info > a.title.ellipsis')
            if a_tag is not None :
                myStr = str(tr.find_all("td")[2].a)
                p = re.compile('[0-9]+')
                m = p.search(myStr)
                id = m.group()
                url = 'https://www.genie.co.kr/detail/albumInfo?axnm={0}'.format(id)
                data_id = requests.get(url, headers = header)
                soup_id = BeautifulSoup(data_id.text, 'html.parser')
                li = soup_id.select('#body-content > div.album-detail-infos > div.info-zone > ul > li')
                genre = li[1].select('span')[1].string
                genrelist.append(genre)
    genre_dic = {
        'genre' : genrelist
    }
    genre_df = pd.DataFrame(genre_dic)

    for gen in genre_df.genre :
        for g in gen.split(' / ') :
            if g in ignorelist :
                continue
            if g in warmlist :
                warm_cnt += 1
            if g in excitinglist :
                exciting_cnt += 1
            if g in wetlist :
                wet_cnt += 1
            if g in solitarylist :
                solitary_cnt += 1
            if g in bouncelist :
                bounce_cnt += 1
            if g in etclist :
                etc_cnt += 1
                
    weather_df.loc[weather_df.day == day, 'warm'] = warm_cnt
    weather_df.loc[weather_df.day == day, 'exciting'] = exciting_cnt
    weather_df.loc[weather_df.day == day, 'wet'] = wet_cnt
    weather_df.loc[weather_df.day == day, 'solitary'] = solitary_cnt
    weather_df.loc[weather_df.day == day, 'bounce'] = bounce_cnt
    weather_df.loc[weather_df.day == day, 'etc'] = etc_cnt
    print("done")


for day in daylist[340:] :
    countgen(day)

weather_df.to_csv("filename.csv", index=False, encoding="utf-8-sig")


weather_df = pd.read_csv('filename.csv')
for day in weather_df.day[340:345] :
    countgen(day)
    print(day)

weather_df.to_csv("filename.csv", index=False, encoding="utf-8")