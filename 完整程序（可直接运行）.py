import tkinter as tk
from tkinter import filedialog, messagebox, font as tkFont # 导入 tkFont 用于检查字体
import pandas as pd
import os
import webbrowser # 用于打开 html 文件

# --- 数据处理和可视化库 ---
import matplotlib.pyplot as plt
from pyecharts import options as opts
from pyecharts.charts import Pie, Map, Bar, Line, Graph # 导入 Graph 用于关系图
from wordcloud import WordCloud
import jieba
import networkx as nx
from itertools import combinations

# --- 全局配置 ---
# !!! 重要：请将 FONT_PATH 修改为你系统上有效的中文字体文件路径 !!!
# 例如: 'C:/Windows/Fonts/simhei.ttf' (Windows)
# 或 '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc' (某些 Linux)
FONT_PATH = 'C:/Windows/Fonts/simhei.ttf' # <--- 修改这里

# 尝试设置 Matplotlib 全局字体
try:
    plt.rcParams['font.sans-serif'] = ['SimHei'] # 指定默认字体
    plt.rcParams['axes.unicode_minus'] = False   # 解决保存图像是负号'-'显示为方块的问题
    # 检查字体是否存在（可选，但有帮助）
    available_fonts = tkFont.families()
    if 'SimHei' not in available_fonts:
         print("警告：系统中可能未找到 'SimHei' 字体，Matplotlib 图表中文可能显示异常。请在代码中修改为可用字体。")
         # 可以在这里尝试备用字体，例如：
         # plt.rcParams['font.sans-serif'] = ['Microsoft YaHei'] # 尝试微软雅黑
except Exception as e:
    print(f"设置 Matplotlib 字体时出错: {e}. 中文可能无法正常显示。")
    print(f"请确保你安装了中文字体，并在代码中正确配置。尝试的字体: SimHei")

# --- 全局变量 ---
student_data = None # 用于存储加载的 DataFrame
root = tk.Tk()    # 主窗口实例
root.title("学生信息分析工具 v1.0")
root.geometry("500x450") # 设置窗口大小

file_path_label_var = tk.StringVar()
file_path_label_var.set("尚未选择 Excel 文件")

# --- 文件选择和加载函数 ---
def select_file():
    global student_data
    filepath = filedialog.askopenfilename(
        title="请选择学生信息 Excel 文件",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
    )
    if not filepath:
        return

    try:
        student_data = pd.read_excel(filepath)
        # --- 基本数据清洗 ---
        if '人生格言' in student_data.columns:
             student_data['人生格言'] = student_data['人生格言'].fillna('')
        else:
             print("警告: Excel 文件中缺少 '人生格言' 列，词云功能将无法使用。")
             student_data['人生格言'] = '' # 创建空列避免后续错误

        rank_cols = ['大一上学期名次', '大一下学期名次', '大二上学期名次', '大二下学期名次', '大三上学期名次']
        for col in rank_cols:
            if col in student_data.columns:
                student_data[col] = pd.to_numeric(student_data[col], errors='coerce')
            else:
                print(f"警告: Excel 文件中缺少 '{col}' 列，成绩相关分析可能不完整。")

        # 检查必要的列是否存在
        required_cols = ['性别', '生源省份', '生源城市', '姓名', '寝室号']
        missing_cols = [col for col in required_cols if col not in student_data.columns]
        if missing_cols:
            messagebox.showwarning("列缺失警告", f"Excel 文件中缺少以下必需列: {', '.join(missing_cols)}\n部分功能可能无法正常工作。")


        filename = os.path.basename(filepath)
        file_path_label_var.set(f"已加载: {filename} (共 {len(student_data)} 条记录)")
        messagebox.showinfo("成功", f"文件 '{filename}' 加载成功！")

    except FileNotFoundError:
        student_data = None
        file_path_label_var.set("加载失败：文件未找到")
        messagebox.showerror("错误", f"文件未找到:\n{filepath}")
    except Exception as e:
        student_data = None
        file_path_label_var.set("加载失败，请检查文件格式或内容")
        messagebox.showerror("错误", f"加载或处理文件时发生错误:\n{e}")

# --- 检查数据是否加载的辅助函数 ---
def check_data_loaded():
    if student_data is None:
        messagebox.showerror("错误", "请先加载学生信息 Excel 文件！")
        return False
    if student_data.empty:
         messagebox.showerror("错误", "加载的数据为空，无法进行分析！")
         return False
    return True

# --- 可视化功能函数 ---

def plot_gender():
    if not check_data_loaded(): return
    if '性别' not in student_data.columns:
         messagebox.showerror("错误", "数据中缺少 '性别' 列！")
         return

    try:
        gender_counts = student_data['性别'].value_counts()
        gender_data_pair = [list(z) for z in zip(gender_counts.index, gender_counts.values.astype(float))] # pyecharts 需要 float

        pie_chart = (
            Pie(init_opts=opts.InitOpts(width="600px", height="400px")) # 设置图表大小
            .add(
                "", # 系列名称，留空
                gender_data_pair,
                radius=["40%", "75%"], # 设置饼图内外半径，做成环状图
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="同学性别分布"),
                legend_opts=opts.LegendOpts(orient="vertical", pos_top="15%", pos_left="2%"), # 图例设置
            )
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c} ({d}%)")) # 标签格式
        )
        output_file = "gender_distribution_pie.html"
        pie_chart.render(output_file)
        messagebox.showinfo("完成", f"性别分布饼图已生成：\n{output_file}\n将尝试在浏览器中打开。")
        webbrowser.open(output_file)
    except Exception as e:
        messagebox.showerror("绘图错误", f"生成性别饼图时出错:\n{e}")

def plot_province():
    if not check_data_loaded(): return
    if '生源省份' not in student_data.columns:
         messagebox.showerror("错误", "数据中缺少 '生源省份' 列！")
         return

    try:
        province_counts = student_data['生源省份'].value_counts()
        # 清理省份名称 (例如去掉 "省", "市", "自治区", "维吾尔", "壮族" 等后缀)
        province_counts.index = province_counts.index.str.replace(
            r'(省|市|自治区|维吾尔|壮族|回族)', '', regex=True
        )
        # 对于特殊名称的处理 (例如 '内蒙古' -> '内蒙古', '黑龙江' -> '黑龙江') - pyecharts 通常能识别短名称
        province_data_pair = [list(z) for z in zip(province_counts.index, province_counts.values.astype(float))]

        max_value = float(province_counts.max()) if not province_counts.empty else 1.0 # 避免空数据出错

        map_chart = (
            Map(init_opts=opts.InitOpts(width="800px", height="600px"))
            .add("生源地人数", province_data_pair, "china")
            .set_global_opts(
                title_opts=opts.TitleOpts(title="同学省份分布地图"),
                visualmap_opts=opts.VisualMapOpts(max_=max_value, is_piecewise=False),
                tooltip_opts=opts.TooltipOpts(formatter="{b}: {c}人") # 鼠标悬停提示
            )
        )
        output_file = "province_distribution_map.html"
        map_chart.render(output_file)
        messagebox.showinfo("完成", f"省份分布地图已生成：\n{output_file}\n将尝试在浏览器中打开。")
        webbrowser.open(output_file)
    except Exception as e:
        messagebox.showerror("绘图错误", f"生成省份地图时出错:\n{e}")


def plot_city():
    if not check_data_loaded(): return
    if '生源城市' not in student_data.columns:
         messagebox.showerror("错误", "数据中缺少 '生源城市' 列！")
         return

    try:
        city_counts = student_data['生源城市'].value_counts()
        city_data_pair = [list(z) for z in zip(city_counts.index, city_counts.values.astype(float))]

        bar_chart = (
            Bar(init_opts=opts.InitOpts(width="900px", height="500px"))
            .add_xaxis(city_counts.index.tolist())
            .add_yaxis("人数", city_counts.values.tolist())
            .set_global_opts(
                title_opts=opts.TitleOpts(title="同学城市分布"),
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-30)), # X轴标签旋转
                datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")], # 添加缩放
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow") # 悬停提示
            )
        )
        output_file = "city_distribution_bar.html"
        bar_chart.render(output_file)
        messagebox.showinfo("完成", f"城市分布柱状图已生成：\n{output_file}\n将尝试在浏览器中打开。")
        webbrowser.open(output_file)
    except Exception as e:
        messagebox.showerror("绘图错误", f"生成城市柱状图时出错:\n{e}")

def plot_wordcloud():
    if not check_data_loaded(): return
    if '人生格言' not in student_data.columns:
         messagebox.showerror("错误", "数据中缺少 '人生格言' 列！")
         return

    try:
        mottos = student_data['人生格言'].dropna().astype(str)
        if mottos.empty:
            messagebox.showinfo("提示", "没有有效的 '人生格言' 数据可供生成词云。")
            return

        text = " ".join(mottos)
        # 过滤掉太短或无意义的词语，以及特定标点符号
        text = text.replace(' ', '').replace('，', '').replace('。', '').replace('！', '').replace('？', '').replace('.', '').replace(',', '').replace('!', '').replace('?', '')
        if not text:
             messagebox.showinfo("提示", "过滤后没有足够的文本内容生成词云。")
             return

        # 使用 jieba 分词
        seg_list = jieba.cut(text, cut_all=False)
        # 定义一些停用词 (可以根据需要添加更多)
        stopwords = {' ', '的', '是', '了', '我', '你', '他', '她', '它', '都', '就', '也', '不', '在', '有', '人', '个', ' ', '\n', '\t'}
        processed_text = " ".join(word for word in seg_list if word not in stopwords and len(word) > 1) # 过滤单字和停用词

        if not processed_text:
             messagebox.showinfo("提示", "分词和过滤后没有足够的词语生成词云。")
             return

        # 检查字体文件是否存在
        if not os.path.exists(FONT_PATH):
             messagebox.showerror("字体错误", f"指定的字体文件未找到:\n{FONT_PATH}\n请在代码顶部修改 FONT_PATH 为有效的字体路径。")
             return

        wordcloud_img = WordCloud(
            font_path=FONT_PATH, # 必须指定中文字体路径
            width=800,
            height=400,
            background_color='white',
            # stopwords=stopwords # WordCloud 内部也有停用词，但我们前面处理过了
        ).generate(processed_text)

        # 使用 Matplotlib 显示词云
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud_img, interpolation='bilinear')
        plt.axis("off")
        plt.title("人生格言词云图")
        # 保存图片 (可选)
        output_image = "motto_wordcloud.png"
        try:
            wordcloud_img.to_file(output_image)
            messagebox.showinfo("完成", f"词云图已生成并显示。\n图片已保存为: {output_image}")
        except Exception as save_err:
             messagebox.showwarning("保存失败", f"词云图已显示，但保存到文件失败:\n{save_err}")
        plt.show() # 显示图像

    except RuntimeError as e:
         messagebox.showerror("字体错误", f"生成词云时可能字体路径配置错误:\n{e}\n请检查代码中的 FONT_PATH 设置。")
    except ImportError:
         messagebox.showerror("库缺失", "请确保已安装 'jieba' 和 'wordcloud' 库:\n pip install jieba wordcloud")
    except Exception as e:
        messagebox.showerror("绘图错误", f"生成词云时出错:\n{e}")


def plot_grades():
    if not check_data_loaded(): return

    rank_cols = ['大一上学期名次', '大一下学期名次', '大二上学期名次', '大二下学期名次', '大三上学期名次']
    # 找出数据中实际存在的成绩列
    valid_rank_cols = [col for col in rank_cols if col in student_data.columns]

    if not valid_rank_cols:
        messagebox.showerror("错误", "数据中没有找到任何有效的成绩排名列！")
        return
    if '姓名' not in student_data.columns:
        messagebox.showerror("错误", "数据中缺少 '姓名' 列！")
        return

    try:
        # 准备数据，将姓名设为索引
        df_grades = student_data[['姓名'] + valid_rank_cols].copy()
        df_grades = df_grades.set_index('姓名')
        # 筛选掉所有成绩都为空的学生
        df_grades = df_grades.dropna(how='all')

        if df_grades.empty:
             messagebox.showinfo("提示", "没有找到有效的学生成绩数据来绘制趋势图。")
             return

        line_chart = (
             Line(init_opts=opts.InitOpts(width="1000px", height="600px"))
             .set_global_opts(
                title_opts=opts.TitleOpts(title="同学成绩名次变化趋势 (名次越低越靠前)"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                xaxis_opts=opts.AxisOpts(type_="category", name="学期"),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    name="名次",
                    is_inverse=True, # Y轴反转，数字小的在上面
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                legend_opts=opts.LegendOpts(type_="scroll", pos_left="10%", orient="horizontal", top="5%"),
                datazoom_opts=[opts.DataZoomOpts(orient="horizontal"), opts.DataZoomOpts(type_="inside", orient="horizontal")],
             )
             .add_xaxis(valid_rank_cols) # X轴是学期名称
        )

        # 为每个学生添加一条线
        for student_name, ranks in df_grades.iterrows():
            # Pyecharts 需要处理 NaN 为 None
            ranks_list = [r if pd.notna(r) else None for r in ranks.values]
            line_chart.add_yaxis(
                student_name,
                ranks_list,
                is_smooth=False, # 不使用平滑曲线
                symbol="circle",
                label_opts=opts.LabelOpts(is_show=False), # 不显示线上标签，太多会乱
                # 设置鼠标悬停时高亮相关项
                emphasis_opts=opts.EmphasisOpts(focus='series')
                )

        output_file = "grade_trends_line.html"
        line_chart.render(output_file)
        messagebox.showinfo("完成", f"成绩趋势折线图已生成：\n{output_file}\n将尝试在浏览器中打开。")
        webbrowser.open(output_file)

    except Exception as e:
        messagebox.showerror("绘图错误", f"生成成绩趋势图时出错:\n{e}")

def plot_dorm_network():
    if not check_data_loaded(): return
    if '姓名' not in student_data.columns or '寝室号' not in student_data.columns:
        messagebox.showerror("错误", "数据中缺少 '姓名' 或 '寝室号' 列！")
        return

    try:
        G = nx.Graph()
        # 添加节点 (学生)，包含寝室信息
        valid_students = student_data.dropna(subset=['姓名', '寝室号'])
        if valid_students.empty:
             messagebox.showinfo("提示", "没有有效的学生姓名和寝室号数据来构建关系图。")
             return

        nodes_data = []
        dorm_map = {} # 用于给不同宿舍分配不同类别/颜色
        dorm_category_index = 0

        for index, row in valid_students.iterrows():
            student_name = str(row['姓名'])
            dorm_number = str(row['寝室号'])
            if dorm_number not in dorm_map:
                dorm_map[dorm_number] = dorm_category_index
                dorm_category_index += 1

            G.add_node(student_name, dorm=dorm_number) # NetworkX 图节点

            # 为 Pyecharts 准备节点数据
            nodes_data.append(
                opts.GraphNode(
                    name=student_name,
                    symbol_size=10, # 节点大小
                    category=dorm_map[dorm_number] # 节点类别，用于区分颜色
                )
            )

        # 添加边 (同一寝室的学生连接)
        links_data = []
        dorm_groups = valid_students.groupby('寝室号')['姓名'].apply(list)
        for dorm, students in dorm_groups.items():
            # 确保学生名字是字符串
            students = [str(s) for s in students]
            if len(students) > 1:
                for u, v in combinations(students, 2):
                    if G.has_node(u) and G.has_node(v): # 再次确认节点存在
                        G.add_edge(u, v, dorm=str(dorm)) # NetworkX 图边
                        # 为 Pyecharts 准备边数据
                        links_data.append(opts.GraphLink(source=u, target=v))

        if not links_data:
             messagebox.showinfo("提示", "没有找到同一寝室超过一人的情况，无法生成关系连线。")
             # 可以选择只显示节点
             # return


        # 生成 Pyecharts 关系图
        categories = [opts.GraphCategory(name=str(dorm)) for dorm in dorm_map.keys()]

        graph_chart = (
            Graph(init_opts=opts.InitOpts(width="1000px", height="700px"))
            .add(
                "", # 系列名称
                nodes=nodes_data,
                links=links_data,
                categories=categories, # 定义节点类别（用于颜色区分）
                layout="force", # 使用力引导布局
                is_rotate_label=True, # 标签是否旋转
                linestyle_opts=opts.LineStyleOpts(color="source", curve=0.3), # 边样式
                label_opts=opts.LabelOpts(is_show=True, position="right"), # 显示标签
                repulsion=80, # 节点间斥力因子
                gravity=0.1, # 引力因子
                edge_symbol=['', 'arrow'] # 边两端形状
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="寝室关系图 (同寝室相连)"),
                legend_opts=opts.LegendOpts(orient='vertical', pos_left='2%', pos_top='20%'), # 显示图例（寝室号）
            )
        )

        output_file = "dorm_relationship_graph.html"
        graph_chart.render(output_file)
        messagebox.showinfo("完成", f"寝室关系图已生成：\n{output_file}\n将尝试在浏览器中打开。")
        webbrowser.open(output_file)


    except ImportError:
         messagebox.showerror("库缺失", "请确保已安装 'networkx' 库:\n pip install networkx")
    except Exception as e:
        messagebox.showerror("绘图错误", f"生成寝室关系图时出错:\n{e}")


# --- Tkinter GUI 布局 ---

# 顶部框架：文件选择
top_frame = tk.Frame(root)
top_frame.pack(pady=10)

select_button = tk.Button(top_frame, text="选择学生信息 Excel 文件", command=select_file, width=25)
select_button.pack(side=tk.LEFT, padx=10)

file_label = tk.Label(top_frame, textvariable=file_path_label_var, width=40, anchor='w')
file_label.pack(side=tk.LEFT)

# 中部框架：功能按钮
button_frame = tk.Frame(root)
button_frame.pack(pady=20, padx=20)

button_width = 18 # 统一按钮宽度
button_pady = 5    # 统一按钮垂直间距

# 功能按钮定义
buttons_info = [
    ("性别分布饼图", plot_gender),
    ("省份分布地图", plot_province),
    ("城市分布柱状图", plot_city),
    ("格言词云", plot_wordcloud),
    ("成绩趋势折线图", plot_grades),
    ("寝室关系图", plot_dorm_network),
]

# 使用 grid 布局按钮
num_cols = 2
for i, (text, command) in enumerate(buttons_info):
    row = i // num_cols
    col = i % num_cols
    button = tk.Button(button_frame, text=text, width=button_width, command=command)
    button.grid(row=row, column=col, padx=10, pady=button_pady, sticky="ew") # sticky='ew' 使按钮在网格单元中水平填充

# 底部状态栏 (可选)
# status_label = tk.Label(root, text="准备就绪", bd=1, relief=tk.SUNKEN, anchor=tk.W)
# status_label.pack(side=tk.BOTTOM, fill=tk.X)

# --- 启动主事件循环 ---
root.mainloop()
