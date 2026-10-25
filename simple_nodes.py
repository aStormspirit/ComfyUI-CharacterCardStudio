# -*- coding: utf-8 -*-
"""Simple linear Qwen Image 2.1 character-card pipeline."""

from __future__ import annotations

import json
from typing import Any

import folder_paths
import nodes as comfy_nodes
from comfy_extras.nodes_qwen import TextEncodeQwenImage21
from PIL import Image, ImageDraw, ImageColor, ImageOps

from .renderer import load_source_images, pil_to_tensor, pils_to_tensor, tensor_to_pil
from .splitter import _draw_label, report_json
from .templates import (
    DEFAULT_NEGATIVE,
    FIVE_TEMPLATE_OPTIONS,
    active_slots,
    get_template,
    normalise_state,
    one_click_state,
    template_from_option,
)


def _preferred(options: list[str], needle: str) -> str:
    return next((item for item in options if needle.lower() in item.lower()), options[0])


def _generation_size(cell: dict[str, Any], card_width: int, card_height: int) -> tuple[int, int]:
    """Return a 16-pixel-aligned generation size matching the target cell ratio."""
    target_w = max(1.0, float(cell.get("w", 1.0)) * card_width)
    target_h = max(1.0, float(cell.get("h", 1.0)) * card_height)
    ratio = target_w / target_h

    if ratio >= 1.0:
        width, height = 768.0 * ratio, 768.0
    else:
        width, height = 768.0, 768.0 / max(0.05, ratio)

    scale = min(1.0, 1536.0 / max(width, height))
    width = max(512.0, width * scale)
    height = max(512.0, height * scale)

    def aligned(value: float) -> int:
        return max(512, min(1536, int(round(value / 16.0) * 16)))

    return aligned(width), aligned(height)


def _cell_generation_prompt(cell: dict[str, Any], slot: dict[str, Any], common: str) -> str:
    role = str(cell.get("role") or slot.get("role") or "custom")
    label = str(slot.get("label") or cell.get("label") or "Ассет")
    detail = str(slot.get("prompt") or cell.get("prompt") or "Сохранять субъект неизменным")

    framing = {
        "hero": (
            "Один ассет персонажа: только один человек, полный рост анфас от макушки до подошв, "
            "субъект по центру с безопасными отступами. Без коллажа, без нескольких ракурсов, без рамки."
        ),
        "turnaround": (
            "Один ассет персонажа: только один человек, полный рост от макушки до подошв, "
            "субъект по центру с безопасными отступами. Без коллажа, без нескольких ракурсов, без рамки."
        ),
        "portrait": (
            "Один плечевой портрет: только один человек, голова и плечи целиком в кадре, "
            "лицо чётко по центру. Не полный рост, без коллажа, без рамки."
        ),
        "expression": (
            "Один плечевой кадр эмоции: только один человек, голова и плечи целиком в кадре, "
            "эмоция явная и отличается от нейтральной. Не полный рост, без коллажа, без рамки."
        ),
        "detail": (
            "Один локальный макрокадр: только указанная деталь одежды, глаз или аксессуара, "
            "без полной головы и полного роста, без коллажа, без рамки."
        ),
        "scene_anchor": (
            "Сгенерировать главный вид сцены анфас. Естественная перспектива, полностью показать "
            "основной рельеф, архитектуру, дороги, растительность или объекты; сцена в центре внимания, "
            "не добавлять людей или животных, без коллажа, без рамки."
        ),
        "scene_view": (
            "Сгенерировать один ракурс кругового обзора той же сцены. Реально повернуть камеру и "
            "показать пространство, которого нет в референсном направлении; сохранить структуру, "
            "ключевые объекты, материалы и освещение; сцена в центре внимания, не добавлять людей "
            "или животных, без коллажа, без рамки."
        ),
        "scene_panorama": (
            "Сгенерировать горизонтальную непрерывную панораму той же сцены 360° в порядке "
            "0°, 90°, 180°, 270°, возврат к 0° с естественными стыками; нельзя повторять одну "
            "композицию; сцена в центре внимания, не добавлять людей или животных, без коллажа, без рамки."
        ),
        "scene_detail": (
            "Сгенерировать один макрокадр материала окружения той же сцены: только материал, "
            "текстура, растительность, архитектурный элемент или декоративный фрагмент; "
            "не полная сцена, не добавлять людей или животных, без коллажа, без рамки."
        ),
    }.get(role, "Один ассет: только один субъект, без коллажа и нескольких ракурсов.")

    return (
        f"{common}"
        f"Название текущего ассета: {label}. {detail}."
        f"{framing}"
        "Не генерировать сетку карты персонажа, не генерировать текст, номера, подписи, рамки или водяные знаки."
    )

def _fit_asset(
    image: Image.Image,
    size: tuple[int, int],
    *,
    contain: bool,
    background: tuple[int, int, int] = (255, 255, 255),
) -> Image.Image:
    width, height = max(1, size[0]), max(1, size[1])
    source = image.convert("RGB")
    if contain:
        fitted = ImageOps.contain(source, (width, height), Image.Resampling.LANCZOS)
    else:
        fitted = ImageOps.fit(source, (width, height), Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    canvas = Image.new("RGB", (width, height), background)
    canvas.paste(fitted, ((width - fitted.width) // 2, (height - fitted.height) // 2))
    return canvas


def _compose_individual_assets(
    assets: list[Image.Image],
    template: dict[str, Any],
    state: dict[str, Any],
) -> tuple[Image.Image, list[Image.Image], dict[str, Any]]:
    defaults = template.get("defaults", {})
    width = int(state.get("width") or template.get("width") or 1920)
    height = int(state.get("height") or template.get("height") or 1080)
    background = str(state.get("background") or defaults.get("background") or "#ffffff")
    accent = str(state.get("accent") or defaults.get("accent") or "#d86b73")
    try:
        canvas_color = ImageColor.getrgb(background)
        accent_color = ImageColor.getrgb(accent)
    except (ValueError, TypeError):
        canvas_color = (255, 255, 255)
        accent_color = (216, 107, 115)

    canvas = Image.new("RGB", (width, height), canvas_color)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, width, max(3, int(height * 0.006))), fill=accent_color)

    slots = active_slots(state)
    fit_mode = str(state.get("fitMode") or "")
    fit_cover = "Заполн" in fit_mode or "填满" in fit_mode or "заполн" in fit_mode
    mapping: list[dict[str, Any]] = []
    asset_cursor = 0

    for slot_index, slot in enumerate(slots):
        cell = next(
            (item for item in template.get("cells", []) if item.get("id") == slot.get("cellId")),
            template.get("cells", [])[slot_index] if slot_index < len(template.get("cells", [])) else {},
        )
        if not cell or asset_cursor >= len(assets):
            continue
        role = str(cell.get("role") or "custom")
        x = int(round(float(cell.get("x", 0.0)) * width))
        y = int(round(float(cell.get("y", 0.0)) * height))
        w = max(1, int(round(float(cell.get("w", 1.0)) * width)))
        h = max(1, int(round(float(cell.get("h", 1.0)) * height)))
        rect = (x, y, min(width - 1, x + w), min(height - 1, y + h))
        box_w = max(1, rect[2] - rect[0])
        box_h = max(1, rect[3] - rect[1])
        fitted = _fit_asset(
            assets[asset_cursor],
            (box_w, box_h),
            contain=not fit_cover,
            background=canvas_color,
        )
        canvas.paste(fitted, (rect[0], rect[1]))
        draw.rectangle(rect, outline=(211, 214, 219), width=max(1, int(min(width, height) / 1400)))
        if state.get("showLabels"):
            _draw_label(draw, rect, str(slot.get("label") or cell.get("label") or f"Ячейка {slot_index + 1}"))
        mapping.append(
            {
                "target": slot_index + 1,
                "cell": cell.get("id"),
                "asset": asset_cursor + 1,
                "role": role,
                "label": str(slot.get("label") or cell.get("label") or ""),
            }
        )
        asset_cursor += 1

    normalized = [_fit_asset(asset, (768, 768), contain=True) for asset in assets]
    report = {
        "mode": "one-asset-per-cell",
        "template": template.get("id"),
        "canvas": [width, height],
        "cellCount": len(slots),
        "uniqueAssets": len(assets),
        "mapping": mapping,
    }
    return canvas, normalized, report


class CardSettingsFive:
    CATEGORY = "AICG3D/Карта персонажа"
    FUNCTION = "build"
    RETURN_TYPES = ("STRING", "IMAGE")
    RETURN_NAMES = ("Настройки карты", "Справочное изображение")
    DESCRIPTION = "Восемь макетов карты персонажа и один общий обзор сцены 360°; ID узлов сохранены для совместимости со старыми workflow."

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        return {
            "required": {
                "card_type": (FIVE_TEMPLATE_OPTIONS, {"default": FIVE_TEMPLATE_OPTIONS[3]}),
                "character_prompt": (
                    "STRING",
                    {
                        "default": "Оригинальный персонаж, кинематографичный полуреалистичный 3D-стиль, чёткие черты лица, продуманная одежда и аксессуары.",
                        "multiline": True,
                    },
                ),
                "title": ("STRING", {"default": "Безымянный персонаж"}),
                "style": ("STRING", {"default": "Кинематографичный дизайн персонажа, чистый фон, мягкий студийный свет, профессиональные ассеты"}),
                "show_labels": ("BOOLEAN", {"default": False}),
                "fit_mode": (["Полностью", "Заполнить с обрезкой"], {"default": "Полностью"}),
                "scene_prompt": (
                    "STRING",
                    {
                        "default": "Полная сцена с ясной пространственной структурой, поддерживает непрерывный обзор 0°, 90°, 180°, 270°; рельеф, архитектура, дороги, растительность или ключевые объекты связаны; реалистичные материалы и единое освещение.",
                        "multiline": True,
                    },
                ),
            },
            "optional": {"reference_image": ("IMAGE", {"forceInput": True})},
        }

    def build(
        self,
        card_type: str,
        character_prompt: str,
        title: str,
        style: str,
        show_labels: bool,
        fit_mode: str,
        scene_prompt: str,
        reference_image: Any = None,
    ):
        selected = template_from_option(card_type) or template_from_option(FIVE_TEMPLATE_OPTIONS[0])
        width = int(selected.get("width", 1920))
        height = int(selected.get("height", 1080))
        is_scene = str(selected.get("kind") or "") == "scene"
        subject_prompt = scene_prompt if is_scene else character_prompt
        subject_title = "Безымянная сцена" if is_scene and title in {"", "未命名角色", "Безымянный персонаж"} else title
        raw = one_click_state(selected, subject_title, subject_prompt, style, show_labels)
        state, _ = normalise_state(raw, width, height)
        state["fitMode"] = fit_mode
        return json.dumps(state, ensure_ascii=False, separators=(",", ":")), reference_image


class Qwen21ModelLoader:
    CATEGORY = "AICG3D/Карта персонажа"
    FUNCTION = "load"
    RETURN_TYPES = ("MODEL", "CLIP", "VAE", "STRING", "IMAGE")
    RETURN_NAMES = ("MODEL", "CLIP", "VAE", "Настройки карты", "Справочное изображение")
    DESCRIPTION = "Выбор модели Qwen Image 2.1, текстового энкодера и VAE в основной цепочке."

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        unets = folder_paths.get_filename_list("diffusion_models")
        clips = folder_paths.get_filename_list("text_encoders")
        vaes = folder_paths.get_filename_list("vae")
        return {
            "required": {
                "settings": ("STRING", {"forceInput": True}),
                "unet_name": (unets, {"default": _preferred(unets, "qwen_image_2.1")}),
                "clip_name": (clips, {"default": _preferred(clips, "qwen3vl_8b_int8")}),
                "vae_name": (vaes, {"default": _preferred(vaes, "qwen_image_2.1_vae")}),
                "weight_dtype": (["default", "fp8_e4m3fn", "fp8_e4m3fn_fast", "fp8_e5m2"], {"default": "default"}),
                "device": (["default", "cpu"], {"default": "default"}),
            },
            "optional": {"reference_image": ("IMAGE", {"forceInput": True})},
        }

    def load(
        self,
        settings: str,
        unet_name: str,
        clip_name: str,
        vae_name: str,
        weight_dtype: str,
        device: str,
        reference_image: Any = None,
    ):
        model = comfy_nodes.UNETLoader().load_unet(unet_name, weight_dtype)[0]
        clip = comfy_nodes.CLIPLoader().load_clip(clip_name, "qwen_image", device)[0]
        vae = comfy_nodes.VAELoader().load_vae(vae_name)[0]
        return model, clip, vae, settings, reference_image


class CharacterCardGeneratorSingle:
    CATEGORY = "AICG3D/Карта персонажа"
    FUNCTION = "generate"
    RETURN_TYPES = ("IMAGE", "IMAGE", "STRING")
    RETURN_NAMES = ("Карта персонажа", "Пакет ассетов", "Отчёт генерации")
    DESCRIPTION = "Каждая включённая ячейка генерируется отдельно, затем точно собирается обратно в карту по координатам того же шаблона."

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        return {
            "required": {
                "settings": ("STRING", {"forceInput": True}),
                "model": ("MODEL",),
                "clip": ("CLIP",),
                "vae": ("VAE",),
                "seed": ("INT", {"default": 42, "min": 0, "max": 0xffffffffffffffff}),
                "steps": ("INT", {"default": 8, "min": 1, "max": 100}),
                "cfg": ("FLOAT", {"default": 3.0, "min": 0.0, "max": 20.0, "step": 0.1}),
                "sampler_name": (["euler", "euler_ancestral", "dpmpp_2m", "sa_solver"], {"default": "euler"}),
                "scheduler": (["simple", "normal", "karras", "beta"], {"default": "simple"}),
            },
            "optional": {"reference_image": ("IMAGE", {"forceInput": True})},
        }

    def generate(
        self,
        settings: str,
        model: Any,
        clip: Any,
        vae: Any,
        seed: int,
        steps: int,
        cfg: float,
        sampler_name: str,
        scheduler: str,
        reference_image: Any = None,
    ):
        import torch
        import comfy.model_management

        config = json.loads(settings)
        template = get_template(config.get("templateId"))
        state, _ = normalise_state(config, int(template.get("width", 1920)), int(template.get("height", 1080)))
        state["fitMode"] = str(config.get("fitMode") or "Полностью")
        slots = active_slots(state)
        if not slots:
            raise ValueError("CharacterCardStudio: no enabled card cells")

        is_scene = str(template.get("kind") or "") == "scene"
        cell_by_id = {cell["id"]: cell for cell in template.get("cells", [])}
        anchor_slot = next(
            (slot for slot in slots if cell_by_id.get(str(slot.get("cellId") or ""), {}).get("role") == "scene_anchor"),
            None,
        )
        anchor_pil = None
        anchor_ref = None
        anchor_source = ""
        if is_scene and anchor_slot and anchor_slot.get("image"):
            loaded = load_source_images([anchor_slot])
            if loaded:
                anchor_pil = loaded[0]
                anchor_ref = pil_to_tensor(anchor_pil)
                anchor_source = "uploaded_cell"
        elif is_scene and reference_image is not None:
            anchor_pil = tensor_to_pil(reference_image)
            anchor_ref = reference_image
            anchor_source = "reference_input"

        scene_refs = [anchor_ref] if is_scene and anchor_ref is not None else []
        subject = state.get("identity") or state.get("appearance") or "Оригинальный субъект"
        style = state.get("style") or "Кинематографичный дизайн персонажа"
        negative = str(state.get("negativePrompt") or DEFAULT_NEGATIVE)
        if is_scene:
            negative += ", добавленные люди, добавленные животные, дрейф структуры сцены, изменение рельефа, сдвиг зданий, деформация ключевых объектов, несогласованные материалы, тот же ракурс камеры, копирование исходника, зеркальная имитация поворота, повторяющиеся четыре ракурса"
            common = (
                f"Одна и та же сцена. Описание сцены: {subject}. Единый стиль: {style}."
                "Референс — единственный пространственный якорь: сохранять рельеф, архитектуру, дороги, растительность, ключевые объекты, материалы, цвета и направление главного света."
                "Непрерывно поворачивать камеру на 0°, 90°, 180°, 270°, в каждом направлении показывать разное пространство, "
                "затем сгенерировать непрерывную панораму 360°; сцена в центре внимания, не добавлять людей или животных, нельзя копировать или зеркалить исходник вместо поворота."
            )
        else:
            identity_lock = (
                "Референс — тот же человек: строго воспроизвести форму лица, черты, цвет глаз, причёску и цвет волос, цвет кожи, одежду и аксессуары."
                if reference_image is not None
                else ""
            )
            common = (
                f"Один и тот же персонаж. Описание персонажа: {subject}. Единый стиль: {style}. {identity_lock}"
                "Сохранять форму лица, черты, цвет глаз, причёску, цвет волос, цвет кожи, пропорции тела, крой одежды и аксессуары полностью идентичными."
            )
        images = []

        for index, slot in enumerate(slots):
            cell = cell_by_id.get(str(slot.get("cellId") or ""))
            if not cell:
                continue
            role = str(cell.get("role") or "")
            if is_scene and role == "scene_anchor" and anchor_pil is not None:
                images.append(anchor_pil)
                continue
            width, height = _generation_size(cell, int(state["width"]), int(state["height"]))
            prompt = _cell_generation_prompt(cell, slot, common)
            refs = {}
            if is_scene and anchor_ref is not None:
                if role == "scene_detail":
                    scene_inputs = scene_refs[:1]
                elif role == "scene_panorama":
                    scene_inputs = scene_refs[:4]
                else:
                    scene_inputs = scene_refs[:3]
                for ref_index, scene_input in enumerate(scene_inputs, start=1):
                    refs[f"image_{ref_index}"] = scene_input
            elif reference_image is not None:
                refs["image_1"] = reference_image
            encoded = TextEncodeQwenImage21.execute(clip, prompt, negative, vae, 1024, refs).result
            positive, neg, _ = encoded
            cell_seed = (int(seed) + index * 0x9E3779B1) & 0xFFFFFFFFFFFFFFFF
            latent = {
                "samples": torch.zeros(
                    (1, 64, height // 16, width // 16),
                    device=comfy.model_management.intermediate_device(),
                )
            }
            sampled = comfy_nodes.common_ksampler(
                model,
                cell_seed,
                int(steps),
                float(cfg),
                sampler_name,
                scheduler,
                positive,
                neg,
                latent,
                denoise=1.0,
            )[0]
            image = vae.decode(sampled["samples"])
            images.append(image)
            if is_scene and role == "scene_anchor" and anchor_ref is None:
                anchor_ref = image
                anchor_pil = tensor_to_pil(image)
                scene_refs = [image]
                anchor_source = "generated_anchor"
            elif is_scene and role in {"scene_view", "scene_panorama"}:
                scene_refs.append(image)
                scene_refs = scene_refs[:4]

        assets = [tensor_to_pil(image) for image in images]
        card, normalized, report = _compose_individual_assets(assets, template, state)
        report["sceneMode"] = is_scene
        report["anchorSource"] = anchor_source if is_scene else ""
        report["orbitReferenceCount"] = len(scene_refs) if is_scene else 0
        return pil_to_tensor(card), pils_to_tensor(normalized), report_json(report)


NODE_CLASS_MAPPINGS = {
    "AICG3D_CardSettingsFive": CardSettingsFive,
    "AICG3D_Qwen21ModelLoader": Qwen21ModelLoader,
    "AICG3D_CharacterCardGeneratorSingle": CharacterCardGeneratorSingle,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AICG3D_CardSettingsFive": "1 Настройка типа карты персонажа/сцены · 9 макетов",
    "AICG3D_Qwen21ModelLoader": "2 Выбор модели Qwen Image 2.1",
    "AICG3D_CharacterCardGeneratorSingle": "3 Поячеечная генерация и вёрстка · готово",
}
