import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os


HISTORY_FILE = "quotes_history.json"


class Quote:
    """Представляет цитату с текстом, автором и темой."""
    
    def __init__(self, text: str, author: str, theme: str):
        self.text = text
        self.author = author
        self.theme = theme
    
    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "author": self.author,
            "theme": self.theme
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Quote':
        return cls(
            text=data.get("text", ""),
            author=data.get("author", ""),
            theme=data.get("theme", "")
        )
    
    def __str__(self) -> str:
        return f'"{self.text}" — {self.author} ({self.theme})'


class RandomQuoteGenerator:
    """Основной класс приложения Генератор случайных цитат."""
    
   
    DEFAULT_QUOTES = [
        Quote("Единственный способ делать великие дела — любить то, что вы делаете.", "Стив Джобс", "Мотивация"),
        Quote("Жизнь — это то, что происходит, пока вы строите другие планы.", "Джон Леннон", "Жизнь"),
        Quote("Будущее принадлежит тем, кто верит в красоту своей мечты.", "Элеонора Рузвельт", "Мечты"),
        Quote("Именно в самые тёмные моменты мы должны сосредоточиться, чтобы увидеть свет.", "Аристотель", "Вдохновение"),
        Quote("Не идите туда, куда ведёт тропа. Идите туда, где тропы нет, и оставьте след.", "Ральф Уолдо Эмерсон", "Мужество"),
        Quote("В середине трудности лежит возможность.", "Альберт Эйнштейн", "Успех"),
        Quote("Успех не окончателен, неудача не фатальна: главное — мужество продолжать.", "Уинстон Черчилль", "Успех"),
        Quote("Верьте, что вы можете, и вы уже на полпути.", "Теодор Рузвельт", "Мотивация"),
        Quote("Единственное невозможное путешествие — то, которое вы никогда не начнёте.", "Тони Роббинс", "Вдохновение"),
        Quote("Счастье — это не что-то готовое. Оно происходит от ваших собственных действий.", "Далай-лама", "Счастье"),
        Quote("Быть собой в мире, который постоянно пытается сделать вас кем-то другим, — величайшее достижение.", "Ральф Уолдо Эмерсон", "Индивидуальность"),
        Quote("Вы промахнётесь 100% раз, если никогда не бросите.", "Уэйн Гретцки", "Мужество"),
        Quote("Думаете ли вы, что можете, или думаете, что не можете — вы правы.", "Генри Форд", "Мышление"),
        Quote("Лучшее время посадить дерево было 20 лет назад. Второе лучшее время — сейчас.", "Китайская пословица", "Мудрость"),
        Quote("Ваше время ограничено, не тратьте его, живя чужой жизнью.", "Стив Джобс", "Жизнь"),
    ]
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Генератор случайных цитат")
        self.root.geometry("800x600")
        
        self.history: list[Quote] = []
        self.available_quotes: list[Quote] = self.DEFAULT_QUOTES.copy()
        
        self._setup_ui()
        self._load_history()
    
    def _setup_ui(self):
        """Настройка пользовательского интерфейса."""
       
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        
        title_label = ttk.Label(main_frame, text="Генератор случайных цитат", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 10))
        
       
        quote_frame = ttk.LabelFrame(main_frame, text="Текущая цитата", padding="10")
        quote_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        quote_frame.columnconfigure(0, weight=1)
        
        self.quote_text_var = tk.StringVar(value='Нажмите «Сгенерировать цитату», чтобы начать!')
        self.quote_label = ttk.Label(quote_frame, textvariable=self.quote_text_var, wraplength=700, font=("Helvetica", 12))
        self.quote_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=2, column=0, pady=(0, 10))
        
        
        self.generate_btn = ttk.Button(buttons_frame, text="🎲 Сгенерировать цитату", command=self.generate_quote)
        self.generate_btn.grid(row=0, column=0, padx=5)
        
        
        self.add_btn = ttk.Button(buttons_frame, text="➕ Добавить цитату", command=self.show_add_quote_dialog)
        self.add_btn.grid(row=0, column=1, padx=5)
        
        
        self.clear_btn = ttk.Button(buttons_frame, text="🗑️ Очистить историю", command=self.clear_history)
        self.clear_btn.grid(row=0, column=2, padx=5)
        
        
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтр истории", padding="10")
        filter_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        filter_frame.columnconfigure(1, weight=1)
        filter_frame.columnconfigure(3, weight=1)
        
       
        ttk.Label(filter_frame, text="Автор:").grid(row=0, column=0, padx=(0, 5))
        self.author_filter_var = tk.StringVar()
        self.author_filter_entry = ttk.Entry(filter_frame, textvariable=self.author_filter_var, width=20)
        self.author_filter_entry.grid(row=0, column=1, padx=(0, 10), sticky=(tk.W, tk.E))
        
       
        ttk.Label(filter_frame, text="Тема:").grid(row=0, column=2, padx=(0, 5))
        self.theme_filter_var = tk.StringVar()
        self.theme_filter_entry = ttk.Entry(filter_frame, textvariable=self.theme_filter_var, width=20)
        self.theme_filter_entry.grid(row=0, column=3, padx=(0, 10), sticky=(tk.W, tk.E))
        
       
        self.filter_btn = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        self.filter_btn.grid(row=0, column=4)
        
       
        self.reset_filter_btn = ttk.Button(filter_frame, text="Сбросить", command=self.reset_filter)
        self.reset_filter_btn.grid(row=0, column=5, padx=(5, 0))
        
      
        history_frame = ttk.LabelFrame(main_frame, text="История", padding="10")
        history_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        
        
        list_container = ttk.Frame(history_frame)
        list_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_container.columnconfigure(0, weight=1)
        list_container.rowconfigure(0, weight=1)
        
        self.history_listbox = tk.Listbox(list_container, height=10, font=("Helvetica", 10))
        self.history_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.history_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.history_listbox.config(yscrollcommand=scrollbar.set)
        
      
        self.status_var = tk.StringVar(value="Готово")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def generate_quote(self):
        """Генерация и отображение случайной цитаты."""
        if not self.available_quotes:
            messagebox.showwarning("Предупреждение", "Нет доступных цитат!")
            return
        
        quote = random.choice(self.available_quotes)
        self.history.append(quote)
        self.quote_text_var.set(str(quote))
        self._update_history_display()
        self._save_history()
        self.status_var.set(f"Сгенерирована цитата автора: {quote.author}")
    
    def _update_history_display(self, filtered_list: list[Quote] = None):
        """Обновление отображения списка истории."""
        self.history_listbox.delete(0, tk.END)
        
        display_list = filtered_list if filtered_list is not None else self.history
        
        for i, quote in enumerate(reversed(display_list)):  # Показывать newest first
            self.history_listbox.insert(tk.END, f"{i+1}. {quote}")
    
    def apply_filter(self):
        """Применение фильтров к списку истории."""
        author_filter = self.author_filter_var.get().strip().lower()
        theme_filter = self.theme_filter_var.get().strip().lower()
        
        filtered = []
        for quote in self.history:
            match_author = not author_filter or author_filter in quote.author.lower()
            match_theme = not theme_filter or theme_filter in quote.theme.lower()
            if match_author and match_theme:
                filtered.append(quote)
        
        self._update_history_display(filtered)
        self.status_var.set(f"Показано {len(filtered)} из {len(self.history)} цитат")
    
    def reset_filter(self):
        """Сброс фильтров и показ всей истории."""
        self.author_filter_var.set("")
        self.theme_filter_var.set("")
        self._update_history_display()
        self.status_var.set(f"Показаны все {len(self.history)} цитат")
    
    def show_add_quote_dialog(self):
        """Показ диалога для добавления новой цитаты."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить новую цитату")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        
        
        ttk.Label(frame, text="Текст цитаты:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        text_entry = ttk.Entry(frame, width=40)
        text_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        
        
        ttk.Label(frame, text="Автор:").grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        author_entry = ttk.Entry(frame, width=40)
        author_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        
        
        ttk.Label(frame, text="Тема:").grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        theme_entry = ttk.Entry(frame, width=40)
        theme_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        
        def save_quote():
            text = text_entry.get().strip()
            author = author_entry.get().strip()
            theme = theme_entry.get().strip()
            
            
            if not text:
                messagebox.showerror("Ошибка валидации", "Текст цитаты не может быть пустым!")
                return
            if not author:
                messagebox.showerror("Ошибка валидации", "Автор не может быть пустым!")
                return
            if not theme:
                messagebox.showerror("Ошибка валидации", "Тема не может быть пустой!")
                return
            
            new_quote = Quote(text, author, theme)
            self.available_quotes.append(new_quote)
            self.status_var.set(f"Добавлена новая цитата автора: {author}")
            messagebox.showinfo("Успех", "Цитата успешно добавлена!")
            dialog.destroy()
        
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(btn_frame, text="Сохранить", command=save_quote).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy).grid(row=0, column=1, padx=5)
        
        text_entry.focus_set()
    
    def clear_history(self):
        """Очистка списка истории."""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить историю?"):
            self.history.clear()
            self._update_history_display()
            self._save_history()
            self.quote_text_var.set('Нажмите «Сгенерировать цитату», чтобы начать!')
            self.status_var.set("История очищена")
    
    def _save_history(self):
        """Сохранение истории в JSON файл."""
        try:
            data = [quote.to_dict() for quote in self.history]
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")
    
    def _load_history(self):
        """Загрузка истории из JSON файла."""
        if not os.path.exists(HISTORY_FILE):
            self.status_var.set("Предыдущая история не найдена")
            return
        
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.history = [Quote.from_dict(item) for item in data]
            self._update_history_display()
            self.status_var.set(f"Загружено {len(self.history)} цитат из истории")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить историю: {e}")
            self.status_var.set("Не удалось загрузить историю")


def main():
    """Точка входа в приложение."""
    root = tk.Tk()
    app = RandomQuoteGenerator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
