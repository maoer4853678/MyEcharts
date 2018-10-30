#coding=utf-8
import os
import json
import numpy as np
import pandas as pd
import shutil
from IPython.display import SVG,HTML

#######################################################################
## 通用函数
def siplitlist(listx,n,axis = 0):
    u'''
    listx: 待分组序列，类型可以是list，np.array,pd.Series...
    n: 若axis=0 n为组别个数,计算生成元素个数,若axis=1 n为每组元素个数,计算生成组别个数
    axis: 若axis=0 按照固定组别个数分组, 若axis=1 按照固定元素个数分组
    '''
    if axis ==0:
        a1,a2 = divmod(len(listx),n)
        N = [a1]*(n-a2)+[a1+1]*a2 if a1!=0 else [1]*len(listx)
        res = [listx[s:s+i] for s,i in enumerate(N) if len(listx[s:s+i])!=0]
    else:
        N = int(len(listx)/n)+1
        res = [listx[i*n:(i+1)*n] for i in range(N) if len(listx[i*n:(i+1)*n])!=0]
    return res
    
def get_template(template):
    with open("template/%s.html"%template,"r") as  f:
        template = f.read()
    return template

def creat_html(template,root,name,width = "900px",height = '600px'):
    ## name中的 特殊字符处理
    for i in '? * : " < > \ / |'.split(' '):
        name = name.replace(i,'')
    name= name.strip()
    if not os.path.exists(root):
        os.makedirs(root)
    jspath = os.path.join(os.path.dirname(root),"js")
    if not os.path.exists(jspath): ## root 所在的根目录没有js文件夹，则将js 文件夹拷贝至此目录下
        shutil.copytree('./js', jspath)
    else: ## 若存在js文件不全的情况下单独拷贝文件
        for i in os.listdir('./js'):
            dstFilePath = os.path.join(jspath,i)
            if not os.path.exists(dstFilePath):
                shutil.copyfile('./js/'+i,dstFilePath)    
    with open("%s/%s.html"%(root,name),"w") as  f:
        f.write(template)
    msg = '<iframe src="%s.html" width="%s" height="%s" frameborder="0" scrolling="no"> </iframe>'%(os.path.join(root,name),width,height)
    return msg

#######################################################################
## 时间序列的箱线图
def tbox_map(root,name,alldata,xdata,lines,width,height):
    template = get_template('tbox')
    box = template%(json.dumps(alldata),json.dumps(xdata),json.dumps(lines))    
    return creat_html(box,root,name,width,height) 
      
def Plot_TBox(df,x,y,kind='date',root='Time_series_analysis',name = None,width = "900px",height = '400px',show =True):
    u'''
    按照指定时间窗口绘制 时序Box图，横轴是日期，可选指定变量
    df: 类型 DataFrame
    x: 横轴时间列，df[x].dtype 必须是 datetime64[ns]
    y: 目标变量，df[y].dtype 必须是 int或者float
    type: 时间窗口颗粒度 {date:每天 ,month:每月,year:每年} 默认每天
    root: 离线网页生成所在目录
    name: 离线网页文件名称
    width: Output 时显示宽度
    height: Output 时显示高度
    show: 在网页中显示Output
    Example:
        df = pd.DataFrame(np.random.rand(70,4),columns = ['var1','var2','var3','var4'])
        df['times'] = pd.date_range(start = '2018-01-02 00:00:00',freq = "1D",periods = len(df))
        Plot_TBox(df,'times','var1',kind = 'month',root = "html")
    '''
    df[kind] = eval('df[x].dt.%s'%kind)
    res = df.groupby(kind).apply(lambda x:x[y].values.tolist())
    res =res.sort_index()
    xdata = res.index.astype(str).tolist()
    alldata = res.values.tolist()
    lines = res.map(lambda x:np.percentile(x,50)).values.tolist()
    if not name:
        name = '%s_%s_box'%(kind,y)
    output = tbox_map(root,name,alldata,xdata,lines,width,height)
    if show:
        return HTML(output)    
    
#######################################################################
## 多变量散点图
def univariate_map(root,name,alldata,column,width,height):
    template = get_template('univariate')
    scatter = template%(json.dumps(alldata),json.dumps(column))
    return creat_html(scatter,root,name,width,height)
        
def Plot_Univariate(df,target,classf=None,varnum = 10,pagenum = None,\
        root='Univariate_analysis',reverse =False,width = "900px",height = '400px',show =True):
    u'''
    Univariate分析
    绘制单变量和目标变量的散点关系图，可以指定每页含有观察变量个数，按照变量顺序生成
    df: 类型 DataFrame
    target: 目标变量
    classf: 可指定类别标签，若指定类别，将自动用颜色分类绘制
    varnum: 在未指定pagenum的情况下，单页显示变量数量
    pagenum: 生成网页数量，若指定pagenum，将优先按照pagenum 进行变量分组
    root: 离线网页生成所在目录
    width: Output 时显示宽度
    height: Output 时显示高度
    show: 在网页中显示Output
    Example:
        df = pd.DataFrame(np.random.rand(50,4),columns = ['var1','var2','var3','target'])
        df['class'] = ['A']*25+['B']*25
        Plot_Univariate(df,'target','class',root = "html")
    '''
    df.index = range(len(df))
    temp = df.drop([target,classf],axis =1) if classf else df.drop([target],axis =1)
    all_columns = temp.columns.tolist()
    ## 根据varnum 和 pagenum 进行变量分组
    columns = siplitlist(all_columns,pagenum,0) if pagenum else siplitlist(all_columns,varnum,1)
    dfs = {}
    if classf:
        for key in df[classf].drop_duplicates():
            dfs[str(key)] = df[df[classf]==key]
    else :
        dfs['all'] = df
    
    for index,column in enumerate(columns):
        alldata ={}
        ## column 为每页所需绘制的变量名称组
        for col in column:
            data= {}
            for temp in dfs: ## temp 是按照classf 区分的不同组别数据
                cols = [target,col] if reverse else [col,target]
                data[temp] = dfs[temp][cols].values.tolist()
            alldata[col] = data
        
        filename = 'Univariate_%d'%(index+1)
        output = univariate_map(root,filename,alldata,column,width,height)
    if show:
        return HTML(output)

#######################################################################
## 箱线图
def Plot_Box(df,columns = None,root = "Box_analysis",\
        name = "box",width = "900px",height = '400px',show =True):
    u'''
    Box箱线图
    绘制多变量(Number) 的Box图
    df: 类型 DataFrame
    columns: 要绘制的变量组[]，默认是None ,即df的全部字段
    root: 离线网页生成所在目录
    name: 文件名称
    width: Output 时显示宽度
    height: Output 时显示高度
    show: 在网页中显示Output
    Example:
        df = pd.DataFrame(np.random.rand(50,4),columns = ['var1','var2','var3','var4'])
        Plot_Box(df,['var1',"var2",'var4'],root = "html")
    '''
    if not columns:
        columns = df.columns.values.tolist()
    
    df1 = df[columns].select_dtypes(exclude = ["object","datetime64[ns]"])    
    data = df1.T.values.tolist()
    xaxis = df1.columns.astype(str).values.tolist()
    template = get_template('box')
    linbar = template%(json.dumps(data),json.dumps(xaxis))
    output = creat_html(linbar,root,name,width,height) 
    if show:
        return HTML(output)
        
        
#######################################################################
## 单变量散点图
def Plot_Scatter(df,x,y,label =None,root = "Scatter_analysis",name = "scatter",\
        width = "900px",height = '400px',show =True):
    u'''
    Scatter分类分析
    绘制变量之间的简单散点关系图
    df: 类型 DataFrame
    x: 变量x ,横轴变量
    y: 变量y ,纵轴变量
    label: 类别标签
    root: 离线网页生成所在目录
    name: 文件名称
    width: Output 时显示宽度
    height: Output 时显示高度
    show: 在网页中显示Output
    Example:
        df = pd.DataFrame(np.random.rand(50,4),columns = ['var1','var2','var3','target'])
        df['class'] = ['A']*25+['B']*25
        Plot_Scatter(df,'var1',"var2",label ='class',root = "html")
    '''
    if label:
        df1 =df[[x,y,label]]
    else :
        df1 =df[[x,y]]
        
    d = {"datetime64[ns]":"time"}
    types = df1[[x,y]].dtypes.astype(str).map(d).fillna("value").values.tolist()
    for i in range(2):
        if types[i]=='time':
            df1[[x,y][i]] = df1[[x,y][i]].astype(str)
    dfs = {}
    if label:
        for key in df1[label].drop_duplicates():
            dfs[str(key)] = df1[df1[label]==key].values.tolist()
    else :
        dfs['all'] = df1.values.tolist()
        
    template = get_template('scatter')
    scatter = template%(json.dumps(dfs),json.dumps(types))
    output = creat_html(scatter,root,name,width,height) 
    if show:
        return HTML(output)
    
#######################################################################
## 线柱图     
def Plot_LineBar(df,columns = None,kind = "line",root = "LineBar_analysis",\
        name = "Linebar",width = "900px",height = '400px',show =True):
    u'''
    LineBar分类分析
    绘制多变量(Number) 的Line图或Bar图，支持在线切换
    df: 类型 DataFrame
    columns: 要绘制的变量组[]，默认是None ,即df的全部字段
    kind: 默认每个字段绘制的图类型，默认是line型,支持[],针对每个字段定义其图类型 ,
            支持{} ,针对每个字段定义其图类型，{}的key是字段名称,value是line 或者 bar
    root: 离线网页生成所在目录
    name: 文件名称
    width: Output 时显示宽度
    height: Output 时显示高度
    show: 在网页中显示Output
    Example:
        df = pd.DataFrame(np.random.rand(50,4),columns = ['var1','var2','var3','var4'])
        df.index= pd.date_range(start = '2018-01-01 00:00:00',freq = "1D",periods = len(df))
        Plot_LineBar(df,['var1',"var2",'var4'],kind =['line','bar','line'],root = "html")
    '''
    curkind = 'line'
    if not columns:
        columns = df.columns
    if isinstance(kind,list):      
        d = dict(zip(columns,kind))
    elif isinstance(kind,dict):
        d = kind
    elif isinstance(kind,str) or isinstance(kind,unicode): 
        d = {}
        curkind = kind
    else:
        d = {}

    df1 = df[columns].select_dtypes(exclude = ["object","datetime64[ns]"])
    
    for col in df1.columns:
        if col not in d.keys():
            d[col] = curkind
    
    data = {}
    for col in df1.columns:
        data[col] = {}
        data[col]['kind'] = d[col]
        data[col]['data'] = df1[col].values.tolist()
    xaxis = df.index.astype(str).values.tolist()
    template = get_template('linbar')
    linbar = template%(json.dumps(data),json.dumps(xaxis))
    output = creat_html(linbar,root,name,width,height) 
    if show:
        return HTML(output)
    
#######################################################################
## 分布图
def hist_map(g,bins,scale = False):
    temp = g.values.tolist()
    temp = g.groupby(pd.cut(g,bins= bins)).apply(len)
    def index_map(s):
        try:
            t = (s.left+s.right)/2.0
        except:
            t = eval(s.replace("(","["))
            t= sum(t)/float(len(t))
        return t
    temp.index.name = ''
    temp.index = temp.index.map(index_map)
    if scale:
        temp = temp/float(temp.max())
    return temp.reset_index().values.tolist()

def Plot_Hist(df,columns = None,bins = 10,scale = False,root = "Hist_analysis",name = "hist",\
        width = "900px",height = '400px',show =True):
    u'''
    Hist分布图
    绘制多变量(Number) 的hist分布图
    df: 类型 DataFrame
    columns: 要绘制的变量组[]，默认是None ,即df的全部字段
    bins: 默认每个字段绘制的图类型，默认是 10,支持[],针对每个字段定义其图类型 ,
            支持{} ,针对每个字段定义其图类型，{}的key是字段名称,value是 bins的值
    scale: Y轴显示归一化显示，默认False, 即按照数量显示
    root: 离线网页生成所在目录
    name: 文件名称
    width: Output 时显示宽度
    height: Output 时显示高度
    show: 在网页中显示Output
    Example:
        df = pd.DataFrame(np.random.rand(3000,4),columns = ['var1','var2','var3','var4'])
        df.index= pd.date_range(start = '2018-01-01 00:00:00',freq = "1D",periods = len(df))
        Plot_Hist(df,columns = ['var1'],bins = {"var1":100},root = "html",scale = True)
    '''
    curkind = 10
    if not columns:
        columns = df.columns
    if isinstance(bins,list):      
        d = dict(zip(columns,bins))
    elif isinstance(bins,dict):
        d = bins
    elif isinstance(bins,int) or isinstance(bins,float): 
        d = {}
        curkind = bins
    else:
        d = {}
    df1 = df[columns].select_dtypes(exclude = ["object","datetime64[ns]"])
    
    for col in df1.columns:
        if col not in d.keys():
            d[col] = curkind
    
    data = {}
    for col in df1.columns:
        data[col] = hist_map(df1[col],d[col],scale)

    template = get_template('hist')
    hist = template%(json.dumps(data))
    output = creat_html(hist,root,name,width,height) 
    if show:
        return HTML(output)

#######################################################################
## 箱线图

def pie_axisdata(columns):
    legend = []
    series = []
    if len(columns) >= 3:
        for x,y, in [['left','10%'],['right','10'],['left','60'],['right','60']][:len(columns)]:
            temp = '''{
                orient: 'vertical',
                %s: '5%%',
                top: '%s',
                data: []
            }'''%(x,y)
            legend.append(temp)
        for x,y, in [['30%','25%'],['65%','25%'],['30%','75%'],['65%','75%']][:len(columns)]:
            temp1 = '''{
            name: '',
            type: 'pie',
            radius : '40%%',
            center: ['%s', '%s'],
            data:[],
            itemStyle: {
                emphasis: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
            }
            }'''%(x,y)
            series.append(temp1)

    elif len(columns) == 2:
        for x,y, in [['left','10%'],['right','10']]:
            temp = '''
            {
                orient: 'vertical',
                %s: '5%%',
                top: '%s',
                data: []
            }
            '''%(x,y)
            legend.append(temp)
        for x,y, in [['30%','50%'],['65%','50%']]:
            temp1 = '''{
            name: '',
            type: 'pie',
            radius : '50%%',
            center: ['%s', '%s'],
            data:[],
            itemStyle: {
                emphasis: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
            }
            }'''%(x,y)
            series.append(temp1)
    else:
        legend.append('''
            {
                orient: 'vertical',
                left: '5%%',
                top: '10%%',
                data: []
            }
        ''')
        series.append('''
        {
            name: '',
            type: 'pie',
            radius : '65%%',
            center: ['50%%', '50%%'],
            data:[],
            itemStyle: {
                emphasis: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
            }
        }
        ''')
    return legend,series

def Plot_Pie(df,columns = None,top = 8,root = "Pie_analysis",\
        name = "pie",width = "900px",height = '400px',show =True):
    u'''
    Box箱线图
    绘制多变量的Pie图,最多支持4个变量同时显示
    df: 类型 DataFrame
    columns: 要绘制的变量组[]，默认是None ,即df的全部字段
    top: 每个变量中最多显示的类别个数，若变量类别多于top数量，剩余类别归为一类 ，标为 其他
    root: 离线网页生成所在目录
    name: 文件名称
    width: Output 时显示宽度
    height: Output 时显示高度
    show: 在网页中显示Output
    Example:
        df = pd.DataFrame([['A']]*25+[['B']]*35,columns = ['var1'])
        df['var2'] = ['a','b','c','d','e','f']*5+['h']*6+['i']*20+['j']*4
        df['var3'] = ['C']*25+['D']*30+['E']*5
        df['var4'] = ['X']*40+['Y']*20
        Plot_Pie(df,['var1',"var2",'var4'],top=6,root = "html")
    '''
    if not columns:
        columns = df.columns.values.tolist()
    columns = columns[:4]
    df1 = df[columns]
    
    legend,series = pie_axisdata(columns)
    
    template = get_template('pie')
    pie = template%(json.dumps(legend),json.dumps(series))
    output = creat_html(pie,root,name,width,height) 
    if show:
        return HTML(output)
        
        
#######################################################################
## 3D散点图        
def Scatter3d_map(df):
    data = df.values.tolist()
    data.insert(0,df.columns.values.tolist())
    return data

def Plot_3DScatter(df,x,y,z,label =None,root = "3DScatter_analysis",name = "3dscatter",\
        width = "900px",height = '400px',show =True):
    u'''
    3DScatter分类分析
    绘制3D散点图
    df: 类型 DataFrame
    x: 变量x ,X轴变量
    y: 变量y ,Y轴变量
    z: 变量z ,Z轴变量
    label: 类别标签
    root: 离线网页生成所在目录
    name: 文件名称
    width: Output 时显示宽度
    height: Output 时显示高度
    show: 在网页中显示Output
    Example:
        df = pd.DataFrame(np.random.rand(100,3),columns = ['var1','var2','var3'])
        df['class'] = ['A']*50+['B']*50
        Plot_3DScatter(df,'var1',"var2","var3",label ='class',root = "html")
    '''
    if label:
        df1 =df[[x,y,z,label]]
    else :
        df1 =df[[x,y,z]]
        
    d = {"datetime64[ns]":"time"}
    types = df1[[x,y,z]].dtypes.astype(str).map(d).fillna("value").values.tolist()
    for i in range(3):
        if types[i]=='time':
            df1[[x,y,z][i]] = df1[[x,y,z][i]].astype(str)
    columns = dict(zip(['X','Y','Z'],[x,y,z]))
    dfs = {}
    if label:
        for key in df1[label].drop_duplicates():
            dfs[str(key)] = Scatter3d_map(df1[df1[label]==key])
    else :
        dfs['all'] = Scatter3d_map(df1)
        
    template = get_template('3dscatter')
    scatter = template%(json.dumps(dfs),json.dumps(types),json.dumps(columns))
    output = creat_html(scatter,root,name,width,height) 
    if show:
        return HTML(output)