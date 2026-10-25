# -*- coding: utf-8 -*-
"""Character-card layout definitions and prompt compilation."""

from __future__ import annotations

import copy
import json
import re
from typing import Any


DEFAULT_NEGATIVE = (
    "низкое качество, размытие, деформации, лишние конечности, неправильные пальцы, "
    "дрейф личности, разрушенное лицо, смена пола, ошибки кроя одежды, пропавшие аксессуары, "
    "хаотичная раскладка панелей, дублирование персонажа, копирование одного и того же лица, "
    "неверное число ячеек, лишние ячейки, недостающие ячейки, слияние ячеек, ошибочная сетка 3×3, "
    "испорченный текст, водяные знаки, логотипы, обрезка головы, обрезка ног, обрезка обуви, "
    "полуфигура вместо полного роста, обрубленные ноги, срезанная голова, "
    "серый фон, тёмно-серый фон, тёмный фон, градиентный фон, текстурный фон, фон с тенями"
)

ROLE_NAMES = {
    "hero": "крупный одиночный ключевой кадр в полный рост",
    "turnaround": "одиночный персонаж в полный рост целиком",
    "portrait": "одиночный портрет головы и плеч",
    "expression": "одиночный портрет головы и плеч с эмоцией",
    "detail": "локальный макро-деталь",
    "scene_anchor": "фронтальный референс сцены",
    "scene_view": "сцена с нескольких ракурсов",
    "scene_panorama": "360° панорама сцены",
    "scene_detail": "детали материалов сцены",
}


def _cell(
    cell_id: str,
    label: str,
    role: str,
    prompt: str,
    x: float,
    y: float,
    w: float,
    h: float,
    mirror: bool = False,
) -> dict[str, Any]:
    return {
        "id": cell_id,
        "label": label,
        "role": role,
        "prompt": prompt,
        "x": x,
        "y": y,
        "w": w,
        "h": h,
        "mirror": mirror,
    }


TEMPLATES: list[dict[str, Any]] = [
    {
        "id": "bighead_body3",
        "name": "4 ячейки · Портрет+",
        "description": "Слева крупный фронтальный портрет головы и плеч, справа рядом три полных роста: анфас, профиль и спина.",
        "layout_prompt": "Две колонки: слева только 1 крупный портрет головы и плеч; справа только 3 равных по ширине вертикальных ячейки полного роста — анфас, профиль, спина. Всего 4 ячейки.",
        "width": 1920,
        "height": 1200,
        "defaults": {
            "title": "Безымянный персонаж",
            "subtitle": "Сеттинг персонажа",
            "style": "единый ассет персонажа, чисто белый студийный фон, мягкий студийный свет, реалистичный кинематографичный вид",
            "background": "#ffffff",
            "accent": "#d86b73",
        },
        "cells": [
            _cell("head_big", "Крупный портрет анфас", "portrait", "Фронтальный портрет головы и плеч, голова и плечи полностью в кадре, черты лица и украшения в волосах чёткие, взгляд в камеру, в кадре только один человек.", 0.03, 0.03, 0.40, 0.94),
            _cell("body_front", "Полный рост анфас", "turnaround", "Полный рост анфас, естественная стойка, руки свободно вдоль тела, от макушки до подошв без обрезки, в кадре только один человек.", 0.46, 0.12, 0.16, 0.78),
            _cell("body_side", "Полный рост профиль", "turnaround", "Строго 90° левый профиль в полный рост, персонаж смотрит вправо кадра, видна только левая половина лица и левое ухо, от макушки до подошв без обрезки.", 0.635, 0.12, 0.16, 0.78),
            _cell("body_back", "Полный рост спина", "turnaround", "Строго 180° вид со спины в полный рост, видны только затылок и спина, от макушки до подошв без обрезки.", 0.81, 0.12, 0.16, 0.78),
        ],
    },
    {
        "id": "dualfour_ref",
        "name": "4 ячейки · Два кадра",
        "description": "Равная сетка 2×2: сверху портреты анфас и три четверти, снизу полный рост анфас и спина.",
        "layout_prompt": "Равная сетка 2 ряда × 2 столбца: сверху слева портрет анфас головы и плеч, справа — три четверти; снизу слева полный рост анфас, справа — спина. Всего 4 ячейки, нельзя добавлять третий ряд.",
        "width": 1920,
        "height": 1200,
        "defaults": {
            "title": "Безымянный персонаж",
            "subtitle": "Двухракурсный сеттинг",
            "style": "единый ассет персонажа, чисто белый студийный фон, мягкий студийный свет, реалистичный кинематографичный вид",
            "background": "#ffffff",
            "accent": "#6b8dd8",
        },
        "cells": [
            _cell("head_front", "Портрет анфас", "portrait", "Крупный план головы и плеч анфас, голова и плечи полностью в кадре, взгляд в камеру, второго человека нет.", 0.03, 0.03, 0.46, 0.43),
            _cell("head_three_quarter", "Портрет три четверти", "portrait", "Крупный план головы и плеч в три четверти, лицо к правому переднему углу кадра, видны контуры обеих щёк, взгляд в камеру.", 0.51, 0.03, 0.46, 0.43),
            _cell("body_front", "Полный рост анфас", "turnaround", "Полный рост анфас, естественная стойка, взгляд в камеру, от макушки до подошв без обрезки, в кадре только один человек.", 0.03, 0.52, 0.46, 0.45),
            _cell("body_back", "Полный рост спина", "turnaround", "Строго 180° вид со спины в полный рост, видны только затылок и спина, от макушки до подошв без обрезки.", 0.51, 0.52, 0.46, 0.45),
        ],
    },
    {
        "id": "fiveref",
        "name": "5 ячеек · Лицо и тело",
        "description": "Сверху портреты анфас и три четверти, снизу три полных роста: анфас, профиль и спина.",
        "layout_prompt": "Два ряда: сверху только 2 ячейки — портреты головы и плеч; снизу только 3 ячейки — полный рост. Всего 5 ячеек.",
        "width": 1920,
        "height": 1200,
        "defaults": {
            "title": "Безымянный персонаж",
            "subtitle": "Пятиракурсный сеттинг",
            "style": "единый ассет персонажа, чисто белый студийный фон, мягкий студийный свет, реалистичный кинематографичный вид",
            "background": "#ffffff",
            "accent": "#65a89a",
        },
        "cells": [
            _cell("head_front", "Портрет анфас", "portrait", "Крупный план головы и плеч анфас, голова и плечи полностью в кадре, взгляд в камеру.", 0.03, 0.03, 0.47, 0.43),
            _cell("head_three_quarter", "Портрет три четверти", "portrait", "Крупный план головы и плеч в три четверти, лицо к правому переднему углу кадра, взгляд в камеру, угол заметно отличается от анфаса.", 0.50, 0.03, 0.47, 0.43),
            _cell("body_front", "Полный рост анфас", "turnaround", "Полный рост анфас, естественная стойка, от макушки до подошв без обрезки, в кадре только один человек.", 0.03, 0.52, 0.305, 0.45),
            _cell("body_side", "Полный рост профиль", "turnaround", "Строго 90° левый профиль в полный рост, персонаж смотрит вправо кадра, от макушки до подошв без обрезки.", 0.348, 0.52, 0.305, 0.45),
            _cell("body_back", "Полный рост спина", "turnaround", "Строго 180° вид со спины в полный рост, видны только затылок и спина, от макушки до подошв без обрезки.", 0.665, 0.52, 0.305, 0.45),
        ],
    },
    {
        "id": "head_body_6",
        "name": "6 ячеек · Три вида",
        "description": "Сверху три портрета головы и плеч: анфас, профиль, затылок; снизу три полных роста: анфас, профиль, спина.",
        "layout_prompt": "Равная сетка 2 ряда × 3 столбца: сверху 3 ячейки — только портреты головы и плеч; снизу 3 ячейки — только полный рост. Всего 6 ячеек, нельзя генерировать сетку 3×3.",
        "width": 1920,
        "height": 1280,
        "defaults": {
            "title": "Безымянный персонаж",
            "subtitle": "Три вида",
            "style": "единый ассет персонажа, чисто белый студийный фон, мягкий студийный свет, реалистичный кинематографичный вид",
            "background": "#ffffff",
            "accent": "#6b8dd8",
        },
        "cells": [
            _cell("head_front", "Портрет анфас", "portrait", "Крупный план головы и плеч анфас, голова и плечи полностью в кадре, взгляд в камеру.", 0.03, 0.03, 0.303, 0.43),
            _cell("head_side", "Портрет профиль", "portrait", "Строго 90° профиль головы и плеч, персонаж смотрит вправо кадра, видна только левая половина лица и левое ухо.", 0.345, 0.03, 0.303, 0.43),
            _cell("head_back", "Портрет затылка", "portrait", "Портрет головы и плеч со спины, видны только затылок и причёска, лица не видно.", 0.66, 0.03, 0.303, 0.43),
            _cell("body_front", "Полный рост анфас", "turnaround", "Полный рост анфас, естественная стойка, от макушки до подошв без обрезки, в кадре только один человек.", 0.03, 0.52, 0.303, 0.45),
            _cell("body_side", "Полный рост профиль", "turnaround", "Строго 90° левый профиль в полный рост, персонаж смотрит вправо кадра, от макушки до подошв без обрезки.", 0.345, 0.52, 0.303, 0.45),
            _cell("body_back", "Полный рост спина", "turnaround", "Строго 180° вид со спины в полный рост, видны только затылок и спина, от макушки до подошв без обрезки.", 0.66, 0.52, 0.303, 0.45),
        ],
    },
    {
        "id": "sixtilt_ref",
        "name": "6 ячеек · Главный вид",
        "description": "Слева крупный ключевой кадр; справа два ряда по две ячейки, внизу горизонтальная полоса детали ткани.",
        "layout_prompt": "Неравномерная раскладка: слева 1 крупный ключевой кадр; справа сверху 2 ячейки (портрет анфас, улыбка), в среднем ряду 2 ячейки (профиль в полный рост, динамичный полный рост), справа внизу 1 горизонтальная полоса детали ткани. Всего 6 ячеек.",
        "width": 1920,
        "height": 1280,
        "defaults": {
            "title": "Безымянный персонаж",
            "subtitle": "Главный визуальный сеттинг",
            "style": "единый ассет персонажа, чисто белый студийный фон, мягкий студийный свет, реалистичный кинематографичный вид",
            "background": "#ffffff",
            "accent": "#9b7dd8",
        },
        "cells": [
            _cell("hero", "Ключевой кадр", "hero", "Фронтальный ключевой кадр в полный рост, естественная стойка, от макушки до подошв полностью в кадре, в кадре только один человек.", 0.03, 0.08, 0.39, 0.84),
            _cell("head_front", "Портрет анфас", "portrait", "Крупный план головы и плеч анфас, голова и плечи полностью в кадре, взгляд в камеру.", 0.45, 0.08, 0.26, 0.25),
            _cell("ex_smile", "Улыбка", "expression", "Крупный план головы и плеч с улыбкой, уголки губ приподняты, глаза слегка прищурены, эмоция заметно отличается от спокойного анфаса.", 0.735, 0.08, 0.235, 0.25),
            _cell("body_side", "Полный рост профиль", "turnaround", "Строго 90° левый профиль в полный рост, персонаж смотрит вправо кадра, от макушки до подошв без обрезки.", 0.45, 0.36, 0.26, 0.27),
            _cell("action_pose", "Динамичный полный рост", "turnaround", "Динамичная стойка в полный рост, поза рук заметно отличается от ключевого кадра, от макушки до подошв без обрезки.", 0.735, 0.36, 0.235, 0.27),
            _cell("de_fabric", "Деталь ткани", "detail", "Горизонтальный макрокадр ткани одежды и вышивки: только текстура, складки и золотая нить, без лица и без полного роста.", 0.45, 0.66, 0.52, 0.26),
        ],
    },
    {
        "id": "expr_body_8",
        "name": "8 ячеек · Эмоции",
        "description": "Сверху 4 портрета головы и плеч с разными эмоциями, снизу четыре полных роста: анфас, профиль, спина и движение.",
        "layout_prompt": "Равная сетка 2 ряда × 4 столбца: сверху 4 ячейки — только портреты головы и плеч с разными эмоциями; снизу 4 ячейки — только полный рост. Всего 8 ячеек.",
        "width": 1920,
        "height": 1200,
        "defaults": {
            "title": "Безымянный персонаж",
            "subtitle": "Многоракурсный сеттинг",
            "style": "единый ассет персонажа, чисто белый студийный фон, мягкий студийный свет, реалистичный кинематографичный вид",
            "background": "#ffffff",
            "accent": "#d86b73",
        },
        "cells": [
            _cell("head_neutral", "Спокойствие", "expression", "Крупный план головы и плеч, нейтральное спокойствие, губы сомкнуты, взгляд прямо, лицо расслаблено.", 0.03, 0.03, 0.225, 0.43),
            _cell("head_happy", "Радостный смех", "expression", "Крупный план головы и плеч, открытый радостный смех с зубами, глаза сощурены дугами, эмоция заметно отличается от первой ячейки.", 0.268, 0.03, 0.225, 0.43),
            _cell("head_serious", "Серьёзность", "expression", "Крупный план головы и плеч, губы плотно сжаты, брови слегка нахмурены, строгий взгляд в камеру.", 0.505, 0.03, 0.225, 0.43),
            _cell("head_surprised", "Удивление", "expression", "Крупный план головы и плеч, глаза широко открыты, брови подняты, рот слегка приоткрыт — выражение удивления.", 0.743, 0.03, 0.225, 0.43),
            _cell("body_front", "Полный рост анфас", "turnaround", "Полный рост анфас, естественная стойка, руки свободно вдоль тела, от макушки до подошв без обрезки.", 0.03, 0.52, 0.225, 0.45),
            _cell("body_profile", "Полный рост левый профиль", "turnaround", "Строго 90° левый профиль в полный рост, персонаж смотрит вправо кадра, от макушки до подошв без обрезки.", 0.268, 0.52, 0.225, 0.45),
            _cell("body_back", "Полный рост спина", "turnaround", "Строго 180° вид со спины в полный рост, видны только затылок и спина, от макушки до подошв без обрезки.", 0.505, 0.52, 0.225, 0.45),
            _cell("body_action", "Полный рост в движении", "turnaround", "Естественная ходьба в полный рост, походка отличается от стоек в первых трёх ячейках, от макушки до подошв без обрезки.", 0.743, 0.52, 0.225, 0.45),
        ],
    },
    {
        "id": "school_ref",
        "name": "10 ячеек · Сеттинг",
        "description": "Слева ключевой кадр; справа сверху три вида, в среднем ряду три эмоции, снизу три детали.",
        "layout_prompt": "Две колонки: слева только 1 крупный ключевой кадр; справа 3 столбца × 3 ряда — сверху 3 ячейки полного роста, в середине 3 эмоции головы и плеч, снизу 3 локальные детали. Всего 10 ячеек.",
        "width": 2000,
        "height": 1400,
        "defaults": {
            "title": "Безымянный персонаж",
            "subtitle": "Набор сеттинга персонажа",
            "style": "единый ассет персонажа, чисто белый студийный фон, мягкий студийный свет",
            "background": "#ffffff",
            "accent": "#e08a9a",
        },
        "cells": [
            _cell("hero", "Ключевой кадр", "hero", "Одиночный фронтальный ключевой кадр в полный рост, естественная стойка, от макушки до подошв полностью в кадре, второго человека или коллажа быть не должно.", 0.03, 0.08, 0.30, 0.86),
            _cell("body_front", "Полный рост анфас", "turnaround", "Полный рост анфас, естественная стойка, от макушки до подошв без обрезки.", 0.36, 0.08, 0.20, 0.40),
            _cell("body_side", "Полный рост профиль", "turnaround", "Строго 90° левый профиль в полный рост, персонаж смотрит вправо кадра, от макушки до подошв без обрезки.", 0.58, 0.08, 0.20, 0.40),
            _cell("body_back", "Полный рост спина", "turnaround", "Строго 180° вид со спины в полный рост, видны только затылок и спина, от макушки до подошв без обрезки.", 0.80, 0.08, 0.17, 0.40),
            _cell("ex_1", "Сладкая улыбка", "expression", "Крупный план головы и плеч, открытая сладкая улыбка с зубами, глаза прищурены, яркая эмоция.", 0.36, 0.52, 0.20, 0.20),
            _cell("ex_2", "Задумчивость", "expression", "Крупный план головы и плеч, голова опущена, взгляд вниз, не в камеру, тихое сдержанное выражение.", 0.58, 0.52, 0.20, 0.20),
            _cell("ex_3", "Удивление с открытым ртом", "expression", "Крупный план головы и плеч, глаза широко открыты, брови подняты, рот открыт — выражение удивления.", 0.80, 0.52, 0.17, 0.20),
            _cell("de_1", "Деталь одежды", "detail", "Локальный макрокадр воротника формы, значка и текстуры ткани, без полного персонажа.", 0.36, 0.75, 0.20, 0.20),
            _cell("de_2", "Деталь аксессуара", "detail", "Локальный макрокадр галстука-бабочки или украшения в волосах, без лица.", 0.58, 0.75, 0.20, 0.20),
            _cell("de_3", "Деталь обуви", "detail", "Локальный макрокадр конструкции и материала обуви, без полного персонажа.", 0.80, 0.75, 0.17, 0.20),
        ],
    },
    {
        "id": "xianxia_ref",
        "name": "14 ячеек · Полный атлас",
        "description": "Слева четыре полных роста и три портрета, справа четыре эмоции и три детали, внизу горизонтальная полоса ткани.",
        "layout_prompt": "Две колонки: слева сверху 4 полных роста, снизу 3 портрета; справа сверху 3 эмоции, в среднем ряду 3 ячейки (1 эмоция + 2 детали), внизу 1 горизонтальная полоса детали ткани. Всего 14 ячеек, нельзя добавлять четвёртый ряд.",
        "width": 2200,
        "height": 1300,
        "defaults": {
            "title": "Безымянный персонаж",
            "subtitle": "Полный атлас",
            "style": "единый ассет персонажа, чисто белый студийный фон, мягкий студийный свет, реалистичная проработка",
            "background": "#ffffff",
            "accent": "#7a9bd8",
        },
        "cells": [
            _cell("body_front", "Полный рост анфас", "turnaround", "Полный рост анфас, естественная стойка, от макушки до подошв без обрезки, в кадре только один человек.", 0.02, 0.03, 0.125, 0.42),
            _cell("body_right", "Полный рост правый профиль", "turnaround", "Строго 90° правый профиль в полный рост, персонаж смотрит влево кадра, видна только правая половина лица и правое ухо, от макушки до подошв без обрезки.", 0.155, 0.03, 0.125, 0.42),
            _cell("body_back", "Полный рост спина", "turnaround", "Строго 180° вид со спины в полный рост, видны только затылок и спина, от макушки до подошв без обрезки.", 0.29, 0.03, 0.125, 0.42),
            _cell("body_left", "Полный рост левый профиль", "turnaround", "Строго 90° левый профиль в полный рост, персонаж смотрит вправо кадра, видна только левая половина лица и левое ухо, направление противоположно правому профилю.", 0.425, 0.03, 0.125, 0.42),
            _cell("head_1", "Портрет анфас", "portrait", "Фронтальный портрет головы и плеч, голова и плечи полностью в кадре, спокойный взгляд в камеру.", 0.02, 0.47, 0.15, 0.43),
            _cell("head_2", "Портрет профиль", "portrait", "Строго 90° профиль головы и плеч, персонаж смотрит вправо кадра, показан контур профиля.", 0.18, 0.47, 0.15, 0.43),
            _cell("head_3", "Портрет три четверти", "portrait", "Портрет головы и плеч в три четверти, лицо к правому переднему углу кадра, взгляд в камеру.", 0.34, 0.47, 0.15, 0.43),
            _cell("ex_1", "Нежная улыбка", "expression", "Крупный план головы и плеч, закрытая нежная улыбка, уголки губ слегка приподняты, мягкий взгляд.", 0.58, 0.03, 0.12, 0.25),
            _cell("ex_2", "Удивление с открытым ртом", "expression", "Крупный план головы и плеч, глаза широко открыты, брови подняты, рот слегка приоткрыт — выражение удивления.", 0.71, 0.03, 0.12, 0.25),
            _cell("ex_3", "Закрытые глаза, задумчивость", "expression", "Крупный план головы и плеч, глаза закрыты, голова слегка опущена, губы слегка сжаты, тихое выражение.", 0.84, 0.03, 0.12, 0.25),
            _cell("ex_4", "Холодный хмурый взгляд", "expression", "Крупный план головы и плеч, брови слегка нахмурены, холодный прямой взгляд, заметно отличается от улыбки.", 0.58, 0.30, 0.12, 0.25),
            _cell("de_1", "Деталь глаза", "detail", "Макрокадр одного глаза: цвет зрачка, текстура радужки и ресницы, без всего лица.", 0.71, 0.30, 0.12, 0.25),
            _cell("de_2", "Деталь аксессуара", "detail", "Макрокадр ожерелья, серьги или украшения в волосах, без лица.", 0.84, 0.30, 0.12, 0.25),
            _cell("de_3", "Деталь ткани", "detail", "Горизонтальный макрокадр ткани одежды и вышивки: только текстура ткани, складки и узор, без персонажа.", 0.58, 0.57, 0.38, 0.37),
        ],
    },
    {
        "id": "scene_six_view",
        "kind": "scene",
        "name": "Сцена · 360° обзор",
        "description": "Загрузите любой кадр сцены и получите полный круговой обзор по 0°, 90°, 180°, 270°, плюс полосу 360° панорамы и деталь окружения.",
        "layout_prompt": "Сверху 4 ячейки слева направо: 0° фронтальный референс, 90° вправо, 180° назад, 270° влево; снизу слева непрерывная длинная 360° панорама, справа — деталь окружения. Всего 6 ячеек.",
        "width": 1920,
        "height": 1280,
        "defaults": {
            "title": "Безымянная сцена",
            "subtitle": "360° круговой обзор сцены",
            "style": "реалистичный концепт сцены, единая пространственная структура, материалы, перспектива и освещение",
            "background": "#ffffff",
            "accent": "#4f8a8b",
        },
        "cells": [
            _cell("scene_front", "0° фронтальный референс", "scene_anchor", "Сохранить загруженный кадр сцены как единственный пространственный якорь: не перерисовывать и не менять композицию; если референса нет — сгенерировать главный 0° фронтальный вид сцены. Сцена главная, не добавлять людей или животных.", 0.03, 0.03, 0.217, 0.43),
            _cell("scene_right", "90° вправо", "scene_view", "С позиции камеры 0° повернуть примерно на 90° вправо и снять правую сторону той же сцены; должно появиться правое пространство, не показанное на 0°, с сохранением рельефа, архитектуры, дорог, растительности, ключевых объектов, материалов и освещения. Сцена главная, не добавлять людей или животных.", 0.271, 0.03, 0.217, 0.43),
            _cell("scene_back", "180° назад", "scene_view", "С позиции камеры 0° развернуться примерно на 180° и снять противоположный ракурс той же сцены; вид должен образовать непрерывное пространство с 0° и 90°, с тем же масштабом, положением ключевых объектов и направлением света. Сцена главная, не добавлять людей или животных.", 0.512, 0.03, 0.217, 0.43),
            _cell("scene_left", "270° влево", "scene_view", "С позиции камеры 0° повернуть примерно на 90° влево, то есть направление 270°; должно появиться левое пространство, не показанное на 0°, и сомкнуться с 90° и 180°. Сцена главная, не добавлять людей или животных.", 0.753, 0.03, 0.217, 0.43),
            _cell("scene_panorama", "360° панорама", "scene_panorama", "Сгенерировать горизонтальную непрерывную 360° развёртку той же сцены: слева направо естественно стыкуются 0°, 90°, 180°, 270° и возврат к 0°; рельеф, архитектура, дороги, растительность, ключевые объекты, материалы и освещение непрерывны. Сцена главная, не добавлять людей или животных.", 0.03, 0.50, 0.64, 0.45),
            _cell("scene_detail", "Деталь окружения", "scene_detail", "Выделить самый узнаваемый материал, текстуру, растительность, архитектурный элемент или декор сцены в локальный макрокадр; цвет и материал должны совпадать с окружением. Сцена главная, не добавлять людей или животных.", 0.70, 0.50, 0.27, 0.45),
        ],
    },
]


TEMPLATE_BY_ID = {template["id"]: template for template in TEMPLATES}
CARD_TEMPLATE_IDS = [template["id"] for template in TEMPLATES]
# Keep the old names import-compatible with existing workflows.
FIVE_TEMPLATE_IDS = CARD_TEMPLATE_IDS
FIVE_TEMPLATE_OPTIONS = [f"{template_id} | {TEMPLATE_BY_ID[template_id]['name']}" for template_id in CARD_TEMPLATE_IDS]
TEMPLATE_OPTIONS = [f"{template['id']} | {template['name']}" for template in TEMPLATES]
CHARACTER_TEMPLATE_OPTIONS = [
    f"{template['id']} | {template['name']}"
    for template in TEMPLATES
    if template.get("kind") != "scene"
]
DEFAULT_TEMPLATE_OPTION = next(
    (option for option in TEMPLATE_OPTIONS if option.startswith("head_body_6 |")),
    TEMPLATE_OPTIONS[0],
)
SOURCE_TEMPLATE_OPTIONS = ["source | Как у входной карты", *TEMPLATE_OPTIONS]


def get_templates_payload() -> dict[str, Any]:
    return {
        "version": 3,
        "templates": copy.deepcopy(TEMPLATES),
        "defaultNegative": DEFAULT_NEGATIVE,
    }


def get_template(template_id: str | None) -> dict[str, Any]:
    return TEMPLATE_BY_ID.get(str(template_id or ""), TEMPLATES[0])


def template_from_option(value: str | None, *, allow_source: bool = False) -> dict[str, Any] | None:
    text = str(value or "").strip()
    if allow_source and text.startswith("source |"):
        return None
    template_id = text.split("|", 1)[0].strip()
    return TEMPLATE_BY_ID.get(template_id, TEMPLATES[0])


def one_click_state(
    template: dict[str, Any],
    title: str,
    character_prompt: str,
    style: str,
    show_labels: bool,
) -> dict[str, Any]:
    defaults = template.get("defaults", {})
    is_scene = str(template.get("kind") or "") == "scene"
    subject_prompt = character_prompt
    subject_style = style
    if is_scene and (not str(subject_prompt).strip() or str(subject_prompt).startswith("Оригинальный персонаж")):
        subject_prompt = "Цельная сцена, ясная пространственная структура, чёткие связи рельефа, архитектуры, дорог, растительности или ключевых объектов, реалистичные материалы и единое освещение."
    if is_scene and str(subject_style).startswith("Кинематографичный дизайн персонажа"):
        subject_style = defaults.get("style", "реалистичный концепт сцены, единая пространственная структура, материалы, перспектива и освещение")
    subject_title = "Безымянная сцена" if is_scene and str(title or "") in {"", "Безымянный персонаж"} else title
    return {
        "templateId": template["id"],
        "title": _safe_text(subject_title, defaults.get("title", "Безымянная сцена" if is_scene else "Безымянный персонаж"), 120),
        "subtitle": defaults.get("subtitle", template.get("name", "карта сеттинга")),
        "identity": _safe_text(subject_prompt, "", 3000),
        "appearance": _safe_text(subject_prompt, "", 3000),
        "outfit": "",
        "palette": "",
        "style": _safe_text(subject_style, defaults.get("style", ""), 1200),
        "negativePrompt": DEFAULT_NEGATIVE,
        "background": defaults.get("background", "#ffffff"),
        "accent": defaults.get("accent", "#d86b73"),
        "showLabels": bool(show_labels),
        "width": template.get("width", 2048),
        "height": template.get("height", 1152),
        "slots": [],
        "library": [],
    }


def parse_state(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return copy.deepcopy(raw)
    if not raw:
        return {}
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {}
        except (TypeError, ValueError):
            return {}
    return {}


def _clamp_int(value: Any, low: int, high: int, default: int) -> int:
    try:
        number = int(float(value))
    except (TypeError, ValueError):
        number = default
    number = max(low, min(high, number))
    return int(round(number / 16.0) * 16)


def _safe_text(value: Any, default: str = "", limit: int = 4000) -> str:
    text = str(value if value is not None else default)
    text = text.replace("\x00", "").strip()
    return text[:limit]


def _safe_float(value: Any, default: float, low: float, high: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    return max(low, min(high, number))


def _safe_image_name(value: Any) -> str:
    text = str(value or "").replace("\\", "/").strip()
    text = re.sub(r"[\r\n\t]", "", text)
    return text[:512]


def _matching_slot(previous_slots: list[Any], cell: dict[str, Any], index: int) -> dict[str, Any]:
    """Match by stable cell id first, with a legacy index fallback for old cards."""
    for item in previous_slots:
        if isinstance(item, dict) and str(item.get("cellId") or "") == str(cell.get("id") or ""):
            return item
    if index < len(previous_slots) and isinstance(previous_slots[index], dict):
        candidate = previous_slots[index]
        if not candidate.get("cellId"):
            return candidate
    return {}


def normalise_state(raw_state: Any, width: int, height: int) -> tuple[dict[str, Any], dict[str, Any]]:
    raw = parse_state(raw_state)
    template = get_template(raw.get("templateId") or raw.get("template_id"))
    defaults = template.get("defaults", {})
    cells = template.get("cells", [])
    previous_slots = raw.get("slots") if isinstance(raw.get("slots"), list) else []

    state: dict[str, Any] = {
        "version": 2,
        "templateId": template["id"],
        "title": _safe_text(raw.get("title"), defaults.get("title", "Безымянный персонаж"), 120),
        "subtitle": _safe_text(raw.get("subtitle"), defaults.get("subtitle", "карта персонажа"), 160),
        "identity": _safe_text(raw.get("identity"), "", 3000),
        "appearance": _safe_text(raw.get("appearance"), "", 3000),
        "outfit": _safe_text(raw.get("outfit"), "", 3000),
        "palette": _safe_text(raw.get("palette"), "", 500),
        "style": _safe_text(raw.get("style"), defaults.get("style", ""), 1200),
        "negativePrompt": _safe_text(raw.get("negativePrompt"), DEFAULT_NEGATIVE, 2400),
        "background": _safe_text(raw.get("background"), defaults.get("background", "#ffffff"), 32),
        "accent": _safe_text(raw.get("accent"), defaults.get("accent", "#d86b73"), 32),
        "showLabels": bool(raw.get("showLabels", False)),
        "width": _clamp_int(raw.get("width") or width, 512, 4096, int(template.get("width", 2048))),
        "height": _clamp_int(raw.get("height") or height, 512, 4096, int(template.get("height", 1152))),
        "slots": [],
        "library": [],
    }

    for index, cell in enumerate(cells):
        source = _matching_slot(previous_slots, cell, index)
        default_fit = "contain" if cell.get("role") in {"turnaround", "hero", "detail", "scene_anchor"} else "cover"
        state["slots"].append(
            {
                "id": _safe_text(source.get("id"), f"slot_{index + 1}", 80),
                "cellId": cell["id"],
                "label": cell.get("label", f"ячейка {index + 1}"),
                "role": cell.get("role", "custom"),
                "prompt": cell.get("prompt", ""),
                "image": _safe_image_name(source.get("image")),
                "subfolder": _safe_image_name(source.get("subfolder")),
                "fit": str(source.get("fit") or default_fit) if str(source.get("fit") or default_fit) in {"contain", "cover"} else default_fit,
                "zoom": round(_safe_float(source.get("zoom"), 1.0, 0.5, 3.0), 3),
                "offsetX": round(_safe_float(source.get("offsetX"), 0.0, -1.0, 1.0), 3),
                "offsetY": round(_safe_float(source.get("offsetY"), 0.0, -1.0, 1.0), 3),
                "lockIdentity": bool(source.get("lockIdentity", True)),
                "enabled": bool(source.get("enabled", True)),
            }
        )

    library = raw.get("library") if isinstance(raw.get("library"), list) else []
    seen: set[tuple[str, str]] = set()
    for item in library:
        if not isinstance(item, dict):
            continue
        image = _safe_image_name(item.get("image") or item.get("name"))
        subfolder = _safe_image_name(item.get("subfolder"))
        if not image:
            continue
        key = (subfolder, image)
        if key in seen:
            continue
        seen.add(key)
        state["library"].append(
            {
                "image": image,
                "subfolder": subfolder,
                "name": _safe_text(item.get("name") or image.rsplit("/", 1)[-1], image, 240),
                "useForIdentity": bool(item.get("useForIdentity", True)),
            }
        )

    for slot in state["slots"]:
        image = slot.get("image")
        if not image:
            continue
        key = (slot.get("subfolder", ""), image)
        if key in seen:
            continue
        seen.add(key)
        state["library"].append(
            {
                "image": image,
                "subfolder": slot.get("subfolder", ""),
                "name": image.rsplit("/", 1)[-1],
                "useForIdentity": True,
            }
        )

    return state, template


def _clean_sentence(text: str) -> str:
    value = _safe_text(text, "", 2400)
    value = re.sub(r"\s+", " ", value)
    return value.rstrip("。；;., ")


def _cell_box(cell: dict[str, Any], width: int, height: int) -> tuple[int, int, int, int]:
    x1 = max(0, min(width - 1, int(round(float(cell.get("x", 0.0)) * width))))
    y1 = max(0, min(height - 1, int(round(float(cell.get("y", 0.0)) * height))))
    x2 = max(x1 + 1, min(width, int(round((float(cell.get("x", 0.0)) + float(cell.get("w", 1.0))) * width))))
    y2 = max(y1 + 1, min(height, int(round((float(cell.get("y", 0.0)) + float(cell.get("h", 1.0))) * height))))
    return x1, y1, x2, y2


def active_slots(state: dict[str, Any]) -> list[dict[str, Any]]:
    slots = state.get("slots") if isinstance(state.get("slots"), list) else []
    return [slot for slot in slots if isinstance(slot, dict) and slot.get("enabled", True)]


def compile_prompt(state: dict[str, Any], template: dict[str, Any]) -> str:
    width = int(state.get("width") or template.get("width") or 2048)
    height = int(state.get("height") or template.get("height") or 1152)
    enabled_slots = active_slots(state)
    cell_by_id = {cell["id"]: cell for cell in template.get("cells", [])}
    cell_count = len(enabled_slots)
    is_scene = str(template.get("kind") or "") == "scene"
    card_kind = "карта сцены" if is_scene else "карта персонажа"
    subject_name = "сцена" if is_scene else "персонаж"

    lines = [
        f"Сгенерируй цельную {card_kind}. Входное изображение 1 — единственный и обязательный референс раскладки, который нужно копировать ячейка за ячейкой.",
        f"Выходной холст {width}×{height}: соотношение сторон, внешние поля и общее число ячеек должны полностью совпадать с референсом раскладки.",
        f"Строго сохрани {cell_count} прямоугольных ячеек из входного изображения 1: положение, пропорции сторон, ряды/столбцы и иерархия размеров должны совпадать.",
        "Запрещено добавлять ячейки, удалять ячейки, сливать ячейки, делить ячейки или дорисовывать новых субъектов в пустых местах.",
        f"Фиксированная раскладка: {_clean_sentence(template.get('layout_prompt') or template.get('description') or '')}.",
        "Пустые ячейки, силуэты содержимого, номера и вспомогательный текст на входном изображении задают только положение и тип содержимого ячеек; "
        "в финале их нужно заменить реальными кадрами, не оставляя плейсхолдеры, номера, направляющие или следы черновика раскладки.",
        "Между ячейками — чистые тонкие линии или узкие белые швы; вид должен быть профессиональным, единым и готовым для библиотеки ассетов.",
    ]

    if is_scene:
        lines.extend(
            [
                "Все ракурсы должны относиться к одной и той же сцене: рельеф, архитектура, дороги, растительность, ключевые объекты, "
                "материалы, цвета, направление главного света и масштаб пространства должны быть непрерывны и согласованы.",
                "Фронтальная референсная ячейка должна по возможности сохранять перспективу, композицию, положение ключевых объектов и свет загруженного оригинала; нельзя самовольно переделывать сцену.",
                "Дополни сцену по азимутам камеры 0°, 90°, 180°, 270°; каждый ракурс должен показывать пространство, невидимое с предыдущего, "
                "и четыре направления должны смыкаться по кругу.",
                "Длинная 360° панорама должна бесшовно развернуть 0°, 90°, 180°, 270° по порядку, без повторения четырёх одинаковых фото.",
                "Сцена главная: не добавлять людей или животных, не связанных с референсом; без текста, водяных знаков и декора, ломающего пространственную непрерывность.",
            ]
        )
    else:
        lines.extend(
            [
                "Все ячейки с персонажем — один и тот же человек: форма лица, черты, цвет глаз, причёска, цвет волос, тон кожи, пропорции тела, "
                "крой одежды, положение аксессуаров и общая палитра должны совпадать.",
                "Один и тот же персонаж может появляться многократно, но нельзя просто копировать одну и ту же композицию в несколько ячеек. "
                "Поза, ракурс, эмоция или кадрирование каждой ячейки должны меняться по списку.",
                "Все ячейки полного роста должны показывать персонажа от макушки до подошв целиком, с безопасными полями сверху и снизу; нельзя обрезать до полуфигуры.",
            ]
        )

    if state.get("identity"):
        label = "Тип сцены и атмосфера" if is_scene else "Личность и характер персонажа"
        lines.append(f"{label}: {_clean_sentence(state['identity'])}.")
    if state.get("appearance"):
        label = "Фиксация структуры пространства и ключевых объектов" if is_scene else "Фиксация внешности"
        lines.append(f"{label}: {_clean_sentence(state['appearance'])}.")
    if state.get("outfit"):
        label = "Фиксация материалов, окружения и освещения" if is_scene else "Фиксация одежды и аксессуаров"
        lines.append(f"{label}: {_clean_sentence(state['outfit'])}.")
    if state.get("palette"):
        lines.append(f"Фиксированная палитра: {_clean_sentence(state['palette'])}.")
    if state.get("style"):
        lines.append(f"Единый стиль: {_clean_sentence(state['style'])}.")

    lines.append("Поячейковый список ниже; строго выполняй по номерам, положению и содержанию:")
    for index, slot in enumerate(enabled_slots, start=1):
        cell = cell_by_id.get(str(slot.get("cellId") or ""), {})
        x1, y1, x2, y2 = _cell_box(cell, width, height)
        role = str(cell.get("role") or slot.get("role") or "custom")
        role_name = ROLE_NAMES.get(role, "одиночная ячейка субъекта")
        label = _clean_sentence(slot.get("label") or cell.get("label") or f"ячейка {index}")
        prompt = _clean_sentence(slot.get("prompt") or cell.get("prompt") or f"сохранять согласованность {subject_name}")
        lines.append(
            f"{index:02d}. Положение: слева {x1}px, сверху {y1}px, справа {x2}px, снизу {y2}px; "
            f"размер: {x2 - x1}×{y2 - y1}px; тип: {role_name}; "
            f"подпись: {label}; содержание: {prompt}."
        )

    if is_scene:
        lines.extend(
            [
                "Азимут камеры между ракурсами должен явно различаться; нельзя копировать, зеркалить или слегка обрезать одно и то же фото сцены.",
                "Ячейка детали окружения показывает только локальный материал или элемент, без новой целой сцены и без добавления людей или животных.",
            ]
        )
    else:
        lines.extend(
            [
                "Между ячейками эмоций должны быть узнаваемые различия: хотя бы одновременно меняются брови/глаза, форма рта или направление взгляда; нельзя менять только подпись.",
                "Ячейки деталей показывают только глаз, аксессуар, ткань или обувь локально; нельзя рисовать портрет или полный рост.",
                "Во всех ячейках субъект по центру, пропорции естественные, руки целые, лицо стабильное; в каждой ячейке только один субъект.",
            ]
        )

    if state.get("showLabels"):
        title = _clean_sentence(state.get("title") or ("Безымянная сцена" if is_scene else "Безымянный персонаж"))
        subtitle = _clean_sentence(state.get("subtitle") or template.get("name") or "карта сеттинга")
        labels = ", ".join(
            f"«{_clean_sentence(slot.get('label') or f'ячейка {index}')}»"
            for index, slot in enumerate(enabled_slots, start=1)
        )
        lines.append(f"Вверху холста покажи заголовок «{title}» и подзаголовок «{subtitle}»; текст должен быть чётким и не перекрывать ячейки.")
        lines.append(
            f"Под каждой ячейкой покажи соответствующие русские подписи; текст должен совпадать со следующим списком: {labels}. "
            "Не допускай опечаток, иероглифов, лишних латинских букв или водяных знаков."
        )
    else:
        lines.append("Внутри кадра не генерируй заголовки, пояснения, буквы, цифры, логотипы или водяные знаки — только чистые визуальные ассеты.")

    lines.append(f"Финальный результат — чистая, пространственно и по содержанию непрерывная, сразу готовая к использованию {card_kind}, а не коллаж-черновик.")
    return "\n".join(lines)

def card_schema_for_ui() -> dict[str, Any]:
    return {
        "version": 3,
        "fields": [
            "templateId",
            "title",
            "subtitle",
            "identity",
            "appearance",
            "outfit",
            "palette",
            "style",
            "negativePrompt",
            "background",
            "accent",
            "showLabels",
            "width",
            "height",
            "slots",
            "library",
        ],
    }
