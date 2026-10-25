# -*- coding: utf-8 -*-
"""Structural checks for all bundled character-card layouts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from templates import CHARACTER_TEMPLATE_OPTIONS, TEMPLATES, compile_prompt, normalise_state, one_click_state


def _overlap(left: dict, right: dict) -> float:
    x_overlap = max(0.0, min(left["x"] + left["w"], right["x"] + right["w"]) - max(left["x"], right["x"]))
    y_overlap = max(0.0, min(left["y"] + left["h"], right["y"] + right["h"]) - max(left["y"], right["y"]))
    return x_overlap * y_overlap


def main() -> None:
    assert len(TEMPLATES) == 9
    assert len({template["id"] for template in TEMPLATES}) == 9
    assert len(CHARACTER_TEMPLATE_OPTIONS) == 8

    for template in TEMPLATES:
        cells = template["cells"]
        assert cells, template["id"]
        assert len({cell["id"] for cell in cells}) == len(cells), template["id"]
        assert len({cell["label"] for cell in cells}) == len(cells), template["id"]
        assert all(cell["role"] in {"hero", "turnaround", "portrait", "expression", "detail", "scene_anchor", "scene_view", "scene_panorama", "scene_detail"} for cell in cells)
        assert all(0.0 <= cell["x"] <= 1.0 and 0.0 <= cell["y"] <= 1.0 for cell in cells)
        assert all(cell["x"] + cell["w"] <= 1.0001 and cell["y"] + cell["h"] <= 1.0001 for cell in cells)
        for index, cell in enumerate(cells):
            for other in cells[index + 1 :]:
                assert _overlap(cell, other) <= 0.000001, (template["id"], cell["id"], other["id"])

        state, resolved = normalise_state(
            {"templateId": template["id"], "title": "Тестовый персонаж"},
            int(template["width"]),
            int(template["height"]),
        )
        prompt = compile_prompt(state, resolved)
        assert prompt.count("Положение:") == len(cells), template["id"]
        assert "в правой половине только 3 ряда" not in prompt, template["id"]
        assert f"Строго сохрани {len(cells)} прямоугольных ячеек из входного изображения 1" in prompt
        assert "Вверху холста покажи заголовок" not in prompt

    scene = next(template for template in TEMPLATES if template.get("kind") == "scene")
    scene_state, scene_resolved = normalise_state(
        {"templateId": scene["id"], "title": "Тестовая сцена"},
        int(scene["width"]),
        int(scene["height"]),
    )
    scene_prompt = compile_prompt(scene_state, scene_resolved)
    assert scene_prompt.count("Положение:") == len(scene["cells"])
    assert "Все ракурсы должны относиться к одной и той же сцене" in scene_prompt
    assert "0°, 90°, 180°, 270°" in scene_prompt
    assert "360° панорама" in scene_prompt
    assert "не добавлять людей или животных, не связанных с референсом" in scene_prompt
    assert "Все ячейки с персонажем — один и тот же человек" not in scene_prompt
    assert "интерьер" not in scene_prompt
    scene_defaults = one_click_state(
        scene,
        "Безымянный персонаж",
        "Оригинальный персонаж, реалистичный кинематографичный",
        "Кинематографичный дизайн персонажа, чистый фон",
        False,
    )
    assert scene_defaults["title"] == "Безымянная сцена"
    assert scene_defaults["identity"].startswith("Цельная сцена")
    assert scene_defaults["style"].startswith("реалистичный концепт")

    template = TEMPLATES[0]
    state, resolved = normalise_state(
        {
            "templateId": template["id"],
            "slots": [
                {
                    "id": "kept",
                    "cellId": "body_front",
                    "enabled": False,
                    "image": "body.png",
                }
            ],
        },
        int(template["width"]),
        int(template["height"]),
    )
    body = next(slot for slot in state["slots"] if slot["cellId"] == "body_front")
    assert body["enabled"] is False
    assert body["image"] == "body.png"
    assert body["label"] == "Полный рост анфас"
    disabled_prompt = compile_prompt(state, resolved)
    assert disabled_prompt.count("Положение:") == len(template["cells"]) - 1

    print(json.dumps({"templates": len(TEMPLATES), "cells": [len(item["cells"]) for item in TEMPLATES]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
