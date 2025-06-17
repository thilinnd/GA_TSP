import sys
import os
import csv
import tempfile
import folium
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QComboBox, QListWidget, QListWidgetItem,
    QLineEdit, QTextEdit, QMessageBox, QProgressBar
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QUrl 
import src.GA
import src.TSP
vn_to_en_provinces = {
    "An Giang": "An Giang",
    "Bà Rịa-Vũng Tàu": "Ba Ria - Vung Tau",
    "Bắc Giang": "Bac Giang",
    "Bắc Kạn": "Bac Kan",
    "Bạc Liêu": "Bac Lieu",
    "Bắc Ninh": "Bac Ninh",
    "Bến Tre": "Ben Tre",
    "Bình Dương": "Binh Duong",
    "Bình Định": "Binh Dinh",
    "Bình Phước": "Binh Phuoc",
    "Bình Thuận": "Binh Thuan",
    "Cà Mau": "Ca Mau",
    "Cao Bằng": "Cao Bang",
    "Thành phố Cần Thơ": "Can Tho City",
    "Cần Thơ": "Can Tho City",
    "Đà Nẵng": "Da Nang City",
    "Đắk Lắk": "Dak Lak",
    "Đắk Nông": "Dak Nong",
    "Điện Biên": "Dien Bien",
    "Đồng Nai": "Dong Nai",
    "Đồng Tháp": "Dong Thap",
    "Gia Lai": "Gia Lai",
    "Hà Giang": "Ha Giang",
    "Hà Nam": "Ha Nam",
    "Hà Nội": "Hanoi",
    "Hà Tĩnh": "Ha Tinh",
    "Hải Dương": "Hai Duong",
    "Hải Phòng": "Hai Phong",
    "Hậu Giang": "Hau Giang",
    "Hòa Bình": "Hoa Binh",
    "Hồ Chí Minh": "Ho Chi Minh City",
    "TP. Hồ Chí Minh": "Ho Chi Minh City",
    "Hưng Yên": "Hung Yen",
    "Khánh Hòa": "Khanh Hoa",
    "Kiên Giang": "Kien Giang",
    "Kon Tum": "Kon Tum",
    "Lai Châu": "Lai Chau",
    "Lâm Đồng": "Lam Dong",
    "Lạng Sơn": "Lang Son",
    "Lào Cai": "Lao Cai",
    "Long An": "Long An",
    "Nam Định": "Nam Dinh",
    "Nghệ An": "Nghe An",
    "Ninh Bình": "Ninh Binh",
    "Ninh Thuận": "Ninh Thuan",
    "Phú Thọ": "Phu Tho",
    "Phú Yên": "Phu Yen",
    "Quảng Bình": "Quang Binh",
    "Quảng Nam": "Quang Nam",
    "Quảng Ngãi": "Quang Ngai",
    "Quảng Ninh": "Quang Ninh",
    "Quảng Trị": "Quang Tri",
    "Sóc Trăng": "Soc Trang",
    "Sơn La": "Son La",
    "Tây Ninh": "Tay Ninh",
    "Thái Bình": "Thai Binh",
    "Thái Nguyên": "Thai Nguyen",
    "Thanh Hóa": "Thanh Hoa",
    "Thừa Thiên - Huế": "Thua Thien Hue",
    "Thừa Thiên Huế": "Thua Thien Hue",
    "Tiền Giang": "Tien Giang",
    "TP Hồ Chí Minh": "Ho Chi Minh City",
    "Trà Vinh": "Tra Vinh",
    "Tuyên Quang": "Tuyen Quang",
    "Vĩnh Long": "Vinh Long",
    "Vĩnh Phúc": "Vinh Phuc",
    "Vũng Tàu": "Vung Tau",
    "Yên Bái": "Yen Bai"
}


class TSPPyQtApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TSP Genetic Algorithm with Embedded Map (PyQt5)")
        self.setGeometry(100, 100, 1400, 800)

        self.city_data = {}
        self.current_route = []
        self.current_coords = []

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # Left panel
        control_panel = QVBoxLayout()

        # Load CSV
        self.csv_file_cb = QComboBox()
        self.csv_file_cb.addItem("Select CSV file")
        import os
        csv_dir = "./data"
        if os.path.exists(csv_dir):
            for fname in os.listdir(csv_dir):
                if fname.endswith('.csv'):
                    full_path = os.path.join(csv_dir, fname)
                    self.csv_file_cb.addItem(fname,full_path)
        self.csv_file_cb.currentIndexChanged.connect(self.load_csv_from_dropdown)
        control_panel.addWidget(QLabel("Select CSV File"))
        control_panel.addWidget(self.csv_file_cb)


        # Start city
        self.start_city_cb = QComboBox()
        self.start_city_cb.currentIndexChanged.connect(self.sync_start_city_selection)
        control_panel.addWidget(QLabel("Start City"))
        control_panel.addWidget(self.start_city_cb)
        self.start_city_cb.currentIndexChanged.connect(self.sync_start_city_selection)


        # City checklist
        control_panel.addWidget(QLabel("Select Cities"))
        self.city_list = QListWidget()
        control_panel.addWidget(self.city_list)

        #Toggle city check state
        self.city_list.itemClicked.connect(self.toggle_city_checkstate)


        #Select all, deselect all buttons
        btn_layout = QHBoxLayout()
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self.select_all_cities)
        btn_layout.addWidget(self.select_all_btn)
        self.deselect_all_btn = QPushButton("Deselect All")
        self.deselect_all_btn.clicked.connect(self.deselect_all_cities)
        btn_layout.addWidget(self.deselect_all_btn)
        control_panel.addLayout(btn_layout)
         #Alogorithm selection
        self.mut_algo_cb = QComboBox()
        self.mut_algo_cb.addItems(['swap', 'scramble', 'inversion', 'insertion'])
        self.cross_algo_cb = QComboBox()
        self.cross_algo_cb.addItems(['order', 'single_point', 'two_point', 'uniform'])
        self.sel_algo_cb = QComboBox()
        self.sel_algo_cb.addItems(['elitism', 'tournament', 'rank', 'roulette_wheel'])


        # GA config
        control_panel.addWidget(QLabel("Generations"))
        self.gen_input = QLineEdit("100")
        control_panel.addWidget(self.gen_input)

        control_panel.addWidget(QLabel("Population Size"))
        self.pop_input = QLineEdit("100")
        control_panel.addWidget(self.pop_input)

        control_panel.addWidget(QLabel("Mutation Rate"))
        self.mut_input = QLineEdit("0.01")
        control_panel.addWidget(self.mut_input)
        control_panel.addWidget(QLabel("Mutation Algorithm"))
        control_panel.addWidget(self.mut_algo_cb)
        control_panel.addWidget(QLabel("Crossover Algorithm"))
        control_panel.addWidget(self.cross_algo_cb)
        control_panel.addWidget(QLabel("Selection Algorithm"))
        control_panel.addWidget(self.sel_algo_cb)


        # Algorithm button
        self.run_button = QPushButton("Run Algorithm")
        self.run_button.clicked.connect(self.run_algorithm)
        control_panel.addWidget(self.run_button)

        # Progress bar
        self.progress = QProgressBar()
        control_panel.addWidget(self.progress)

        # Result text
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        control_panel.addWidget(self.result_text)

        # Add left panel
        main_layout.addLayout(control_panel, 4)

        # Map view
        self.map_view = QWebEngineView()
        main_layout.addWidget(self.map_view, 6)
    def toggle_city_checkstate(self, item):
        if not (item.flags() & Qt.ItemIsEnabled):
           return

        if item.checkState() == Qt.Checked:
           item.setCheckState(Qt.Unchecked)
        else:
           item.setCheckState(Qt.Checked)

    def select_all_cities(self):
        for i in range(self.city_list.count()):
            item = self.city_list.item(i)
            if item.flags() & Qt.ItemIsEnabled:
               item.setCheckState(Qt.Checked)
    def deselect_all_cities(self):
        for i in range(self.city_list.count()):
            item = self.city_list.item(i)
            if item.flags() & Qt.ItemIsEnabled:
                item.setCheckState(Qt.Unchecked)

    def sync_start_city_selection(self):
        selected_start = self.start_city_cb.currentText()

        for i in range(self.city_list.count()):
            item = self.city_list.item(i)

        # Enable tất cả trước
            item.setFlags(item.flags() | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)

            if item.text() == selected_start:
               item.setCheckState(Qt.Checked)
               item.setFlags(item.flags() & ~Qt.ItemIsEnabled) 


    def load_csv_from_dropdown(self):
        path = self.csv_file_cb.currentData()
        if not path or not path.endswith('.csv'):
            return

        self.city_data.clear()
        self.city_list.clear()
        self.start_city_cb.clear()

        try:
            with open(path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                cities = []
                for row in reader:
                    city = row.get('province') or row.get('city') or row.get('name')
                    lat = row.get('lat')
                    lon = row.get('lon')
                    if city and lat and lon:
                        self.city_data[city] = (float(lat), float(lon))
                        cities.append(city)
            if not cities:
                QMessageBox.warning(self, "Warning", "No valid cities found in CSV.")
                return
            cities_en = [vn_to_en_provinces.get(city, city) for city in cities]
            self.en_to_vn_city = {
            en: vn for vn, en in zip(cities, cities_en)
            }

            default_start = cities_en[0]
            self.start_city_cb.addItems(cities_en)
            self.start_city_cb.setCurrentText(default_start)
            for city in cities_en:
                item = QListWidgetItem(city)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                if city == default_start:
                    item.setCheckState(Qt.Checked)
                    item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
                else:
                    item.setCheckState(Qt.Unchecked)
                self.city_list.addItem(item)


        
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def run_algorithm(self):
        start_city = self.start_city_cb.currentText()
        if not start_city:
            QMessageBox.warning(self, "Warning", "Please select a start city.")
            return
        selected_cities = []
        for i in range(self.city_list.count()):
            item = self.city_list.item(i)
            if item.checkState() == Qt.Checked or not (item.flags() & Qt.ItemIsEnabled):
                selected_cities.append(item.text())
        if start_city not in selected_cities:
            selected_cities.insert(0, start_city)

        if len(selected_cities) < 3:
            QMessageBox.warning(self, "Warning", "Select at least 3 cities.")
            return

        try:
            generations = int(self.gen_input.text())
            population = int(self.pop_input.text())
            mutation_rate = float(self.mut_input.text())
        except:
            QMessageBox.warning(self, "Error", "Invalid input parameters.")
            return
        mutation_algo = self.mut_algo_cb.currentText()
        crossover_algo = self.cross_algo_cb.currentText()
        selection_algo = self.sel_algo_cb.currentText()

        coords = [self.city_data[self.en_to_vn_city[city_en]] for city_en in selected_cities]
        dist_matrix = src.TSP.compute_distance_matrix(coords)

        best_result = None
        nums_run =5
        for i in range(nums_run):
            self.progress.setValue(int((i + 1) / nums_run * 100))
            result = src.GA.genetic_algorithm(
                n_cities=len(coords),
                distances=dist_matrix,
                population_size=population,
                generations=generations,
                mutation_rate=mutation_rate,
                mutation_algorithm= mutation_algo,
                selection_algorithm= selection_algo,
                crossover_algorithm= crossover_algo,
            )
            if not best_result or result["distance"] < best_result["distance"]:
                best_result = result.copy()
                

        route = best_result["route"]
        route_coords = [coords[i] for i in route]
        route_names = [selected_cities[i] for i in route]
        if route_names[0].strip().lower() == route_names[-1].strip().lower():
            route_names = route_names[:-1]
            route_coords = route_coords[:-1]
        if start_city in route_names:
            start_idx = route_names.index(start_city)
            route_names = route_names[start_idx:] + route_names[:start_idx]
            route_coords = route_coords[start_idx:] + route_coords[:start_idx]
        route_names.append(route_names[0])
        route_coords.append(route_coords[0])
        route_names_en = [vn_to_en_provinces.get(name, name) for name in route_names]
        print("Final route names (after rotate + fix):", route_names_en)

        self.result_text.clear()
        self.result_text.append("<b>Optimal TSP Route:</b>")
        self.result_text.append(" → ".join(route_names_en))
        self.result_text.append(f"<b>Distance:</b> {best_result['distance']:.2f} km")

        self.current_route = route_names_en
        self.current_coords = route_coords
        self.show_map()

    def show_map(self):
        if not self.current_coords:
            return

        m = folium.Map(location=self.current_coords[0], zoom_start=6)
        for i, (city, coord) in enumerate(zip(self.current_route, self.current_coords)):
            
            if i == len(self.current_route) - 1 and city == self.current_route[0]:
                 icon = folium.Icon(color='red', icon='stop', prefix='fa')
                 popup_text = f"Starting and ending: {city}"
            else:
                icon = folium.Icon(color='blue', icon='map-marker', prefix='fa')
                popup_text = f"{i}. {city}"
            folium.Marker(coord, popup=popup_text, icon=icon).add_to(m)
        folium.PolyLine(self.current_coords, color="red").add_to(m)

        import uuid, tempfile, os
        tmp_path = os.path.join(tempfile.gettempdir(), f"map_{uuid.uuid4().hex}.html")
        m.save(tmp_path)
        self.map_view.load(QUrl.fromLocalFile(tmp_path))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TSPPyQtApp()
    window.show()
    sys.exit(app.exec_())
