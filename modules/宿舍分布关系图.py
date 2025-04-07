import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations

G = nx.Graph()

# Add nodes (students). Use '姓名' or '学号' as node ID. Assuming '姓名' is unique enough here.
# Add dorm info as node attribute
for index, row in df.iterrows():
    # Check if '姓名' and '寝室号' are not NaN/None before adding
    if pd.notna(row['姓名']) and pd.notna(row['寝室号']):
        G.add_node(row['姓名'], dorm=str(row['寝室号'])) # Ensure dorm is string

# Group students by dorm
dorm_groups = df.dropna(subset=['姓名', '寝室号']).groupby('寝室号')['姓名'].apply(list)

# Add edges between students in the same dorm
for dorm, students in dorm_groups.items():
    if len(students) > 1:
        for u, v in combinations(students, 2):
            # Check if nodes exist before adding edge (due to potential NaNs handled above)
            if G.has_node(u) and G.has_node(v):
                G.add_edge(u, v, dorm=str(dorm))

# --- Matplotlib Visualization ---
plt.figure(figsize=(15, 15))
# Use a layout algorithm
pos = nx.spring_layout(G, k=0.6, iterations=50) # k adjusts spacing

# Draw nodes - color by dorm? (Complex coloring logic omitted for simplicity)
# Node labels need the Chinese font
nx.draw_networkx_nodes(G, pos, node_size=200, node_color='lightblue')
nx.draw_networkx_edges(G, pos, alpha=0.5, edge_color='gray')
nx.draw_networkx_labels(G, pos, font_size=8, font_family='SimHei') # Use Chinese font

plt.title('寝室关系图 (线连接同寝室同学)', fontproperties={'family':'SimHei', 'size': 16})
plt.axis('off') # Hide axes
plt.show()

# Note: Pyecharts Graph visualization is also possible but more complex to set up node categories/colors based on dorms.
