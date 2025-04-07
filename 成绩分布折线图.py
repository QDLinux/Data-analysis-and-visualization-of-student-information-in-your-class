import matplotlib.pyplot as plt
from pyecharts.charts import Line

# Select relevant columns
df_grades = df[['姓名'] + rank_cols].copy()
# Make sure '姓名' is suitable as an identifier, or use '学号'
df_grades = df_grades.set_index('姓名') # Use name as index for plotting

# --- Matplotlib Version (Plotting first 10 students) ---
plt.figure(figsize=(12, 7))
# Plot only students who have at least one non-NaN rank
students_to_plot = df_grades.dropna(how='all').head(10) # Plot first 10 with data
for student_name, ranks in students_to_plot.iterrows():
    plt.plot(rank_cols, ranks.values, marker='o', linestyle='-', label=student_name)

plt.title('部分同学成绩名次变化趋势 (Matplotlib)')
plt.xlabel('学期')
plt.ylabel('名次 (数字越小越好)')
plt.xticks(rotation=15)
plt.gca().invert_yaxis() # Invert y-axis: lower rank is higher position
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left') # Place legend outside
plt.grid(True, axis='y', linestyle='--')
plt.tight_layout()
plt.show()

# --- Pyecharts Version (Interactive, plots all students) ---
line_chart = Line().set_global_opts(
    title_opts=opts.TitleOpts(title="同学成绩名次变化趋势 (Pyecharts)"),
    tooltip_opts=opts.TooltipOpts(trigger="axis"),
    xaxis_opts=opts.AxisOpts(type_="category", name="学期"),
    yaxis_opts=opts.AxisOpts(
        type_="value",
        name="名次",
        is_inverse=True, # Invert Y-axis
        splitline_opts=opts.SplitLineOpts(is_show=True),
    ),
    legend_opts=opts.LegendOpts(type_="scroll", pos_left="10%", orient="horizontal"), # Scrollable legend
    datazoom_opts=[opts.DataZoomOpts(orient="horizontal"), opts.DataZoomOpts(type_="inside", orient="horizontal")],
)

line_chart.add_xaxis(rank_cols)
# Add a line for each student who has at least one rank
for student_name, ranks in df_grades.dropna(how='all').iterrows():
     # Pyecharts needs numeric values, NaNs might break rendering or appear as gaps
     # Convert NaN to None for pyecharts (it handles None gracefully)
    ranks_list = [r if pd.notna(r) else None for r in ranks.values]
    line_chart.add_yaxis(student_name, ranks_list, is_smooth=False, symbol="circle", label_opts=opts.LabelOpts(is_show=False)) # Show labels optionally

line_chart.render("grade_trends_line.html")
print("Generated grade_trends_line.html")
