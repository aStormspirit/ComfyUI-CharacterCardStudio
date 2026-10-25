# -*- coding: utf-8 -*-
"""Build the simple linear five-template character card workflow."""

from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "workflows" / "карта_ассеты_QwenImage21.json"
TARGET = ROOT / "workflows" / "карта_персонажа_9_макетов_линейный.json"
PROMPT_TARGET = ROOT / "workflows" / "карта_персонажа_9_макетов_текст_линейный.json"


def templates() -> dict[int, dict]:
    data = json.loads(BASE.read_text(encoding="utf-8"))
    return {node["id"]: copy.deepcopy(node) for node in data["nodes"]}


def reset(node: dict, node_id: int, pos: list[int], order: int) -> None:
    node["id"] = node_id
    node["pos"] = pos
    node["order"] = order
    node["flags"] = {}
    node["mode"] = 0
    for item in node.get("inputs", []):
        item["link"] = None
    for item in node.get("outputs", []):
        item["links"] = None


def main() -> None:
    base = templates()
    nodes: list[dict] = []
    links: list[list] = []
    by_id: dict[int, dict] = {}

    def add(node: dict) -> None:
        nodes.append(node)
        by_id[node["id"]] = node

    def connect(origin: int, origin_slot: int, target: int, target_slot: int, kind: str) -> None:
        link_id = len(links) + 1
        links.append([link_id, origin, origin_slot, target, target_slot, kind])
        output = by_id[origin]["outputs"][origin_slot]
        output["links"] = (output.get("links") or []) + [link_id]
        by_id[target]["inputs"][target_slot]["link"] = link_id

    load_image = copy.deepcopy(base[100])
    reset(load_image, 100, [-1720, 120], 0)
    load_image["widgets_values"] = ["", "image"]
    add(load_image)

    settings = {
        "id": 1,
        "type": "AICG3D_CardSettingsFive",
        "pos": [-1320, 120],
        "size": [480, 430],
        "flags": {},
        "order": 1,
        "mode": 0,
        "inputs": [
            {"label": "Справочное изображение", "name": "reference_image", "type": "IMAGE", "link": None},
        ],
        "outputs": [
            {"label": "Настройки карты", "name": "Настройки карты", "type": "STRING", "slot_index": 0, "links": None},
            {"label": "Справочное изображение", "name": "Справочное изображение", "type": "IMAGE", "slot_index": 1, "links": None},
        ],
        "properties": {"Node name for S&R": "AICG3D_CardSettingsFive"},
        "widgets_values": [
            "head_body_6 | 6 ячеек · Три вида",
            "Оригинальный мужской персонаж, 20 лет, чёрные короткие волосы, серо-голубые глаза, худощавое лицо, тёмно-серая футболка, чёрные брюки и белые кроссовки.",
            "Безымянный персонаж",
            "Кинематографичный дизайн персонажа, чистый фон, мягкий студийный свет, профессиональные ассеты",
            False,
            "Полностью",
        ],
    }
    add(settings)

    model_loader = {
        "id": 2,
        "type": "AICG3D_Qwen21ModelLoader",
        "pos": [-780, 120],
        "size": [500, 420],
        "flags": {},
        "order": 2,
        "mode": 0,
        "inputs": [
            {"label": "Настройки карты", "name": "settings", "type": "STRING", "link": None},
            {"label": "Имя UNET", "name": "unet_name", "type": "COMBO", "widget": {"name": "unet_name"}, "link": None},
            {"label": "Имя CLIP", "name": "clip_name", "type": "COMBO", "widget": {"name": "clip_name"}, "link": None},
            {"label": "Имя VAE", "name": "vae_name", "type": "COMBO", "widget": {"name": "vae_name"}, "link": None},
            {"label": "Тип весов", "name": "weight_dtype", "type": "COMBO", "widget": {"name": "weight_dtype"}, "link": None},
            {"label": "Устройство", "name": "device", "type": "COMBO", "widget": {"name": "device"}, "link": None},
            {"label": "Справочное изображение", "name": "reference_image", "type": "IMAGE", "link": None},
        ],
        "outputs": [
            {"label": "MODEL", "name": "MODEL", "type": "MODEL", "slot_index": 0, "links": None},
            {"label": "CLIP", "name": "CLIP", "type": "CLIP", "slot_index": 1, "links": None},
            {"label": "VAE", "name": "VAE", "type": "VAE", "slot_index": 2, "links": None},
            {"label": "Настройки карты", "name": "Настройки карты", "type": "STRING", "slot_index": 3, "links": None},
            {"label": "Справочное изображение", "name": "Справочное изображение", "type": "IMAGE", "slot_index": 4, "links": None},
        ],
        "properties": {"Node name for S&R": "AICG3D_Qwen21ModelLoader"},
        "widgets_values": [
            "qwen\\qwen_image_2.1_bf16.safetensors",
            "qwen3vl_8b_int8_convrot.safetensors",
            "qwen_image_2.1_vae_bf16.safetensors",
            "default",
            "default",
        ],
    }
    add(model_loader)

    generator = {
        "id": 3,
        "type": "AICG3D_CharacterCardGeneratorSingle",
        "pos": [-180, 120],
        "size": [460, 430],
        "flags": {},
        "order": 3,
        "mode": 0,
        "inputs": [
            {"label": "Настройки карты", "name": "settings", "type": "STRING", "link": None},
            {"label": "MODEL", "name": "model", "type": "MODEL", "link": None},
            {"label": "CLIP", "name": "clip", "type": "CLIP", "link": None},
            {"label": "VAE", "name": "vae", "type": "VAE", "link": None},
            {"label": "Сид", "name": "seed", "type": "INT", "widget": {"name": "seed"}, "link": None},
            {"label": "Шаги", "name": "steps", "type": "INT", "widget": {"name": "steps"}, "link": None},
            {"label": "CFG", "name": "cfg", "type": "FLOAT", "widget": {"name": "cfg"}, "link": None},
            {"label": "Семплер", "name": "sampler_name", "type": "COMBO", "widget": {"name": "sampler_name"}, "link": None},
            {"label": "Планировщик", "name": "scheduler", "type": "COMBO", "widget": {"name": "scheduler"}, "link": None},
            {"label": "Справочное изображение", "name": "reference_image", "type": "IMAGE", "link": None},
        ],
        "outputs": [
            {"label": "Карта персонажа", "name": "Карта персонажа", "type": "IMAGE", "slot_index": 0, "links": None},
            {"label": "Пакет ассетов", "name": "Пакет ассетов", "type": "IMAGE", "slot_index": 1, "links": None},
            {"label": "Отчёт генерации", "name": "Отчёт генерации", "type": "STRING", "slot_index": 2, "links": None},
        ],
        "properties": {"Node name for S&R": "AICG3D_CharacterCardGeneratorSingle"},
        "widgets_values": [42, 8, 3.0, "euler", "simple"],
    }
    add(generator)

    preview = copy.deepcopy(base[501])
    reset(preview, 4, [380, 120], 4)
    preview["size"] = [760, 760]
    add(preview)

    save = copy.deepcopy(base[502])
    reset(save, 5, [380, 930], 5)
    save["size"] = [620, 760]
    save["widgets_values"] = ["карта_9_макетов"]
    add(save)

    assets_preview = copy.deepcopy(base[503])
    reset(assets_preview, 6, [-180, 600], 6)
    assets_preview["size"] = [460, 520]
    add(assets_preview)

    connect(100, 0, 1, 0, "IMAGE")
    connect(1, 0, 2, 0, "STRING")
    connect(1, 1, 2, 6, "IMAGE")
    connect(2, 3, 3, 0, "STRING")
    connect(2, 0, 3, 1, "MODEL")
    connect(2, 1, 3, 2, "CLIP")
    connect(2, 2, 3, 3, "VAE")
    connect(2, 4, 3, 9, "IMAGE")
    connect(3, 0, 4, 0, "IMAGE")
    connect(3, 0, 5, 0, "IMAGE")
    connect(3, 1, 6, 0, "IMAGE")

    workflow = {
        "id": "f6d7c551-5fe8-4d5a-9b20-fivecardlinear",
        "revision": 0,
        "last_node_id": 6,
        "last_link_id": len(links),
        "nodes": nodes,
        "links": links,
        "groups": [
            {"id": 1, "title": "Одна линия: настройки → модель → генерация → результат", "bounding": [-1740, 20, 2920, 1740], "color": "#3f789e", "flags": {}},
        ],
        "config": {},
        "extra": {"frontendVersion": "1.53.6"},
        "version": 0.4,
    }
    TARGET.write_text(json.dumps(workflow, ensure_ascii=False, indent=2), encoding="utf-8")
    print(TARGET)

    prompt_only = copy.deepcopy(workflow)
    prompt_only["id"] = "f6d7c551-5fe8-4d5a-9b20-fivecardprompt"
    prompt_only["nodes"] = [node for node in prompt_only["nodes"] if node["type"] != "LoadImage"]
    prompt_only["links"] = [
        [new_id, *link[1:]]
        for new_id, link in enumerate(
            [link for link in prompt_only["links"] if link[1] != 100],
            start=1,
        )
    ]
    for node in prompt_only["nodes"]:
        if node["type"] == "AICG3D_CardSettingsFive":
            node["inputs"][0]["link"] = None
    # Re-number all reference ids after removing the input image link.
    remap = {old: new for new, old in enumerate(
        [link[0] for link in workflow["links"] if link[1] != 100],
        start=1,
    )}
    prompt_only["links"] = [[new_id, *link[1:]] for new_id, link in enumerate(
        [link for link in workflow["links"] if link[1] != 100], start=1
    )]
    prompt_only["last_link_id"] = len(prompt_only["links"])
    for node in prompt_only["nodes"]:
        for item in node.get("inputs", []):
            if item.get("link") in remap:
                item["link"] = remap[item["link"]]
            elif item.get("link") == 1 and node["type"] == "AICG3D_CardSettingsFive":
                item["link"] = None
        for item in node.get("outputs", []):
            if item.get("links"):
                item["links"] = [remap[value] for value in item["links"] if value in remap]
    PROMPT_TARGET.write_text(json.dumps(prompt_only, ensure_ascii=False, indent=2), encoding="utf-8")
    print(PROMPT_TARGET)


if __name__ == "__main__":
    main()
