import requests
from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mb

# Функция для обновления подписей валют на экране
def update_currency_labels(event):
    base1_code = base1_combobox.get()
    base2_code = base2_combobox.get()
    target_code = target_combobox.get()
    
    base1_label.config(text=currencies.get(base1_code, ""))
    base2_label.config(text=currencies.get(base2_code, ""))
    target_label.config(text=currencies.get(target_code, ""))

# Функция очистки всех полей
def clear_fields():
    base1_combobox.set('')
    base2_combobox.set('')
    target_combobox.set('')
    date_label.config(text="Дата обновления: не определена")
    update_currency_labels() # Стирает текстовые подписи под комбобоксами

# Функция получения и вывода курсов для двух валют
def exchange():
    base1_code = base1_combobox.get()
    base2_code = base2_combobox.get()
    target_code = target_combobox.get()
    
    # Проверка, что все три поля заполнены
    if not base1_code or not base2_code or not target_code:
        mb.showwarning('Внимание', 'Пожалуйста, выберите все три валюты!')
        return
        
    try:
        # 1. Запрос для первой базовой валюты
        res1 = requests.get(f"https://open.er-api.com/v6/latest/{base1_code}")
        res1.raise_for_status()
        data1 = res1.json() # Получаем данные в формате JSON
        
        # 2. Запрос для второй базовой валюты
        res2 = requests.get(f"https://open.er-api.com/v6/latest/{base2_code}")
        res2.raise_for_status()
        data2 = res2.json() # Получаем данные в формате JSON
        
        # Проверяем, есть ли целевая валюта в ответах API
        if target_code in data1['rates'] and target_code in data2['rates']:
            rate1 = data1['rates'][target_code]
            rate2 = data2['rates'][target_code]
            
            b1_name = currencies[base1_code]
            b2_name = currencies[base2_code]
            t_name = currencies[target_code]

            # Извлекаем дату последнего обновления из JSON-ответа от первой валюты в формате: "27 Sep 2026 00:00:01"
            last_update_utc = data1.get('time_last_update_utc', 'Не указано')
            last_update_utc = last_update_utc[5:-6] if len(last_update_utc) > 11 else 'Не указано'
            # Обновляем текст метки на главном экране
            date_label.config(text=f"Дата обновления:\n{last_update_utc}")
            
            # Формируем общее сообщение с двумя курсами
            message = (
                f"Курс обмена:\n\n"
                f"1 {b1_name} = {rate1:.2f} {t_name}\n"
                f"1 {b2_name} = {rate2:.2f} {t_name}"
            )
            mb.showinfo('Курсы обмена', message)
        else:
            mb.showerror('Ошибка', f'Целевая валюта {target_code} не найдена.')

    except Exception as e:
        mb.showerror('Ошибка сети', f'Не удалось получить данные с сервера:\n{e}')

# Словарь доступных валют
currencies = {
    "USD": "Американский доллар",
    "EUR": "Евро",
    "CNY": "Юань",
    "RUB": "Российский рубль",
}

root = Tk()
root.title("Курсы обмена валют")
root.geometry("300x450") # Высота окна под новые элементы

# --- Первая базовая валюта ---
Label(text='Базовая валюта').pack(pady=(10, 2))
base1_combobox = ttk.Combobox(values=list(currencies.keys()), state="readonly")
base1_combobox.pack()
base1_label = Label(text="", fg="gray")
base1_label.pack(pady=(2, 5))

# --- Вторая базовая валюта ---
Label(text='Вторая базовая валюта').pack(pady=(5, 2))
base2_combobox = ttk.Combobox(values=list(currencies.keys()), state="readonly")
base2_combobox.pack()
base2_label = Label(text="", fg="gray")
base2_label.pack(pady=(2, 5))

# --- Целевая валюта ---
Label(text='Целевая валюта').pack(pady=(5, 2))
target_combobox = ttk.Combobox(values=list(currencies.keys()), state="readonly")
target_combobox.pack()
target_label = Label(text="", fg="gray")
target_label.pack(pady=(2, 10))

# --- Кнопка очистки ---
button_clear = Button(
    text='Очистить', 
    command=clear_fields, 
    bg="#383A3A",            # Светло-красный цвет фона
    fg='white',              # Белый цвет текста
    activebackground='#ff4d4d', # Цвет при нажатии кнопки
    activeforeground='white'
)
button_clear.pack(pady=5)

# --- Кнопка действия ---
button = Button(text='Получить курс обмена', command=exchange)
button.pack(pady=5)

# Кнопка Закрывает главное окно приложения
button_exit = Button(text='Выход', command=root.destroy) 
button_exit.pack(pady=5)

# --- Метка для отображения даты обновления курсов ---
date_label = Label(text="Дата обновления: не определена", fg="blue", justify=CENTER)
date_label.pack(pady=(10, 5))

# Привязка обновления текстовых меток при выборе значений
base1_combobox.bind("<<ComboboxSelected>>", update_currency_labels)
base2_combobox.bind("<<ComboboxSelected>>", update_currency_labels)
target_combobox.bind("<<ComboboxSelected>>", update_currency_labels)

# Установка начальных значений по умолчанию
base1_combobox.set('USD')
base2_combobox.set('EUR')
target_combobox.set('RUB')
#update_currency_labels()

root.mainloop()
