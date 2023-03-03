import pandas as pd
from fbprophet import Prophet

# 生成模拟数据
sales_data = pd.DataFrame({'ds': pd.date_range(start='2022-01-01', periods=30, freq='D'),
                           'y': [50 + x for x in range(30)] + [30 + x for x in range(20)]})

# 创建模型
model = Prophet()

# 拟合数据
model.fit(sales_data)

# 预测未来30天的销量
future = model.make_future_dataframe(periods=30)
forecast = model.predict(future)

# 输出预测结果
forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(30)