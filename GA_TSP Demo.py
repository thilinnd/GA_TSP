import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import csv
import os
import threading
import webbrowser
import tempfile
import folium
from folium import plugins
import src.GA
import src.TSP

class TSPGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TSP Genetic Algorithm với Bản đồ Vệ tinh")
        self.geometry("1200x800")
        self.configure(bg="#ffffff")

        self.city_data = {}  # name -> (lat, lon)
        self.city_vars = {}  # city name -> tk.BooleanVar()
        self.current_route = []  # Lưu trữ lộ trình hiện tại
        self.current_coords = []  # Lưu trữ tọa độ của lộ trình
        
        # Thêm biến để lưu lộ trình tốt nhất
        self.best_route = []  # Lưu lộ trình tốt nhất
        self.best_distance = float('inf')  # Lưu khoảng cách tốt nhất

        self.setup_ui()
        self.refresh_file_list()

    def setup_ui(self):
        # Tạo main container với 2 panel
        main_container = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)

        # Panel trái: Controls
        left_panel = ttk.Frame(main_container)
        main_container.add(left_panel, weight=1)

        # Panel phải: Bản đồ
        right_panel = ttk.Frame(main_container)
        main_container.add(right_panel, weight=1)

        # ======= Panel trái: Các điều khiển =======
        self.setup_left_panel(left_panel)

        # ======= Panel phải: Bản đồ =======
        self.setup_right_panel(right_panel)

    def setup_left_panel(self, parent):
        # ======= Phần trên cùng: Dữ liệu và chọn thành phố =======
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill="x", padx=5, pady=5)

        # Khung chọn file và thành phố bắt đầu
        data_frame = ttk.LabelFrame(top_frame, text="Dữ liệu")
        data_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(data_frame, text="Chọn file CSV:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.file_cb = ttk.Combobox(data_frame, state="readonly", width=25)
        self.file_cb.grid(row=0, column=1, padx=5, pady=5)
        self.file_cb.bind("<<ComboboxSelected>>", self.load_selected_file)

        ttk.Label(data_frame, text="Thành phố bắt đầu:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.start_city_cb = ttk.Combobox(data_frame, state="readonly", width=25)
        self.start_city_cb.grid(row=1, column=1, padx=5, pady=5)
        self.start_city_cb.bind("<<ComboboxSelected>>", self.update_start_city)

        # Khung chọn thành phố qua (checkbox)
        city_frame = ttk.LabelFrame(top_frame, text="Chọn thành phố muốn đi qua")
        city_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.city_canvas = tk.Canvas(city_frame, height=150)
        self.city_canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(city_frame, orient="vertical", command=self.city_canvas.yview)
        scrollbar.pack(side="right", fill="y")

        self.city_canvas.configure(yscrollcommand=scrollbar.set)
        self.city_canvas.bind('<Configure>', lambda e: self.city_canvas.configure(scrollregion=self.city_canvas.bbox("all")))

        self.city_inner_frame = ttk.Frame(self.city_canvas)
        self.city_canvas.create_window((0,0), window=self.city_inner_frame, anchor="nw")

        # Nút chọn tất cả / bỏ chọn tất cả
        btn_frame = ttk.Frame(city_frame)
        btn_frame.pack(fill="x", pady=5)
        self.btn_select_all = ttk.Button(btn_frame, text="Chọn tất cả", command=self.select_all_cities)
        self.btn_select_all.pack(side="left", padx=5)
        self.btn_deselect_all = ttk.Button(btn_frame, text="Bỏ chọn tất cả", command=self.deselect_all_cities)
        self.btn_deselect_all.pack(side="left", padx=5)

        # ======= Phần giữa: cấu hình thuật toán =======
        middle_frame = ttk.LabelFrame(parent, text="Cấu hình thuật toán di truyền")
        middle_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(middle_frame, text="Thuật toán đột biến:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.mut_algo_cb = ttk.Combobox(middle_frame, values=['swap', 'scramble', 'inversion', 'insertion'], state='readonly', width=15)
        self.mut_algo_cb.current(0)
        self.mut_algo_cb.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(middle_frame, text="Thuật toán lai ghép:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.cross_algo_cb = ttk.Combobox(middle_frame, values=['order', 'single_point', 'two_point', 'uniform'], state='readonly', width=15)
        self.cross_algo_cb.current(0)
        self.cross_algo_cb.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(middle_frame, text="Thuật toán chọn lọc:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.sel_algo_cb = ttk.Combobox(middle_frame, values=['elitism', 'tournament', 'rank', 'roulette_wheel'], state='readonly', width=15)
        self.sel_algo_cb.current(0)
        self.sel_algo_cb.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(middle_frame, text="Số thế hệ:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.gen_entry = ttk.Entry(middle_frame, width=17)
        self.gen_entry.insert(0, "100")
        self.gen_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(middle_frame, text="Kích thước quần thể:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.pop_entry = ttk.Entry(middle_frame, width=17)
        self.pop_entry.insert(0, "100")
        self.pop_entry.grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(middle_frame, text="Tỉ lệ đột biến:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.mut_entry = ttk.Entry(middle_frame, width=17)
        self.mut_entry.insert(0, "0.01")
        self.mut_entry.grid(row=5, column=1, padx=5, pady=5)

        # Nút chạy thuật toán
        self.btn_process = ttk.Button(parent, text="▶ Chạy thuật toán", command=self.start_process)
        self.btn_process.pack(pady=10, ipadx=10, ipady=5)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progressbar = ttk.Progressbar(parent, variable=self.progress_var, maximum=100)
        self.progressbar.pack(fill="x", padx=10, pady=5)

        # ======= Phần dưới: kết quả =======
        result_frame = ttk.LabelFrame(parent, text="Kết quả")
        result_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, font=("Consolas", 10), height=8)
        self.result_text.pack(fill="both", expand=True)

        # Status bar
        self.status_var = tk.StringVar(value="Sẵn sàng")
        self.status_label = ttk.Label(parent, textvariable=self.status_var, relief="sunken", anchor="w")
        self.status_label.pack(fill="x", side="bottom")

    def setup_right_panel(self, parent):
        # Khung bản đồ
        map_frame = ttk.LabelFrame(parent, text="Bản đồ Vệ tinh - Lộ trình TSP")
        map_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Nút điều khiển bản đồ
        map_control_frame = ttk.Frame(map_frame)
        map_control_frame.pack(fill="x", padx=5, pady=5)

        self.btn_show_map = ttk.Button(map_control_frame, text="🗺️ Hiển thị bản đồ", command=self.show_map)
        self.btn_show_map.pack(side="left", padx=5)

        self.btn_show_cities = ttk.Button(map_control_frame, text="📍 Hiển thị thành phố", command=self.show_cities_only)
        self.btn_show_cities.pack(side="left", padx=5)

        # Khung hiển thị thông tin bản đồ
        self.map_info_text = scrolledtext.ScrolledText(map_frame, wrap=tk.WORD, font=("Consolas", 9), height=25)
        self.map_info_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Thêm thông tin hướng dẫn ban đầu
        self.map_info_text.insert(tk.END, "🗺️ HƯỚNG DẪN SỬ DỤNG BẢN ĐỒ\n")
        self.map_info_text.insert(tk.END, "="*50 + "\n\n")
        self.map_info_text.insert(tk.END, "1. Chọn file CSV chứa dữ liệu thành phố\n")
        self.map_info_text.insert(tk.END, "2. Chọn thành phố xuất phát\n")
        self.map_info_text.insert(tk.END, "3. Chọn các thành phố muốn đi qua\n")
        self.map_info_text.insert(tk.END, "4. Nhấn 'Hiển thị thành phố' để xem vị trí các thành phố\n")
        self.map_info_text.insert(tk.END, "5. Chạy thuật toán để tìm lộ trình tối ưu\n")
        self.map_info_text.insert(tk.END, "6. Nhấn 'Hiển thị bản đồ' để xem lộ trình trên bản đồ vệ tinh\n\n")
        self.map_info_text.insert(tk.END, "📍 Bản đồ sẽ mở trong trình duyệt web của bạn\n")
        self.map_info_text.insert(tk.END, "🛰️ Sử dụng ảnh vệ tinh chất lượng cao\n")

    def refresh_file_list(self):
        data_folder = "./data"
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)

        csv_files = [f for f in os.listdir(data_folder) if f.endswith(".csv")]
        self.file_cb['values'] = csv_files
        if csv_files:
            self.file_cb.current(0)
            self.load_selected_file()

    def load_selected_file(self, event=None):
        selected_file = self.file_cb.get()
        if not selected_file:
            return

        path = os.path.join("./data", selected_file)
        try:
            with open(path, newline='', encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.city_data = {}
                for row in reader:
                    if 'province' in row and 'lat' in row and 'lon' in row:
                        try:
                            lat = float(row['lat'])
                            lon = float(row['lon'])
                            self.city_data[row['province']] = (lat, lon)
                        except:
                            continue
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không đọc được file: {e}")
            return

        cities = list(self.city_data.keys())
        self.start_city_cb['values'] = cities
        if cities:
            self.start_city_cb.current(0)

        # Xóa checkbox cũ
        for widget in self.city_inner_frame.winfo_children():
            widget.destroy()
        self.city_vars.clear()

        # Tạo checkbox cho từng thành phố
        for city in cities:
            var = tk.BooleanVar(value=False)
            chk = ttk.Checkbutton(self.city_inner_frame, text=city, variable=var)
            chk.pack(anchor="w", padx=5, pady=2)
            self.city_vars[city] = var
            
        # Cập nhật scroll region
        self.city_inner_frame.update_idletasks()
        self.city_canvas.configure(scrollregion=self.city_canvas.bbox("all"))
            
        # Tự động chọn thành phố xuất phát
        self.update_start_city()

        # Cập nhật thông tin bản đồ
        self.update_map_info()

    def update_start_city(self, event=None):
        """Cập nhật trạng thái checkbox khi chọn thành phố xuất phát"""
        start_city = self.start_city_cb.get()
        if start_city and start_city in self.city_vars:
            # Tự động chọn thành phố xuất phát và vô hiệu hóa checkbox của nó
            self.city_vars[start_city].set(True)
            
            # Tìm và vô hiệu hóa checkbox của thành phố xuất phát
            for widget in self.city_inner_frame.winfo_children():
                if isinstance(widget, ttk.Checkbutton) and widget.cget("text") == start_city:
                    widget.config(state="disabled")
                else:
                    widget.config(state="normal")

    def select_all_cities(self):
        """Chọn tất cả các thành phố trừ thành phố xuất phát (đã được chọn riêng)"""
        for city, var in self.city_vars.items():
            var.set(True)

    def deselect_all_cities(self):
        """Bỏ chọn tất cả các thành phố trừ thành phố xuất phát"""
        start_city = self.start_city_cb.get()
        for city, var in self.city_vars.items():
            if city != start_city:  # Giữ nguyên thành phố xuất phát đã chọn
                var.set(False)

    def update_map_info(self):
        """Cập nhật thông tin về dữ liệu đã tải"""
        self.map_info_text.delete("1.0", tk.END)
        
        if not self.city_data:
            self.map_info_text.insert(tk.END, "Chưa có dữ liệu thành phố.\n")
            return
            
        self.map_info_text.insert(tk.END, f"📊 THÔNG TIN DỮ LIỆU\n")
        self.map_info_text.insert(tk.END, "="*30 + "\n\n")
        self.map_info_text.insert(tk.END, f"📁 File: {self.file_cb.get()}\n")
        self.map_info_text.insert(tk.END, f"🏙️ Số thành phố: {len(self.city_data)}\n\n")
        
        self.map_info_text.insert(tk.END, "📍 DANH SÁCH THÀNH PHỐ:\n")
        self.map_info_text.insert(tk.END, "-"*30 + "\n")
        
        for i, (city, (lat, lon)) in enumerate(self.city_data.items(), 1):
            self.map_info_text.insert(tk.END, f"{i:2d}. {city:<20} ({lat:.4f}, {lon:.4f})\n")

    def create_map(self, show_route=True):
        """Tạo bản đồ với ảnh vệ tinh"""
        if not self.city_data:
            return None

        # Tính toán trung tâm bản đồ
        lats = [coord[0] for coord in self.city_data.values()]
        lons = [coord[1] for coord in self.city_data.values()]
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)

        # Tạo bản đồ với ảnh vệ tinh
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=6,
            tiles=None
        )

        # Thêm nhiều lớp bản đồ
        folium.TileLayer('OpenStreetMap', name='Bản đồ đường').add_to(m)
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Ảnh vệ tinh',
            overlay=False,
            control=True
        ).add_to(m)
        
        # Thêm lớp ảnh vệ tinh với nhãn
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Ảnh vệ tinh + Nhãn',
            overlay=True,
            control=True
        ).add_to(m)

        selected_cities = [city for city, var in self.city_vars.items() if var.get()] if self.city_vars else list(self.city_data.keys())
        start_city = self.start_city_cb.get()

        # Thêm marker cho các thành phố
        for city in selected_cities:
            if city in self.city_data:
                lat, lon = self.city_data[city]
                
                # Màu sắc khác nhau cho thành phố xuất phát
                if city == start_city:
                    icon_color = 'red'
                    icon_icon = 'home'
                    popup_text = f"🚩 XUẤT PHÁT: {city}"
                else:
                    icon_color = 'blue'
                    icon_icon = 'info-sign'
                    popup_text = f"📍 {city}"
                
                folium.Marker(
                    [lat, lon],
                    popup=folium.Popup(popup_text, max_width=200),
                    tooltip=city,
                    icon=folium.Icon(color=icon_color, icon=icon_icon)
                ).add_to(m)

        # Vẽ đường đi nếu có lộ trình
        if show_route and self.current_route and self.current_coords:
            # Vẽ đường đi chính
            folium.PolyLine(
                self.current_coords,
                color='red',
                weight=4,
                opacity=0.8,
                popup='Lộ trình tối ưu TSP'
            ).add_to(m)
            
            # Thêm marker số thứ tự cho từng điểm trong lộ trình
            for i, (city, coord) in enumerate(zip(self.current_route, self.current_coords)):
                if i < len(self.current_route) - 1:  # Không đánh số cho điểm cuối (trùng với điểm đầu)
                    folium.CircleMarker(
                        coord,
                        radius=15,
                        popup=f"Thứ tự: {i+1}",
                        color='white',
                        fill=True,
                        fillColor='red',
                        fillOpacity=0.8,
                        weight=2
                    ).add_to(m)
                    
                    # Thêm số thứ tự
                    folium.Marker(
                        coord,
                        icon=folium.DivIcon(
                            html=f'<div style="color: white; font-weight: bold; font-size: 12px; text-align: center; line-height: 15px;">{i+1}</div>',
                            icon_size=(15, 15),
                            icon_anchor=(7, 7)
                        )
                    ).add_to(m)

        # Thêm điều khiển lớp
        folium.LayerControl().add_to(m)
        
        # Thêm plugin fullscreen
        plugins.Fullscreen().add_to(m)
        
        # Thêm plugin đo khoảng cách
        plugins.MeasureControl().add_to(m)

        return m

    def show_cities_only(self):
        """Hiển thị chỉ các thành phố đã chọn trên bản đồ"""
        if not self.city_data:
            messagebox.showwarning("Cảnh báo", "Vui lòng tải dữ liệu thành phố trước.")
            return

        selected_cities = [city for city, var in self.city_vars.items() if var.get()]
        if len(selected_cities) < 2:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất 2 thành phố.")
            return

        try:
            # Tạo bản đồ chỉ hiển thị thành phố
            m = self.create_map(show_route=False)
            if m is None:
                return

            # Lưu bản đồ tạm thời và mở trong trình duyệt
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
            m.save(temp_file.name)
            webbrowser.open('file://' + temp_file.name)

            self.status_var.set(f"Đã hiển thị {len(selected_cities)} thành phố trên bản đồ")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo bản đồ: {e}")

    def show_map(self):
        """Hiển thị bản đồ với lộ trình (nếu có)"""
        if not self.current_route:
            self.show_cities_only()
            return

        try:
            # Tạo bản đồ với lộ trình
            m = self.create_map(show_route=True)
            if m is None:
                return

            # Lưu bản đồ tạm thời và mở trong trình duyệt
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
            m.save(temp_file.name)
            webbrowser.open('file://' + temp_file.name)

            self.status_var.set("Đã hiển thị lộ trình TSP trên bản đồ vệ tinh")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo bản đồ: {e}")

    def start_process(self):
        # Khóa nút chạy trong lúc chạy
        self.btn_process.config(state="disabled")
        self.status_var.set("Đang chạy thuật toán...")
        self.progress_var.set(0)
        self.result_text.delete("1.0", tk.END)
        
        # Reset lộ trình tốt nhất
        self.best_route = []
        self.best_distance = float('inf')

        # Chạy thuật toán trên luồng riêng để không làm đơ giao diện
        threading.Thread(target=self.process).start()

    def process(self):
        start_city = self.start_city_cb.get()
        selected_cities = [city for city, var in self.city_vars.items() if var.get()]

        if not start_city:
            messagebox.showerror("Lỗi", "Vui lòng chọn thành phố bắt đầu.")
            self.status_var.set("Lỗi: chưa chọn thành phố bắt đầu")
            self.btn_process.config(state="normal")
            return
            
        if len(selected_cities) < 3:
            messagebox.showerror("Lỗi", "Vui lòng chọn ít nhất 3 thành phố (bao gồm thành phố xuất phát).")
            self.status_var.set("Lỗi: chưa chọn đủ thành phố")
            self.btn_process.config(state="normal")
            return
        
        # Sắp xếp các thành phố theo longitude, sau đó là latitude
        selected_cities.sort(key=lambda city: (self.city_data[city][0], self.city_data[city][1]) if city in self.city_data else (float('inf'), float('inf')))

        # Đảm bảo thành phố xuất phát ở đầu mảng
        if start_city in selected_cities:
            selected_cities.remove(start_city)
        selected_cities.insert(0, start_city)

        try:
            generations = int(self.gen_entry.get())
            population = int(self.pop_entry.get())
            mutation_rate = float(self.mut_entry.get())
            if generations <= 0 or population <= 0 or not (0 <= mutation_rate <= 1):
                raise ValueError("Thông số không hợp lệ")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Thông số không hợp lệ: {e}")
            self.status_var.set("Lỗi: thông số không hợp lệ")
            self.btn_process.config(state="normal")
            return

        valid_cities = []
        valid_city_names = []
        for city in selected_cities:
            if city in self.city_data:
                valid_cities.append(self.city_data[city])
                valid_city_names.append(city)

        if len(valid_cities) < 3:
            messagebox.showerror("Lỗi", "Cần ít nhất 3 thành phố có tọa độ hợp lệ.")
            self.status_var.set("Lỗi: thiếu tọa độ hợp lệ")
            self.btn_process.config(state="normal")
            return

        dist_matrix = src.TSP.compute_distance_matrix(valid_cities)

        try:
            # Chạy thuật toán nhiều lần để tìm lộ trình tốt nhất
            num_runs = 5  # Số lần chạy để tìm kết quả tốt nhất
            best_result = None
            
            for run in range(num_runs):
                # Cập nhật progress bar
                progress = (run / num_runs) * 100
                self.progress_var.set(progress)
                
                # Chạy thuật toán
                current_result = src.GA.genetic_algorithm(
                    n_cities=len(valid_cities),
                    distances=dist_matrix,
                    population_size=population,
                    generations=generations,
                    mutation_rate=mutation_rate,
                    mutation_algorithm=self.mut_algo_cb.get(),
                    selection_algorithm=self.sel_algo_cb.get(),
                    crossover_algorithm=self.cross_algo_cb.get()
                )
                
                # Kiểm tra kết quả hợp lệ
                if 'route' not in current_result or 'distance' not in current_result:
                    continue
                    
                # So sánh với kết quả tốt nhất hiện tại
                if (best_result is None or 
                    current_result['distance'] < best_result['distance']):
                    best_result = current_result.copy()
                    self.best_distance = current_result['distance']
                    self.best_route = current_result['route'].copy()
                
                # Cập nhật status
                self.status_var.set(f"Đang chạy lần {run+1}/{num_runs}... Tốt nhất: {self.best_distance:.2f} km")
            
            # Sử dụng kết quả tốt nhất
            if best_result is None:
                raise ValueError("Không có kết quả hợp lệ")
                
            result = best_result
            route = [i % len(valid_city_names) for i in result['route']]
            final_distance = result['distance']

            route_names_raw = [valid_city_names[i] for i in route]

            # Đưa start_city về đầu tuyến đường
            start_city_name = valid_city_names[0]
            if start_city_name in route_names_raw:
                start_idx = route_names_raw.index(start_city_name)
                route_names = route_names_raw[start_idx:] + route_names_raw[:start_idx]
            else:
                route_names = route_names_raw
                
            # Loại bỏ các thành phố trùng lặp liên tiếp trong lộ trình
            unique_route = []
            for city in route_names:
                if not unique_route or unique_route[-1] != city:
                    unique_route.append(city)
            
            # Đảm bảo tuyến đường kết thúc tại điểm xuất phát
            if unique_route and unique_route[0] != unique_route[-1]:
                unique_route.append(unique_route[0])

            # Lưu lộ trình và tọa độ để hiển thị trên bản đồ
            self.current_route = unique_route
            self.current_coords = []
            for city in unique_route:
                if city in self.city_data:
                    self.current_coords.append(list(self.city_data[city]))

            # Hiển thị kết quả
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, "🎯 KẾT QUẢ THUẬT TOÁN DI TRUYỀN TSP\n")
            self.result_text.insert(tk.END, "="*50 + "\n\n")
            self.result_text.insert(tk.END, f"⭐ LỘ TRÌNH TỐI ƯU NHẤT (Tốt nhất trong {num_runs} lần chạy):\n")
            self.result_text.insert(tk.END, f"   {' → '.join(unique_route)}\n\n")
            self.result_text.insert(tk.END, f"📏 Tổng khoảng cách tối ưu: {final_distance:.2f} km\n")
            self.result_text.insert(tk.END, f"🏙️ Số thành phố: {len(unique_route)-1}\n")
            self.result_text.insert(tk.END, f"🔄 Số lần chạy: {num_runs}\n")
            self.result_text.insert(tk.END, f"🧬 Số thế hệ mỗi lần: {generations}\n")
            self.result_text.insert(tk.END, f"👥 Kích thước quần thể: {population}\n")
            self.result_text.insert(tk.END, f"🔄 Tỉ lệ đột biến: {mutation_rate}\n\n")
            self.result_text.insert(tk.END, "🗺️ Nhấn 'Hiển thị bản đồ' để xem lộ trình tối ưu trên ảnh vệ tinh!\n")

            # Cập nhật thông tin bản đồ
            self.update_route_info()

            self.status_var.set("Hoàn thành! Đã tìm được lộ trình tối ưu.")
            self.progress_var.set(100)
            
        except Exception as e:
            import traceback
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, f"❌ Lỗi khi chạy thuật toán:\n{traceback.format_exc()}")
            self.status_var.set("Lỗi khi chạy thuật toán")

        self.btn_process.config(state="normal")

    def update_route_info(self):
        """Cập nhật thông tin lộ trình trên panel bản đồ"""
        if not self.current_route:
            return
            
        self.map_info_text.delete("1.0", tk.END)
        
        self.map_info_text.insert(tk.END, "🎯 THÔNG TIN LỘ TRÌNH TỐI ƯU NHẤT\n")
        self.map_info_text.insert(tk.END, "="*40 + "\n\n")
        
        # Thông tin tổng quan
        total_distance = 0
        self.map_info_text.insert(tk.END, f"🚩 Điểm xuất phát: {self.current_route[0]}\n")
        self.map_info_text.insert(tk.END, f"🏁 Điểm kết thúc: {self.current_route[-1]}\n")
        self.map_info_text.insert(tk.END, f"🏙️ Số thành phố: {len(self.current_route)-1}\n")
        if hasattr(self, 'best_distance') and self.best_distance < float('inf'):
            self.map_info_text.insert(tk.END, f"📏 Khoảng cách tối ưu: {self.best_distance:.2f} km\n\n")
        else:
            self.map_info_text.insert(tk.END, "\n")
        
        # Chi tiết từng đoạn đường
        self.map_info_text.insert(tk.END, "📍 CHI TIẾT LỘ TRÌNH TỐI ƯU:\n")
        self.map_info_text.insert(tk.END, "-"*35 + "\n")
        
        for i in range(len(self.current_route)-1):
            from_city = self.current_route[i]
            to_city = self.current_route[i+1]
            
            if from_city in self.city_data and to_city in self.city_data:
                from_coord = self.city_data[from_city]
                to_coord = self.city_data[to_city]
                
                # Tính khoảng cách giữa 2 thành phố (công thức Haversine)
                distance = self.calculate_distance(from_coord, to_coord)
                total_distance += distance
                
                self.map_info_text.insert(tk.END, f"{i+1:2d}. {from_city:<15} → {to_city:<15} ({distance:.1f} km)\n")
        
        self.map_info_text.insert(tk.END, f"\n📏 Tổng khoảng cách tính toán: {total_distance:.2f} km\n\n")
        
        # Hướng dẫn sử dụng bản đồ
        self.map_info_text.insert(tk.END, "🗺️ CÁCH SỬ DỤNG BẢN ĐỒ:\n")
        self.map_info_text.insert(tk.END, "-"*25 + "\n")
        self.map_info_text.insert(tk.END, "• Nhấn 'Hiển thị bản đồ' để xem lộ trình tối ưu\n")
        self.map_info_text.insert(tk.END, "• Bản đồ sẽ mở trong trình duyệt web\n")
        self.map_info_text.insert(tk.END, "• Có thể chuyển đổi giữa ảnh vệ tinh và bản đồ đường\n")
        self.map_info_text.insert(tk.END, "• Sử dụng nút zoom để phóng to/thu nhỏ\n")
        self.map_info_text.insert(tk.END, "• Click vào marker để xem thông tin thành phố\n")
        self.map_info_text.insert(tk.END, "• Đường màu đỏ hiển thị lộ trình tối ưu nhất\n")
        self.map_info_text.insert(tk.END, "• Số trên marker hiển thị thứ tự đi qua\n")

    def calculate_distance(self, coord1, coord2):
        """Tính khoảng cách giữa 2 tọa độ (Haversine formula)"""
        import math
        
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        # Chuyển đổi sang radian
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Bán kính Trái Đất (km)
        r = 6371
        
        return c * r

if __name__ == "__main__":
    try:
        app = TSPGUI()
        app.mainloop()
    except ImportError as e:
        print("Lỗi: Thiếu thư viện cần thiết!")
        print("Vui lòng cài đặt: pip install folium")
        print(f"Chi tiết lỗi: {e}")