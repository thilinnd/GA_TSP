import pandas as pd
import numpy as np
import folium

from GA import solve  # hàm GA giải TSP trả về (distance, route, fitness)
from TSP import compute_distance_matrix

# 1. Đọc dữ liệu từ CSV (đường dẫn đúng với cấu trúc thư mục)
df = pd.read_csv('../data/5_CentralRegion.csv')

# 2. Lấy tọa độ dạng [(lat, lon), ...]
locations = list(zip(df['lat'], df['lon']))

# 3. Tạo ma trận khoảng cách
distance_matrix = compute_distance_matrix(locations)

# 4. Chạy thuật toán GA giải TSP
distance, route, fitness_history = solve(
    problem=distance_matrix,
    population_size=100,
    generations=200,
    mutation_rate=0.02,
    mutation_algorithm='swap',
    crossover_algorithm='single_point',
    selection_algorithm='tournament'
)

print(f"Khoảng cách tối ưu: {distance:.2f} km")
print(f"Lộ trình tối ưu (chỉ số tỉnh theo thứ tự): {route}")

# 5. Chuẩn bị danh sách điểm theo route (trừ 1 vì route bắt đầu từ 1 trong GA.py)
route_idx = [r - 1 for r in route]

# 6. Tạo map Folium với tâm trung bình tọa độ
center_lat = np.mean(df['lat'])
center_lon = np.mean(df['lon'])
m = folium.Map(location=[center_lat, center_lon], zoom_start=6)

# 7. Đánh dấu các điểm tỉnh trên map
for i, row in df.iterrows():
    folium.Marker(
        location=[row['lat'], row['lon']],
        tooltip=f"{row['province']} (Index: {i})"
    ).add_to(m)

# 8. Vẽ đường đi tối ưu theo thứ tự route, nối vòng kín
route_points = [locations[i] for i in route_idx]
route_points.append(route_points[0])  # quay về điểm đầu

folium.PolyLine(route_points, color='red', weight=4, opacity=0.7).add_to(m)

# 9. Lưu bản đồ ra file HTML
m.save('tsp_folium_map.html')
print("Bản đồ đã được lưu vào file: tsp_folium_map.html")
