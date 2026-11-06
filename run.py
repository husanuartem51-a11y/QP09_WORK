"""Единая точка запуска учебного расчёта QP09. Внешние пакеты не нужны."""
import sys

if sys.version_info < (3, 10):
    raise SystemExit("Нужен Python 3.10 или новее.")

import argparse
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
PROGRAM = HERE / "program"
sys.path.insert(0, str(PROGRAM))
from shop_core import RuleError, quote, sorted_products


def main():
    parser = argparse.ArgumentParser(
        description="Расчёт учебной корзины. Без параметров запускается example.json.")
    parser.add_argument("--input", metavar="ФАЙЛ", default="example.json",
                        help="JSON корзины; относительный путь отсчитывается от папки run.py")
    parser.add_argument("--version", choices=("reference", "candidate"), default="reference",
                        help="вариант программы для исходной задачи; по умолчанию reference")
    parser.add_argument("--json", action="store_true", help="вывести результат в формате JSON")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--sort", action="store_true", help="показать каталог по возрастанию цены")
    group.add_argument("--check", action="store_true", help="выполнить две стартовые проверки запуска")
    args = parser.parse_args()

    if args.check:
        suite = unittest.defaultTestLoader.discover(str(PROGRAM / "tests"))
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        return 0 if result.wasSuccessful() else 1

    try:
        if args.sort:
            result = {"products": sorted_products(args.version)}
        else:
            path = Path(args.input)
            if not path.is_absolute():
                path = HERE / path
            try:
                data = json.loads(path.read_text(encoding="utf-8-sig"))
            except (OSError, UnicodeError, json.JSONDecodeError) as error:
                print("Не удалось прочитать JSON корзины: " + str(error), file=sys.stderr)
                return 1
            if not isinstance(data, dict):
                print("JSON корзины должен быть объектом с полями items, promo, fulfillment.", file=sys.stderr)
                return 1
            result = quote(data.get("items"), data.get("promo", ""),
                           data.get("fulfillment", "delivery"), args.version)
        payload = {"model": "offline-fixture-v1", "version": args.version,
                   "ok": True, "result": result}
    except RuleError as error:
        payload = {"model": "offline-fixture-v1", "version": args.version,
                   "ok": False, "error": error.code}
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print("Модель: offline-fixture-v1; версия программы: " + args.version)
            print("Расчёт отклонён. Код ошибки: " + error.code)
            print("Сверьте входные данные с 02_ТРЕБОВАНИЯ_К_МАГАЗИНУ.md.")
        return 2

    if args.json or args.sort:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("УЧЕБНЫЙ РАСЧЁТ QP09")
        print("Модель: offline-fixture-v1; версия программы: " + args.version)
        print("Входные данные: " + str(path))
        print("Все суммы ниже указаны в копейках.\n")
        fields = (("subtotal", "Сумма товаров до скидки"),
                  ("eligible_subtotal", "Сумма товаров, участвующих в акции"),
                  ("discount", "Скидка"),
                  ("after_discount", "Сумма товаров после скидки"),
                  ("delivery", "Доставка"),
                  ("total", "ИТОГО"))
        for key, title in fields:
            print(f"{title} ({key}): {result[key]}")
        print("\nЭто фактический ответ программы. Ожидание рассчитайте по требованиям.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
