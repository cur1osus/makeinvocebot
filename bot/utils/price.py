from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
import re
from difflib import get_close_matches
from collections import defaultdict
from typing_extensions import Iterable

TEXT = """
Куриные рулетики в панировке с зеленью — 800₽/кг
Куриные рулетики в панировке с грибами — 800₽/кг
Куриные рулетики в панировке с сыром — 800₽/кг
Котлеты по-киевски — 800₽/кг
Кордон блю — 800₽/кг
Котлеты по-донбасски (говядина + свинина) — 800₽/кг
Люля-кебаб свино-говяжий — 800₽/кг
Котлеты бургерные свино-говяжьи — 825₽/кг
Котлеты бургерные куриные — 775₽/кг
Котлеты рыбные — 675₽/кг
Котлеты рыбные без панировки — 700₽/кг
Котлеты куриные — 675₽/кг
Котлеты куриные без панировки — 675₽/кг
Котлеты свиные — 700₽/кг
Котлеты свино-говяжьи — 725₽/кг
Котлеты из индейки без панировки — 800₽/кг
Отбивные куриные — 675₽/кг
Отбивные свиные — 725₽/кг
Тефтели из курицы — 650₽/кг
Тефтели из свинины — 650₽/кг
Тефтели свино-говяжьи — 700₽/кг
Солянка с курицей и копчёностями — 225₽ (0.5 л)
Суп со свиными фрикадельками и с курицей — 200₽ (0.5 л)
Суп сырный с шампиньонами и с курицей — 200₽ (0.5 л)
Борщ домашний — 200₽ (0.5 л)
Куриный суп лапша — 200₽ (0.5 л)
Суп гороховый с копчёной курицей — 200₽ (0.5 л)
Суп харчо с курицей — 200₽ (0.5 л)
Лагман с говядиной — 225₽ (0.5 л)
Тайский суп (Том Ям с морепродуктами, грибами и острой заправкой) — 375₽ (0.5 л)
Уха с сёмгой — 300₽ (0.5 л)
Жюльен — 250₽ (300 г)
Паста карбонара — 250₽ (450 г)
Паста болоньезе — 250₽ (450 г)
Картофельное пюре с куриной отбивной (с помидором и сыром сверху) — 250₽ (450 г)
Бризоль (рулет, внутри сыр и помидор) с картофельным пюре — 250₽ (450 г)
Рис в сливочном соусе и минтай в кляре (с помидором и сыром сверху) — 250₽ (380 г)
Вареники с картошкой — 425₽/кг
Вареники картошка + грибы — 450₽/кг
Вареники картошка + печень — 450₽/кг
Вареники с капустой — 425₽/кг
Вареники с солёным творогом и укропом — 450₽/кг
Вареники с творогом — 450₽/кг
Вареники с вишней — 750₽/кг
Пельмени с курицей — 600₽/кг
Пельмени со свининой — 600₽/кг
Пельмени свино-говяжьи — 600₽/кг
Пельмени с индейкой — 600₽/кг
Пельмени с креветкой, творожным сыром и чесноком — 975₽/кг
Манты с курицей — 650₽/кг
Манты со свининой — 650₽/кг
Манты говядина + свинина — 700₽/кг
Чебуреки с курицей — 750₽/кг
Чебуреки со свининой — 750₽/кг
Чебуреки с сыром — 750₽/кг
Самса с курицей — 675₽/кг
Слойки с вишней — 625₽/кг
Слойки с абрикосом — 600₽/кг
Слойки с шоколадом — 600₽/кг
Слойки с клубникой — 600₽/кг
Слойки с курицей, сыром и помидором — 650₽/кг
Слойки с яблоком — 625₽/кг
Кубете — 650₽/кг
Хачапури с сыром — 625₽/кг
Сырники — 550₽/кг
Сырники с изюмом — 575₽/кг
Блины с курицей — 625₽/кг
Блины с курицей и грибами — 625₽/кг
Блины с мясом (свинина) — 625₽/кг
Блины с творогом — 600₽/кг
Блины с ветчиной и сыром — 625₽/кг
Блины с вишней, маком и творогом (трио) — 750₽/кг
Блины жюльен (сыр + грибы) — 625₽/кг
Блины с яблоками и корицей — 575₽/кг
Блины картофель + грибы — 525₽/кг
Блины картофель + печень — 525₽/кг
Блины с сёмгой и творожным сыром — 1425₽/кг
Голубцы с курицей — 650₽/кг
Голубцы со свининой — 650₽/кг
Голубцы свино-говяжьи — 700₽/кг
Фаршированный перец с курицей — 650₽/кг
Фаршированный перец свино-говяжий — 700₽/кг
Картофельные зразы с курицей — 650₽/кг
Картофельные зразы с курицей и грибами — 700₽/кг
Стейк зуратки (150-400 гр): 700 ₽)
Стейк семги (250-350 гр): 2170 ₽)
Стейк кеты (250-500 гр): 940 ₽)
Килька пряный посол: 390 ₽)
Сельдь по-домашнему в уксусе масляной заливке: 720 ₽)
Сардина (мясо тушки в масле скумбрия в масле): 750 ₽)
Горель по-тайски масле морской коктейль в масле с ЛОСОСЕМ (5 компонентов): 2500 ₽)
Мидии в укс.-мас. заливке: 1250 ₽)
Дорадо ЖЕЕР (450-500 гр): 230 ₽)
Кнепи из ИКРЫ СОСА (300-350 гр): 190 ₽)
Кнепи из СЕЛЁДКА (300-350 гр): 165 ₽)
Рупет КИЖУЧ (300-400 гр): 300 ₽)
Филе кижуч, морской гребешок, икра тобико: 370 ₽)
Рупет лосось, тигровая креветка, творожный сыр, зелень: 200 ₽)
Филе тунец, морской гребешок, сливочный сыр: 300 ₽)
Филе форель (300-400 гр): 185 ₽)
Сивас с овощами (400-450 гр): 200 ₽)
Сивас с томатами (300-450 гр): 320 ₽)
Шашлычки из СЕЛЁДКИ и ШПИНАТОМ (300-400 гр): 470 ₽)
Шашлычки с гребешком в беконе (200-250 гр): 240 ₽)
Гребешки с моцареллой (3 шт.): 620 ₽)
Селень и моцарелла чеснок под муссой пармезана: 550 ₽)
Мидии тобико (бут.) 200 гр. ун.: 550 ₽)
Креветки в панировке (40/50), (1 кг.): 1650 ₽)
Колбаса ПАЛЛАРЬ в кляре (1 кг.): 1150 ₽)
Сырные палочки (1 кг.): 1050 ₽)
Наггетсы куриные в темпуре: 850 ₽)
Навор том ЯМ суп на 2 порции (НЕ острый) (370 гр.): 775 ₽)
Навор том ЯМ суп на 2 порции (ОСТРЫЙ) (370 гр.): 775 ₽)
Навор том КХА суп на 2 порции (400 гр.): 800 ₽)
Навор удон с морепродуктами на 2 порции (390 гр.): 825 ₽)
Креветки (31-40) сырые: 980 ₽)
Креветки тигровые сырые лангустины (гол. и гол.), вареные креветки очищенные с хвостом (26/30), сырые: 1250 ₽)
Креветки очищенные с хвостом (26/30), сырые: 1520 ₽)
Креветки северная (120+), вареная: 1240 ₽)
Креветки ванаamey (40-50), сырая: 850 ₽)
Креветки белоногая (50-70), вареная: 870 ₽)
Креветки очищенная варено-мороженые (200-300 шт): 1400 ₽)
Калмар (филе) (~250-300 гр): 920 ₽)
Салат чукча: 550 ₽)
Краевые палочки columbus мясо рапана морской коктейль (кальм, креветки, мидии, кальмар, лангустины): 750 ₽)
Осьминоги (филе) (40/60): 1190 ₽)
Мидии в подливке (30-45 шт.): 670 ₽)
Филе тревика (свежемороженое, (80-100 шт. на 1 кг)): 3250 ₽
Икра осетра премиум (черная) (~250 гр, пастеризован тара): 3000 ₽
Икра осетра премиум (черная) (~50 гр, стекло): 4500 ₽
Икра осетра премиум (черная) (~100 гр, стекло): 9500 ₽
Карась (~200 гр): 1190 ₽)
Вомер (~200-300 гр): 395 ₽)
Кефаль (тополови) (~400 гр): 1070 ₽)
Окунь (~300-500 гр): 1050 ₽)
Масляная (филе на коже) (~1-5 кг): 1950 ₽)
Скумбрия (~300-350 гр): 1000 ₽)
Шипальца калимача (40-60 шт. на 1 кг): 2140 ₽)
Толстолоб (1-2 кг): 670 ₽)
Килька толька: 600 ₽)
Сардину (ивси) ивсикоокеанская филе сельдь атлантической ставрида (~600-800 гр): 630 ₽)
Горбуша (~1-2 кг): 1450 ₽)
Бычок (ошпаренный) (~50 гр): 2400 ₽
Камбала (еловрюха) (~300-500 гр): 1270 ₽
Кефаль (шаланда) (~400 гр): 870 ₽
Лещ астраханский (~200-300 гр): 615 ₽
Лещ шмплянский (~700-900 гр): 820 ₽
Плоти (~100-150 гр): 780 ₽
Судак (~200-400 гр): 850 ₽
Чехонь (~150 гр): 1020 ₽
Вобла (~100 гр): 1200 ₽
Вомер (150-200 гр): 642 ₽ (474 ₽)
Лакедра (800-1,5 кг): 1135 ₽
Дорадо (400-600 гр): 1 кг 1135 ₽
Скумбрия неразделанная (400-600 гр): 1 кг 577 ₽
Ставрида головон (900+ гр): 1 кг 419 ₽
Хек (300-400 гр): 1 кг 604 ₽
Терпуг (1-1,5 кг): 1 кг 548 ₽
Кихучь без головы (4+ кг, Чили): 1 кг 1535 ₽
Кета потрошеная без головы (1-1,5 кг): 1 кг 902 ₽
Форель без головы (1-1,5 кг, Турция): 1 кг 1386 ₽
Форель без головы (2-7,4 кг, Турция): 1 кг 1572 ₽
Семга с головой (5-6 кг, Чили, премиум): 1 кг 1850 ₽
Филе пангасиуса свежемороженое (500-600 гр): 1 кг 372 ₽
Филе сельди свежемороженое (150 гр): 1 кг 409 ₽
Филе пантуса свежемороженое, на коже (200-300 гр): 1 кг 678 ₽
Филе окуня свежемороженое, на коже (200-300 гр): 1 кг 750 ₽
Филе трески свежемороженое, на коже (500-600 гр): 1 кг 850 ₽
Филе судака свежемороженое, на коже (350-550 гр): 1 кг 950 ₽
Филе тиляпии свежемороженое (150-200 гр): 1 кг 900 ₽
Филе туна свежемороженое (Tuna Fillet, 2-4, 350-600 гр): 1 кг 1280 ₽
Филе креветки свежемороженое (Shrimp Fillet, 350-600 гр): 1 кг 2200 ₽
Филе гребешков свежемороженое, на коже (Scallop Fillet, 350-500 гр): 1 кг 735 ₽
Филе лосося свежемороженое, атл. (Salmon Fillet, 350-600 гр): 1 кг 2316 ₽
Раки варёные замороженные (10-15 шт): 3650 ₽
Раки варёные замороженные (16-24 шт): 3150 ₽
Сыр творожный савушкин (0,9 кг): 875 ₽
Икра "маслото" красная премиум натуральная (500 гр): 650 ₽
Икра "только" красная премиум натуральная (500 гр): 1050 ₽
Хондалии рыбий бульон сухой приправа премиум (1 кг): 1050 ₽
Угорь жареный в унаги 10% (700-800 гр): 2200 ₽
"""


@dataclass
class ItemPrice:
    name: str
    unit_price: Decimal
    discount_threshold: Decimal | None = None  # в кг или шт
    discounted_price: Decimal | None = None  # цена при скидке


def parse_price_line(line: str) -> ItemPrice | None:
    """
    Разбор строки типа: 'Креветки в панировке (40/50), (1 кг.): 1650 ₽)'
    или: 'Куриные рулетики в панировке с зеленью — 800₽/кг'
    """
    line = line.strip()
    if not line:
        return None

    name_part, *price_parts = re.split(r"—|:", line)
    name = name_part.strip()

    price_info = ":".join(price_parts).strip()

    # Ищем цену, скидку и порог
    base_price_match = re.search(r"(\d+)\s?[₽р]", price_info)

    if base_price_match:
        base_price = Decimal(base_price_match.group(1))
        return ItemPrice(name=name, unit_price=base_price)
    return None


def parse_weight_input(input_str: str) -> Decimal:
    """Преобразует строку с весом в килограммы"""
    match = re.match(r"(?i)^\s*([\d.]+)\s*(г|гр|грамм|кг|кг|литр|л\.?)\s*$", input_str)
    if not match:
        raise ValueError("Некорректный формат веса. Пример: '0.5 кг' или '300 г или 3 л'")
    amount = Decimal(match.group(1).replace(",", "."))
    unit = match.group(2).lower()
    if "г" in unit and "к" not in unit:
        amount /= 1000
    elif "л" in unit:
        amount *= 1000
    return amount.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)


def get_price(item: ItemPrice, amount_str: str) -> Decimal:
    """Вычисляет итоговую цену товара по весу или количеству"""
    is_piece = re.search(r"шт|порц|п|бут|уп|штук|позиц", amount_str, re.I)
    is_volume = re.search(r"л|литр", amount_str, re.I)
    if is_piece:
        quantity = Decimal(re.sub(r"[^\d.]", "", amount_str).replace(",", "."))
        price = item.unit_price
        if price is None:
            raise ValueError("Цена товара не указана")
        total = quantity * price
    elif is_volume:
        volume = parse_weight_input(amount_str)
        volume = Decimal(re.sub(r"[^\d.]", "", amount_str).replace(",", "."))
        price = item.unit_price
        if price is None:
            raise ValueError("Цена товара не указана")
        total = volume * price * 2
    else:
        weight_kg = parse_weight_input(amount_str)
        price = item.unit_price
        if price is None:
            raise ValueError("Цена товара не указана")
        total = weight_kg * price

    return total.quantize(Decimal("0"))


def load_items_from_text(text: str) -> dict[str, ItemPrice]:
    """Парсит текстовый прайс в словарь"""
    items: dict[str, ItemPrice] = {}
    for line in text.splitlines():
        item = parse_price_line(line)
        if item:
            items[item.name] = item
    return items


def search(input: str, catalog: Iterable) -> list[str]:
    """Поиск по частичным совпадениям, ранжированный по числу совпадений"""
    terms = input.lower().split()
    scores = defaultdict(int)

    for item in catalog:
        lowered = item.lower()
        match_count = sum(term in lowered for term in terms)
        if match_count > 0:
            scores[item] = match_count

    return sorted(scores, key=lambda x: (-scores[x], x))


def find_best_match(user_input: str) -> ItemPrice:
    """Ищет точное или ближайшее совпадение по названию"""
    if user_input in catalog:
        return catalog[user_input]

    _search = search(user_input, catalog)
    if _search:
        print(f"[!] Использовано приближённое совпадение: '{_search[0]}' вместо '{user_input}'")
        return catalog[_search[0]]
    matches = get_close_matches(user_input, catalog.keys(), n=1, cutoff=0.5)
    if matches:
        print(f"[!] Использовано приближённое совпадение: '{matches[0]}' вместо '{user_input}'")
        return catalog[matches[0]]

    return ItemPrice(unit_price=Decimal(0), name="Unknown")


catalog = load_items_from_text(TEXT)


def calculate_price(name_product: str, quantity: str = "1") -> tuple[str, Decimal]:
    item = find_best_match(name_product)
    price = get_price(item, quantity)
    return item.name, price
