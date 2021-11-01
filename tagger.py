# from matplotlib import pyplot as plt
import json
from dateutil import parser

from db_manager import get_items_from_date_range

#ICHIMOKU COMPONENTS
def calculateChikouSpan(closing_prices, offset=26):
    return closing_prices[offset:]+[0]*offset

def calculateTenkanSen(low_prices, high_prices, periods=9, complete_lenght=True):
    TS=[]
    n_low_periods = low_prices[:periods]
    n_high_periods = high_prices[:periods]
    limit=len(low_prices)-periods+1
    for i in range(limit):
        M=max(n_high_periods)
        m=min(n_low_periods)
        TS.append(round((M+m)/2, getDecimalsCount(low_prices[0])))
        n_low_periods=n_low_periods[1:]
        n_high_periods=n_high_periods[1:]
        if(i!=limit-1):
            n_low_periods.append(low_prices[i+periods])
            n_high_periods.append(high_prices[i+periods])
    if complete_lenght:
        TS=[0]*(len(low_prices)-limit)+TS
    return TS

def calculateKijunSen(low_prices, high_prices, periods=26, complete_lenght=True):
    KS=[]
    n_low_periods = low_prices[:periods]
    n_high_periods = high_prices[:periods]
    limit=len(low_prices)-periods+1
    for i in range(limit):
        M=max(n_high_periods)
        m=min(n_low_periods)
        KS.append(round((M+m)/2, getDecimalsCount(low_prices[0])))
        n_low_periods=n_low_periods[1:]
        n_high_periods=n_high_periods[1:]
        if(i!=limit-1):
            n_low_periods.append(low_prices[i+periods])
            n_high_periods.append(high_prices[i+periods])
    if complete_lenght:
        KS=[0]*(len(low_prices)-limit)+KS
    return KS

def calculateSenkouSpanA(tenkan_sen, kijun_sen, offset=26, complete_lenght=True):
    SSA=[]
    for i in range(len(tenkan_sen)):
        SSA.append((tenkan_sen[i]+kijun_sen[i])/2)
    return [0]*offset+SSA[:(len(tenkan_sen)-offset)]

def calculateSenkouSpanB(low_prices, high_prices, periods=52, complete_lenght=True):
    SSB=[]
    n_low_periods = low_prices[:periods]
    n_high_periods = high_prices[:periods]
    limit=len(low_prices)-periods+1
    for i in range(limit):
        M=max(n_high_periods)
        m=min(n_low_periods)
        SSB.append(round((M+m)/2, getDecimalsCount(low_prices[0])))
        n_low_periods=n_low_periods[1:]
        n_high_periods=n_high_periods[1:]
        if(i!=limit-1):
            n_low_periods.append(low_prices[i+periods])
            n_high_periods.append(high_prices[i+periods])
    if complete_lenght:
        SSB=[0]*(len(low_prices)-limit)+SSB
    return [0]*26+SSB[:(len(low_prices)-26)]

#TAGGING
def getTaggedValues(closing_prices, senkou_span_a, senkou_span_b, tenkan_sen, kijun_sen, chikou_span):
    tags=[]
    for i in range(len(closing_prices)):
        count=0
        #POSITIVE
        if(closing_prices[i]>senkou_span_a[i] and closing_prices[i]>senkou_span_b[i]):
            count+=0.5
        if(tenkan_sen[i]>kijun_sen[i]):
            count+=0.5
        if(i>=26):
            if(closing_prices[i-26]<chikou_span[i-26]):
                count+=0.5
        #NEGATIVE
        if(closing_prices[i]<senkou_span_a[i] and closing_prices[i]<senkou_span_b[i]):
            count-=0.5
        if(tenkan_sen[i]<kijun_sen[i]):
            count-=0.5
        if(i>=26):
            if(closing_prices[i-26]>chikou_span[i-26]):
                count-=0.5
        #INDECISION
        if((closing_prices[i]>=senkou_span_a[i] and closing_prices[i]<=senkou_span_b[i]) or (closing_prices[i]<=senkou_span_a[i] and closing_prices[i]>=senkou_span_b[i])):
            count=0
        tags.append(count)
    return tags

#AUXILIARY FUNCTIONS
def getDecimalsCount(number):
    cad = str(number)
    cad=cad[::-1]
    count=0
    for c in cad:
        if c=='.':
            break
        count+=1
    return count

def getX_Axis(lenght):
    x=[]
    for i in range(lenght):
        x.append(i)
    return x

#MAIN FUNCTION
def get_json_tags_from_date_range(temporality="Day", date_start="2000-01-01", date_end="2023-01-01", ):
    dates=[]
    o_prices=[]
    h_prices=[]
    l_prices=[]
    c_prices=[]

    # hours=[]
    # days=[]
    # months=[]

    #GETTING PRICES FROM DB
    items_list=get_items_from_date_range(temporality, date_start, date_end)
    # if(temporality=="EURUSDHour"):
    # if(temporality=="Hour"):
    #     for item in items_list:
    #         # print(item["_id"])
    #         hours.append(parser.parse(item['_id']).hour)

    for item in items_list:
        # days.append(parser.parse(item['_id']).day)
        # months.append(parser.parse(item['_id']).month)
        dates.append(str(item['_id']))
        o_prices.append(float(item['open']))
        h_prices.append(float(item['high']))
        l_prices.append(float(item['low']))
        c_prices.append(float(item['close']))
    
    # for item in items_list:
    #     dates.append(str(parser.parse(item['_id'])))
    #     o_prices.append(float(item['open']))
    #     h_prices.append(float(item['high']))
    #     l_prices.append(float(item['low']))
    #     c_prices.append(float(item['close']))

    #ICHIMOKU ELEMENTS
    cs=calculateChikouSpan(c_prices)
    ts=calculateTenkanSen(l_prices, h_prices)
    ks=calculateKijunSen(l_prices, h_prices)
    ssa=calculateSenkouSpanA(ts, ks)
    ssb=calculateSenkouSpanB(l_prices, h_prices)

    #TAGS
    tags_prices=getTaggedValues(c_prices, ssa, ssb, ts, ks, cs)

    #GRAPH PRICES
    # x_axis=getX_Axis(len(c_prices))
    # plt.plot(x_axis,tags_prices, color='purple', linewidth=1)
    # plt.plot(x_axis,c_prices, color='black', linewidth=2)
    # plt.plot(x_axis,cs, color='gray', linewidth=1)
    # plt.plot(x_axis,ts, color='pink', linewidth=1)
    # plt.plot(x_axis,ks, color='blue', linewidth=1)
    # plt.plot(x_axis,ssa, color='green', linewidth=1)
    # plt.plot(x_axis,ssb, color='red', linewidth=1)
    # plt.show()

    #PACKAGING
    groups=[]
    for i in range(len(c_prices)-51):
        group={}
        candles=[]
        group.update({"tag":tags_prices[i+51]})
        for j in range(52):
            candle={}
            candle.update({"datetime":dates[i+j]})
            # if(temporality=="Hour"):
            # # if(temporality=="EURUSDHour"):
            #     candle.update({"hour":hours[i+j]})
            # candle.update({"day":days[i+j]})
            # candle.update({"month":months[i+j]})
            candle.update({"open":o_prices[i+j]})
            candle.update({"high":h_prices[i+j]})
            candle.update({"low":l_prices[i+j]})
            candle.update({"close":c_prices[i+j]})
            candles.append(candle)
        group.update({"candles":candles})
        groups.append(group)

    return groups
    #JSON WRITING
    # file = open(temporality+'.json', "w")
    # json.dump(groups, file)
    # file.close()
# --------------------------------------------------
# TESTS:
# --------------------------------------------------
if __name__ == "__main__":    
    # export_json_tags_from_date_range(date_start="2000-01-01", date_end="2010-01-01")
    # export_json_tags_from_date_range(date_start="2021-01-01", date_end="2010-01-01", temporality="EURUSDHour")
    # export_json_tags_from_date_range(date_start="2000-01-01")
    # export_json_tags_from_date_range(date_start="2021-01-01", temporality="EURUSDHour")
    get_json_tags_from_date_range(date_start="2021-01-01", temporality="Hour")