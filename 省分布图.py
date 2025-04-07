from pyecharts.charts import Map

province_counts = df['生源省份'].value_counts()
province_data_pair = [list(z) for z in zip(province_counts.index, province_counts.values)]

# Ensure province names match pyecharts expectations (e.g., '黑龙江省' vs '黑龙江')
# You might need a mapping if names differ significantly. Pyecharts is generally good with short names.

map_chart = (
    Map()
    .add("生源地", province_data_pair, "china")
    .set_global_opts(
        title_opts=opts.TitleOpts(title="同学省份分布"),
        visualmap_opts=opts.VisualMapOpts(max_=int(province_counts.max()), is_piecewise=False), # Adjust max value if needed
    )
    .render("province_distribution_map.html")
)
print("Generated province_distribution_map.html")
