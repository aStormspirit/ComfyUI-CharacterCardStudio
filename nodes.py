# -*- coding: utf-8 -*-
"""ComfyUI nodes for automatic character-card generation and slicing."""

from __future__ import annotations

import json
import folder_paths
import nodes as comfy_nodes
from typing import Any

from .renderer import (
    pil_to_tensor,
    pils_to_tensor,
    render_identity_sheet,
    render_layout,
    tensor_to_pil,
)
from .asset_composer import compose_role_card
from comfy_extras.nodes_qwen import TextEncodeQwenImage21
from .splitter import recompose_card, report_json
from .templates import (
    CHARACTER_TEMPLATE_OPTIONS,
    FIVE_TEMPLATE_OPTIONS,
    DEFAULT_TEMPLATE_OPTION,
    DEFAULT_NEGATIVE,
    TEMPLATE_OPTIONS,
    compile_prompt,
    get_template,
    normalise_state,
    one_click_state,
    template_from_option,
)


class CharacterCardStudio:
    CATEGORY = "AICG3D/Карта персонажа"
    FUNCTION = "build"
    RETURN_TYPES = ("STRING", "STRING", "IMAGE", "IMAGE", "STRING", "INT", "INT")
    RETURN_NAMES = ("Промпт", "Негативный промпт", "Справочное изображение вёрстки", "Справочное изображение идентичности", "JSON карты", "Ширина", "Высота")
    DESCRIPTION = "Визуальная вёрстка карты персонажа/сцены, повторное использование референсов, перестановка ячеек и компиляция промптов для Qwen Image 2.1."

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        return {
            "required": {
                "card_state": (
                    "STRING",
                    {"default": "{}", "multiline": False, "dynamicPrompts": False},
                ),
                "width": ("INT", {"default": 1920, "min": 512, "max": 4096, "step": 16}),
                "height": ("INT", {"default": 1080, "min": 512, "max": 4096, "step": 16}),
            }
        }

    @classmethod
    def IS_CHANGED(cls, card_state: str, width: int, height: int, **_: Any) -> str:
        return f"{width}x{height}:{card_state}"

    def build(
        self, card_state: str, width: int, height: int
    ) -> tuple[str, str, Any, Any, str, int, int]:
        state, template = normalise_state(card_state, width, height)
        prompt = compile_prompt(state, template)
        negative = str(state.get("negativePrompt") or DEFAULT_NEGATIVE)
        layout = render_layout(state, template)
        identity = render_identity_sheet(state, layout)
        card_json = json.dumps(state, ensure_ascii=False, separators=(",", ":"))
        return (
            prompt,
            negative,
            pil_to_tensor(layout),
            pil_to_tensor(identity),
            card_json,
            int(state["width"]),
            int(state["height"]),
        )


class CharacterCardOneClick:
    CATEGORY = "AICG3D/Карта персонажа"
    FUNCTION = "build"
    RETURN_TYPES = ("STRING", "STRING", "IMAGE", "STRING", "INT", "INT", "STRING")
    RETURN_NAMES = ("Промпт", "Негативный промпт", "Направляющее изображение макета", "JSON карты", "Ширина", "Высота", "Вариант карты")
    DESCRIPTION = "Одно референс-изображение или промпт персонажа: централизованное управление макетом, порядком, отображением в полный рост и размером вывода."

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        return {
            "required": {
                "template": (TEMPLATE_OPTIONS, {"default": DEFAULT_TEMPLATE_OPTION}),
                "character_prompt": (
                    "STRING",
                    {
                        "default": "Оригинальный персонаж, кинематографичный полуреалистичный 3D-стиль, чёткие черты лица, продуманная одежда и аксессуары.",
                        "multiline": True,
                    },
                ),
                "title": ("STRING", {"default": "Безымянный персонаж"}),
                "style": (
                    "STRING",
                    {"default": "Единая карта персонажа, кинематографичные ассеты, чистый фон, мягкий студийный свет, профессиональная вёрстка"},
                ),
                "show_labels": ("BOOLEAN", {"default": False}),
                "panel_order": ("STRING", {"default": "1-17"}),
                "fit_mode": (["Полностью", "Заполнить с обрезкой"], {"default": "Полностью"}),
                "inset": (
                    "FLOAT",
                    {"default": 0.008, "min": 0.0, "max": 0.12, "step": 0.002},
                ),
            }
        }

    def build(
        self,
        template: str,
        character_prompt: str,
        title: str,
        style: str,
        show_labels: bool,
        panel_order: str,
        fit_mode: str,
        inset: float,
    ) -> tuple[str, str, Any, str, int, int, str]:
        selected = template_from_option(template) or template_from_option(TEMPLATE_OPTIONS[0])
        width = int(selected.get("width", 2048))
        height = int(selected.get("height", 1152))
        raw_state = one_click_state(selected, title, character_prompt, style, show_labels)
        state, resolved = normalise_state(raw_state, width, height)
        state["identity"] = character_prompt
        state["appearance"] = character_prompt
        state["title"] = title or "Безымянный персонаж"
        state["showLabels"] = bool(show_labels)
        state["panelOrder"] = panel_order
        state["fitMode"] = fit_mode
        state["inset"] = float(inset)
        prompt = compile_prompt(state, resolved)
        negative = str(state.get("negativePrompt") or DEFAULT_NEGATIVE)
        guide = render_layout(state, resolved)
        card_json = json.dumps(state, ensure_ascii=False, separators=(",", ":"))
        template_option = f"{resolved['id']} | {resolved['name']}"
        return (
            prompt,
            negative,
            pil_to_tensor(guide),
            card_json,
            int(state["width"]),
            int(state["height"]),
            template_option,
        )


class CharacterSheetSplitter:
    CATEGORY = "AICG3D/Карта персонажа"
    FUNCTION = "split"
    RETURN_TYPES = ("IMAGE", "IMAGE", "STRING")
    RETURN_NAMES = ("Перекомпонованная карта", "Пакет нарезок", "Отчёт о нарезке")
    DESCRIPTION = "Автоматически читает конфигурацию карты из первого узла, выполняет нарезку, полное отображение в рост и перекомпоновку — без дополнительных параметров."

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        return {
            "required": {
                "images": ("IMAGE",),
                "card_config": (
                    "STRING",
                    {"default": "{}", "forceInput": True},
                ),
            }
        }

    def split(self, images: Any, card_config: str) -> tuple[Any, Any, str]:
        config: dict[str, Any] = {}
        try:
            parsed = json.loads(str(card_config or "{}"))
            if isinstance(parsed, dict):
                config = parsed
        except (TypeError, ValueError):
            config = {}
        template = get_template(config.get("templateId"))
        panel_order = str(config.get("panelOrder") or "1-99")
        fit_mode = str(config.get("fitMode") or "Полностью")
        inset = float(config.get("inset") or 0.008)
        show_labels = bool(config.get("showLabels", False))
        source_image = tensor_to_pil(images)
        card, panels, report = recompose_card(
            source_image,
            template,
            template,
            panel_order,
            inset,
            show_labels,
            fit_mode,
        )
        return pil_to_tensor(card), pils_to_tensor(panels), report_json(report)


NODE_CLASS_MAPPINGS = {
    "AICG3D_CharacterCardStudio": CharacterCardStudio,
    "AICG3D_CharacterCardOneClick": CharacterCardOneClick,
    "AICG3D_CharacterSheetSplitter": CharacterSheetSplitter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AICG3D_CharacterCardStudio": "Рабочий стол карты персонажа/сцены · Qwen Image 2.1",
    "AICG3D_CharacterCardOneClick": "Промпт карты персонажа/сцены в один клик · Qwen Image 2.1",
    "AICG3D_CharacterSheetSplitter": "Автонарезка карты персонажа/сцены · без настроек",
}


class CharacterCardAssetPrompt:
    CATEGORY = "AICG3D/Карта персонажа"
    FUNCTION = "build"
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "IMAGE", "INT", "INT")
    RETURN_NAMES = ("Анфас в полный рост", "Профиль в полный рост", "Спина в полный рост", "Портрет", "Действие A", "Действие B", "Группа эмоций", "Группа деталей", "Негативный промпт", "Конфиг карты", "Направляющее изображение макета", "Ширина", "Высота")
    DESCRIPTION = "Отдельно генерирует промпты ассетов для полного роста, портрета, эмоций и деталей, затем компонует по дизайн-макету карты."

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        return {
            "required": {
                "template": (CHARACTER_TEMPLATE_OPTIONS, {"default": DEFAULT_TEMPLATE_OPTION}),
                "character_prompt": ("STRING", {"default": "Оригинальный персонаж, кинематографичный полуреалистичный 3D-стиль, чёткие черты лица, продуманная одежда и аксессуары.", "multiline": True}),
                "title": ("STRING", {"default": "Безымянный персонаж"}),
                "style": ("STRING", {"default": "Кинематографичный дизайн персонажа, чистый фон, мягкий студийный свет, профессиональные ассеты"}),
                "show_labels": ("BOOLEAN", {"default": False}),
                "fit_mode": (["Полностью", "Заполнить с обрезкой"], {"default": "Полностью"}),
            }
        }

    def build(self, template: str, character_prompt: str, title: str, style: str, show_labels: bool, fit_mode: str):
        selected = template_from_option(template) or template_from_option(TEMPLATE_OPTIONS[0])
        width = int(selected.get("width", 2048))
        height = int(selected.get("height", 1152))
        raw_state = one_click_state(selected, title, character_prompt, style, show_labels)
        state, resolved = normalise_state(raw_state, width, height)
        state["fitMode"] = fit_mode
        state["panelOrder"] = "role-aware"
        state["inset"] = 0.008
        common = (
            f"Один и тот же оригинальный персонаж, имя: {title}. Описание персонажа: {character_prompt}."
            f"Единый стиль: {style}. Сохранять форму лица, черты, цвет глаз, причёску, цвет волос, цвет кожи, пропорции тела, крой одежды и аксессуары полностью идентичными."
        )
        full_front = common + "Ассет персонажа в полный рост анфас. Фигура целиком от макушки до подошв в кадре, с безопасными отступами сверху и снизу; нельзя обрезать голову, обувь или стопы; чистый светло-серо-белый студийный фон; взгляд на уровне глаз; руки свободно опущены."
        full_profile = common + "Ассет персонажа в полный рост строго в профиль 90°. Фигура целиком от макушки до подошв в кадре; нельзя обрезать голову, обувь или стопы; чистый светло-серо-белый студийный фон; пропорции тела совпадают с анфасом."
        full_back = common + "Ассет персонажа в полный рост строго со спины 180°. Фигура целиком от макушки до подошв в кадре; нельзя обрезать голову, обувь или стопы; полностью показать конструкцию одежды со спины; чистый светло-серо-белый студийный фон."
        headshot = common + "Крупный портрет анфас. Только голова и плечи, лицо по центру, взгляд в камеру; чёткие черты, макияж, причёска и серьги; светло-серо-белый студийный фон; не полный рост; не обрезать макушку."
        action_a = common + "Динамичная поза персонажа A. Полный рост целиком от макушки до подошв; естественное выразительное движение; чёткая конструкция одежды; чистый светло-серо-белый студийный фон."
        action_b = common + "Динамичная поза персонажа B. Полный рост целиком от макушки до подошв; поза явно отличается от позы A; одежда и аксессуары те же; чистый светло-серо-белый студийный фон."
        expression = common + "Сетка эмоций 2×3. Все шесть ячеек — плечевой портрет одного персонажа: спокойный, счастливый, злой, грустный, удивление, застенчивый. Единая композиция в каждой ячейке, чёткое лицо, явные различия эмоций, тонкие белые разделители, без текста и водяных знаков."
        detail = common + "Сетка деталей персонажа 3×3. Девять ячеек: крупный план глаз, рот или макияж, кисть руки, текстура ткани A, текстура ткани B, пуговица или шов, узор одежды, обувь, характерный аксессуар. В каждой ячейке разный цельный кадр, тонкие белые разделители, без текста и водяных знаков."
        negative = str(state.get("negativePrompt") or DEFAULT_NEGATIVE) + ", обрезанная голова, обрезанные ноги, полуфигура вместо полного роста, неверное содержимое ячейки, полный рост в ячейке эмоций, портрет в ячейке полного роста"
        guide = render_layout(state, resolved)
        card_config = json.dumps(state, ensure_ascii=False, separators=(",", ":"))
        return full_front, full_profile, full_back, headshot, action_a, action_b, expression, detail, negative, card_config, pil_to_tensor(guide), int(state["width"]), int(state["height"])


class CharacterCardAssetComposer:
    CATEGORY = "AICG3D/Карта персонажа"
    FUNCTION = "compose"
    RETURN_TYPES = ("IMAGE", "IMAGE", "STRING")
    RETURN_NAMES = ("Карта персонажа", "Пакет ассетов", "Отчёт компоновки")
    DESCRIPTION = "Компонует отдельно сгенерированные анфас/профиль/спина в полный рост, портрет, группы эмоций и деталей по макету карты персонажа."

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        return {
            "required": {
                "full_front": ("IMAGE",),
                "full_profile": ("IMAGE",),
                "full_back": ("IMAGE",),
                "action_a": ("IMAGE",),
                "action_b": ("IMAGE",),
                "headshot": ("IMAGE",),
                "expression_sheet": ("IMAGE",),
                "detail_sheet": ("IMAGE",),
                "card_config": ("STRING", {"default": "{}", "forceInput": True}),
            }
        }

    def compose(self, full_front: Any, full_profile: Any, full_back: Any, action_a: Any, action_b: Any, headshot: Any, expression_sheet: Any, detail_sheet: Any, card_config: str):
        config: dict[str, Any] = {}
        try:
            parsed = json.loads(str(card_config or "{}"))
            if isinstance(parsed, dict):
                config = parsed
        except (TypeError, ValueError):
            config = {}
        template = get_template(config.get("templateId"))
        card, assets, report = compose_role_card(
            full_front=tensor_to_pil(full_front),
            full_profile=tensor_to_pil(full_profile),
            full_back=tensor_to_pil(full_back),
            action_a=tensor_to_pil(action_a),
            action_b=tensor_to_pil(action_b),
            headshot=tensor_to_pil(headshot),
            expression_sheet=tensor_to_pil(expression_sheet),
            detail_sheet=tensor_to_pil(detail_sheet),
            template=template,
            fit_mode=str(config.get("fitMode") or "Полностью"),
            show_labels=bool(config.get("showLabels", False)),
        )
        return pil_to_tensor(card), pils_to_tensor(assets), report_json(report)

NODE_CLASS_MAPPINGS.update({
    "AICG3D_CharacterCardAssetPrompt": CharacterCardAssetPrompt,
    "AICG3D_CharacterCardAssetComposer": CharacterCardAssetComposer,
})

NODE_DISPLAY_NAME_MAPPINGS.update({
    "AICG3D_CharacterCardAssetPrompt": "Промпты ассетов карты персонажа · Qwen Image 2.1",
    "AICG3D_CharacterCardAssetComposer": "Профессиональная вёрстка карты · авторазмещение",
})

from .simple_nodes import NODE_CLASS_MAPPINGS as SIMPLE_NODE_CLASS_MAPPINGS
from .simple_nodes import NODE_DISPLAY_NAME_MAPPINGS as SIMPLE_NODE_DISPLAY_NAME_MAPPINGS

NODE_CLASS_MAPPINGS.update(SIMPLE_NODE_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(SIMPLE_NODE_DISPLAY_NAME_MAPPINGS)
