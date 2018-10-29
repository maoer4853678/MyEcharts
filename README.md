# MyEcharts
# 基于echarts 工具开发的定制化 分析模板，js采用离线加载方式，好处是加载速度相对较快

API 目录架构
/js
    /dataTool.js
    /dataTool.min.js
    /echarts.js
    /echarts.min.js
    /echarts.sankey.js
    /ecStat.js
    /jquery.js
/templates
    /box.html
    /scatter.html
    /univariate.html
MyEcharts.py


目前支持分析模板及对应函数 
Plot_Box :  绘制基于时间序列的箱线图
Example:
    from MyEcharts import Plot_Box
    df = pd.DataFrame(np.random.rand(70,4),columns = ['var1','var2','var3','var4'])
    df['times'] = pd.date_range(start = '2018-01-02 00:00:00',freq = "1D",periods = len(df))
    Plot_Box(df,'times','var1',kind = 'month')
![Image text](./image/box.jpg)

Plot_Univariate :  绘制多个变量和目标变量的散点图
Example:
    from MyEcharts import Plot_Univariate
    df = pd.DataFrame(np.random.rand(50,4),columns = ['var1','var2','var3','target'])
    df['class'] = ['A']*25+['B']*25
    Plot_Univariate(df,'target','class')
![Image text](./image/univariate.jpg)

Plot_Scatter :  绘制一对变量的散点图
Example:
    from MyEcharts import Plot_Scatter
    df = pd.DataFrame(np.random.rand(50,4),columns = ['var1','var2','var3','target'])
    df['class'] = ['A']*25+['B']*25
    Plot_Scatter(df,'var1',"var2",label ='class')
![Image text](./image/scatter.jpg)

