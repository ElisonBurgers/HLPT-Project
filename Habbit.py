import sqlite3
import datetime
import os


class HabitTracker:
    def __init__(self):
        # Подключаемся к базе данных
        self.conn = sqlite3.connect('habits_tracker.db')
        self.cursor = self.conn.cursor()
        self.setup_database()

    def setup_database(self):
        """Создаем таблицы в базе данных"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                created_date DATE NOT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER,
                date DATE NOT NULL,
                FOREIGN KEY (habit_id) REFERENCES habits(id)
            )
        ''')
        self.conn.commit()



    def clear_screen(self):
        """Очистка экрана консоли"""
        os.system('cls' if os.name == 'nt' else 'clear')



    def print_header(self, title):
        """Вывод заголовка"""
        print("=" * 50)
        print(f" {title}")
        print("=" * 50)



    def show_menu(self):
        """Главное меню"""
        self.clear_screen()
        self.print_header("ТРЕКЕР ПРИВЫЧЕК")
        print("1. Добавить привычку")
        print("2. Показать все привычки")
        print("3. Отметить выполнение")
        print("4. Показать прогресс ((пока нету))")
        print("5. Удалить привычку ((пока нету))")
        print("0. Выход")
        print("-" * 50)



    def add_habit(self):
        """Добавление новой привычки"""
        self.clear_screen()
        self.print_header("ДОБАВИТЬ ПРИВЫЧКУ")

        name = input("Название привычки (например, 'Зарядка'): ").strip()
        if not name:
            print("❌ Название не может быть пустым!")
            input("\nНажмите Enter чтобы продолжить...")
            return

        description = input("Описание (необязательно): ").strip()

        try:
            self.cursor.execute(
                "INSERT INTO habits (name, description, created_date) VALUES (?, ?, ?)",
                (name, description, datetime.date.today())
            )
            self.conn.commit()
            print(f"✅ Привычка '{name}' успешно добавлена!")

        except Exception as e:
            print(f"❌ Ошибка при добавлении: {e}")

        input("\nНажмите Enter чтобы продолжить...")



    def show_all_habits(self):
        """Показать все привычки"""
        self.clear_screen()
        self.print_header("ВСЕ ПРИВЫЧКИ")

        self.cursor.execute("SELECT id, name, description FROM habits")
        habits = self.cursor.fetchall()

        if not habits:
            print("😕 У вас пока нет привычек. Добавьте первую!")
        else:
            print(f"Всего привычек: {len(habits)}\n")
            for i, (habit_id, name, description) in enumerate(habits, 1):
                # Получаем количество выполненных дней
                self.cursor.execute(
                    "SELECT COUNT(*) FROM completions WHERE habit_id = ?",
                    (habit_id,)
                )
                completed_days = self.cursor.fetchone()[0]

                # Получаем дату последнего выполнения
                self.cursor.execute(
                    "SELECT date FROM completions WHERE habit_id = ? ORDER BY date DESC LIMIT 1",
                    (habit_id,)
                )
                last_done = self.cursor.fetchone()

                print(f"{i}. {name}")
                if description:
                    print(f"   📝 {description}")
                print(f"   ✅ Выполнено дней: {completed_days}")
                if last_done:
                    print(f"   📅 Последний раз: {last_done[0]}")
                print()

        input("\nНажмите Enter чтобы продолжить...")



    def mark_completion(self):
        """Отметить выполнение привычки"""
        self.clear_screen()
        self.print_header("ОТМЕТИТЬ ВЫПОЛНЕНИЕ")

        # Показываем привычки для выбора
        self.cursor.execute("SELECT id, name FROM habits")
        habits = self.cursor.fetchall()

        if not habits:
            print("😕 У вас пока нет привычек. Добавьте первую!")
            input("\nНажмите Enter чтобы продолжить...")
            return

        print("Выберите привычку для отметки:\n")
        for i, (habit_id, name) in enumerate(habits, 1):
            print(f"{i}. {name}")

        try:
            choice = int(input("\nВведите номер привычки: ")) - 1
            if choice < 0 or choice >= len(habits):
                print("❌ Неверный номер привычки!")
                input("\nНажмите Enter чтобы продолжить...")
                return

            habit_id, habit_name = habits[choice]
            today = datetime.date.today()

            # Проверяем, не отметили ли уже сегодня
            self.cursor.execute(
                "SELECT id FROM completions WHERE habit_id = ? AND date = ?",
                (habit_id, today)
            )
            if self.cursor.fetchone():
                print(f"🤔 Привычка '{habit_name}' уже отмечена сегодня!")
            else:
                self.cursor.execute(
                    "INSERT INTO completions (habit_id, date) VALUES (?, ?)",
                    (habit_id, today)
                )
                self.conn.commit()
                print(f"✅ Отлично! Привычка '{habit_name}' выполнена сегодня!")

        except ValueError:
            print("❌ Введите число!")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

        input("\nНажмите Enter чтобы продолжить...")



    def show_progress(self):
        """Показать прогресс"""


    def delete_habit(self):
        """Удалить привычку"""


    def run(self):
        """Запуск основного цикла приложения"""
        while True:
            self.show_menu()

            try:
                choice = input("Выберите действие (0-5): ").strip()

                if choice == "0":
                    print("\n👋 До свидания! Ваши данные сохранены.")
                    break
                elif choice == "1":
                    self.add_habit()
                elif choice == "2":
                    self.show_all_habits()
                elif choice == "3":
                    self.mark_completion()
                #elif choice == "4":
                    #self.show_progress()
                #elif choice == "5":
                    #self.delete_habit()
                else:
                    print("❌ Неверный выбор! Попробуйте снова.")
                    input("\nНажмите Enter чтобы продолжить...")

            except KeyboardInterrupt:
                print("\n\n👋 Программа завершена.")
                break
            except Exception as e:
                print(f"❌ Произошла ошибка: {e}")
                input("\nНажмите Enter чтобы продолжить...")

        # Закрываем соединение с базой данных при выходе
        self.conn.close()


# Запуск приложения
if __name__ == "__main__":
    print("Запуск Трекера Привычек...")
    tracker = HabitTracker()
    tracker.run()