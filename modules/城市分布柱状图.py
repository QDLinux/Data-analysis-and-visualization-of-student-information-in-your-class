import matplotlib.pyplot as plt
from pyecharts.charts import Bar

city_counts = df['生源城市'].value_counts()

# --- Matplotlib Version ---
plt.figure(figsize=(12, 7))
city_counts.plot(kind='bar')
plt.title('同学城市分布 (Matplotlib)')
plt.ylabel('人数')
plt.xlabel('城市')
plt.xticks(rotation=45, ha='right') # Rotate labels for better readability
plt.tight_layout() # Adjust layout
plt.show()


# --- Pyecharts Version ---
bar_chart = (
    Bar()
    .add_xaxis(city_counts.index.tolist())
    .add_yaxis("人数", city_counts.values.tolist())
    .set_global_opts(
        title_opts=opts.TitleOpts(title="同学城市分布 (Pyecharts)"),
        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-30)), # Rotate labels
        datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")], # Add zoom
    )
    .render("city_distribution_bar.html")
)
print("Generated city_distribution_bar.html")
