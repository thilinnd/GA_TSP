import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import csv
import os
import threading
import src.GA
import src.TSP

class TSPGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TSP Genetic Algorithm")
        self.geometry("900x700")
        self.configure(bg="#ffffff")

        self.city_data = {}  # name -> (lat, lon)
        self.city_vars = {}  # city name -> tk.BooleanVar()

        self.setup_ui()
        self.refresh_file_list()

    def setup_ui(self):
        # ======= Phần trên cùng: Dữ liệu và chọn thành phố =======
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", padx=10, pady=10)

        # Khung chọn file và thành phố bắt đầu
        data_frame = ttk.LabelFrame(top_frame, text="Dữ liệu")
        data_frame.pack(side="left", fill="y", padx=5, pady=5)

        ttk.Label(data_frame, text="Chọn file CSV:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.file_cb = ttk.Combobox(data_frame, state="readonly", width=25)
        self.file_cb.grid(row=0, column=1, padx=5, pady=5)
        self.file_cb.bind("<<ComboboxSelected>>", self.load_selected_file)

        ttk.Label(data_frame, text="Thành phố bắt đầu:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.start_city_cb = ttk.Combobox(data_frame, state="readonly", width=25)
        self.start_city_cb.grid(row=1, column=1, padx=5, pady=5)
        # Thêm binding cho sự kiện chọn thành phố xuất phát
        self.start_city_cb.bind("<<ComboboxSelected>>", self.update_start_city)

        # Khung chọn thành phố qua (checkbox)
        city_frame = ttk.LabelFrame(top_frame, text="Chọn thành phố muốn đi qua")
        city_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.city_canvas = tk.Canvas(city_frame)
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

        # ======= Phần giữa: cấu hình thuật toán + nút chạy + progress bar =======
        middle_frame = ttk.LabelFrame(self, text="Cấu hình thuật toán di truyền")
        middle_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(middle_frame, text="Thuật toán đột biến:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.mut_algo_cb = ttk.Combobox(middle_frame, values=['swap', 'scramble', 'inversion', 'insertion'], state='readonly', width=15)
        self.mut_algo_cb.current(0)
        self.mut_algo_cb.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(middle_frame, text="Thuật toán lai ghép:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.cross_algo_cb = ttk.Combobox(middle_frame, values=['order', 'single_point', 'two_point', 'uniform'], state='readonly', width=15)
        self.cross_algo_cb.current(0)
        self.cross_algo_cb.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(middle_frame, text="Thuật toán chọn lọc:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.sel_algo_cb = ttk.Combobox(middle_frame, values=['elitism', 'tournament', 'rank', 'roulette_wheel'], state='readonly', width=15)
        self.sel_algo_cb.current(0)
        self.sel_algo_cb.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(middle_frame, text="Số thế hệ:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.gen_entry = ttk.Entry(middle_frame, width=17)
        self.gen_entry.insert(0, "100")
        self.gen_entry.grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(middle_frame, text="Kích thước quần thể:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.pop_entry = ttk.Entry(middle_frame, width=17)
        self.pop_entry.insert(0, "100")
        self.pop_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(middle_frame, text="Tỉ lệ đột biến:").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.mut_entry = ttk.Entry(middle_frame, width=17)
        self.mut_entry.insert(0, "0.01")
        self.mut_entry.grid(row=2, column=3, padx=5, pady=5)

        # Nút chạy thuật toán to, màu xanh
        self.btn_process = ttk.Button(self, text="▶ Chạy thuật toán", command=self.start_process)
        self.btn_process.pack(pady=10, ipadx=10, ipady=5)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progressbar = ttk.Progressbar(self, variable=self.progress_var, maximum=100)
        self.progressbar.pack(fill="x", padx=20, pady=5)

        # Status bar
        self.status_var = tk.StringVar(value="Sẵn sàng")
        self.status_label = ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w")
        self.status_label.pack(fill="x", side="bottom")

        # ======= Phần dưới: kết quả =======
        result_frame = ttk.LabelFrame(self, text="Kết quả")
        result_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, font=("Consolas", 11))
        self.result_text.pack(fill="both", expand=True)

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
            
        # Tự động chọn thành phố xuất phát
        self.update_start_city()

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

    def start_process(self):
        # Khóa nút chạy trong lúc chạy
        self.btn_process.config(state="disabled")
        self.status_var.set("Đang chạy thuật toán...")
        self.progress_var.set(0)
        self.result_text.delete("1.0", tk.END)

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
            # Giả lập cập nhật progress để UI không bị "đóng băng"
            def progress_callback(progress_percent):
                self.progress_var.set(progress_percent)
                self.status_var.set(f"Đang chạy thuật toán... {progress_percent:.1f}%")
                self.update_idletasks()

            # Nếu GA không hỗ trợ callback, ta có thể fake progress
            # hoặc chỉnh sửa src.GA.genetic_algorithm để nhận callback nếu muốn.

            result = src.GA.genetic_algorithm(
                n_cities=len(valid_cities),
                distances=dist_matrix,
                population_size=population,
                generations=generations,
                mutation_rate=mutation_rate,
                mutation_algorithm=self.mut_algo_cb.get(),
                selection_algorithm=self.sel_algo_cb.get(),
                crossover_algorithm=self.cross_algo_cb.get()
                # Có thể thêm callback=progress_callback nếu bạn sửa src.GA
            )

            if 'route' not in result or 'distance' not in result:
                raise ValueError("Kết quả không hợp lệ")

            route = [i % len(valid_city_names) for i in result['route']]
            route_names_raw = [valid_city_names[i] for i in route]

            # Đưa start_city về đầu tuyến đường
            start_city_name = valid_city_names[0]  # Thành phố xuất phát đã được đưa vào vị trí đầu tiên
            if start_city_name in route_names_raw:
                start_idx = route_names_raw.index(start_city_name)
                route_names = route_names_raw[start_idx:] + route_names_raw[:start_idx]
            else:
                route_names = route_names_raw
                
            # Loại bỏ các thành phố trùng lặp liên tiếp trong lộ trình
            unique_route = []
            for city in route_names:
                # Chỉ thêm thành phố vào lộ trình nếu nó khác với thành phố trước đó
                if not unique_route or unique_route[-1] != city:
                    unique_route.append(city)
            
            # Đảm bảo tuyến đường kết thúc tại điểm xuất phát
            if unique_route and unique_route[0] != unique_route[-1]:
                unique_route.append(unique_route[0])  # Thêm thành phố bắt đầu vào cuối để hoàn thành chu trình

            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, f"Lộ trình tối ưu:\n{' -> '.join(unique_route)}\n")
            self.result_text.insert(tk.END, f"Tổng khoảng cách: {result['distance']:.2f} km\n")
            self.status_var.set("Hoàn thành")
            self.progress_var.set(100)
        except Exception as e:
            import traceback
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, f"Lỗi khi chạy thuật toán:\n{traceback.format_exc()}")
            self.status_var.set("Lỗi khi chạy thuật toán")

        self.btn_process.config(state="normal")

if __name__ == "__main__":
    app = TSPGUI()
    app.mainloop()