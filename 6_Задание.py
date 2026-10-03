import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import requests

# Константы настроек API
# Для бесплатных Demo-ключей адрес
API_URL = "https://api.coingecko.com/api/v3/simple/price?"

# Вставляем созданный ключ из личного кабинета CoinGecko 
API_KEY = "CG-m8wYmqCgXzZjTZo6zsGB3jdq" 

# Список отслеживаемых криптовалют (id в системе CoinGecko : Отображаемое имя)
COINS = {
    "bitcoin": "Bitcoin (BTC)",
    "ethereum": "Ethereum (ETH)",
    "solana": "Solana (SOL)",
    "binancecoin": "Binance Coin (BNB)",
    "ripple": "Ripple (XRP)"
}

class CryptoTickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CryptoTicker_v1.1")
        self.root.geometry("550x350")
        self.root.resizable(False, False)
        
        self.setup_ui()
        self.refresh_rates()  # Автоматическая загрузка данных при старте приложения

    def setup_ui(self):
        """Отрисовка элементов графического интерфейса"""
        # Настройка визуальных стилей таблицы
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))
        style.configure("Treeview", font=("Helvetica", 12), rowheight=30)
        
        # Верхний заголовок приложения
        header = tk.Label(self.root, text="Текущие курсы криптовалют (CoinGecko_API)", 
                          font=("Helvetica", 14, "bold"), pady=10)
        header.pack()

        # Создание таблицы (Treeview)
        columns = ("name", "price", "change")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=5)
        
        # Заголовки колонок
        self.tree.heading("name", text="Криптовалюта")
        self.tree.heading("price", text="Цена (USD)")
        self.tree.heading("change", text="Изменение за 24ч")
        
        # Геометрия колонок
        self.tree.column("name", width=200, anchor="w")
        self.tree.column("price", width=150, anchor="e")
        self.tree.column("change", width=150, anchor="center")
        
        self.tree.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Цветовые теги для цен (зеленый для роста, красный для падения)
        self.tree.tag_configure("positive", foreground="green")
        self.tree.tag_configure("negative", foreground="red")

        # Нижняя панель для статуса и кнопки обновления
        bottom_frame = tk.Frame(self.root, padx=20, pady=10)
        bottom_frame.pack(fill="x", side="bottom")

        self.status_label = tk.Label(bottom_frame, text="Загрузка данных...", 
                                     font=("Helvetica", 9, "italic"), fg="gray")
        self.status_label.pack(side="left")

        self.refresh_btn = ttk.Button(bottom_frame, text="Обновить ↻", command=self.refresh_rates)
        self.refresh_btn.pack(side="right")

    def refresh_rates(self):
        """Функция безопасного запроса данных из API с обходом ошибки 403"""
        self.refresh_btn.config(state="disabled")
        self.status_label.config(text="Обновление котировок...", fg="orange")
        self.root.update_idletasks()

        # Параметры запроса к CoinGecko
        params = {
            "ids": ",".join(COINS.keys()),
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        }

        # Заголовки: имитируем браузер (User-Agent) и передаем Demo API Ключ
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "x-cg-demo-api-key": API_KEY
        }

        try:
            # Выполняем GET-запрос с таймаутом 5 секунд
            response = requests.get(API_URL, params=params, headers=headers, timeout=5)
            
            # Точечная обработка частых ошибок API
            if response.status_code == 403:
                raise requests.exceptions.RequestException(
                    "Ошибка 403 (Доступ запрещен).\n\n"
                    "Проверьте, указали ли вы правильный API-ключ в переменной API_KEY.\n"
                    "Убедитесь, что вы не используете VPN, который заблокирован Cloudflare."
                )
            elif response.status_code == 429:
                raise requests.exceptions.RequestException("Превышен лимит запросов (Rate Limit). Подождите 1-2 минуты.")
                
            response.raise_for_status()
            data = response.json()
            
            # Очищаем таблицу перед выводом новых данных
            for row in self.tree.get_children():
                self.tree.delete(row)

            # Перебираем конфигурацию монет и наполняем таблицу полученными данными
            for coin_id, display_name in COINS.items():
                if coin_id in data:
                    price = data[coin_id].get("usd", 0.0)
                    change = data[coin_id].get("usd_24h_change", 0.0)
                    
                    # Красивое форматирование чисел
                    price_str = f"$ {price:,.2f}" if price >= 1 else f"$ {price:.4f}"
                    change_str = f"{'▲' if change >= 0 else '▼'} {change:.2f}%"
                    
                    # Определяем цвет строки на основе знака изменения цены
                    row_tag = "positive" if change >= 0 else "negative"
                    
                    self.tree.insert("", "end", values=(display_name, price_str, change_str), tags=(row_tag,))

            # Выводим время последнего успешного обновления
            current_time = datetime.now().strftime("%H:%M:%S")
            self.status_label.config(text=f"Последнее обновление: {current_time}", fg="green")

        except requests.exceptions.RequestException as e:
            # Обработка сетевых сбоев, ошибок таймаута и неверных ключей
            self.status_label.config(text="Ошибка обновления", fg="red")
            messagebox.showerror("Ошибка получения данных", f"Не удалось обновить курсы:\n\n{str(e)}")
        
        finally:
            # В любом случае возвращаем кнопку «Обновить» в рабочее состояние
            self.refresh_btn.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoTickerApp(root)
    root.mainloop()
