import asyncio
import datetime as dt
import random
from decimal import Decimal
from typing import Iterable, List

from loguru import logger

from eyemath_models import (
    User,
    Author,
    Seller,
    Warehouse,
    ProductType,
    Product,
    Purchase,
    PurchaseItem,
    Delivery,
    DeliveryGroup,
    UserRole,
    PaymentMethodEnum,
    DeliveryGroupStatusEnum,
    DeliveryStatusEnum,
)

from src.services.db.database import DataBase

from sqlalchemy.orm import configure_mappers
configure_mappers()



def chunked(iterable: Iterable, size: int) -> Iterable[list]:
    it = iter(iterable)
    while True:
        batch = []
        try:
            for _ in range(size):
                batch.append(next(it))
        except StopIteration:
            if batch:
                yield batch
            break
        if batch:
            yield batch


FIRST_NAMES = [
    "Алексей","Максим","Мария","Ольга","Дмитрий","Анна","Сергей","Елена","Иван","Наталья",
    "Андрей","Екатерина","Михаил","Татьяна","Владимир","Светлана","Александр","Ирина","Юрий","Людмила",
    "Константин","Виктор","Ксения","Павел","Полина","Григорий","Вероника","Борис","Диана","Роман",
    "Кирилл","Жанна","Василиса","Рустам","Дарья","Роберт","Лилия","Игорь","Нина","Тимофей",
]

LAST_NAMES = [
    "Иванов","Петров","Сидоров","Федоров","Васильев","Кузнецов","Попов","Морозов","Волков","Соколов",
    "Новиков","Фишер","Козлов","Орлов","Лебедев","Семенов","Егоров","Павлов","Захаров","Степанов",
    "Никитин","Макаров","Алексеев","Гусев","Лазарев","Медведев","Крылов","Гаврилов","Дорофеев","Виноградов",
    "Карпов","Поляков","Осипов","Прохоров","Фролов","Антонов","Романов","Шестаков","Николаев","Афанасьев",
]

MIDDLE_NAMES = [
    "Алексеевич","Максимович","Дмитриевич","Сергеевич","Иванович","Андреевич","Михайлович","Александрович","Владимирович","Петрович",
    "Алексеевна","Максимовна","Дмитриевна","Сергеевна","Ивановна","Андреевна","Михайловна","Александровна","Владимировна","Петровна",
    "Николаевич","Викторович","Николаевна","Викторовна","Григорьевич","Григорьевна","Юрьевич","Юрьевна","Романович","Романовна",
    "Борисович","Борисовна","Тимофеевич","Тимофеевна","Константинович","Константиновна","Рустамович","Рустамовна","Дмитриевна","Дмитриевич",
]

AUTHORS = [
    "Александр Пушкин","Лев Толстой","Федор Достоевский","Антон Чехов","Иван Тургенев","Николай Гоголь","Михаил Лермонтов","Анна Ахматова",
    "Борис Пастернак","Владимир Маяковский","Сергей Есенин","Марина Цветаева","Иосиф Бродский","Варлам Шаламов","Александр Солженицын","Василий Шукшин",
    "Николай Некрасов","Дмитрий Мережковский","Иван Бунин","Михаил Булгаков","Юрий Олеша","Набоков Владимир","Александр Грибоедов","Валентин Распутин",
    "Всеволод Иванов","Юрий Трифонов","Константин Паустовский","Владимир Набоков","Лидия Чуковская","Валерий Брюсов","Ольга Берггольц",
    "Осип Мандельштам","Михаил Пришвин","Виктор Астафьев","Валентин Катаев","Константин Симонов","Михаил Зощенко",
]

PRODUCT_NAMES = [
    "Война и мир", "Анна Каренина", "Преступление и наказание", "Идиот", "Братья Карамазовы",
    "Евгений Онегин", "Мастер и Маргарита", "Белая гвардия", "Собачье сердце", "Тихий Дон",
    "Доктор Живаго", "Герой нашего времени", "Мёртвые души", "Отцы и дети", "Дубровский",
    "Капитанская дочка", "Обломов", "Дети Арбата", "Зулейха открывает глаза", "Петербург",
    "Чевенгур", "Хаджи-Мурат", "Матрёнин двор", "Записки из подполья", "Мы",
    "Пикник на обочине", "Трудно быть богом", "Солярис", "Дом в котором", "Горе от ума",
    "Ревизор", "Вишнёвый сад", "Чайка", "Алые паруса", "Понедельник начинается в субботу",
    "Москва — Петушки", "Колымские рассказы", "Архипелаг ГУЛАГ", "Лолита", "Защита Лужина",
    "Дар", "Портрет Дориана Грея", "Сто лет одиночества", "1984", "О дивный новый мир",
    "Цветы для Элджернона", "Убить пересмешника", "Американская трагедия", "Парфюмер", "Имя розы",
]


LOCATIONS = [
    "Москва, ул. Тверская 1","Санкт-Петербург, Невский пр. 10","Новосибирск, ул. Ленина 25","Екатеринбург, ул. Малышева 15",
    "Казань, ул. Баумана 30","Нижний Новгород, ул. Большая Покровская 5","Челябинск, ул. Кирова 20","Самара, ул. Ленинградская 35",
    "Омск, ул. Маркса 40","Ростов-на-Дону, пр. Ворошиловский 12","Владивосток, ул. Светланская 2","Ярославль, ул. Волковская 14",
    "Иркутск, ул. Ленина 10","Томск, пр. Ленина 50","Оренбург, ул. Советская 9","Уфа, ул. Ленина 1","Воронеж, ул. Плехановская 60",
    "Пермь, ул. Ленина 53","Краснодар, ул. Красная 80","Волгоград, пр. Ленина 45","Рязань, ул. Соборная 12","Нижнекамск, ул. Мира 5",
    "Череповец, ул. Ленина 33","Кемерово, пр. Советский 22","Тула, ул. Советская 99","Иваново, ул. Радищева 7","Липецк, ул. Октябрьская 15",
    "Тамбов, ул. Советская 12","Саратов, ул. Мичурина 18","Ульяновск, ул. Ленина 20","Барнаул, пр. Ленина 30","Калининград, ул. Театральная 1",
    "Сургут, пр. Мира 40","Новороссийск, ул. Советская 11","Мурманск, ул. Ленинградская 5","Севастополь, пр. Нахимова 3",
]

CATEGORIES = [
    "FICTION","NONFICTION","BUSINESS","SCIENCE","SELF_HELP","PSYCHOLOGY","HISTORY","BIOGRAPHY",
    "CHILDREN","YOUNG_ADULT","FANTASY","SCIENCE_FICTION","MYSTERY_THRILLER","ROMANCE","COMICS_MANGA",
    "ART_PHOTOGRAPHY","COOKBOOKS_FOOD","HEALTH_FITNESS","EDUCATION_TEACHING","TRAVEL",
]



def random_publication_ts(year_from: int = 1200, year_to: int = 1969) -> int:
    y = random.randint(year_from, year_to)
    m = random.randint(1, 12)
    is_leap = (y % 4 == 0) and (y % 100 != 0 or y % 400 == 0)
    dmax = [31, 29 if is_leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
    d = random.randint(1, dmax)
    return int(dt.datetime(y, m, d, 0, 0).timestamp())


def random_past_ts(max_days: int = 365 * 5) -> int:
    d = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=random.randint(0, max_days))
    return int(d.timestamp())

data_base = DataBase()
BATCH = 500


async def seed_data() -> None:
    async with data_base.async_session() as session:
        try:
            # ---------- USERS ----------
            n_users = random.randint(220, 420)
            logger.info(f"Seeding {n_users} users...")

            users: List[User] = []
            base_phone = 79000000000
            for i in range(n_users):
                first = random.choice(FIRST_NAMES)
                last = random.choice(LAST_NAMES)
                middle = random.choice(MIDDLE_NAMES)
                users.append(
                    User(
                        user_name=f"user_{i}",
                        hashed_password="Password123!",
                        first_name=first,
                        last_name=last,
                        middle_name=middle,
                        email=f"user{i}@example.com",
                        phone=str(base_phone + i),
                        role=UserRole.user,
                        is_seller=False,
                    )
                )

            for batch in chunked(users, BATCH):
                session.add_all(batch)
                await session.flush()
            await session.commit()
            logger.info(f"{len(users)} users created.")

            # ---------- AUTHORS ----------
            n_authors = random.randint(30, 80)
            logger.info(f"Seeding {n_authors} authors...")
            authors = [Author(name=name) for name in random.sample(AUTHORS, k=min(n_authors, len(AUTHORS)))]
            session.add_all(authors)
            await session.flush()
            await session.commit()
            logger.info(f"{len(authors)} authors created.")

            # ---------- SELLERS ----------
            n_sellers = max(20, len(users) // 30)
            logger.info(f"Seeding {n_sellers} sellers...")
            seller_users = random.sample(users, n_sellers)
            sellers: List[Seller] = []
            for u in seller_users:
                u.is_seller = True
                sellers.append(Seller(user_id=u.id, name=f"{u.first_name}'s shop"))
            for batch in chunked(sellers, BATCH):
                session.add_all(batch)
                await session.flush()
            await session.commit()
            logger.info(f"{len(sellers)} sellers created.")

            # ---------- WAREHOUSES ----------
            n_warehouses = 40
            logger.info(f"Seeding {n_warehouses} warehouses...")
            warehouses = [Warehouse(available=True, location=random.choice(LOCATIONS)) for _ in range(n_warehouses)]
            session.add_all(warehouses)
            await session.flush()
            await session.commit()
            logger.info(f"{len(warehouses)} warehouses created.")

            # ---------- PRODUCT TYPES ----------
            n_product_types = random.randint(110, 200)
            logger.info(f"Seeding {n_product_types} product types...")

            product_types: List[ProductType] = []
            for _ in range(n_product_types):
                seller_choice = random.choice(sellers)
                author_choice = random.choice(authors)
                # если у тебя Enum Category в моделях:
                # category = random.choice(list(Category))
                category = random.choice(CATEGORIES)
                product_types.append(
                    ProductType(
                        seller_id=seller_choice.id,
                        available=True,
                        name=random.choice(PRODUCT_NAMES),
                        cost=Decimal(f"{random.uniform(10, 500):.2f}"),
                        sale=round(random.uniform(0.0, 0.5), 3),
                        author_id=author_choice.id,
                        date_publication=random_publication_ts(),
                        category=category,
                    )
                )
            for batch in chunked(product_types, BATCH):
                session.add_all(batch)
                await session.flush()
            await session.commit()
            logger.info(f"{len(product_types)} product types created.")

            # ---------- PRODUCTS ----------
            logger.info("Seeding products (several per product type)...")
            products: List[Product] = []
            for pt in product_types:
                for _ in range(random.randint(1, 7)):
                    products.append(
                        Product(
                            product_type_id=pt.id,
                            warehouse_id=random.choice(warehouses).id,
                        )
                    )
            for batch in chunked(products, BATCH):
                session.add_all(batch)
                await session.flush()
            await session.commit()
            logger.info(f"{len(products)} products created.")

        except Exception:
            await session.rollback()
            logger.exception("Error seeding data")
            raise