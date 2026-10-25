# -*- coding: utf-8 -*-
"""Build the role-aware multi-branch character card workflow."""

from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_WORKFLOW = ROOT / "workflows" / "карта_в_один_клик_QwenImage21.json"
TARGET = ROOT / "workflows" / "карта_ассеты_QwenImage21.json"
PROMPT_TARGET = ROOT / "workflows" / "карта_ассеты_промпт_QwenImage21.json"


def load_templates() -> dict[int, dict]:
    workflow = json.loads(BASE_WORKFLOW.read_text(encoding="utf-8"))
    return {node["id"]: copy.deepcopy(node) for node in workflow["nodes"]}


def reset_node(node: dict, node_id: int, pos: list[int], order: int) -> None:
    node["id"] = node_id
    node["pos"] = pos
    node["order"] = order
    node["flags"] = {}
    node["mode"] = 0
    for item in node.get("inputs", []):
        item["link"] = None
    for item in node.get("outputs", []):
        item["links"] = None


def asset_prompt_node() -> dict:
    return {
        "id": 1,
        "type": "AICG3D_CharacterCardAssetPrompt",
        "pos": [-2420, 120],
        "size": [520, 420],
        "flags": {},
        "order": 0,
        "mode": 0,
        "inputs": [],
        "outputs": [
            {"label": "Анфас в полный рост", "name": "Анфас в полный рост", "type": "STRING", "slot_index": 0, "links": None},
            {"label": "Профиль в полный рост", "name": "Профиль в полный рост", "type": "STRING", "slot_index": 1, "links": None},
            {"label": "Спина в полный рост", "name": "Спина в полный рост", "type": "STRING", "slot_index": 2, "links": None},
            {"label": "Портрет", "name": "Портрет", "type": "STRING", "slot_index": 3, "links": None},
            {"label": "Действие A", "name": "Действие A", "type": "STRING", "slot_index": 4, "links": None},
            {"label": "Действие B", "name": "Действие B", "type": "STRING", "slot_index": 5, "links": None},
            {"label": "Группа эмоций", "name": "Группа эмоций", "type": "STRING", "slot_index": 6, "links": None},
            {"label": "Группа деталей", "name": "Группа деталей", "type": "STRING", "slot_index": 7, "links": None},
            {"label": "Негативный промпт", "name": "Негативный промпт", "type": "STRING", "slot_index": 8, "links": None},
            {"label": "Конфиг карты", "name": "Конфиг карты", "type": "STRING", "slot_index": 9, "links": None},
            {"label": "Направляющее изображение макета", "name": "Направляющее изображение макета", "type": "IMAGE", "slot_index": 10, "links": None},
            {"label": "Ширина", "name": "Ширина", "type": "INT", "slot_index": 11, "links": None},
            {"label": "Высота", "name": "Высота", "type": "INT", "slot_index": 12, "links": None},
        ],
        "properties": {"Node name for S&R": "AICG3D_CharacterCardAssetPrompt"},
        "widgets_values": [
            "head_body_6 | 6 ячеек · Три вида",
            "Оригинальный мужской персонаж, 20 лет, чёрные короткие волосы, серо-голубые глаза, худощавое лицо, тёмно-серая футболка, чёрные брюки и белые кроссовки.",
            "Безымянный персонаж",
            "Кинематографичный дизайн персонажа, чистый фон, мягкий студийный свет, профессиональные ассеты",
            False,
            "Полностью",
        ],
    }


def composer_node() -> dict:
    inputs = []
    for name, label in [
        ("full_front", "Анфас в полный рост"),
        ("full_profile", "Профиль в полный рост"),
        ("full_back", "Спина в полный рост"),
        ("action_a", "Действие A"),
        ("action_b", "Действие B"),
        ("headshot", "Портрет"),
        ("expression_sheet", "Группа эмоций"),
        ("detail_sheet", "Группа деталей"),
        ("card_config", "Конфиг карты"),
    ]:
        item = {"label": label, "name": name, "type": "IMAGE" if name != "card_config" else "STRING", "link": None}
        inputs.append(item)
    return {
        "id": 500,
        "type": "AICG3D_CharacterCardAssetComposer",
        "pos": [620, 640],
        "size": [460, 420],
        "flags": {},
        "order": 40,
        "mode": 0,
        "inputs": inputs,
        "outputs": [
            {"label": "Карта персонажа", "name": "Карта персонажа", "type": "IMAGE", "slot_index": 0, "links": None},
            {"label": "Пакет ассетов", "name": "Пакет ассетов", "type": "IMAGE", "slot_index": 1, "links": None},
            {"label": "Отчёт компоновки", "name": "Отчёт компоновки", "type": "STRING", "slot_index": 2, "links": None},
        ],
        "properties": {"Node name for S&R": "AICG3D_CharacterCardAssetComposer"},
        "widgets_values": [],
    }


def main() -> None:
    templates = load_templates()
    nodes: list[dict] = []
    links: list[list] = []
    by_id: dict[int, dict] = {}

    def add(node: dict) -> dict:
        nodes.append(node)
        by_id[node["id"]] = node
        return node

    def connect(origin_id: int, origin_slot: int, target_id: int, target_slot: int, kind: str) -> None:
        link_id = len(links) + 1
        links.append([link_id, origin_id, origin_slot, target_id, target_slot, kind])
        origin = by_id[origin_id]["outputs"][origin_slot]
        if origin.get("links") is None:
            origin["links"] = []
        origin["links"].append(link_id)
        by_id[target_id]["inputs"][target_slot]["link"] = link_id

    asset_prompt = add(asset_prompt_node())
    load_image = copy.deepcopy(templates[11])
    reset_node(load_image, 100, [-3060, 120], 1)
    load_image["widgets_values"] = ["", "image"]
    load_image["outputs"][0]["links"] = None
    add(load_image)

    unet = copy.deepcopy(templates[2])
    reset_node(unet, 2, [-1840, 100], 2)
    add(unet)
    clip = copy.deepcopy(templates[3])
    reset_node(clip, 3, [-1840, 260], 3)
    add(clip)
    vae = copy.deepcopy(templates[4])
    reset_node(vae, 4, [-1840, 450], 4)
    add(vae)

    branch_specs = [
        ("full_front", 101, 201, 301, 401, 0, 0, 768, 1152),
        ("full_profile", 102, 202, 302, 402, 1, 1, 768, 1152),
        ("full_back", 103, 203, 303, 403, 2, 2, 768, 1152),
        ("headshot", 104, 204, 304, 404, 3, 5, 1024, 1024),
        ("action_a", 105, 205, 305, 405, 4, 3, 768, 1152),
        ("action_b", 106, 206, 306, 406, 5, 4, 768, 1152),
        ("expression_sheet", 107, 207, 307, 407, 6, 6, 1536, 1024),
        ("detail_sheet", 108, 208, 308, 408, 7, 7, 1536, 1536),
    ]

    decoders: list[dict] = []
    for index, (_, text_id, latent_id, sampler_id, decode_id, _, _, width, height) in enumerate(branch_specs):
        col = index % 4
        row = index // 4
        base_x = -1300 + col * 560
        base_y = 40 + row * 980
        text = copy.deepcopy(templates[5])
        reset_node(text, text_id, [base_x, base_y], 10 + index * 4)
        text["size"] = [330, 300]
        text["widgets_values"] = ["", "", 1024]
        add(text)
        latent = copy.deepcopy(templates[6])
        reset_node(latent, latent_id, [base_x, base_y + 350], 11 + index * 4)
        latent["widgets_values"] = [width, height, 1]
        add(latent)
        sampler = copy.deepcopy(templates[7])
        reset_node(sampler, sampler_id, [base_x + 370, base_y], 12 + index * 4)
        sampler["widgets_values"] = [42 + index, "fixed", 20, 4, "euler", "simple", 1]
        add(sampler)
        decode = copy.deepcopy(templates[8])
        reset_node(decode, decode_id, [base_x + 370, base_y + 630], 13 + index * 4)
        add(decode)
        decoders.append(decode)

    composer = add(composer_node())
    preview = copy.deepcopy(templates[9])
    reset_node(preview, 501, [1120, 120], 50)
    preview["size"] = [760, 760]
    add(preview)
    save = copy.deepcopy(templates[10])
    reset_node(save, 502, [1120, 930], 51)
    save["size"] = [620, 760]
    save["widgets_values"] = ["карта_ассеты"]
    add(save)
    asset_preview = copy.deepcopy(templates[9])
    reset_node(asset_preview, 503, [620, 1100], 52)
    asset_preview["size"] = [460, 520]
    add(asset_preview)

    # Prompt, reference and model routing.
    for index, (_, text_id, latent_id, sampler_id, decode_id, prompt_slot, composer_slot, _, _) in enumerate(branch_specs):
        connect(1, prompt_slot, text_id, 3, "STRING")
        connect(1, 8, text_id, 4, "STRING")
        connect(100, 0, text_id, 1, "IMAGE")
        connect(3, 0, text_id, 0, "CLIP")
        connect(4, 0, text_id, 2, "VAE")
        connect(2, 0, sampler_id, 0, "MODEL")
        connect(text_id, 0, sampler_id, 1, "CONDITIONING")
        connect(text_id, 1, sampler_id, 2, "CONDITIONING")
        connect(latent_id, 0, sampler_id, 3, "LATENT")
        connect(sampler_id, 0, decode_id, 0, "LATENT")
        connect(4, 0, decode_id, 1, "VAE")
        connect(decode_id, 0, 500, composer_slot, "IMAGE")
    connect(1, 9, 500, 8, "STRING")
    connect(500, 0, 501, 0, "IMAGE")
    connect(500, 0, 502, 0, "IMAGE")
    connect(500, 1, 503, 0, "IMAGE")

    workflow = {
        "id": "e4b9c7d2-4c34-4a13-8a77-roleawarecardqwen21",
        "revision": 0,
        "last_node_id": 503,
        "last_link_id": len(links),
        "nodes": nodes,
        "links": links,
        "groups": [
            {"id": 1, "title": "Ввод персонажа и промпты ассетов", "bounding": [-3080, 20, 1120, 620], "color": "#3f789e", "flags": {}},
            {"id": 2, "title": "Qwen Image 2.1 · шесть независимых веток", "bounding": [-1880, 0, 2440, 1900], "color": "#8a6d3b", "flags": {}},
            {"id": 3, "title": "Профессиональная авторазметка карты", "bounding": [600, 600, 1300, 1100], "color": "#3f789e", "flags": {}},
        ],
        "config": {},
        "extra": {"frontendVersion": "1.53.6"},
        "version": 0.4,
    }
    TARGET.write_text(json.dumps(workflow, ensure_ascii=False, indent=2), encoding="utf-8")
    print(TARGET)

    prompt_only = copy.deepcopy(workflow)
    prompt_only["id"] = "e4b9c7d2-4c34-4a13-8a77-roleawarepromptqwen21"
    prompt_only["nodes"] = [node for node in prompt_only["nodes"] if node["type"] != "LoadImage"]
    for node in prompt_only["nodes"]:
        if node["type"] == "TextEncodeQwenImage21":
            node["inputs"][1]["link"] = None
    prompt_only["links"] = [link for link in prompt_only["links"] if not (link[1] == 100 and link[2] == 0)]
    # Re-number links while preserving endpoints.
    remap = {}
    new_links = []
    for new_id, link in enumerate(prompt_only["links"], start=1):
        remap[link[0]] = new_id
        new_links.append([new_id, *link[1:]])
    prompt_only["links"] = new_links
    prompt_only["last_link_id"] = len(new_links)
    for node in prompt_only["nodes"]:
        for item in node.get("inputs", []):
            if item.get("link") in remap:
                item["link"] = remap[item["link"]]
        for item in node.get("outputs", []):
            if item.get("links"):
                item["links"] = [remap.get(value, value) for value in item["links"]]
    PROMPT_TARGET.write_text(json.dumps(prompt_only, ensure_ascii=False, indent=2), encoding="utf-8")
    print(PROMPT_TARGET)


if __name__ == "__main__":
    main()
