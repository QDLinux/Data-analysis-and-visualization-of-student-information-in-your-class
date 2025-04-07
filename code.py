import matplotlib.pyplot as plt
from pyecharts import options as opts
from pyecharts.charts import Pie

# --- Matplotlib Version ---
gender_counts = df['性别'].value_counts()
plt.figure(figsize=(6, 6))
plt.rcParams['font.sans-serif'] = ['SimHei'] # Or your specific font name
plt.rcParams['axes.unicode_minus'] = False # Display minus sign correctly
plt.pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%', startangle=90)
plt.title('同学性别分布 (Matplotlib)')
plt.show()

# --- Pyecharts Version (Interactive) ---
gender_data_pair = [list(z) for z in zip(gender_counts.index, gender_counts.values)]
pie_chart = (
    Pie()
    .add("", gender_data_pair)
    .set_global_opts(title_opts=opts.TitleOpts(title="同学性别分布 (Pyecharts)"))
    .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c} ({d}%)"))
    .render("gender_distribution_pie.html") # Saves an HTML file
)
print("Generated gender_distribution_pie.html")