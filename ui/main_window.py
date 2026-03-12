# -*- coding: utf-8 -*-
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from core.config_generator import sinh_config
from core.connect import build_router_connect
from core.subnet import tinh_subnet
from core.routing import RoutingConfig
from core.routing_static import compute_static_routes, build_interface_ip_map
from core.topology import tao_topology
from services.exporter import export_configs
from services.preview_service import render_topology_diagram
from utils.constants import PROTOCOLS, TOPOLOGIES, normalize_topology_name


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cisco Network Builder v6.1")
        self.root.option_add("*Font", ("Segoe UI", 10))
        self.root.geometry("1100x760")
        self.root.minsize(650, 650)

        self.configs = {}
        self.router_entries = []
        self.router_cards = []
        self.router_card_width = 320
        self._layout_after_id = None

        self.build_ui()
        self._bind_global_mousewheel()

        self.root.mainloop()

    def build_ui(self):
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        self.config_tab = ttk.Frame(self.tabs)
        self.cli_tab = ttk.Frame(self.tabs)
        self.diagram_tab = ttk.Frame(self.tabs)

        self.tabs.add(self.config_tab, text="Cấu hình router")
        self.tabs.add(self.cli_tab, text="CLI")
        self.tabs.add(self.diagram_tab, text="Sơ đồ")

        self._build_config_tab()
        self.cli_text = self._create_text_tab(self.cli_tab)
        self.diagram_text = self._create_text_tab(self.diagram_tab)

    def _build_config_tab(self):
        header = ttk.LabelFrame(self.config_tab, text="Thiết lập chung")
        header.pack(fill=tk.X, padx=12, pady=8)

        header.columnconfigure(1, weight=1)
        header.columnconfigure(3, weight=1)

        ttk.Label(header, text="Mạng gốc").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.network_entry = ttk.Entry(header)
        self.network_entry.insert(0, "192.168.92.0/24")
        self.network_entry.grid(row=0, column=1, sticky="ew", padx=6, pady=4)

        ttk.Label(header, text="Số router").grid(row=0, column=2, sticky="w", padx=6, pady=4)
        self.router_count_var = tk.IntVar(value=2)
        self.router_count_entry = ttk.Entry(header, textvariable=self.router_count_var, width=8)
        self.router_count_entry.grid(row=0, column=3, sticky="w", padx=6, pady=4)

        ttk.Label(header, text="Kiểu kết nối").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        self.topology_combo = ttk.Combobox(header, values=TOPOLOGIES, state="readonly")
        self.topology_combo.current(0)
        self.topology_combo.grid(row=1, column=1, sticky="ew", padx=6, pady=4)

        ttk.Label(header, text="Routing động").grid(row=1, column=2, sticky="w", padx=6, pady=4)
        self.protocol_combo = ttk.Combobox(header, values=PROTOCOLS, state="readonly")
        self.protocol_combo.current(0)
        self.protocol_combo.grid(row=1, column=3, sticky="w", padx=6, pady=4)

        ttk.Label(header, text="Loại định tuyến").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        self.routing_type_var = tk.StringVar(value="Dynamic")
        self.routing_type_combo = ttk.Combobox(
            header,
            values=["Static", "Dynamic"],
            state="readonly",
            textvariable=self.routing_type_var,
        )
        self.routing_type_combo.grid(row=2, column=1, sticky="w", padx=6, pady=4)
        self.routing_type_combo.bind("<<ComboboxSelected>>", lambda _e: self._update_routing_fields())

        self.static_note = ttk.Label(
            header,
            text="Static: tự động tính toán (không cần nhập Network/Mask/Next Hop).",
            foreground="#444",
        )
        self.static_note.grid(row=3, column=0, columnspan=4, sticky="w", padx=6, pady=(0, 4))

        self.dhcp_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(header, text="Bật DHCP", variable=self.dhcp_var).grid(
            row=4, column=0, sticky="w", padx=6, pady=4
        )

        ttk.Button(header, text="Tạo router", command=self.build_router_panels).grid(
            row=4, column=1, sticky="w", padx=6, pady=4
        )
        ttk.Button(header, text="Sinh CLI", command=lambda: self.generate(select="cli")).grid(
            row=4, column=2, sticky="w", padx=6, pady=4
        )
        ttk.Button(header, text="Sinh sơ đồ", command=lambda: self.generate(select="diagram")).grid(
            row=4, column=3, sticky="w", padx=6, pady=4
        )
        ttk.Button(header, text="Xuất file", command=self.export).grid(
            row=4, column=4, sticky="w", padx=6, pady=4
        )

        guide = ttk.Label(
            self.config_tab,
            text=(
                "Hướng dẫn: Mỗi router có ít nhất 1 Ethernet và 2 Serial. "
                "Nhấn 'Thêm' để thêm cổng, 'Bớt' để bỏ cổng cuối."
            ),
        )
        guide.pack(fill=tk.X, padx=12, pady=(0, 6))

        self.label_check = ttk.Label(self.config_tab, text="Sơ đồ kết nối")
        self.label_check.pack(fill=tk.X, padx=12, pady=(0, 6))

        self.router_canvas = tk.Canvas(self.config_tab, highlightthickness=0)
        self.router_scroll = ttk.Scrollbar(self.config_tab, orient="vertical", command=self.router_canvas.yview)
        self.router_canvas.configure(yscrollcommand=self.router_scroll.set)

        self.router_container = ttk.Frame(self.router_canvas)
        self.router_container.bind(
            "<Configure>",
            lambda event: self.router_canvas.configure(scrollregion=self.router_canvas.bbox("all")),
        )
        self.router_canvas.bind("<Configure>", self._on_router_canvas_resize)

        self.router_canvas.create_window((0, 0), window=self.router_container, anchor="nw")
        self.router_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        self.router_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 12))

        self.build_router_panels()
        self._update_routing_fields()

    def _create_text_tab(self, container):
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        text = tk.Text(container, wrap="none")
        vsb = ttk.Scrollbar(container, orient="vertical", command=text.yview)
        hsb = ttk.Scrollbar(container, orient="horizontal", command=text.xview)

        text.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        text.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        return text

    def build_router_panels(self):
        for child in self.router_container.winfo_children():
            child.destroy()

        self.router_entries = []
        self.router_cards = []

        try:
            so_router = int(self.router_count_entry.get())
        except ValueError:
            raise ValueError("Số router không hợp lệ.")

        if so_router < 1:
            raise ValueError("Số router phải lớn hơn hoặc bằng 1.")

        for index in range(so_router):
            router_label = f"R{index + 1}"
            frame = ttk.LabelFrame(self.router_container, text=f"Router {router_label}")
            frame.configure(width=self.router_card_width)

            ethernet_entries = self._create_port_section(
                frame,
                title="Ethernet",
                router_label=router_label,
                min_count=1,
                default_values=["fa1/0"],
            )
            serial_entries = self._create_port_section(
                frame,
                title="Serial",
                router_label=router_label,
                min_count=2,
                default_values=["se2/0", "se3/0"],
            )

            self.router_entries.append({"eth": ethernet_entries, "ser": serial_entries})
            self.router_cards.append(frame)

        self._layout_router_cards()

    def _layout_router_cards(self):
        if not self.router_cards:
            return

        available_width = self.router_canvas.winfo_width()
        if available_width <= 1:
            available_width = self.router_container.winfo_width()

        card_width = self.router_card_width
        column_count = max(1, available_width // (card_width + 24))

        for index, card in enumerate(self.router_cards):
            row = index // column_count
            col = index % column_count
            card.grid(row=row, column=col, padx=8, pady=6, sticky="nw")

        for col in range(column_count):
            self.router_container.columnconfigure(col, minsize=self.router_card_width)

    def _on_router_canvas_resize(self, _event):
        if self._layout_after_id is not None:
            self.root.after_cancel(self._layout_after_id)
        self._layout_after_id = self.root.after(80, self._layout_router_cards)

    def _bind_global_mousewheel(self):
        self.root.bind_all("<MouseWheel>", self._on_mousewheel, add="+")
        self.root.bind_all("<Shift-MouseWheel>", self._on_shift_mousewheel, add="+")

    def _on_mousewheel(self, event):
        self._scroll_widget(event, horizontal=False)

    def _on_shift_mousewheel(self, event):
        self._scroll_widget(event, horizontal=True)

    def _scroll_widget(self, event, horizontal):
        target = self.root.winfo_containing(self.root.winfo_pointerx(), self.root.winfo_pointery())
        if target is None:
            return

        delta = int(-1 * (event.delta / 120))

        widget = target
        while widget is not None:
            if horizontal and hasattr(widget, "xview_scroll"):
                widget.xview_scroll(delta, "units")
                return "break"
            if not horizontal and hasattr(widget, "yview_scroll"):
                widget.yview_scroll(delta, "units")
                return "break"
            widget = widget.master

    def _update_routing_fields(self):
        routing_type = self.routing_type_var.get()
        if routing_type == "Static":
            self.static_note.grid()
            self.protocol_combo.configure(state="disabled")
        else:
            self.static_note.grid_remove()
            self.protocol_combo.configure(state="readonly")

    def _create_port_section(self, parent, title, router_label, min_count, default_values):
        section = ttk.Frame(parent)
        section.pack(fill=tk.X, padx=10, pady=6)

        ttk.Label(section, text=f"{title} của {router_label} (tối thiểu {min_count})").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            section,
            text="Thêm/bớt cổng bằng các nút bên dưới.",
            foreground="#444",
        ).grid(row=1, column=0, sticky="w", pady=(0, 6))

        entries_frame = ttk.Frame(section)
        entries_frame.grid(row=2, column=0, sticky="ew")
        entries_frame.columnconfigure(0, weight=1)
        entries_frame.columnconfigure(1, weight=1)

        entries = []

        def layout_entries():
            for idx, entry in enumerate(entries):
                row = idx // 2
                col = idx % 2
                entry.grid(row=row, column=col, padx=(0, 6), pady=4, sticky="w")

        def add_port(default_value=""):
            entry = ttk.Entry(entries_frame, width=20)
            entry.insert(0, default_value)
            entries.append(entry)
            layout_entries()

        def remove_port():
            if len(entries) <= min_count:
                return
            entry = entries.pop()
            entry.destroy()
            layout_entries()

        for value in default_values:
            add_port(value)

        buttons = ttk.Frame(section)
        buttons.grid(row=3, column=0, sticky="w", pady=(4, 0))
        ttk.Button(buttons, text=f"Thêm {title}", command=add_port).pack(side=tk.LEFT)
        ttk.Button(buttons, text=f"Bớt {title}", command=remove_port).pack(side=tk.LEFT, padx=(6, 0))

        return entries

    def _collect_ports(self):
        routers = []
        for index, router in enumerate(self.router_entries):
            router_label = f"R{index + 1}"
            ethernet_ports = [entry.get().strip() for entry in router["eth"] if entry.get().strip()]
            serial_ports = [entry.get().strip() for entry in router["ser"] if entry.get().strip()]
            routers.append(build_router_connect(router_label, ethernet_ports, serial_ports))
        return routers

    def generate(self, select="cli"):
        try:
            mang = self.network_entry.get().strip()
            so_router = int(self.router_count_entry.get())
            topology = normalize_topology_name(self.topology_combo.get())
            dhcp = self.dhcp_var.get()
            routing_type = self.routing_type_var.get()
            protocol = self.protocol_combo.get()

            routing_config = RoutingConfig(
                routing_type="STATIC" if routing_type == "Static" else "DYNAMIC",
                protocol=protocol if routing_type != "Static" else None,
                auto_static=True if routing_type == "Static" else False,
            )
            routing_config.validate()

            if so_router != len(self.router_entries):
                raise ValueError("Vui lòng nhấn 'Tạo router' sau khi đổi số router.")

            router_ports = self._collect_ports()

            lan, wan = tinh_subnet(mang, so_router, topology)
            serial_ports_by_router = [router.serial_ports for router in router_ports]
            topo, edges = tao_topology(so_router, wan, topology, serial_ports_by_router)

            static_routes = None
            if routing_config.routing_type == "STATIC":
                static_routes = compute_static_routes(lan, topo)

            interface_map = build_interface_ip_map(
                lan,
                topo,
                [router.ethernet_ports for router in router_ports],
            )

            self.configs = {}
            for i in range(so_router):
                cfg = sinh_config(
                    i + 1,
                    lan[i],
                    topo[i],
                    dhcp,
                    ethernet_ports=router_ports[i].ethernet_ports,
                    routing_type=routing_config.routing_type,
                    routing_protocol=protocol,
                    static_routes=static_routes[i] if static_routes else None,
                )
                self.configs[f"R{i + 1}"] = cfg

            self.cli_text.delete(1.0, tk.END)
            for router_name, config_text in self.configs.items():
                self.cli_text.insert(tk.END, f"\n===== {router_name} =====\n")
                self.cli_text.insert(tk.END, config_text)

            if routing_config.routing_type == "STATIC":
                routing_label = "Routing: Static"
            else:
                routing_label = f"Routing: {protocol}"
            diagram_text = render_topology_diagram(
                edges, routing_label=routing_label, router_interfaces=interface_map
            )
            self.diagram_text.delete(1.0, tk.END)
            self.diagram_text.insert(tk.END, diagram_text)

            if select == "diagram":
                self.tabs.select(self.diagram_tab)
            else:
                self.tabs.select(self.cli_tab)

        except Exception as exc:
            messagebox.showerror("Lỗi", str(exc))

    def export(self):
        try:
            if not self.configs:
                raise ValueError("Chưa có config để xuất file.")

            output_dir = filedialog.askdirectory(title="Chọn thư mục lưu file")
            if not output_dir:
                return

            base_name = simpledialog.askstring("Tên file", "Nhập tên file (không cần .txt)")
            if base_name is None:
                return
            base_name = base_name.strip()
            if not base_name:
                raise ValueError("Tên file không được để trống.")

            for router_name in self.configs.keys():
                path = os.path.join(output_dir, f"{base_name}_{router_name}.txt")
                if os.path.exists(path):
                    overwrite = messagebox.askyesno(
                        "Ghi đè file",
                        f"File đã tồn tại:\n{path}\nBạn có muốn ghi đè không?",
                    )
                    if not overwrite:
                        return
                    break

            export_configs(self.configs, output_dir, base_name)
            messagebox.showinfo("Thành công", "Đã xuất config theo thư mục đã chọn.")
        except Exception as exc:
            messagebox.showerror("Lỗi", str(exc))
