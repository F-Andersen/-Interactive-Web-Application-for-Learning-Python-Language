from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.content import Course, Lesson, Module, Task, TestCase
from app.models.user import Role, User


def get_or_create_role(db: Session, name: str, description: str) -> Role:
    role = db.query(Role).filter_by(name=name).first()
    if role:
        return role
    role = Role(name=name, description=description)
    db.add(role)
    db.flush()
    return role


def get_or_create_user(db: Session, role: Role, username: str, email: str, password: str) -> User:
    user = db.query(User).filter_by(email=email).first()
    if user:
        return user
    user = User(username=username, email=email, password_hash=get_password_hash(password), role_id=role.id)
    db.add(user)
    db.flush()
    return user


def create_course_bundle(db: Session, admin: User, title: str, description: str, difficulty: str, modules: list[dict]) -> None:
    if db.query(Course).filter_by(title=title).first():
        return
    course = Course(
        created_by=admin.id,
        title=title,
        description=description,
        difficulty_level=difficulty,
        publish_status="published",
    )
    db.add(course)
    db.flush()
    for module_index, module_data in enumerate(modules, start=1):
        module = Module(
            course_id=course.id,
            title=module_data["title"],
            description=module_data["description"],
            order_index=module_index,
        )
        db.add(module)
        db.flush()
        for lesson_index, lesson_data in enumerate(module_data["lessons"], start=1):
            lesson = Lesson(
                module_id=module.id,
                title=lesson_data["title"],
                content=lesson_data["content"],
                order_index=lesson_index,
            )
            db.add(lesson)
            db.flush()
            for task_index, task_data in enumerate(lesson_data["tasks"], start=1):
                task = Task(
                    lesson_id=lesson.id,
                    title=task_data["title"],
                    statement=task_data["statement"],
                    difficulty=task_data.get("difficulty", "easy"),
                    starter_code=task_data.get("starter_code", ""),
                    order_index=task_index,
                )
                db.add(task)
                db.flush()
                for case_index, case_data in enumerate(task_data["cases"], start=1):
                    db.add(
                        TestCase(
                            task_id=task.id,
                            input_data=case_data.get("input_data", ""),
                            expected_output=case_data["expected_output"],
                            is_hidden=case_data.get("is_hidden", False),
                            order_index=case_index,
                        )
                    )


def seed() -> None:
    db = SessionLocal()
    try:
        roles = {
            "student": get_or_create_role(db, "student", "Learns Python and solves tasks"),
            "admin": get_or_create_role(db, "admin", "Manages users and learning content"),
            "manager": get_or_create_role(db, "manager", "Future analytics and content planning role"),
            "developer": get_or_create_role(db, "developer", "Future platform development role"),
        }
        admin = get_or_create_user(db, roles["admin"], "admin", "admin@example.com", "admin123")
        get_or_create_user(db, roles["student"], "student", "student@example.com", "student123")

        if not db.query(Course).filter_by(title="Основи Python").first():
            course = Course(
                created_by=admin.id,
                title="Основи Python",
                description="Перший курс для знайомства із синтаксисом, змінними, введенням, умовами та циклами.",
                difficulty_level="beginner",
                publish_status="published",
            )
            db.add(course)
            db.flush()

            module_intro = Module(course_id=course.id, title="Старт із Python", description="Вивід, змінні та базовий синтаксис.", order_index=1)
            module_logic = Module(course_id=course.id, title="Логіка програм", description="Введення, умови й прості цикли.", order_index=2)
            db.add_all([module_intro, module_logic])
            db.flush()

            lesson_hello = Lesson(
                module_id=module_intro.id,
                title="Hello, World!",
                content="Python дозволяє швидко писати зрозумілі програми. Для виводу тексту використовується функція `print()`.",
                order_index=1,
            )
            lesson_vars = Lesson(
                module_id=module_intro.id,
                title="Змінні та типи",
                content="Змінна зберігає значення. Python сам визначає тип значення під час виконання програми.",
                order_index=2,
            )
            lesson_input = Lesson(
                module_id=module_logic.id,
                title="Введення даних",
                content="Функція `input()` читає рядок із стандартного вводу. Для чисел використовуйте `int()` або `float()`.",
                order_index=1,
            )
            db.add_all([lesson_hello, lesson_vars, lesson_input])
            db.flush()

            hello_task = Task(
                lesson_id=lesson_hello.id,
                title="Hello, World!",
                statement="Напишіть програму, яка виводить Hello, World!",
                difficulty="easy",
                starter_code='print("")',
                order_index=1,
            )
            sum_task = Task(
                lesson_id=lesson_input.id,
                title="Сума двох чисел",
                statement="Зчитайте два цілі числа з окремих рядків і виведіть їх суму.",
                difficulty="easy",
                starter_code='a = int(input())\nb = int(input())\nprint()',
                order_index=1,
            )
            db.add_all([hello_task, sum_task])
            db.flush()

            db.add_all(
                [
                    TestCase(task_id=hello_task.id, input_data="", expected_output="Hello, World!", is_hidden=False, order_index=1),
                    TestCase(task_id=hello_task.id, input_data="", expected_output="Hello, World!", is_hidden=True, order_index=2),
                    TestCase(task_id=sum_task.id, input_data="2\n3\n", expected_output="5", is_hidden=False, order_index=1),
                    TestCase(task_id=sum_task.id, input_data="-4\n10\n", expected_output="6", is_hidden=True, order_index=2),
                ]
            )

        create_course_bundle(
            db,
            admin,
            "Python: умови та цикли",
            "Практичний курс про керування потоком виконання: порівняння, if/elif/else, while, for і range.",
            "basic",
            [
                {
                    "title": "Умовні оператори",
                    "description": "Навчіться приймати рішення у програмі.",
                    "lessons": [
                        {
                            "title": "Порівняння та bool",
                            "content": (
                                "Булеві значення `True` і `False` з'являються після порівнянь: `>`, `<`, `==`, `!=`. "
                                "Умовний оператор `if` виконує блок коду лише тоді, коли умова істинна. "
                                "Для кількох сценаріїв використовуйте `elif`, а для запасної гілки - `else`."
                            ),
                            "tasks": [
                                {
                                    "title": "Додатне число",
                                    "statement": "Зчитайте ціле число. Виведіть positive, якщо воно більше 0, і not positive в іншому випадку.",
                                    "starter_code": "n = int(input())\n# write your code here\n",
                                    "cases": [
                                        {"input_data": "5\n", "expected_output": "positive"},
                                        {"input_data": "0\n", "expected_output": "not positive"},
                                        {"input_data": "-9\n", "expected_output": "not positive", "is_hidden": True},
                                    ],
                                },
                                {
                                    "title": "Парність",
                                    "statement": "Зчитайте ціле число і виведіть even для парного або odd для непарного.",
                                    "starter_code": "n = int(input())\nprint()\n",
                                    "cases": [
                                        {"input_data": "8\n", "expected_output": "even"},
                                        {"input_data": "7\n", "expected_output": "odd"},
                                        {"input_data": "-4\n", "expected_output": "even", "is_hidden": True},
                                    ],
                                },
                            ],
                        },
                        {
                            "title": "Вкладені умови",
                            "content": (
                                "Коли рішення залежить від кількох ознак, умови можна комбінувати через `and`, `or`, `not`. "
                                "Вкладені `if` інколи корисні, але частіше читабельніше записати логіку через окремі `elif`."
                            ),
                            "tasks": [
                                {
                                    "title": "Оцінка за балами",
                                    "statement": "Зчитайте бал 0-100. Виведіть A для 90+, B для 75-89, C для 60-74, F для менш ніж 60.",
                                    "difficulty": "medium",
                                    "starter_code": "score = int(input())\n",
                                    "cases": [
                                        {"input_data": "95\n", "expected_output": "A"},
                                        {"input_data": "82\n", "expected_output": "B"},
                                        {"input_data": "61\n", "expected_output": "C"},
                                        {"input_data": "40\n", "expected_output": "F", "is_hidden": True},
                                    ],
                                }
                            ],
                        },
                    ],
                },
                {
                    "title": "Цикли",
                    "description": "Повторення дій через while і for.",
                    "lessons": [
                        {
                            "title": "for та range",
                            "content": (
                                "`for` проходить по елементах послідовності. `range(n)` генерує числа від 0 до n-1, "
                                "а `range(a, b)` - від a до b-1. Це основний інструмент для повторення відомої кількості разів."
                            ),
                            "tasks": [
                                {
                                    "title": "Сума від 1 до n",
                                    "statement": "Зчитайте n і виведіть суму чисел від 1 до n включно.",
                                    "starter_code": "n = int(input())\ntotal = 0\n# use loop\nprint(total)\n",
                                    "cases": [
                                        {"input_data": "5\n", "expected_output": "15"},
                                        {"input_data": "1\n", "expected_output": "1"},
                                        {"input_data": "100\n", "expected_output": "5050", "is_hidden": True},
                                    ],
                                },
                                {
                                    "title": "Таблиця множення",
                                    "statement": "Зчитайте n. Виведіть 10 рядків у форматі n x i = result для i від 1 до 10.",
                                    "difficulty": "medium",
                                    "starter_code": "n = int(input())\n",
                                    "cases": [
                                        {"input_data": "2\n", "expected_output": "2 x 1 = 2\n2 x 2 = 4\n2 x 3 = 6\n2 x 4 = 8\n2 x 5 = 10\n2 x 6 = 12\n2 x 7 = 14\n2 x 8 = 16\n2 x 9 = 18\n2 x 10 = 20"},
                                        {"input_data": "7\n", "expected_output": "7 x 1 = 7\n7 x 2 = 14\n7 x 3 = 21\n7 x 4 = 28\n7 x 5 = 35\n7 x 6 = 42\n7 x 7 = 49\n7 x 8 = 56\n7 x 9 = 63\n7 x 10 = 70", "is_hidden": True},
                                    ],
                                },
                            ],
                        },
                        {
                            "title": "while",
                            "content": (
                                "`while` повторює блок, доки умова істинна. Важливо змінювати змінні всередині циклу, "
                                "щоб програма не стала нескінченною. Для дострокового виходу існує `break`."
                            ),
                            "tasks": [
                                {
                                    "title": "Кількість цифр",
                                    "statement": "Зчитайте невід'ємне ціле число і виведіть кількість його цифр.",
                                    "starter_code": "n = int(input())\n",
                                    "cases": [
                                        {"input_data": "0\n", "expected_output": "1"},
                                        {"input_data": "12345\n", "expected_output": "5"},
                                        {"input_data": "1000000\n", "expected_output": "7", "is_hidden": True},
                                    ],
                                }
                            ],
                        },
                    ],
                },
            ],
        )

        create_course_bundle(
            db,
            admin,
            "Функції та структури даних",
            "Курс про декомпозицію коду, списки, словники, рядки та прості алгоритми обробки даних.",
            "intermediate",
            [
                {
                    "title": "Функції",
                    "description": "Повторне використання логіки через def і return.",
                    "lessons": [
                        {
                            "title": "def, параметри, return",
                            "content": (
                                "Функція оголошується через `def name(params):`. Вона може приймати аргументи і повертати результат через `return`. "
                                "Гарна функція робить одну зрозумілу дію і має назву, яка описує результат."
                            ),
                            "tasks": [
                                {
                                    "title": "Функція square",
                                    "statement": "Створіть функцію square(n), яка повертає квадрат числа. Зчитайте n і виведіть square(n).",
                                    "starter_code": "def square(n):\n    pass\n\nn = int(input())\nprint(square(n))\n",
                                    "cases": [
                                        {"input_data": "4\n", "expected_output": "16"},
                                        {"input_data": "-3\n", "expected_output": "9"},
                                        {"input_data": "0\n", "expected_output": "0", "is_hidden": True},
                                    ],
                                },
                                {
                                    "title": "Максимум з трьох",
                                    "statement": "Напишіть функцію max3(a, b, c), яка повертає найбільше з трьох чисел.",
                                    "starter_code": "def max3(a, b, c):\n    pass\n\na = int(input())\nb = int(input())\nc = int(input())\nprint(max3(a, b, c))\n",
                                    "cases": [
                                        {"input_data": "1\n9\n3\n", "expected_output": "9"},
                                        {"input_data": "-1\n-5\n-3\n", "expected_output": "-1", "is_hidden": True},
                                    ],
                                },
                            ],
                        }
                    ],
                },
                {
                    "title": "Списки та словники",
                    "description": "Збереження наборів значень і пошук за ключами.",
                    "lessons": [
                        {
                            "title": "Списки",
                            "content": (
                                "Список зберігає впорядковану колекцію значень. До елементів звертаються за індексом, "
                                "а цикл `for item in items` дозволяє обробити всі значення."
                            ),
                            "tasks": [
                                {
                                    "title": "Середнє значення",
                                    "statement": "Зчитайте числа в одному рядку через пробіл і виведіть їх середнє значення як float.",
                                    "difficulty": "medium",
                                    "starter_code": "numbers = list(map(int, input().split()))\n",
                                    "cases": [
                                        {"input_data": "2 4 6\n", "expected_output": "4.0"},
                                        {"input_data": "10 20\n", "expected_output": "15.0"},
                                        {"input_data": "1 2 3 4\n", "expected_output": "2.5", "is_hidden": True},
                                    ],
                                },
                                {
                                    "title": "Фільтр додатних",
                                    "statement": "Зчитайте числа через пробіл і виведіть тільки додатні числа через пробіл.",
                                    "starter_code": "numbers = list(map(int, input().split()))\n",
                                    "cases": [
                                        {"input_data": "-1 0 2 5\n", "expected_output": "2 5"},
                                        {"input_data": "3 -2 7 -8\n", "expected_output": "3 7", "is_hidden": True},
                                    ],
                                },
                            ],
                        },
                        {
                            "title": "Словники",
                            "content": (
                                "Словник зберігає пари ключ-значення. Це зручно для підрахунку частот, налаштувань, профілів користувачів "
                                "і будь-яких даних, де потрібен швидкий доступ за назвою."
                            ),
                            "tasks": [
                                {
                                    "title": "Підрахунок слів",
                                    "statement": "Зчитайте рядок слів через пробіл і виведіть, скільки разів зустрічається слово python.",
                                    "starter_code": "words = input().split()\n",
                                    "cases": [
                                        {"input_data": "python java python\n", "expected_output": "2"},
                                        {"input_data": "go rust python js\n", "expected_output": "1"},
                                        {"input_data": "java kotlin\n", "expected_output": "0", "is_hidden": True},
                                    ],
                                }
                            ],
                        },
                    ],
                },
            ],
        )

        create_course_bundle(
            db,
            admin,
            "Міні-проєкти Python",
            "Невеликі задачі, схожі на реальні сценарії: форматування даних, перевірки, прості обчислення.",
            "intermediate",
            [
                {
                    "title": "Практика з рядками",
                    "description": "Обробка тексту та форматування виводу.",
                    "lessons": [
                        {
                            "title": "Рядкові методи",
                            "content": (
                                "Рядки мають методи `.lower()`, `.upper()`, `.strip()`, `.replace()`, `.split()`. "
                                "Вони допомагають нормалізувати введення користувача і готувати чистий вивід."
                            ),
                            "tasks": [
                                {
                                    "title": "Нормалізація імені",
                                    "statement": "Зчитайте ім'я, приберіть зайві пробіли і виведіть його з великої літери.",
                                    "starter_code": "name = input()\n",
                                    "cases": [
                                        {"input_data": "  andrii  \n", "expected_output": "Andrii"},
                                        {"input_data": "oLENA\n", "expected_output": "Olena"},
                                        {"input_data": "  python\n", "expected_output": "Python", "is_hidden": True},
                                    ],
                                },
                                {
                                    "title": "Email домен",
                                    "statement": "Зчитайте email і виведіть домен після символу @.",
                                    "starter_code": "email = input().strip()\n",
                                    "cases": [
                                        {"input_data": "student@example.com\n", "expected_output": "example.com"},
                                        {"input_data": "admin@python.dev\n", "expected_output": "python.dev", "is_hidden": True},
                                    ],
                                },
                            ],
                        }
                    ],
                },
                {
                    "title": "Маленькі алгоритми",
                    "description": "Задачі на уважність і поєднання базових конструкцій.",
                    "lessons": [
                        {
                            "title": "Перевірки та обчислення",
                            "content": (
                                "Алгоритм - це послідовність кроків. Перед написанням коду корисно вручну пройти кілька прикладів "
                                "і зрозуміти, які умови та змінні потрібні."
                            ),
                            "tasks": [
                                {
                                    "title": "Простий калькулятор знижки",
                                    "statement": "Зчитайте ціну і відсоток знижки. Виведіть фінальну ціну, округлену до 2 знаків.",
                                    "starter_code": "price = float(input())\ndiscount = float(input())\n",
                                    "cases": [
                                        {"input_data": "100\n15\n", "expected_output": "85.0"},
                                        {"input_data": "250\n12.5\n", "expected_output": "218.75", "is_hidden": True},
                                    ],
                                },
                                {
                                    "title": "Паліндром",
                                    "statement": "Зчитайте рядок і виведіть yes, якщо він однаково читається зліва направо і справа наліво, і no інакше.",
                                    "difficulty": "medium",
                                    "starter_code": "text = input().strip().lower()\n",
                                    "cases": [
                                        {"input_data": "level\n", "expected_output": "yes"},
                                        {"input_data": "python\n", "expected_output": "no"},
                                        {"input_data": "Madam\n", "expected_output": "yes", "is_hidden": True},
                                    ],
                                },
                            ],
                        }
                    ],
                },
            ],
        )

        db.commit()
        print("Seed completed")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
