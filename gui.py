import tkinter as tk
from tkinter import ttk, messagebox
from db_connection import list_computers, add_computer, add_router, resolve_dns, delete_computer_by_id, update_computer, list_routers, delete_router_by_id, get_computer_by_id  # Не забывайте создать функцию add_router

class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Management App")
        self.root.geometry("900x600")  # Увеличенное окно
        self.root.config(bg="#e0f7fa")  # Фон приложения
        self.root.iconbitmap("assets/icon.ico")  # Иконка приложения
        self.create_tabs()

    def create_tabs(self):
        tab_control = ttk.Notebook(self.root)
        self.tab_computers = ttk.Frame(tab_control)
        self.tab_dns = ttk.Frame(tab_control)
        self.tab_add_computer = ttk.Frame(tab_control)
        self.tab_add_router = ttk.Frame(tab_control)
        self.tab_routers = ttk.Frame(tab_control)  # Новая вкладка для маршрутизаторов

        tab_control.add(self.tab_computers, text="Computers", padding=10)
        tab_control.add(self.tab_dns, text="DNS Resolver", padding=10)
        tab_control.add(self.tab_add_computer, text="Add Computer", padding=10)
        tab_control.add(self.tab_add_router, text="Add Router", padding=10)
        tab_control.add(self.tab_routers, text="Routers", padding=10)  # Добавляем вкладку маршрутизаторов

        tab_control.pack(expand=1, fill="both", padx=20, pady=20)

        self.create_computers_tab()
        self.create_dns_tab()
        self.create_add_computer_tab()
        self.create_add_router_tab()
        self.create_routers_tab()  # Создаем вкладку маршрутизаторов

        self.tab_simulation = ttk.Frame(tab_control)  # Новая вкладка Simulation
        tab_control.add(self.tab_simulation, text="Simulation", padding=10)
        self.create_simulation_tab()  # Создаём вкладку Simulation

    def create_routers_tab(self):
        self.routers_label = tk.Label(self.tab_routers, text="Routers List", font=("Arial", 20, "bold"), bg="#0097A7", fg="white", pady=10)
        self.routers_label.pack(fill="x", padx=10)

        self.routers_listbox = tk.Listbox(self.tab_routers, font=("Arial", 14), height=10, bg="#ffffff", fg="#333333")
        self.routers_listbox.pack(fill="both", expand=True, padx=10, pady=10)

        # Кнопка обновления списка маршрутизаторов
        self.refresh_routers_button = ttk.Button(self.tab_routers, text="Refresh", command=self.refresh_routers_list, style="TButton")
        self.refresh_routers_button.pack(pady=5)

        # Кнопка для удаления маршрутизатора
        self.delete_router_button = ttk.Button(self.tab_routers, text="Delete Router", command=self.delete_router, style="TButton")
        self.delete_router_button.pack(pady=5)

        self.refresh_routers_list()  # Первоначальное заполнение списка

    def refresh_routers_list(self):
        """Обновляет список маршрутизаторов."""
        self.routers_listbox.delete(0, tk.END)
        routers = list_routers()  # Получаем список маршрутизаторов из базы данных
        for router in routers:
            self.routers_listbox.insert(tk.END, f"ID: {router[0]} | IP: {router[1]} | MAC: {router[2]}")

    def delete_router(self):
        """Удаляет выбранный маршрутизатор."""
        selected = self.routers_listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "Please select a router to delete.")
            return

        router_info = self.routers_listbox.get(selected)
        router_id = router_info.split('|')[0].strip().replace("ID: ", "")

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Router ID: {router_id}?")
        if confirm:
            try:
                delete_router_by_id(router_id)  # Вызов функции удаления из базы данных
                messagebox.showinfo("Success", f"Router ID: {router_id} deleted successfully!")
                self.refresh_routers_list()  # Обновляем список после удаления
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete router: {e}")



    def create_computers_tab(self):
        # Вкладка с компьютерами
        self.computers_label = tk.Label(self.tab_computers, text="Computers List", font=("Arial", 20, "bold"), bg="#0097A7", fg="white", pady=10)
        self.computers_label.pack(fill="x", padx=10)

        self.computers_listbox = tk.Listbox(self.tab_computers, font=("Arial", 14), height=10, bg="#ffffff", fg="#333333", bd=0, highlightthickness=0, selectmode=tk.SINGLE)
        self.computers_listbox.pack(fill="both", expand=True, padx=10, pady=10)

        # Кнопка обновления списка
        self.refresh_computers_button = ttk.Button(self.tab_computers, text="Refresh", command=self.refresh_computers, style="TButton")
        self.refresh_computers_button.pack(pady=5)

        # Кнопка добавления компьютера
        self.add_computer_button = ttk.Button(self.tab_computers, text="Add Computer", command=self.switch_to_add_computer_tab, style="TButton")
        self.add_computer_button.pack(pady=5)
        # Для редактирования
        self.edit_computer_button = ttk.Button(self.tab_computers, text="Edit Computer", command=self.edit_computer, style="TButton")  # Новая кнопка
        self.edit_computer_button.pack(pady=5)

        # Кнопка удаления компьютера
        self.delete_computer_button = ttk.Button(self.tab_computers, text="Delete Computer", command=self.delete_computer, style="TButton")
        self.delete_computer_button.pack(pady=5)

        self.refresh_computers()

    def edit_computer(self):
        selected = self.computers_listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "Please select a computer to edit.")
            return

        computer_info = self.computers_listbox.get(selected)
        computer_id = computer_info.split('|')[0].replace("ID: ", "").strip()

        # Сохраняем ID для редактирования
        self.current_editing_id = computer_id

        # Получаем полную информацию о компьютере
        computer_data = get_computer_by_id(computer_id)

        if computer_data:
            ip, mac, router_id, network_name = computer_data

            # Заполняем поля во вкладке "Add Computer"
            self.ip_entry_computer.delete(0, tk.END)
            self.ip_entry_computer.insert(0, ip)

            self.mac_entry_computer.delete(0, tk.END)
            self.mac_entry_computer.insert(0, mac)

            self.router_id_entry_computer.delete(0, tk.END)
            self.router_id_entry_computer.insert(0, router_id if router_id else "")

            self.network_name_entry_computer.delete(0, tk.END)
            self.network_name_entry_computer.insert(0, network_name if network_name else "")

            # Переключаемся на вкладку "Add Computer"
            self.switch_to_add_computer_tab()

            # Меняем текст кнопки на "Change"
            self.submit_button_computer.config(text="Change", command=self.change_computer)
        else:
            messagebox.showerror("Error", "Failed to load computer data.")

    def change_computer(self):
        ip = self.ip_entry_computer.get()
        mac = self.mac_entry_computer.get()
        router_id = self.router_id_entry_computer.get()
        network_name = self.network_name_entry_computer.get()

        if ip and mac and router_id and network_name:
            try:
                update_computer(self.current_editing_id, ip, mac, router_id, network_name)  # Обновляем данные
                messagebox.showinfo("Success", "Computer updated successfully!")
                self.clear_computer_fields()
                self.submit_button_computer.config(text="Add Computer", command=self.submit_computer)  # Возвращаем кнопку к исходному состоянию
                self.refresh_computers()
                self.switch_to_computers_tab()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update computer: {e}")
        else:
            messagebox.showerror("Error", "Please fill in all fields.")

    def parse_computer_info(self, computer_info):
        parts = computer_info.split('|')
        computer_id = parts[0].replace("ID: ", "").strip()
        ip = parts[1].replace("IP: ", "").strip()
        mac = parts[2].replace("MAC: ", "").strip()
        return computer_id, ip, mac

    def refresh_computers(self):
        self.refresh_computers_button.config(text="Loading...", state=tk.DISABLED)  # Ожидание
        self.root.update()  # Обновляем интерфейс

        # Получаем список компьютеров и отображаем их
        computers = list_computers()
        self.computers_listbox.delete(0, tk.END)
        for computer in computers:
            self.computers_listbox.insert(tk.END, f"ID: {computer[0]} | IP: {computer[1]} | MAC: {computer[2]}")

        self.refresh_computers_button.config(text="Refresh", state=tk.NORMAL)  # Возвращаем кнопке исходное состояние

    def switch_to_add_computer_tab(self):
        self.root.nametowidget(self.root.winfo_children()[0].winfo_name()).select(self.tab_add_computer)

    def create_add_computer_tab(self):
        # Поля для добавления компьютера
        self.ip_label_computer = tk.Label(self.tab_add_computer, text="IP Address", font=("Arial", 14))
        self.ip_label_computer.pack(pady=5)
        self.ip_entry_computer = ttk.Entry(self.tab_add_computer, font=("Arial", 14))
        self.ip_entry_computer.pack(pady=5)

        self.mac_label_computer = tk.Label(self.tab_add_computer, text="MAC Address", font=("Arial", 14))
        self.mac_label_computer.pack(pady=5)
        self.mac_entry_computer = ttk.Entry(self.tab_add_computer, font=("Arial", 14))
        self.mac_entry_computer.pack(pady=5)

        self.router_id_label_computer = tk.Label(self.tab_add_computer, text="Router ID", font=("Arial", 14))
        self.router_id_label_computer.pack(pady=5)
        self.router_id_entry_computer = ttk.Entry(self.tab_add_computer, font=("Arial", 14))
        self.router_id_entry_computer.pack(pady=5)

        self.network_name_label_computer = tk.Label(self.tab_add_computer, text="Network Name", font=("Arial", 14))
        self.network_name_label_computer.pack(pady=5)
        self.network_name_entry_computer = ttk.Entry(self.tab_add_computer, font=("Arial", 14))
        self.network_name_entry_computer.pack(pady=5)

        self.submit_button_computer = ttk.Button(self.tab_add_computer, text="Add Computer", command=self.submit_computer, style="TButton")
        self.submit_button_computer.pack(pady=10)

    def submit_computer(self):
        ip = self.ip_entry_computer.get()
        mac = self.mac_entry_computer.get()
        router_id = self.router_id_entry_computer.get()
        network_name = self.network_name_entry_computer.get()

        if ip and mac and router_id and network_name:
            try:
                add_computer(ip, mac, router_id, network_name)
                messagebox.showinfo("Success", "Computer added successfully!")
                self.clear_computer_fields()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add computer: {e}")
        else:
            messagebox.showerror("Error", "Please fill in all fields.")

    def delete_computer(self):
        selected = self.computers_listbox.curselection()  # Получаем индекс выбранного элемента
        if not selected:
            messagebox.showerror("Error", "Please select a computer to delete.")
            return

    # Получаем текст выбранного элемента и извлекаем ID
        computer_info = self.computers_listbox.get(selected)
        computer_id = computer_info.split('|')[0].strip().replace("ID: ", "")

    # Подтверждение удаления
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Computer ID: {computer_id}?")
        if not confirm:
            return

        try:
            delete_computer_by_id(computer_id)  # Вызов функции удаления
            messagebox.showinfo("Success", f"Computer ID: {computer_id} deleted successfully!")
            self.refresh_computers()  # Обновляем список после удаления
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete computer: {e}")

    def switch_to_computers_tab(self):
        self.root.nametowidget(self.root.winfo_children()[0].winfo_name()).select(self.tab_computers)

    def create_dns_tab(self):
        # Вкладка с DNS
        self.dns_label = tk.Label(self.tab_dns, text="DNS Resolver", font=("Arial", 20, "bold"), bg="#0097A7", fg="white", pady=10)
        self.dns_label.pack(fill="x", padx=10)

        self.dns_entry = ttk.Entry(self.tab_dns, font=("Arial", 14), width=30)
        self.dns_entry.pack(pady=10)

        self.dns_button = ttk.Button(self.tab_dns, text="Resolve", command=self.resolve_dns, style="TButton")
        self.dns_button.pack(pady=10)

        self.dns_result_label = tk.Label(self.tab_dns, text="Result: ", font=("Arial", 14), bg="#e0f7fa", fg="#333333")
        self.dns_result_label.pack(pady=10)

    def resolve_dns(self):
        domain_name = self.dns_entry.get()
        result = resolve_dns(domain_name)
        if result:
            self.dns_result_label.config(text=f"Result: {result}")
        else:
            messagebox.showerror("Error", "Domain not found!")

    def create_add_router_tab(self):
        # Поля для добавления маршрутизатора
        self.ip_label_router = tk.Label(self.tab_add_router, text="IP Address", font=("Arial", 14))
        self.ip_label_router.pack(pady=5)
        self.ip_entry_router = ttk.Entry(self.tab_add_router, font=("Arial", 14))
        self.ip_entry_router.pack(pady=5)

        self.mac_label_router = tk.Label(self.tab_add_router, text="MAC Address", font=("Arial", 14))
        self.mac_label_router.pack(pady=5)
        self.mac_entry_router = ttk.Entry(self.tab_add_router, font=("Arial", 14))
        self.mac_entry_router.pack(pady=5)

        self.public_ip_label_router = tk.Label(self.tab_add_router, text="Public IP Address", font=("Arial", 14))
        self.public_ip_label_router.pack(pady=5)
        self.public_ip_entry_router = ttk.Entry(self.tab_add_router, font=("Arial", 14))
        self.public_ip_entry_router.pack(pady=5)

        self.network_name_label_router = tk.Label(self.tab_add_router, text="Network Name", font=("Arial", 14))
        self.network_name_label_router.pack(pady=5)
        self.network_name_entry_router = ttk.Entry(self.tab_add_router, font=("Arial", 14))
        self.network_name_entry_router.pack(pady=5)

        self.submit_router_button = ttk.Button(self.tab_add_router, text="Add Router", command=self.submit_router, style="TButton")
        self.submit_router_button.pack(pady=10)

    def submit_router(self):
        ip = self.ip_entry_router.get()
        mac = self.mac_entry_router.get()
        public_ip = self.public_ip_entry_router.get()
        network_name = self.network_name_entry_router.get()

        if ip and mac and public_ip and network_name:
            try:
                add_router(ip, mac, public_ip, network_name)
                messagebox.showinfo("Success", "Router added successfully!")
                self.clear_router_fields()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add router: {e}")
        else:
            messagebox.showerror("Error", "Please fill in all fields.")

    def clear_computer_fields(self):
        self.ip_entry_computer.delete(0, tk.END)
        self.mac_entry_computer.delete(0, tk.END)
        self.router_id_entry_computer.delete(0, tk.END)
        self.network_name_entry_computer.delete(0, tk.END)

    def clear_router_fields(self):
        self.ip_entry_router.delete(0, tk.END)
        self.mac_entry_router.delete(0, tk.END)
        self.public_ip_entry_router.delete(0, tk.END)
        self.network_name_entry_router.delete(0, tk.END)

    def create_simulation_tab(self):
        # Заголовок вкладки
        self.simulation_label = tk.Label(self.tab_simulation, text="Simulation", font=("Arial", 20, "bold"), bg="#0097A7", fg="white", pady=10)
        self.simulation_label.pack(fill="x", padx=10)

        # Выпадающий список для IP компьютеров
        self.computer_ip_label = tk.Label(self.tab_simulation, text="Select Computer IP", font=("Arial", 14))
        self.computer_ip_label.pack(pady=5)
        self.computer_ip_combobox = ttk.Combobox(self.tab_simulation, font=("Arial", 14), state="readonly")
        self.computer_ip_combobox.pack(pady=5)

        # Выпадающий список для IP маршрутизаторов
        self.router_ip_label = tk.Label(self.tab_simulation, text="Select Router IP", font=("Arial", 14))
        self.router_ip_label.pack(pady=5)
        self.router_ip_combobox = ttk.Combobox(self.tab_simulation, font=("Arial", 14), state="readonly")
        self.router_ip_combobox.pack(pady=5)

        # Поле для вывода информации
        self.simulation_output_label = tk.Label(self.tab_simulation, text="Output", font=("Arial", 14))
        self.simulation_output_label.pack(pady=5)
        self.simulation_output_text = tk.Text(self.tab_simulation, font=("Arial", 12), height=10, width=50, state="disabled", wrap="word")
        self.simulation_output_text.pack(pady=5)

        # Кнопка для выполнения симуляции
        self.simulate_button = ttk.Button(self.tab_simulation, text="Run Simulation", command=self.run_simulation, style="TButton")
        self.simulate_button.pack(pady=10)

        # Заполняем выпадающие списки
        self.populate_simulation_dropdowns()

    def populate_simulation_dropdowns(self):
        """Заполняет выпадающие списки IP-адресами компьютеров и маршрутизаторов."""
        # Получаем список компьютеров и маршрутизаторов
        computer_ips = [comp[1] for comp in list_computers()]  # IP-адреса компьютеров
        router_ips = [router[1] for router in list_routers()]  # IP-адреса маршрутизаторов

        # Заполняем выпадающие списки
        self.computer_ip_combobox["values"] = computer_ips
        self.router_ip_combobox["values"] = router_ips

    def run_simulation(self):
        """Выполняет симуляцию и выводит результат."""
        computer_ip = self.computer_ip_combobox.get()
        router_ip = self.router_ip_combobox.get()

        if not computer_ip or not router_ip:
            messagebox.showerror("Error", "Please select both a Computer IP and a Router IP.")
            return

        # МАТВЕЙ ТЕБЕ СЮДА ПИСАТЬ КУ-КУ - код для обработки симуляции здесь
        simulation_result = f"Simulating connection between Computer IP: {computer_ip} and Router IP: {router_ip}"

        # Выводим результат в текстовое поле
        self.simulation_output_text.config(state="normal")
        self.simulation_output_text.delete(1.0, tk.END)  # Очищаем предыдущее содержимое
        self.simulation_output_text.insert(tk.END, simulation_result)
        self.simulation_output_text.config(state="disabled")  # Запрещаем редактирование

# Создание стилей для кнопок и вкладок
def create_styles():
    style = ttk.Style()

    # Стиль для кнопок
    style.configure("TButton",
                    font=("Arial", 12),
                    relief="flat",
                    background="#ffffff",  # Белый фон по умолчанию
                    foreground="black",     # Черный текст
                    padding=10)
    style.map("TButton", background=[("active", "#f2f2f2")])  # Изменение цвета при наведении

    # Стиль для вкладок
    style.configure("TNotebook", padding=5, background="#0097A7", width=400, height=300)

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    create_styles()  # Применяем стили для кнопок
    app = MyApp(root)
    root.mainloop()
