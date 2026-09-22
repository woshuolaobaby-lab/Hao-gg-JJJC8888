# -*- coding: utf-8 -*-
"""基金智能监控雷达 PRO MAX V9.2 · 153只基金 · 多通道加速稳定版"""
import re,time,json,math
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime
import numpy as np,pandas as pd,requests,streamlit as st

ROOT=Path(__file__).resolve().parent
HEAD={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/151 Safari/537.36","Referer":"https://fund.eastmoney.com/","Accept":"*/*","Connection":"keep-alive"}
st.set_page_config(page_title="基金智能监控雷达 PRO MAX V9",page_icon="📡",layout="wide")

# 原V7的115只基金：内置，防止升级后丢失
BUILTIN_FUNDS=[
    ('001549', '天弘上证50ETF'),
    ('530000', '天弘上证50场内'),
    ('006021', '广发沪深300'),
    ('510300', '沪深300ETF'),
    ('011609', '易方达科创50'),
    ('588080', '科创50场内'),
    ('019817', '广发创业板ETF'),
    ('159952', '创业板场内'),
    ('588000', '科创50ETF华夏'),
    ('013305', '科创创业50'),
    ('023918', '自由现金流'),
    ('159201', '自由现金流场内'),
    ('017512', '北证50'),
    ('020465', '招商半导体'),
    ('561980', '半导体设备ETF'),
    ('020482', '机器人'),
    ('560770', '机器人ETF'),
    ('020900', '通信设备'),
    ('515880', '通信ETF'),
    ('024195', '卫星'),
    ('159206', '卫星ETF'),
    ('012734', '人工智能'),
    ('006503', '集成电路'),
    ('001072', '智能装备'),
    ('022364', '永赢科技'),
    ('019830', '数字产业'),
    ('016664', '高端制造'),
    ('008989', '科技创新'),
    ('009049', '易方达高端'),
    ('159852', '软件服务ETF'),
    ('012621', '软件服务场内'),
    ('002170', '东吴移动'),
    ('515250', '智能汽车场内'),
    ('013292', '富国智能汽车'),
    ('008586', '华夏人工智能'),
    ('019062', '易方达软件'),
    ('562930', '软件易方达场内'),
    ('020686', '科创新材料'),
    ('588160', '科创新材料场内'),
    ('019170', '云计算'),
    ('023885', '金融科技'),
    ('516100', '金融科技场内'),
    ('001630', '计算机'),
    ('159998', '计算机场内'),
    ('017877', '新能源'),
    ('018926', '电池'),
    ('019875', '稀有金属'),
    ('001410', '信澳新能源'),
    ('161028', '新能源汽车'),
    ('501226', '全球新能源'),
    ('019058', '绿色电力'),
    ('260112', '基建能源'),
    ('013817', '光伏'),
    ('516290', '光伏场内'),
    ('159755', '电池ETF'),
    ('159608', '稀有金属ETF'),
    ('159611', '电力ETF'),
    ('016185', '电力公用'),
    ('013476', '智能电动车'),
    ('016900', '碳中和'),
    ('562990', '碳中和场内'),
    ('025857', '电网设备'),
    ('159326', '电网设备场内'),
    ('006113', '创新药'),
    ('501009', '生物科技'),
    ('159892', '恒生医药ETF'),
    ('012738', '创新药广发'),
    ('515120', '创新药场内'),
    ('007883', '医药易方达'),
    ('512010', '医药ETF场内'),
    ('015945', '国防军工'),
    ('512560', '军工ETF'),
    ('025732', '航天航空'),
    ('028091', '航天航空行业'),
    ('161725', '白酒'),
    ('000083', '消费行业'),
    ('012857', '主要消费'),
    ('159928', '消费场内'),
    ('560880', '家电场内'),
    ('015040', '食品饮料'),
    ('159736', '食品饮料场内'),
    ('512690', '酒ETF'),
    ('005064', '家用电器'),
    ('159732', '消费电子ETF'),
    ('001469', '金融地产'),
    ('159940', '金融地产场内'),
    ('012874', '证券指数'),
    ('005663', '金融精选'),
    ('161029', '银行指数'),
    ('006697', '华宝银行'),
    ('512800', '银行场内'),
    ('512880', '证券ETF'),
    ('018099', '保险'),
    ('010365', '香港银行'),
    ('015896', '化工指数'),
    ('159870', '化工ETF'),
    ('005224', '基建工程'),
    ('516970', '基建场内'),
    ('014415', '畜牧养殖'),
    ('516670', '畜牧场内'),
    ('010770', '天弘农业'),
    ('512620', '农业场内'),
    ('008190', '钢铁'),
    ('515210', '钢铁场内'),
    ('008280', '煤炭'),
    ('515220', '煤炭场内'),
    ('008987', '上海金'),
    ('518600', '金场内'),
    ('165520', '800有色'),
    ('018853', '标普石油'),
    ('100039', '通胀通缩'),
    ('007786', '一带一路'),
    ('515150', '一带一路场内'),
    ('011036', '稀土产业'),
    ('159698', '粮食场内'),
    ('021087', '粮食产业'),
    ('020904', '工程机械'),
    ('560280', '工程机械场内'),
    ('161715', '大宗商品'),
    ('270023', '全球精选'),
    ('017731', '全球产业升级'),
    ('005698', '全球科技先锋'),
    ('018230', '全球优质企业'),
    ('100055', '全球科技互联网'),
    ('016702', '海外量化'),
    ('000043', '美国成长'),
    ('040046', '纳斯达克'),
    ('006479', '广发纳斯达克'),
    ('018147', '新兴市场'),
    ('008254', '华宝致远'),
    ('006328', '中概互联网'),
    ('513050', '中概互联网ETF'),
    ('000979', '港股深'),
    ('005555', '恒生国企ETF'),
    ('159954', '恒生国企场内'),
    ('013402', '恒生科技'),
    ('014674', '港股通互联网'),
    ('159792', '港股通互联网场内'),
    ('020969', '全球商品QDII'),
    ('012769', '动漫游戏'),
    ('159869', '动漫游戏场内'),
    ('004753', '传媒'),
    ('512980', '传媒场内'),
    ('000390', '华商优势'),
    ('166301', '华商新趋势'),
    ('720001', '财通价值动量'),
    ('001170', '宏利复兴'),
    ('001412', '德邦鑫星'),
    ('001438', '瑞享灵活'),
    ('001048', '新兴产业'),
    ('025942', '广发新动力'),
    ('002163', '东方惠新'),
    ('001194', '稳健回报'),
]
ETF_CODES=set(['159201', '159206', '159326', '159608', '159611', '159698', '159732', '159736', '159755', '159792', '159852', '159869', '159870', '159892', '159928', '159940', '159952', '159954', '159998', '510300', '512010', '512560', '512620', '512690', '512800', '512880', '512980', '513050', '515120', '515150', '515210', '515220', '515250', '515880', '516100', '516290', '516670', '516970', '518600', '560280', '560770', '560880', '561980', '562930', '562990', '588000', '588080', '588160'])
MACRO={"上证50":"510050","沪深300":"510300","科创50":"588000","创业板":"159915","QQQ":"QQQ","VOO":"VOO"}

SESSION=requests.Session(); SESSION.headers.update(HEAD)

@st.cache_data(ttl=900,show_spinner=False)
def http_get(url,params=None,timeout=15,referer=None):
    """统一网络通道：短超时 + 3次重试，失败尽快切换下一数据源。"""
    last=None
    headers=dict(HEAD)
    if referer:
        headers["Referer"]=referer
    for attempt in range(3):
        try:
            r=SESSION.get(url,params=params,headers=headers,timeout=timeout)
            r.raise_for_status()
            return r
        except Exception as e:
            last=e
            if attempt<2:
                time.sleep(0.35*(2**attempt))
    raise RuntimeError(f"通道请求失败（已重试3次）: {last}")

@st.cache_data(ttl=86400,show_spinner=False)
def fund_hist(code):
    """开放式基金历史净值：主通道 pingzhongdata，备用 F10 JSON，再备用 F10 HTML。"""
    code=str(code).zfill(6); errors=[]
    # 通道1：pingzhongdata JS
    try:
        r=http_get(f"https://fund.eastmoney.com/pingzhongdata/{code}.js",{"v":int(time.time()*1000)},timeout=12)
        m=re.search(r"Data_netWorthTrend\s*=\s*(\[[\s\S]*?\]);",r.text)
        if m:
            rows=[]
            for z in json.loads(m.group(1)):
                try: rows.append((pd.to_datetime(int(z["x"]),unit="ms"),float(z["y"])))
                except: pass
            if len(rows)>=40:
                return pd.DataFrame(rows,columns=["date","close"]).set_index("date").sort_index().assign(volume=np.nan)
        errors.append("pingzhongdata无有效历史")
    except Exception as e: errors.append(f"pingzhongdata:{e}")
    # 通道2：F10 JSON 历史净值
    try:
        p={"fundCode":code,"pageIndex":1,"pageSize":500,"startDate":"","endDate":"","_":int(time.time()*1000)}
        r=http_get("https://api.fund.eastmoney.com/f10/lsjz",p,timeout=12,referer="https://fundf10.eastmoney.com/")
        z=r.json(); rows=[]
        for item in ((z.get("Data") or {}).get("LSJZList") or []):
            try: rows.append((pd.to_datetime(item["FSRQ"]),float(item["DWJZ"])))
            except: pass
        if len(rows)>=40:
            return pd.DataFrame(rows,columns=["date","close"]).set_index("date").sort_index().assign(volume=np.nan)
        errors.append(f"F10 JSON仅{len(rows)}条")
    except Exception as e: errors.append(f"F10 JSON:{e}")
    # 通道3：F10DataApi HTML 表格
    try:
        p={"type":"lsjz","code":code,"page":1,"per":200}
        r=http_get("https://fund.eastmoney.com/f10/F10DataApi.aspx",p,timeout=12,referer="https://fundf10.eastmoney.com/")
        dates=re.findall(r'<td>(\d{4}-\d{2}-\d{2})</td>\s*<td class="tor bold">([0-9.]+)</td>',r.text)
        rows=[(pd.to_datetime(d),float(v)) for d,v in dates]
        if len(rows)>=40:
            return pd.DataFrame(rows,columns=["date","close"]).set_index("date").sort_index().assign(volume=np.nan)
        errors.append(f"F10 HTML仅{len(rows)}条")
    except Exception as e: errors.append(f"F10 HTML:{e}")
    raise RuntimeError("基金历史数据3通道全部失败："+" | ".join(errors[-3:]))

@st.cache_data(ttl=86400,show_spinner=False)
def etf_hist(code):
    """ETF历史K线多通道：东财双节点 → 腾讯 → 新浪 → 基金净值 → Yahoo。"""
    code=str(code).zfill(6); errors=[]
    secid=("1."+code) if code.startswith(("5","6","68")) else ("0."+code)
    p={"secid":secid,"fields1":"f1,f2,f3,f4,f5,f6","fields2":"f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61","klt":"101","fqt":"1","beg":"0","end":"20500101","lmt":"500"}
    for endpoint in ["https://push2his.eastmoney.com/api/qt/stock/kline/get","https://push2.eastmoney.com/api/qt/stock/kline/get"]:
        try:
            j=http_get(endpoint,p,timeout=10).json(); ks=((j.get("data") or {}).get("klines") or [])
            rows=[]
            for item in ks:
                z=item.split(",")
                try: rows.append({"date":z[0],"open":float(z[1]),"close":float(z[2]),"high":float(z[3]),"low":float(z[4]),"volume":float(z[5])})
                except: pass
            if len(rows)>=40: return pd.DataFrame(rows)
            errors.append(f"{endpoint.split('//')[1].split('/')[0]}仅{len(rows)}条")
        except Exception as e: errors.append(f"东财:{e}")
    # 腾讯日K
    try:
        tq=("sh" if code.startswith(("5","6","68")) else "sz")+code
        url="https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
        r=http_get(url,{"_var":"kline_dayqfq","param":f"{tq},day,,,{500},qfq"},timeout=10,referer="https://finance.qq.com/")
        raw=r.text; raw=raw[raw.find("=")+1:] if "=" in raw else raw
        z=json.loads(raw); d=((z.get("data") or {}).get(tq) or {}); arr=d.get("qfqday") or d.get("day") or []
        rows=[]
        for a in arr:
            try: rows.append({"date":a[0],"open":float(a[1]),"close":float(a[2]),"high":float(a[3]),"low":float(a[4]),"volume":float(a[5])})
            except: pass
        if len(rows)>=40: return pd.DataFrame(rows)
        errors.append(f"腾讯K线仅{len(rows)}条")
    except Exception as e: errors.append(f"腾讯K线:{e}")
    # 新浪日K
    try:
        sg=("sh" if code.startswith(("5","6","68")) else "sz")+code
        r=http_get("https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData",{"symbol":sg,"scale":240,"ma":"no","datalen":1023},timeout=10,referer="https://finance.sina.com.cn/")
        arr=r.json(); rows=[]
        for a in arr:
            try: rows.append({"date":a["day"],"open":float(a["open"]),"close":float(a["close"]),"high":float(a["high"]),"low":float(a["low"]),"volume":float(a["volume"])})
            except: pass
        if len(rows)>=40: return pd.DataFrame(rows)
        errors.append(f"新浪K线仅{len(rows)}条")
    except Exception as e: errors.append(f"新浪K线:{e}")
    try:
        d=fund_hist(code)
        if len(d)>=40: return d
    except Exception as e: errors.append(f"基金净值:{e}")
    suffix=".SS" if code.startswith(("5","6","68")) else ".SZ"
    try:
        d=yahoo_hist(code+suffix)
        if len(d)>=40: return d
    except Exception as e: errors.append(f"Yahoo:{e}")
    raise RuntimeError("ETF历史数据5通道全部失败："+" | ".join(errors[-5:]))

@st.cache_data(ttl=300,show_spinner=False)
def fund_rt(code):
    code=str(code).zfill(6); errors=[]
    # 天天基金估值
    try:
        r=http_get(f"https://fundgz.1234567.com.cn/js/{code}.js",{"rt":int(time.time()*1000)},timeout=8)
        m=re.search(r"jsonpgz\((.*)\)",r.text)
        if m:
            z=json.loads(m.group(1)); price=float(z["gsz"]) if z.get("gsz") not in (None,"") else np.nan; pct=float(z["gszzl"]) if z.get("gszzl") not in (None,"") else np.nan
            return {"price":price,"pct":pct,"time":z.get("gztime","")}
        errors.append("天天基金无返回")
    except Exception as e: errors.append(f"天天基金:{e}")
    # 腾讯基金基础净值兜底：用于最新值/涨跌，字段随基金类型可能缺失，所以只在可解析时使用
    try:
        r=http_get(f"https://qt.gtimg.cn/q=jj{code}",timeout=8,referer="https://fund.qq.com/")
        txt=r.content.decode("gbk",errors="ignore"); m=re.search(r'="(.*?)"',txt)
        if m:
            a=m.group(1).split("~"); nums=[]
            for v in a:
                try: nums.append(float(v))
                except: nums.append(np.nan)
            vals=[v for v in nums if pd.notna(v) and v>0]
            if vals:
                price=vals[-1]
                return {"price":price,"pct":np.nan,"time":"腾讯基金兜底"}
        errors.append("腾讯基金无可用净值")
    except Exception as e: errors.append(f"腾讯基金:{e}")
    raise RuntimeError("基金实时估值2通道失败："+" | ".join(errors))

@st.cache_data(ttl=180,show_spinner=False)
def tencent_quote(code):
    code=str(code).zfill(6); sym=("sh" if code.startswith(("5","6","68")) else "sz")+code
    r=http_get("https://qt.gtimg.cn/q="+sym,timeout=8,referer="https://finance.qq.com/")
    txt=r.content.decode("gbk",errors="ignore"); m=re.search(r'="(.*?)"',txt)
    if not m: raise RuntimeError("腾讯行情无返回")
    a=m.group(1).split("~")
    if len(a)<33: raise RuntimeError("腾讯行情字段不足")
    price=float(a[3]); pct=float(a[32])
    return {"price":price,"pct":pct}

@st.cache_data(ttl=180,show_spinner=False)
def sina_quote(code):
    code=str(code).zfill(6); sym=("sh" if code.startswith(("5","6","68")) else "sz")+code
    r=http_get("https://hq.sinajs.cn/list="+sym,timeout=8,referer="https://finance.sina.com.cn/")
    txt=r.content.decode("gbk",errors="ignore"); m=re.search(r'="(.*?)"',txt)
    if not m: raise RuntimeError("新浪行情无返回")
    a=m.group(1).split(",")
    if len(a)<4: raise RuntimeError("新浪行情字段不足")
    return {"price":float(a[3]),"pct":(float(a[3])-float(a[2]))/float(a[2])*100 if float(a[2]) else np.nan}

@st.cache_data(ttl=180,show_spinner=False)
def etf_rt(code):
    code=str(code).zfill(6); errors=[]; secid=("1."+code) if code.startswith(("5","6","68")) else ("0."+code)
    try:
        z=(http_get("https://push2.eastmoney.com/api/qt/stock/get",{"secid":secid,"fields":"f43,f58,f169,f170"},timeout=8).json().get("data") or {})
        if z: return {"price":float(z["f43"]),"pct":float(z["f170"])/100,"channel":"东方财富"}
        errors.append("东财无返回")
    except Exception as e: errors.append(f"东财:{e}")
    try:
        z=tencent_quote(code); z["channel"]="腾讯"; return z
    except Exception as e: errors.append(f"腾讯:{e}")
    try:
        z=sina_quote(code); z["channel"]="新浪"; return z
    except Exception as e: errors.append(f"新浪:{e}")
    raise RuntimeError("ETF实时3通道失败："+" | ".join(errors))

@st.cache_data(ttl=21600,show_spinner=False)
def yahoo_hist(sym):
    end=int(time.time()); start=end-370*86400
    r=http_get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}",{"period1":start,"period2":end,"interval":"1d","events":"history"})
    z=(r.json().get("chart") or {}).get("result") or []
    if not z: raise RuntimeError("Yahoo无数据")
    z=z[0]; q=z["indicators"]["quote"][0]; d=pd.to_datetime(z["timestamp"],unit="s")
    out=pd.DataFrame({"close":q["close"],"volume":q.get("volume")},index=d).dropna(subset=["close"])
    if len(out)<40: raise RuntimeError("Yahoo历史数据不足40条")
    return out

def indicators(d):
    x=d.copy(); c=pd.to_numeric(x["close"],errors="coerce").astype(float)
    x["MA5"]=c.rolling(5).mean(); x["MA20"]=c.rolling(20).mean(); x["MA60"]=c.rolling(60).mean(); x["MA120"]=c.rolling(120).mean()
    de=c.diff(); g=de.clip(lower=0).rolling(14).mean(); l=(-de.clip(upper=0)).rolling(14).mean(); x["RSI"]=100-100/(1+g/l.replace(0,np.nan))
    e12=c.ewm(span=12,adjust=False).mean(); e26=c.ewm(span=26,adjust=False).mean(); x["MACD"]=e12-e26; x["SIGNAL"]=x.MACD.ewm(span=9,adjust=False).mean(); x["HIST"]=x.MACD-x.SIGNAL
    x["RET20"]=c.pct_change(20)*100; x["RET60"]=c.pct_change(60)*100; x["DD"]=(c/c.cummax()-1)*100
    mid=c.rolling(20).mean(); sd=c.rolling(20).std(); x["BB_POS"]=(c-(mid-2*sd))/(4*sd)*100; x["VOL"]=c.pct_change().rolling(20).std()*math.sqrt(252)*100
    x["MA20_SLOPE"]=x.MA20.pct_change(5)*100; x["MA60_SLOPE"]=x.MA60.pct_change(10)*100
    x["MA_GOLDEN"]=(x.MA5>x.MA20)&(x.MA5.shift(1)<=x.MA20.shift(1)); x["MA_DEAD"]=(x.MA5<x.MA20)&(x.MA5.shift(1)>=x.MA20.shift(1))
    x["MACD_GOLDEN"]=(x.MACD>x.SIGNAL)&(x.MACD.shift(1)<=x.SIGNAL.shift(1)); x["MACD_DEAD"]=(x.MACD<x.SIGNAL)&(x.MACD.shift(1)>=x.SIGNAL.shift(1))
    x["MA_GOLDEN_10D"]=x.MA_GOLDEN.rolling(10).max().fillna(False).astype(bool)
    x["MACD_GOLDEN_10D"]=x.MACD_GOLDEN.rolling(10).max().fillna(False).astype(bool)
    return x

def score(x):
    """严格版多指标评分：100分制，且买入信号有硬性门槛，避免仅靠金叉/短期动量就误判。"""
    r=x.iloc[-1]; s=0; why=[]; risk=[]
    def add(cond, pts, good):
        nonlocal s
        if pd.notna(cond) and bool(cond): s += pts; why.append(good)

    # 1) 趋势 35 分：必须尽量站在中长期趋势之上
    add(r.close>r.MA20,6,"价格站上MA20")
    add(r.MA20>r.MA60,7,"MA20>MA60")
    add(r.close>r.MA60,5,"价格站上MA60")
    add(r.MA60>r.MA120,4,"MA60>MA120")
    add(r.close>r.MA120,3,"价格站上MA120")
    add(r.MA20_SLOPE>0,5,"MA20向上")
    add(r.MA60_SLOPE>0,5,"MA60向上")

    # 2) 动量 20 分：短中期都要有确认
    add(r.RET20>0,5,"20日动量为正")
    add(r.RET20>3,3,"20日动量>3%")
    add(r.RET60>0,5,"60日动量为正")
    add(r.RET60>5,3,"60日动量>5%")

    # 3) MACD 20 分：不仅看多头，还看零轴与柱体改善
    add(r.MACD>r.SIGNAL,6,"MACD多头")
    add(r.MACD>0,4,"MACD在零轴上方")
    hist_rising = len(x)>=2 and pd.notna(x.HIST.iloc[-1]) and pd.notna(x.HIST.iloc[-2]) and x.HIST.iloc[-1]>x.HIST.iloc[-2]
    if hist_rising: s+=5; why.append("MACD柱体改善")
    if bool(r.MACD_GOLDEN_10D): s+=5; why.append("10日内MACD金叉")

    # 4) RSI 15 分：健康区间优先，极端高位严禁追涨
    if pd.notna(r.RSI):
        if 52<=r.RSI<=68: s+=15; why.append("RSI健康52-68")
        elif 48<=r.RSI<52: s+=10; why.append("RSI接近健康区")
        elif 68<r.RSI<=72: s+=7; why.append("RSI偏强但可控")
        elif r.RSI>72: risk.append("RSI过热")
        elif r.RSI<35: s+=3; why.append("RSI超跌，需等待确认")

    # 5) 风险/位置 10 分：避免追高与异常波动
    if pd.notna(r.DD):
        if -12<=r.DD<=-3: s+=5; why.append("回撤区间较适合分批")
        elif r.DD>-3: risk.append("距离高点过近，追高风险")
        elif r.DD<-20: risk.append("回撤过大")
        else: s+=2; why.append("回撤可接受")
    if pd.notna(r.VOL):
        if r.VOL<30: s+=5; why.append("波动率较低")
        elif r.VOL>45: risk.append("波动率偏高")
        else: s+=2

    # 硬性否决/扣分
    if bool(r.MA_DEAD): s-=10; risk.append("MA死叉")
    if bool(r.MACD_DEAD): s-=10; risk.append("MACD死叉")
    if pd.notna(r.RSI) and r.RSI>72: s-=10
    if pd.notna(r.RET60) and r.RET60<-8: s-=8; risk.append("60日趋势明显偏弱")
    if pd.notna(r.RET20) and r.RET20<-8: s-=6; risk.append("20日动量明显偏弱")

    s=max(0,min(100,round(s)))
    return s,"、".join(why),risk

def classify(x,s):
    r=x.iloc[-1]
    ma_trend=bool(pd.notna(r.close) and pd.notna(r.MA20) and pd.notna(r.MA60) and r.close>r.MA20>r.MA60)
    macd_ok=bool(pd.notna(r.MACD) and pd.notna(r.SIGNAL) and r.MACD>r.SIGNAL)
    rsi_ok=bool(pd.notna(r.RSI) and 48<=r.RSI<=68)
    mom_ok=bool(pd.notna(r.RET20) and r.RET20>0 and pd.notna(r.RET60) and r.RET60>0)
    no_dead=not bool(r.MA_DEAD or r.MACD_DEAD)
    not_overheat=not (pd.notna(r.RSI) and r.RSI>72)
    strong=ma_trend and macd_ok and rsi_ok and mom_ok and no_dead and not_overheat and s>=82
    add=ma_trend and macd_ok and pd.notna(r.RSI) and 45<=r.RSI<=65 and pd.notna(r.RET60) and r.RET60>0 and no_dead and s>=75
    if strong: return "🟢 强买入", "趋势+MACD+RSI+20/60日动量同时确认"
    if add: return "🟡 回调加仓", "中期趋势未坏，适合等待回调分批"
    if s>=70: return "🔵 观察", "技术面偏强，但尚未达到严格买入门槛"
    if s>=55: return "⚪ 持有/等待", "趋势一般，等待更多确认"
    if s>=45: return "🟠 减仓/观望", "技术面偏弱或风险上升"
    return "🔴 高风险/回避", "多项指标未通过"

def load_items():
    p=ROOT/"fund_codes.csv"
    if not p.exists(): return BUILTIN_FUNDS.copy()
    try:
        d=pd.read_csv(p,dtype=str); cc=next((c for c in d.columns if c.lower() in ("code","代码")),None); nc=next((c for c in d.columns if c.lower() in ("name","名称")),None)
        if not cc: return BUILTIN_FUNDS.copy()
        out=[]
        for _,row in d.iterrows():
            c=str(row[cc]).strip()
            if c and c.lower()!="nan": out.append((c,str(row[nc]).strip() if nc else c))
        return out or BUILTIN_FUNDS.copy()
    except: return BUILTIN_FUNDS.copy()

def get_data(code):
    code=str(code).strip()
    if re.fullmatch(r"\d{6}",code):
        return (etf_hist(code),"东方财富ETF K线") if code in ETF_CODES else (fund_hist(code),"东方财富历史净值")
    return yahoo_hist(code),"Yahoo Finance"

def process_one(code,name):
    out={"代码":code,"名称":name,"状态":"失败","错误":""}
    try:
        d,source=get_data(code)
        if len(d)<30: raise RuntimeError("历史数据不足30条")
        x=indicators(d); r=x.iloc[-1]; s,why,risk=score(x); latest=float(r.close); pct=float((r.close/x.close.iloc[-2]-1)*100)
        try:
            rt=etf_rt(code) if code in ETF_CODES else fund_rt(code) if re.fullmatch(r"\d{6}",code) else None
        except: rt=None
        if rt and pd.notna(rt.get("price")):
            latest=float(rt["price"]); pct=float(rt["pct"]) if pd.notna(rt.get("pct")) else pct
        level,level_reason=classify(x,s)
        out.update({"状态":"正常","数据源":source,"实时通道":rt.get("channel", "天天基金") if rt else "历史数据", "最新值":round(latest,4),"涨跌%":round(pct,2),"评分":s,"买入等级":level,"等级说明":level_reason,"RSI":round(float(r.RSI),2) if pd.notna(r.RSI) else np.nan,"MA5/20":"金叉" if bool(r.MA_GOLDEN) else ("多头" if r.MA5>r.MA20 else "空头"),"MACD":"金叉" if bool(r.MACD_GOLDEN) else ("多头" if r.MACD>r.SIGNAL else "空头"),"MA20趋势":"向上" if pd.notna(r.MA20_SLOPE) and r.MA20_SLOPE>0 else "向下","20日动量%":round(float(r.RET20),2) if pd.notna(r.RET20) else np.nan,"60日动量%":round(float(r.RET60),2) if pd.notna(r.RET60) else np.nan,"回撤%":round(float(r.DD),2) if pd.notna(r.DD) else np.nan,"布林位置%":round(float(r.BB_POS),2) if pd.notna(r.BB_POS) else np.nan,"年化波动%":round(float(r.VOL),2) if pd.notna(r.VOL) else np.nan,"建议":level,"共振理由":why,"风险提示":"、".join(risk) if risk else "暂无明显风险"})
    except Exception as e: out["错误"]=str(e)
    return out

@st.cache_data(ttl=21600,show_spinner=False)
def macro_one(n,c):
    try:
        d=yahoo_hist(c) if c in ("QQQ","VOO") else (etf_hist(c) if c in ETF_CODES else fund_hist(c)); x=indicators(d); s,_,_=score(x)
        return {"名称":n,"评分":s,"建议":"多头" if s>=70 else ("中性" if s>=50 else "偏弱")}
    except Exception as e:
        return {"名称":n,"评分":np.nan,"建议":"数据失败","错误":str(e)}

@st.cache_data(ttl=21600,show_spinner=False)
def macro_snapshot():
    with ThreadPoolExecutor(max_workers=6) as ex:
        return pd.DataFrame(list(ex.map(lambda kv: macro_one(*kv), MACRO.items())))

def channel_probe():
    """从当前部署服务器实测主要数据通道；用于排查云端网络/接口波动。"""
    tests=[
        ("东方财富 ETF K线", "https://push2his.eastmoney.com/api/qt/stock/kline/get", {"secid":"1.510300","fields1":"f1,f2,f3,f4,f5,f6","fields2":"f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61","klt":"101","fqt":"1","beg":"0","end":"20500101","lmt":"60"}),
        ("东方财富 ETF实时", "https://push2.eastmoney.com/api/qt/stock/get", {"secid":"1.510300","fields":"f43,f58,f169,f170"}),
        ("天天基金估值", "https://fundgz.1234567.com.cn/js/001549.js", {"rt":int(time.time()*1000)}),
        ("东方财富基金历史", "https://fund.eastmoney.com/pingzhongdata/001549.js", {"v":int(time.time()*1000)}),
        ("腾讯 ETF实时", "https://qt.gtimg.cn/q=sh510300", None),
        ("新浪 ETF实时", "https://hq.sinajs.cn/list=sh510300", None),
        ("Yahoo ETF历史", "https://query1.finance.yahoo.com/v8/finance/chart/510300.SS", {"period1":int(time.time())-90*86400,"period2":int(time.time()),"interval":"1d"}),
    ]
    out=[]
    for name,url,params in tests:
        t=time.time()
        try:
            r=http_get(url,params,timeout=6)
            ok=len(r.content)>20
            out.append({"通道":name,"状态":"🟢 通畅" if ok else "🟠 有响应但内容异常","耗时(秒)":round(time.time()-t,2),"HTTP":r.status_code,"返回字节":len(r.content),"错误":""})
        except Exception as e:
            out.append({"通道":name,"状态":"🔴 失败","耗时(秒)":round(time.time()-t,2),"HTTP":"-","返回字节":0,"错误":str(e)[:160]})
    return pd.DataFrame(out)

with st.sidebar:
    st.header("📡 V9.2 · 153只基金 · 多通道加速版")
    if st.button("🔄 立即刷新全部数据",use_container_width=True): st.cache_data.clear(); st.rerun()
    if st.button("🧪 测试数据通道是否通畅",use_container_width=True):
        st.session_state["channel_probe"]=channel_probe()
    search=st.text_input("搜索代码/名称")
    threshold=st.slider("最低技术评分",0,100,60,5)
    signal=st.selectbox("信号筛选",["全部","🟢 强买入","🟡 回调加仓","🔵 观察","⚪ 持有/等待","🟠 减仓/观望","🔴 高风险/回避","金叉","多头"])
    st.caption("自动刷新：15分钟。历史数据采用多通道：东方财富→F10→腾讯→新浪→Yahoo；实时数据采用东方财富→腾讯→新浪备用。并发8路，历史缓存24小时。")
    if "channel_probe" in st.session_state:
        st.success("通道测试完成：下面主页面会显示详细结果。")
try:
    from streamlit_autorefresh import st_autorefresh; st_autorefresh(interval=900000,key="v91_auto15")
except: pass

items=load_items()
if len(items)<153: items=BUILTIN_FUNDS.copy()
if len({c for c,_ in items}) < 153: items=BUILTIN_FUNDS.copy()
st.title("📡 基金智能监控雷达 PRO MAX V9.2")
if "channel_probe" in st.session_state:
    with st.expander("🧪 最近一次数据通道实测结果",expanded=True):
        st.dataframe(st.session_state["channel_probe"],use_container_width=True,hide_index=True)
st.caption("153只基金 · 多通道加速稳定版：东方财富 / F10 / 腾讯 / 新浪 / Yahoo 多源备用 · 严格多指标共振：趋势 + MACD + RSI + 20/60日动量 + 回撤 + 波动率 · 买入信号采用硬性门槛")

st.subheader("🌍 大环境 / QQQ / VOO")
mc=st.columns(6)
try:
    md=macro_snapshot()
    for col,(_,row) in zip(mc,md.iterrows()): col.metric(row["名称"],"—" if pd.isna(row["评分"]) else int(row["评分"]),row["建议"])
except: pass

st.subheader("🔥 今日决策中心")
bar=st.progress(0,f"正在获取{len(items)}只基金数据……"); rows=[]
with ThreadPoolExecutor(max_workers=8) as ex:
    fs=[ex.submit(process_one,c,n) for c,n in items]
    for i,f in enumerate(as_completed(fs),1):
        try: rows.append(f.result())
        except Exception as e: rows.append({"代码":"?","名称":"未知","状态":"失败","错误":str(e)})
        bar.progress(i/max(1,len(fs)),f"正在获取 {i} / {len(fs)}")
bar.empty()
df=pd.DataFrame(rows)
if df.empty: st.error("没有读取到任何基金数据。")
else:
    ok=df[df["状态"]=="正常"].copy(); view=ok.copy()
    if search:
        q=search.lower().strip(); view=view[view.apply(lambda r:q in str(r["代码"]).lower() or q in str(r["名称"]).lower(),axis=1)]
    if signal!="全部":
        if signal=="金叉": view=view[(view["MA5/20"]=="金叉")|(view["MACD"]=="金叉")]
        elif signal=="多头": view=view[(view["MA5/20"].isin(["金叉","多头"]))&(view["MACD"].isin(["金叉","多头"]))]
        else: view=view[view["买入等级"]==signal]
    view=view.sort_values(["评分","20日动量%"],ascending=False)
    strong=ok[ok["买入等级"]=="🟢 强买入"]
    add=ok[ok["买入等级"]=="🟡 回调加仓"]
    watch=ok[ok["买入等级"]=="🔵 观察"]
    a,b,c,d,e,f=st.columns(6)
    a.metric("监控品种",len(items)); b.metric("数据正常",len(ok)); c.metric("🟢 强买入",len(strong)); d.metric("🟡 回调加仓",len(add)); e.metric("🔵 观察",len(watch)); f.metric("数据失败",len(df)-len(ok))

    # 顶部两个快捷入口：点击后只看真正严格信号
    q1,q2,q3=st.columns(3)
    with q1:
        if st.button(f"🟢 强买入（{len(strong)}）",use_container_width=True):
            st.session_state["quick_filter"]="🟢 强买入"
    with q2:
        if st.button(f"🟡 回调加仓（{len(add)}）",use_container_width=True):
            st.session_state["quick_filter"]="🟡 回调加仓"
    with q3:
        if st.button(f"🔵 观察（{len(watch)}）",use_container_width=True):
            st.session_state["quick_filter"]="🔵 观察"
    qf=st.session_state.get("quick_filter")
    if qf:
        st.info(f"当前快捷查看：{qf} · 下面只显示这一类基金")
        view=ok[ok["买入等级"]==qf].sort_values(["评分","20日动量%"],ascending=False)

    cols=["代码","名称","最新值","涨跌%","评分","买入等级","RSI","MA5/20","MACD","MA20趋势","20日动量%","60日动量%","回撤%","年化波动%","等级说明","风险提示"]
    st.dataframe(view[view["评分"]>=threshold][[c for c in cols if c in view.columns]],use_container_width=True,hide_index=True,column_config={"评分":st.column_config.ProgressColumn("技术评分",min_value=0,max_value=100,format="%d")})

with st.expander("📡 数据通道说明 / 本轮实际使用通道"):
    st.markdown("**历史：** 东方财富 pingzhongdata / F10 JSON / F10 HTML；ETF额外启用东方财富K线双节点、腾讯K线、新浪K线、Yahoo。\n\n**实时：** 开放式基金优先天天基金，失败后腾讯基金兜底；ETF优先东方财富，失败后腾讯、再新浪。\n\n**加速：** 153只基金并发提升到8路；历史数据缓存24小时，实时数据缓存3–5分钟。")
    if not df.empty and "实时通道" in df.columns:
        st.dataframe(df["实时通道"].value_counts().rename_axis("通道").reset_index(name="数量"),use_container_width=True,hide_index=True)

with st.expander(f"⚠️ 数据源诊断（失败 {len(df[df['状态']!='正常']) if not df.empty else 0} 个）"):
    bad=df[df["状态"]!="正常"] if not df.empty else pd.DataFrame()
    if not bad.empty: st.dataframe(bad[["代码","名称","错误"]],use_container_width=True,hide_index=True)
    else: st.success("本轮153只基金全部成功获取。")
st.caption(f"V9.2 多通道加速版 · 内置153只基金 · 历史缓存24小时 / 实时缓存3-5分钟 · 最后刷新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} · 信号仅作辅助，不构成投资建议")

