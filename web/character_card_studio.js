import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

const NODE_ID = "AICG3D_CharacterCardStudio";
const STATE_WIDGET = "card_state";
const WIDTH_WIDGET = "width";
const HEIGHT_WIDGET = "height";
const CSS_URL = new URL("./character_card_studio.css", import.meta.url).href;
const SLOT_MIME = "application/x-character-card-slot";
const IMAGE_MIME = "application/x-character-card-image";

const FALLBACK_TEMPLATES = [{"id":"bighead_body3","name":"4 ячейки · Портрет+","description":"Слева крупный фронтальный портрет головы и плеч, справа рядом три полных роста: анфас, профиль и спина.","layout_prompt":"Две колонки: слева только 1 крупный портрет головы и плеч; справа только 3 равных по ширине вертикальных ячейки полного роста — анфас, профиль, спина. Всего 4 ячейки.","width":1920,"height":1200,"defaults":{"title":"Безымянный персонаж","subtitle":"Сеттинг персонажа","style":"единый ассет персонажа, чисто белый студийный фон, мягкий студийный свет, реалистичный кинематографичный вид","background":"#ffffff","accent":"#d86b73"},"cells":[{"id":"head_big","label":"Крупный портрет анфас","role":"portrait","prompt":"Фронтальный портрет головы и плеч, голова и плечи полностью в кадре, черты лица и украшения в волосах чёткие, взгляд в камеру, в кадре только один человек.","x":0.03,"y":0.03,"w":0.4,"h":0.94,"mirror":false},{"id":"body_front","label":"Полный рост анфас","role":"turnaround","prompt":"Полный рост анфас, естественная стойка, руки свободно вдоль тела, от макушки до подошв без обрезки, в кадре только один человек.","x":0.46,"y":0.12,"w":0.16,"h":0.78,"mirror":false},{"id":"body_side","label":"Полный рост профиль","role":"turnaround","prompt":"Строго 90° левый профиль в полный рост, персонаж смотрит вправо кадра, видна только левая половина лица и левое ухо, от макушки до подошв без обрезки.","x":0.635,"y":0.12,"w":0.16,"h":0.78,"mirror":false},{"id":"body_back","label":"Полный рост спина","role":"turnaround","prompt":"Строго 180° вид со спины в полный рост, видны только затылок и спина, от макушки до подошв без обрезки.","x":0.81,"y":0.12,"w":0.16,"h":0.78,"mirror":false}]},{"id":"dualfour_ref","name":"4 ячейки · Два кадра","description":"Равная сетка 2×2: сверху портреты анфас и три четверти, снизу полный рост анфас и спина.","layout_prompt":"Равная сетка 2 ряда × 2 столбца: сверху слева портрет анфас головы и плеч, справа — три четверти; снизу слева полный рост анфас, справа — спина. Всего 4 ячейки, нельзя добавлять третий ряд.","width":1920,"height":1200,"defaults":{"title":"Безымянный персонаж","subtitle":"Двухракурсный сеттинг","style":"единый ассет персонажа, чисто белый студийный фон, мягкий студийный свет, реалистичный кинематографичный вид","background":"#ffffff","accent":"#6b8dd8"},"cells":[{"id":"head_front","label":"Портрет анфас","role":"portrait","prompt":"Крупный план головы и плеч анфас, голова и плечи полностью в кадре, взгляд в камеру, второго человека нет.","x":0.03,"y":0.03,"w":0.46,"h":0.43,"mirror":false},{"id":"head_three_quarter","label":"Портрет три четверти","role":"portrait","prompt":"Крупный план головы и плеч в три четверти, лицо к правому переднему углу кадра, видны контуры обеих щёк, взгляд в камеру.","x":0.51,"y":0.03,"w":0.46,"h":0.43,"mirror":false},{"id":"body_front","label":"Полный рост анфас","role":"turnaround","prompt":"Полный рост анфас, естественная стойка, взгляд в камеру, от макушки до подошв без обрезки, в кадре только один человек.","x":0.03,"y":0.52,"w":0.46,"h":0.45,"mirror":false},{"id":"body_back","label":"Полный рост спина","role":"turnaround","prompt":"Строго 180° вид со спины в полный рост, видны только затылок и спина, от макушки до подошв без обрезки.","x":0.51,"y":0.52,"w":0.46,"h":0.45,"mirror":false}]},{"id":"fiveref","name":"5 ячеек · Лицо и тело","description":"Сверху портреты анфас и три четверти, снизу три полных роста: анфас, профиль и спина.","layout_prompt":"Два ряда: сверху только 2 ячейки — портреты головы и плеч; снизу только 3 ячейки — полный рост. Всего 5 ячеек.","width":1920,"height":1200,"defaults":{"title":"Безымянный персонаж","subtitle":"Пятиракурсный сеттинг","style":"единый ассет персонажа, чисто белый студийный фон, мягкий студийный свет, реалистичный кинематографичный вид","background":"#ffffff","accent":"#65a89a"},"cells":[{"id":"head_front","label":"Портрет анфас","role":"portrait","prompt":"Крупный план головы и плеч анфас, голова и плечи полностью в кадре, взгляд в камеру.","x":0.03,"y":0.03,"w":0.47,"h":0.43,"mirror":false},{"id":"head_three_quarter","label":"Портрет три четверти","role":"portrait","prompt":"Крупный план головы и плеч в три четверти, лицо к правому переднему углу кадра, взгляд в камеру, угол заметно отличается от анфаса.","x":0.5,"y":0.03,"w":0.47,"h":0.43,"mirror":false},{"id":"body_front","label":"Полный рост анфас","role":"turnaround","prompt":"Полный рост анфас, естественная стойка, от макушки до подошв без обрезки, в кадре только один человек.","x":0.03,"y":0.52,"w":0.305,"h":0.45,"mirror":false},{"id":"body_side","label":"Полный рост профиль","role":"turnaround","prompt":"Строго 90° левый профиль в полный рост, персонаж смотрит вправо кадра, от макушки до подошв без обрезки.","x":0.348,"y":0.52,"w":0.305,"h":0.45,"mirror":false},{"id":"body_back","label":"Полный рост спина","role":"turnaround","prompt":"Строго 180° вид со спины в полный рост, видны только затылок и спина, от макушки до подошв без обрезки.","x":0.665,"y":0.52,"w":0.305,"h":0.45,"mirror":false}]},{"id":"head_body_6","name":"6 ячеек · Три вида","description":"Сверху три портрета головы и плеч: анфас, профиль, затылок; снизу три полных роста: анфас, профиль, спина.","layout_prompt":"Равная сетка 2 ряда × 3 столбца: сверху 3 ячейки — только портреты головы и плеч; снизу 3 ячейки — только полный рост. Всего 6 ячеек, нельзя генерировать сетку 3×3.","width":1920,"height":1280,"defaults":{"title":"Безымянный персонаж","subtitle":"Три вида","style":"единый ассет персонажа, чисто белый студийный фон, мягкий студийный свет, реалистичный кинематографичный вид","background":"#ffffff","accent":"#6b8dd8"},"cells":[{"id":"head_front","label":"Портрет анфас","role":"portrait","prompt":"Крупный план головы и плеч анфас, голова и плечи полностью в кадре, взгляд в камеру.","x":0.03,"y":0.03,"w":0.303,"h":0.43,"mirror":false},{"id":"head_side","label":"Портрет профиль","role":"portrait","prompt":"Строго 90° профиль головы и плеч, персонаж смотрит вправо кадра, видна только левая половина лица и левое ухо.","x":0.345,"y":0.03,"w":0.303,"h":0.43,"mirror":false},{"id":"head_back","label":"Портрет затылка","role":"portrait","prompt":"Портрет головы и плеч со спины, видны только затылок и причёска, лица не видно.","x":0.66,"y":0.03,"w":0.303,"h":0.43,"mirror":false},{"id":"body_front","label":"Полный рост анфас","role":"turnaround","prompt":"Полный рост анфас, естественная стойка, от макушки до подошв без обрезки, в кадре только один человек.","x":0.03,"y":0.52,"w":0.303,"h":0.45,"mirror":false},{"id":"body_side","label":"Полный рост профиль","role":"turnaround","prompt":"Строго 90° левый профиль в полный рост, персонаж смотрит вправо кадра, от макушки до подошв без обрезки.","x":0.345,"y":0.52,"w":0.303,"h":0.45,"mirror":false},{"id":"body_back","label":"Полный рост спина","role":"turnaround","prompt":"Строго 180° вид со спины в полный рост, видны только затылок и спина, от макушки до подошв без обрезки.","x":0.66,"y":0.52,"w":0.303,"h":0.45,"mirror":false}]},{"id":"sixtilt_ref","name":"6 ячеек · Главный вид","description":"Слева крупный ключевой кадр; справа два ряда по две ячейки, внизу горизонтальная полоса детали ткани.","layout_prompt":"Неравномерная раскладка: слева 1 крупный ключевой кадр; справа сверху 2 ячейки (портрет анфас, улыбка), в среднем ряду 2 ячейки (профиль в полный рост, динамичный полный рост), справа внизу 1 горизонтальная полоса детали ткани. Всего 6 ячеек.","width":1920,"height":1280,"defaults":{"title":"Безымянный персонаж","subtitle":"Главный визуальный сеттинг","style":"единый ассет персонажа, чисто белый студийный фон, мягкий студийный свет, реалистичный кинематографичный вид","background":"#ffffff","accent":"#9b7dd8"},"cells":[{"id":"hero","label":"Ключевой кадр","role":"hero","prompt":"Фронтальный ключевой кадр в полный рост, естественная стойка, от макушки до подошв полностью в кадре, в кадре только один человек.","x":0.03,"y":0.08,"w":0.39,"h":0.84,"mirror":false},{"id":"head_front","label":"Портрет анфас","role":"portrait","prompt":"Крупный план головы и плеч анфас, голова и плечи полностью в кадре, взгляд в камеру.","x":0.45,"y":0.08,"w":0.26,"h":0.25,"mirror":false},{"id":"ex_smile","label":"Улыбка","role":"expression","prompt":"Крупный план головы и плеч с улыбкой, уголки губ приподняты, глаза слегка прищурены, эмоция заметно отличается от спокойного анфаса.","x":0.735,"y":0.08,"w":0.235,"h":0.25,"mirror":false},{"id":"body_side","label":"Полный рост профиль","role":"turnaround","prompt":"Строго 90° левый профиль в полный рост, персонаж смотрит вправо кадра, от макушки до подошв без обрезки.","x":0.45,"y":0.36,"w":0.26,"h":0.27,"mirror":false},{"id":"action_pose","label":"Динамичный полный рост","role":"turnaround","prompt":"Динамичная стойка в полный рост, поза рук заметно отличается от ключевого кадра, от макушки до подошв без обрезки.","x":0.735,"y":0.36,"w":0.235,"h":0.27,"mirror":false},{"id":"de_fabric","label":"Деталь ткани","role":"detail","prompt":"Горизонтальный макрокадр ткани одежды и вышивки: только текстура, складки и золотая нить, без лица и без полного роста.","x":0.45,"y":0.66,"w":0.52,"h":0.26,"mirror":false}]},{"id":"expr_body_8","name":"8 ячеек · Эмоции","description":"Сверху 4 портрета головы и плеч с разными эмоциями, снизу четыре полных роста: анфас, профиль, спина и движение.","layout_prompt":"Равная сетка 2 ряда × 4 столбца: сверху 4 ячейки — только портреты головы и плеч с разными эмоциями; снизу 4 ячейки — только полный рост. Всего 8 ячеек.","width":1920,"height":1200,"defaults":{"title":"Безымянный персонаж","subtitle":"Многоракурсный сеттинг","style":"единый ассет персонажа, чисто белый студийный фон, мягкий студийный свет, реалистичный кинематографичный вид","background":"#ffffff","accent":"#d86b73"},"cells":[{"id":"head_neutral","label":"Спокойствие","role":"expression","prompt":"Крупный план головы и плеч, нейтральное спокойствие, губы сомкнуты, взгляд прямо, лицо расслаблено.","x":0.03,"y":0.03,"w":0.225,"h":0.43,"mirror":false},{"id":"head_happy","label":"Радостный смех","role":"expression","prompt":"Крупный план головы и плеч, открытый радостный смех с зубами, глаза сощурены дугами, эмоция заметно отличается от первой ячейки.","x":0.268,"y":0.03,"w":0.225,"h":0.43,"mirror":false},{"id":"head_serious","label":"Серьёзность","role":"expression","prompt":"Крупный план головы и плеч, губы плотно сжаты, брови слегка нахмурены, строгий взгляд в камеру.","x":0.505,"y":0.03,"w":0.225,"h":0.43,"mirror":false},{"id":"head_surprised","label":"Удивление","role":"expression","prompt":"Крупный план головы и плеч, глаза широко открыты, брови подняты, рот слегка приоткрыт — выражение удивления.","x":0.743,"y":0.03,"w":0.225,"h":0.43,"mirror":false},{"id":"body_front","label":"Полный рост анфас","role":"turnaround","prompt":"Полный рост анфас, естественная стойка, руки свободно вдоль тела, от макушки до подошв без обрезки.","x":0.03,"y":0.52,"w":0.225,"h":0.45,"mirror":false},{"id":"body_profile","label":"Полный рост левый профиль","role":"turnaround","prompt":"Строго 90° левый профиль в полный рост, персонаж смотрит вправо кадра, от макушки до подошв без обрезки.","x":0.268,"y":0.52,"w":0.225,"h":0.45,"mirror":false},{"id":"body_back","label":"Полный рост спина","role":"turnaround","prompt":"Строго 180° вид со спины в полный рост, видны только затылок и спина, от макушки до подошв без обрезки.","x":0.505,"y":0.52,"w":0.225,"h":0.45,"mirror":false},{"id":"body_action","label":"Полный рост в движении","role":"turnaround","prompt":"Естественная ходьба в полный рост, походка отличается от стоек в первых трёх ячейках, от макушки до подошв без обрезки.","x":0.743,"y":0.52,"w":0.225,"h":0.45,"mirror":false}]},{"id":"school_ref","name":"10 ячеек · Сеттинг","description":"Слева ключевой кадр; справа сверху три вида, в среднем ряду три эмоции, снизу три детали.","layout_prompt":"Две колонки: слева только 1 крупный ключевой кадр; справа 3 столбца × 3 ряда — сверху 3 ячейки полного роста, в середине 3 эмоции головы и плеч, снизу 3 локальные детали. Всего 10 ячеек.","width":2000,"height":1400,"defaults":{"title":"Безымянный персонаж","subtitle":"Набор сеттинга персонажа","style":"единый ассет персонажа, чисто белый студийный фон, мягкий студийный свет","background":"#ffffff","accent":"#e08a9a"},"cells":[{"id":"hero","label":"Ключевой кадр","role":"hero","prompt":"Одиночный фронтальный ключевой кадр в полный рост, естественная стойка, от макушки до подошв полностью в кадре, второго человека или коллажа быть не должно.","x":0.03,"y":0.08,"w":0.3,"h":0.86,"mirror":false},{"id":"body_front","label":"Полный рост анфас","role":"turnaround","prompt":"Полный рост анфас, естественная стойка, от макушки до подошв без обрезки.","x":0.36,"y":0.08,"w":0.2,"h":0.4,"mirror":false},{"id":"body_side","label":"Полный рост профиль","role":"turnaround","prompt":"Строго 90° левый профиль в полный рост, персонаж смотрит вправо кадра, от макушки до подошв без обрезки.","x":0.58,"y":0.08,"w":0.2,"h":0.4,"mirror":false},{"id":"body_back","label":"Полный рост спина","role":"turnaround","prompt":"Строго 180° вид со спины в полный рост, видны только затылок и спина, от макушки до подошв без обрезки.","x":0.8,"y":0.08,"w":0.17,"h":0.4,"mirror":false},{"id":"ex_1","label":"Сладкая улыбка","role":"expression","prompt":"Крупный план головы и плеч, открытая сладкая улыбка с зубами, глаза прищурены, яркая эмоция.","x":0.36,"y":0.52,"w":0.2,"h":0.2,"mirror":false},{"id":"ex_2","label":"Задумчивость","role":"expression","prompt":"Крупный план головы и плеч, голова опущена, взгляд вниз, не в камеру, тихое сдержанное выражение.","x":0.58,"y":0.52,"w":0.2,"h":0.2,"mirror":false},{"id":"ex_3","label":"Удивление с открытым ртом","role":"expression","prompt":"Крупный план головы и плеч, глаза широко открыты, брови подняты, рот открыт — выражение удивления.","x":0.8,"y":0.52,"w":0.17,"h":0.2,"mirror":false},{"id":"de_1","label":"Деталь одежды","role":"detail","prompt":"Локальный макрокадр воротника формы, значка и текстуры ткани, без полного персонажа.","x":0.36,"y":0.75,"w":0.2,"h":0.2,"mirror":false},{"id":"de_2","label":"Деталь аксессуара","role":"detail","prompt":"Локальный макрокадр галстука-бабочки или украшения в волосах, без лица.","x":0.58,"y":0.75,"w":0.2,"h":0.2,"mirror":false},{"id":"de_3","label":"Деталь обуви","role":"detail","prompt":"Локальный макрокадр конструкции и материала обуви, без полного персонажа.","x":0.8,"y":0.75,"w":0.17,"h":0.2,"mirror":false}]},{"id":"xianxia_ref","name":"14 ячеек · Полный атлас","description":"Слева четыре полных роста и три портрета, справа четыре эмоции и три детали, внизу горизонтальная полоса ткани.","layout_prompt":"Две колонки: слева сверху 4 полных роста, снизу 3 портрета; справа сверху 3 эмоции, в среднем ряду 3 ячейки (1 эмоция + 2 детали), внизу 1 горизонтальная полоса детали ткани. Всего 14 ячеек, нельзя добавлять четвёртый ряд.","width":2200,"height":1300,"defaults":{"title":"Безымянный персонаж","subtitle":"Полный атлас","style":"единый ассет персонажа, чисто белый студийный фон, мягкий студийный свет, реалистичная проработка","background":"#ffffff","accent":"#7a9bd8"},"cells":[{"id":"body_front","label":"Полный рост анфас","role":"turnaround","prompt":"Полный рост анфас, естественная стойка, от макушки до подошв без обрезки, в кадре только один человек.","x":0.02,"y":0.03,"w":0.125,"h":0.42,"mirror":false},{"id":"body_right","label":"Полный рост правый профиль","role":"turnaround","prompt":"Строго 90° правый профиль в полный рост, персонаж смотрит влево кадра, видна только правая половина лица и правое ухо, от макушки до подошв без обрезки.","x":0.155,"y":0.03,"w":0.125,"h":0.42,"mirror":false},{"id":"body_back","label":"Полный рост спина","role":"turnaround","prompt":"Строго 180° вид со спины в полный рост, видны только затылок и спина, от макушки до подошв без обрезки.","x":0.29,"y":0.03,"w":0.125,"h":0.42,"mirror":false},{"id":"body_left","label":"Полный рост левый профиль","role":"turnaround","prompt":"Строго 90° левый профиль в полный рост, персонаж смотрит вправо кадра, видна только левая половина лица и левое ухо, направление противоположно правому профилю.","x":0.425,"y":0.03,"w":0.125,"h":0.42,"mirror":false},{"id":"head_1","label":"Портрет анфас","role":"portrait","prompt":"Фронтальный портрет головы и плеч, голова и плечи полностью в кадре, спокойный взгляд в камеру.","x":0.02,"y":0.47,"w":0.15,"h":0.43,"mirror":false},{"id":"head_2","label":"Портрет профиль","role":"portrait","prompt":"Строго 90° профиль головы и плеч, персонаж смотрит вправо кадра, показан контур профиля.","x":0.18,"y":0.47,"w":0.15,"h":0.43,"mirror":false},{"id":"head_3","label":"Портрет три четверти","role":"portrait","prompt":"Портрет головы и плеч в три четверти, лицо к правому переднему углу кадра, взгляд в камеру.","x":0.34,"y":0.47,"w":0.15,"h":0.43,"mirror":false},{"id":"ex_1","label":"Нежная улыбка","role":"expression","prompt":"Крупный план головы и плеч, закрытая нежная улыбка, уголки губ слегка приподняты, мягкий взгляд.","x":0.58,"y":0.03,"w":0.12,"h":0.25,"mirror":false},{"id":"ex_2","label":"Удивление с открытым ртом","role":"expression","prompt":"Крупный план головы и плеч, глаза широко открыты, брови подняты, рот слегка приоткрыт — выражение удивления.","x":0.71,"y":0.03,"w":0.12,"h":0.25,"mirror":false},{"id":"ex_3","label":"Закрытые глаза, задумчивость","role":"expression","prompt":"Крупный план головы и плеч, глаза закрыты, голова слегка опущена, губы слегка сжаты, тихое выражение.","x":0.84,"y":0.03,"w":0.12,"h":0.25,"mirror":false},{"id":"ex_4","label":"Холодный хмурый взгляд","role":"expression","prompt":"Крупный план головы и плеч, брови слегка нахмурены, холодный прямой взгляд, заметно отличается от улыбки.","x":0.58,"y":0.3,"w":0.12,"h":0.25,"mirror":false},{"id":"de_1","label":"Деталь глаза","role":"detail","prompt":"Макрокадр одного глаза: цвет зрачка, текстура радужки и ресницы, без всего лица.","x":0.71,"y":0.3,"w":0.12,"h":0.25,"mirror":false},{"id":"de_2","label":"Деталь аксессуара","role":"detail","prompt":"Макрокадр ожерелья, серьги или украшения в волосах, без лица.","x":0.84,"y":0.3,"w":0.12,"h":0.25,"mirror":false},{"id":"de_3","label":"Деталь ткани","role":"detail","prompt":"Горизонтальный макрокадр ткани одежды и вышивки: только текстура ткани, складки и узор, без персонажа.","x":0.58,"y":0.57,"w":0.38,"h":0.37,"mirror":false}]},{"id":"scene_six_view","kind":"scene","name":"Сцена · 360° обзор","description":"Загрузите любой кадр сцены и получите полный круговой обзор по 0°, 90°, 180°, 270°, плюс полосу 360° панорамы и деталь окружения.","layout_prompt":"Сверху 4 ячейки слева направо: 0° фронтальный референс, 90° вправо, 180° назад, 270° влево; снизу слева непрерывная длинная 360° панорама, справа — деталь окружения. Всего 6 ячеек.","width":1920,"height":1280,"defaults":{"title":"Безымянная сцена","subtitle":"360° круговой обзор сцены","style":"реалистичный концепт сцены, единая пространственная структура, материалы, перспектива и освещение","background":"#ffffff","accent":"#4f8a8b"},"cells":[{"id":"scene_front","label":"0° фронтальный референс","role":"scene_anchor","prompt":"Сохранить загруженный кадр сцены как единственный пространственный якорь: не перерисовывать и не менять композицию; если референса нет — сгенерировать главный 0° фронтальный вид сцены. Сцена главная, не добавлять людей или животных.","x":0.03,"y":0.03,"w":0.217,"h":0.43,"mirror":false},{"id":"scene_right","label":"90° вправо","role":"scene_view","prompt":"С позиции камеры 0° повернуть примерно на 90° вправо и снять правую сторону той же сцены; должно появиться правое пространство, не показанное на 0°, с сохранением рельефа, архитектуры, дорог, растительности, ключевых объектов, материалов и освещения. Сцена главная, не добавлять людей или животных.","x":0.271,"y":0.03,"w":0.217,"h":0.43,"mirror":false},{"id":"scene_back","label":"180° назад","role":"scene_view","prompt":"С позиции камеры 0° развернуться примерно на 180° и снять противоположный ракурс той же сцены; вид должен образовать непрерывное пространство с 0° и 90°, с тем же масштабом, положением ключевых объектов и направлением света. Сцена главная, не добавлять людей или животных.","x":0.512,"y":0.03,"w":0.217,"h":0.43,"mirror":false},{"id":"scene_left","label":"270° влево","role":"scene_view","prompt":"С позиции камеры 0° повернуть примерно на 90° влево, то есть направление 270°; должно появиться левое пространство, не показанное на 0°, и сомкнуться с 90° и 180°. Сцена главная, не добавлять людей или животных.","x":0.753,"y":0.03,"w":0.217,"h":0.43,"mirror":false},{"id":"scene_panorama","label":"360° панорама","role":"scene_panorama","prompt":"Сгенерировать горизонтальную непрерывную 360° развёртку той же сцены: слева направо естественно стыкуются 0°, 90°, 180°, 270° и возврат к 0°; рельеф, архитектура, дороги, растительность, ключевые объекты, материалы и освещение непрерывны. Сцена главная, не добавлять людей или животных.","x":0.03,"y":0.5,"w":0.64,"h":0.45,"mirror":false},{"id":"scene_detail","label":"Деталь окружения","role":"scene_detail","prompt":"Выделить самый узнаваемый материал, текстуру, растительность, архитектурный элемент или декор сцены в локальный макрокадр; цвет и материал должны совпадать с окружением. Сцена главная, не добавлять людей или животных.","x":0.7,"y":0.5,"w":0.27,"h":0.45,"mirror":false}]}];

const PAYLOAD_FALLBACK = {
    version: 3,
    templates: FALLBACK_TEMPLATES,
    defaultNegative: "низкое качество, размытие, деформации, лишние конечности, неправильные пальцы, дрейф личности, разрушенное лицо, смена пола, ошибки кроя одежды, пропавшие аксессуары, хаотичная раскладка панелей, дублирование персонажа, копирование одного и того же лица, неверное число ячеек, лишние ячейки, недостающие ячейки, слияние ячеек, ошибочная сетка 3×3, испорченный текст, водяные знаки, логотипы, обрезка головы, обрезка ног, обрезка обуви, полуфигура вместо полного роста, обрубленные ноги, срезанная голова, серый фон, тёмно-серый фон, тёмный фон, градиентный фон, текстурный фон, фон с тенями",
};

let payloadPromise = null;
let stylePromise = null;

function el(tag, className = "", text = "") {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
}

function ensureStyle() {
    if (stylePromise) return stylePromise;
    stylePromise = new Promise((resolve) => {
        const existing = document.getElementById("ccs-character-card-style");
        if (existing) {
            resolve();
            return;
        }
        const link = document.createElement("link");
        link.id = "ccs-character-card-style";
        link.rel = "stylesheet";
        link.href = CSS_URL;
        link.addEventListener("load", resolve, { once: true });
        link.addEventListener("error", resolve, { once: true });
        document.head.append(link);
    });
    return stylePromise;
}

function loadPayload() {
    if (payloadPromise) return payloadPromise;
    payloadPromise = (async () => {
        try {
            const response = await api.fetchApi("/aicg3d/character-card/templates");
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            if (!Array.isArray(data?.templates) || !data.templates.length) throw new Error("empty templates");
            return {
                version: data.version || 1,
                templates: data.templates,
                defaultNegative: String(data.defaultNegative || PAYLOAD_FALLBACK.defaultNegative),
            };
        } catch (error) {
            console.warn("[CharacterCardStudio] Using bundled templates:", error);
            return PAYLOAD_FALLBACK;
        }
    })();
    return payloadPromise;
}

function widgetOf(node, name) {
    return node?.widgets?.find((widget) => widget?.name === name);
}

function setWidgetValue(node, name, value) {
    const widget = widgetOf(node, name);
    if (!widget) return false;
    if (widget.value !== value) widget.value = value;
    return true;
}

function markWidgetHidden(widget) {
    if (!widget) return;
    if (!widget.__ccsNative) {
        widget.__ccsNative = {
            type: widget.type,
            hidden: widget.hidden,
            computeSize: widget.computeSize,
            optionsHidden: widget.options?.hidden,
            optionsCanvasOnly: widget.options?.canvasOnly,
        };
    }
    widget.options = widget.options || {};
    widget.options.hidden = true;
    widget.options.canvasOnly = true;
    if (widget._state?.options) {
        widget._state.options.hidden = true;
        widget._state.options.canvasOnly = true;
    }
    widget.hidden = true;
    widget.type = "hidden";
    widget.computeSize = () => [0, -4];
}

function autoHideWidgets(nodeType, names) {
    const prototype = nodeType?.prototype;
    if (!prototype || prototype.__ccsAutoHide || typeof prototype.addWidget !== "function") return;
    const wanted = new Set(names);
    const original = prototype.addWidget;
    prototype.__ccsAutoHide = true;
    prototype.addWidget = function (...args) {
        const widget = original.apply(this, args);
        try {
            const name = widget?.name ?? (typeof args[1] === "string" ? args[1] : "");
            if (wanted.has(name)) markWidgetHidden(widget);
        } catch (error) {
            console.error("[CharacterCardStudio]", error);
        }
        return widget;
    };
}

function refreshVueWidgets(node) {
    if (!globalThis.LiteGraph?.vueNodesMode) return;
    const list = node?.widgets;
    if (!Array.isArray(list) || !list.length) return;
    try {
        node._widgets = [...list];
        node.setDirtyCanvas?.(true, true);
    } catch (error) {
        console.warn("[CharacterCardStudio] Widget refresh failed", error);
    }
}

function refreshNode(node) {
    node._widgetSlotsDirty = true;
    node.setDirtyCanvas?.(true, true);
    app.graph?.setDirtyCanvas?.(true, true);
}

function clone(value) {
    return JSON.parse(JSON.stringify(value));
}

function clampNumber(value, low, high, fallback) {
    const number = Number(value);
    return Number.isFinite(number) ? Math.max(low, Math.min(high, number)) : fallback;
}

function roundDimension(value) {
    const clamped = clampNumber(value, 512, 4096, 1024);
    return Math.round(clamped / 16) * 16;
}

function uid() {
    return `slot_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 7)}`;
}

function slotFromCell(cell, index) {
    return {
        id: uid(),
        cellId: cell.id,
        label: cell.label || `ячейка ${index + 1}`,
        role: cell.role || "custom",
        prompt: cell.prompt || "",
        image: "",
        subfolder: "",
        fit: ["turnaround", "hero", "scene_anchor"].includes(cell.role) ? "contain" : "cover",
        zoom: 1,
        offsetX: 0,
        offsetY: 0,
        lockIdentity: true,
        enabled: true,
    };
}

function defaultState(template, payload, previous = null) {
    const defaults = template.defaults || {};
    const previousTemplate = payload.templates.find((item) => item.id === previous?.templateId);
    const kindChanged = Boolean(previousTemplate && previousTemplate.kind !== template.kind);
    const leavingScene = kindChanged && previousTemplate?.kind === "scene";
    const genericTitle = ["", "Безымянный персонаж", "Безымянная сцена", "未命名角色", "未命名场景"].includes(previous?.title || "");
    const state = {
        version: 2,
        templateId: template.id,
        title: kindChanged && genericTitle ? (defaults.title || "Безымянный объект") : (previous?.title || defaults.title || "Безымянный объект"),
        subtitle: kindChanged ? (defaults.subtitle || template.name || "карта сеттинга") : (previous?.subtitle || defaults.subtitle || template.name || "карта сеттинга"),
        identity: kindChanged ? "" : (previous?.identity || ""),
        appearance: kindChanged ? "" : (previous?.appearance || ""),
        outfit: kindChanged ? "" : (previous?.outfit || ""),
        palette: leavingScene ? "" : (previous?.palette || ""),
        style: kindChanged ? (defaults.style || "") : (previous?.style || defaults.style || ""),
        negativePrompt: previous?.negativePrompt || payload.defaultNegative,
        background: previous?.background || defaults.background || "#ffffff",
        accent: previous?.accent || defaults.accent || "#d86b73",
        showLabels: previous?.showLabels ?? false,
        width: roundDimension(previous?.width || template.width || 1920),
        height: roundDimension(previous?.height || template.height || 1080),
        slots: template.cells.map((cell, index) => {
            const base = slotFromCell(cell, index);
            const old = previous?.slots?.find((slot) => slot?.cellId === cell.id);
            if (!old) return base;
            // On template switch: always use new template labels/prompts; keep image and visual tweaks only
            return {
                ...base,
                id: old.id || base.id,
                image: old.image || "",
                subfolder: old.subfolder || "",
                fit: ["contain", "cover"].includes(old.fit) ? old.fit : base.fit,
                zoom: clampNumber(old.zoom, 0.5, 3, 1),
                offsetX: clampNumber(old.offsetX, -1, 1, 0),
                offsetY: clampNumber(old.offsetY, -1, 1, 0),
                lockIdentity: old.lockIdentity !== false,
                enabled: old.enabled !== false,
            };
        }),
        library: Array.isArray(previous?.library) ? clone(previous.library) : [],
    };
    return state;
}

function normaliseState(raw, payload, template) {
    const base = defaultState(template, payload);
    if (!raw || typeof raw !== "object") return base;
    const result = {
        ...base,
        version: 2,
        title: String(raw.title ?? base.title),
        subtitle: String(raw.subtitle ?? base.subtitle),
        identity: String(raw.identity ?? ""),
        appearance: String(raw.appearance ?? ""),
        outfit: String(raw.outfit ?? ""),
        palette: String(raw.palette ?? ""),
        style: String(raw.style ?? base.style),
        negativePrompt: String(raw.negativePrompt ?? payload.defaultNegative),
        background: String(raw.background ?? base.background),
        accent: String(raw.accent ?? base.accent),
        showLabels: Boolean(raw.showLabels),
        width: roundDimension(raw.width ?? base.width),
        height: roundDimension(raw.height ?? base.height),
    };
    const slots = Array.isArray(raw.slots) ? raw.slots : [];
    result.slots = template.cells.map((cell, index) => {
        const indexed = slots[index] && typeof slots[index] === "object" ? slots[index] : {};
        const source = slots.find((item) => item && typeof item === "object" && item.cellId === cell.id)
            || (!indexed.cellId ? indexed : {});
        return {
            ...slotFromCell(cell, index),
            id: String(source.id || uid()),
            image: String(source.image || ""),
            subfolder: String(source.subfolder || ""),
            fit: source.fit === "contain" || (source.fit == null && ["turnaround", "hero", "scene_anchor"].includes(cell.role)) ? "contain" : "cover",
            zoom: clampNumber(source.zoom, 0.5, 3, 1),
            offsetX: clampNumber(source.offsetX, -1, 1, 0),
            offsetY: clampNumber(source.offsetY, -1, 1, 0),
            lockIdentity: source.lockIdentity !== false,
            enabled: source.enabled !== false,
        };
    });
    const seen = new Set();
    result.library = [];
    for (const item of Array.isArray(raw.library) ? raw.library : []) {
        if (!item || typeof item !== "object") continue;
        const image = String(item.image || item.name || "");
        const subfolder = String(item.subfolder || "");
        const key = `${subfolder}\u0000${image}`;
        if (!image || seen.has(key)) continue;
        seen.add(key);
        result.library.push({
            image,
            subfolder,
            name: String(item.name || image.split("/").pop() || image),
            useForIdentity: item.useForIdentity !== false,
        });
    }
    for (const slot of result.slots) {
        if (!slot.image) continue;
        const key = `${slot.subfolder}\u0000${slot.image}`;
        if (seen.has(key)) continue;
        seen.add(key);
        result.library.push({
            image: slot.image,
            subfolder: slot.subfolder,
            name: slot.image.split("/").pop() || slot.image,
            useForIdentity: true,
        });
    }
    return result;
}

function stateFromWidget(node, payload) {
    const widget = widgetOf(node, STATE_WIDGET);
    const rawText = String(widget?.value || "{}");
    let raw = {};
    try {
        raw = JSON.parse(rawText);
    } catch (error) {
        raw = {};
    }
    const templateId = String(raw?.templateId || raw?.template_id || payload.templates[0].id);
    const template = payload.templates.find((item) => item.id === templateId) || payload.templates[0];
    return normaliseState(raw, payload, template);
}

function queueStateSync(node, state) {
    const text = JSON.stringify(state);
    const widget = widgetOf(node, STATE_WIDGET);
    if (widget) widget.value = text;
    setWidgetValue(node, WIDTH_WIDGET, state.width);
    setWidgetValue(node, HEIGHT_WIDGET, state.height);
    clearTimeout(node.__ccsSyncTimer);
    node.__ccsSyncTimer = setTimeout(() => {
        refreshNode(node);
    }, 40);
}

function imageUrl(item) {
    if (!item?.image) return "";
    const params = new URLSearchParams({
        filename: item.image,
        type: "input",
        preview: "webp",
    });
    if (item.subfolder) params.set("subfolder", item.subfolder);
    const path = `/view?${params.toString()}`;
    try {
        return api.apiURL ? api.apiURL(path) : path;
    } catch (error) {
        return path;
    }
}

function imageItem(slot) {
    return { image: slot?.image || "", subfolder: slot?.subfolder || "" };
}

function templateFor(state, payload) {
    return payload.templates.find((item) => item.id === state.templateId) || payload.templates[0];
}

function formatDimensions(state) {
    return `${state.width} × ${state.height}`;
}

function makeField(label, control, top = false) {
    const row = el("div", `ccs-form-row${top ? " is-top" : ""}`);
    row.append(el("label", "", label), control);
    return row;
}

function makeSwitch(isOn, onChange, title = "") {
    const button = el("button", `ccs-switch${isOn ? " is-on" : ""}`);
    button.type = "button";
    if (title) button.title = title;
    button.addEventListener("click", () => {
        const next = !button.classList.contains("is-on");
        button.classList.toggle("is-on", next);
        onChange(next);
    });
    return button;
}

function makeTextarea(rows = 4) {
    const area = el("textarea", "ccs-textarea");
    area.rows = rows;
    area.spellcheck = false;
    return area;
}

function makeColorField(value, onChange, label = "") {
    const wrap = el("div", "ccs-color-field");
    if (label) wrap.append(el("div", "ccs-color-label", label));
    const picker = document.createElement("input");
    picker.type = "color";
    picker.value = /^#[0-9a-f]{6}$/i.test(value) ? value : "#d86b73";
    const text = el("input", "ccs-input");
    text.value = value || picker.value;
    picker.addEventListener("input", () => {
        text.value = picker.value;
        onChange(picker.value);
    });
    text.addEventListener("change", () => {
        const next = /^#[0-9a-f]{6}$/i.test(text.value) ? text.value : picker.value;
        text.value = next;
        picker.value = next;
        onChange(next);
    });
    wrap.append(picker, text);
    return wrap;
}

function buildTemplateMini(template) {
    const mini = el("div", "ccs-template-mini");
    mini.style.aspectRatio = `${template.width || 16} / ${template.height || 10}`;
    for (const cell of template.cells || []) {
        const block = el("span");
        block.style.left = `${cell.x * 100}%`;
        block.style.top = `${cell.y * 100}%`;
        block.style.width = `${cell.w * 100}%`;
        block.style.height = `${cell.h * 100}%`;
        block.style.background = cell.role === "hero" ? "#949ba5" : "#b1b7bf";
        mini.append(block);
    }
    return mini;
}

function buildUi(node, payload, state) {
    const root = el("div", "ccs-root");
    root.addEventListener("pointerdown", (event) => event.stopPropagation());
    root.addEventListener("wheel", (event) => event.stopPropagation(), { passive: true });

    const ui = {
        node,
        payload,
        state,
        root,
        selectedIndex: 0,
        activeTab: "cell",
        updating: false,
        toastTimer: null,
        boardObserver: null,
    };

    const topbar = el("div", "ccs-topbar");
    const brand = el("div", "ccs-brand");
    brand.append(el("div", "ccs-mark", "CC"));
    const brandCopy = el("div", "ccs-brand-copy");
    brandCopy.append(el("div", "ccs-brand-title", "Рабочий стол карты персонажа"), el("div", "ccs-brand-sub", "Qwen Image 2.1"));
    brand.append(brandCopy);

    const toolbar = el("div", "ccs-toolbar");
    const templateField = el("label", "ccs-field-inline");
    templateField.append(el("span", "ccs-field-label", "Макет"));
    const templateSelect = el("select", "ccs-select");
    templateSelect.style.minWidth = "154px";
    for (const template of payload.templates) {
        const option = document.createElement("option");
        option.value = template.id;
        option.textContent = template.name;
        templateSelect.append(option);
    }
    templateField.append(templateSelect);
    toolbar.append(templateField);

    const dimensions = el("div", "ccs-dimension", formatDimensions(state));
    toolbar.append(dimensions);
    toolbar.append(el("div", "ccs-toolbar-spacer"));

    const uploadButton = el("button", "ccs-btn ccs-btn--accent", "Загрузить ассеты");
    uploadButton.type = "button";
    const copyButton = el("button", "ccs-btn", "Копировать JSON");
    copyButton.type = "button";
    toolbar.append(uploadButton, copyButton);
    topbar.append(brand, toolbar);

    const body = el("div", "ccs-body");
    const stage = el("section", "ccs-stage");
    const stageHead = el("div", "ccs-stage-head");
    const stageTitle = el("div", "ccs-stage-title", "Превью макета");
    const stageMeta = el("div", "ccs-stage-meta");
    const stageSpacer = el("div", "ccs-stage-spacer");
    const restoreButton = el("button", "ccs-btn ccs-btn--small", "Восстановить всё");
    restoreButton.type = "button";
    restoreButton.title = "Снова включить все ячейки";
    const fillEmptyButton = el("button", "ccs-btn ccs-btn--small", "Заполнить по порядку");
    fillEmptyButton.type = "button";
    stageHead.append(stageTitle, stageMeta, stageSpacer, restoreButton, fillEmptyButton);

    const boardWrap = el("div", "ccs-board-wrap");
    const board = el("div", "ccs-board");
    boardWrap.append(board);

    const templateStrip = el("div", "ccs-template-strip");
    stage.append(stageHead, boardWrap, templateStrip);

    const sidebar = el("aside", "ccs-sidebar");
    const tabs = el("div", "ccs-tabs");
    const cellTab = el("button", "ccs-tab is-active", "Текущая ячейка");
    const globalTab = el("button", "ccs-tab", "Персонаж и вывод");
    cellTab.type = "button";
    globalTab.type = "button";
    tabs.append(cellTab, globalTab);

    const cellPane = el("div", "ccs-pane");
    const globalPane = el("div", "ccs-pane");
    globalPane.hidden = true;
    sidebar.append(tabs, cellPane, globalPane);

    const library = el("div", "ccs-library");
    const libraryHead = el("div", "ccs-library-head");
    const libraryTitle = el("div", "ccs-library-title", "Библиотека");
    const libraryMeta = el("div", "ccs-library-meta", "0 шт.");
    const libraryUpload = el("button", "ccs-btn ccs-btn--small", "Добавить изображение");
    libraryUpload.type = "button";
    libraryHead.append(libraryTitle, libraryMeta, libraryUpload);
    const libraryList = el("div", "ccs-library-list");
    library.append(libraryHead, libraryList);

    body.append(stage, sidebar);
    root.append(topbar, body, library);

    const fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.accept = "image/*";
    fileInput.multiple = true;
    fileInput.className = "ccs-hidden-input";
    root.append(fileInput);

    const toast = el("div", "ccs-toast");
    root.append(toast);

    Object.assign(ui, {
        templateSelect,
        dimensions,
        uploadButton,
        copyButton,
        stageMeta,
        fillEmptyButton,
        restoreButton,
        boardWrap,
        board,
        templateStrip,
        cellTab,
        globalTab,
        cellPane,
        globalPane,
        libraryMeta,
        libraryUpload,
        libraryList,
        fileInput,
        toast,
    });

    ui.showToast = (message, isError = false) => {
        toast.textContent = message;
        toast.classList.toggle("is-error", Boolean(isError));
        toast.classList.add("is-visible");
        clearTimeout(ui.toastTimer);
        ui.toastTimer = setTimeout(() => toast.classList.remove("is-visible"), 2200);
    };

    buildCellPane(ui);
    buildGlobalPane(ui);

    templateSelect.addEventListener("change", () => {
        switchTemplate(ui, templateSelect.value);
    });
    uploadButton.addEventListener("click", () => openFilePicker(ui, null));
    libraryUpload.addEventListener("click", () => openFilePicker(ui, null));
    fileInput.addEventListener("change", async () => {
        const files = [...(fileInput.files || [])];
        fileInput.value = "";
        if (!files.length) return;
        const target = Number.isInteger(Number(fileInput.dataset.slotIndex))
            ? Number(fileInput.dataset.slotIndex)
            : null;
        await uploadFiles(ui, files, target);
    });
    cellTab.addEventListener("click", () => setActiveTab(ui, "cell"));
    globalTab.addEventListener("click", () => setActiveTab(ui, "global"));
    copyButton.addEventListener("click", () => copyState(ui));
    fillEmptyButton.addEventListener("click", () => fillEmptySlots(ui));
    restoreButton.addEventListener("click", () => {
        let count = 0;
        for (const slot of ui.state.slots) {
            if (slot.enabled === false) {
                slot.enabled = true;
                count++;
            }
        }
        commitUi(ui, { board: true, inspector: true, sync: true });
        ui.showToast(count ? `Восстановлено ${count} ячеек` : "Все ячейки включены");
    });

    ui.renderAll = () => {
        renderTemplateStrip(ui);
        renderBoard(ui);
        renderLibrary(ui);
        syncInspector(ui);
        syncHeader(ui);
    };
    ui.renderAll();
    bindBoardResize(ui);
    return ui;
}

function setActiveTab(ui, tab) {
    ui.activeTab = tab;
    ui.cellTab.classList.toggle("is-active", tab === "cell");
    ui.globalTab.classList.toggle("is-active", tab === "global");
    ui.cellPane.hidden = tab !== "cell";
    ui.globalPane.hidden = tab !== "global";
}

function buildCellPane(ui) {
    const pane = ui.cellPane;
    const state = ui.state;

    const mediaSection = el("div", "ccs-section");
    mediaSection.append(el("div", "ccs-section-label", "Референс"));
    const preview = el("div", "ccs-media-preview");
    const previewImage = el("img");
    previewImage.alt = "";
    const previewEmpty = el("div", "ccs-media-empty", "Изображение не выбрано");
    preview.append(previewImage, previewEmpty);
    const mediaActions = el("div", "ccs-media-actions");
    const replaceButton = el("button", "ccs-btn ccs-btn--small", "Выбрать изображение");
    const clearButton = el("button", "ccs-btn ccs-btn--icon", "×");
    const lockButton = el("button", "ccs-btn ccs-btn--icon", "ID");
    replaceButton.type = "button";
    clearButton.type = "button";
    lockButton.type = "button";
    clearButton.title = "Очистить изображение ячейки";
    lockButton.title = "Включить в коллаж identity-референса";
    mediaActions.append(replaceButton, clearButton, lockButton);
    mediaSection.append(preview, mediaActions);

    const contentSection = el("div", "ccs-section");
    contentSection.append(el("div", "ccs-section-label", "Настройки ячейки"));
    const labelInput = el("input", "ccs-input");
    const roleSelect = el("select", "ccs-select");
    for (const [value, label] of [
        ["hero", "Главный вид"],
        ["turnaround", "Разворот / полный рост"],
        ["portrait", "Портрет"],
        ["expression", "Эмоция"],
        ["detail", "Деталь"],
        ["scene_anchor", "Фронт сцены"],
        ["scene_view", "Ракурс сцены"],
        ["scene_panorama", "Панорама 360°"],
        ["scene_detail", "Материал сцены"],
        ["custom", "Свой"],
    ]) {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = label;
        roleSelect.append(option);
    }
    const promptArea = makeTextarea(5);
    const fitSelect = el("select", "ccs-select");
    for (const [value, label] of [["cover", "Заполнить с обрезкой"], ["contain", "Полностью"]]) {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = label;
        fitSelect.append(option);
    }
    contentSection.append(
        makeField("Название", labelInput),
        makeField("Тип", roleSelect),
        makeField("Описание кадра", promptArea, true),
        makeField("Подгонка", fitSelect),
    );

    const cropSection = el("div", "ccs-section");
    cropSection.append(el("div", "ccs-section-label is-teal", "Подстройка кадра"));
    const zoom = buildRange(0.5, 3, 0.05);
    const offsetX = buildRange(-1, 1, 0.01);
    const offsetY = buildRange(-1, 1, 0.01);
    cropSection.append(
        makeField("Масштаб", zoom.wrap),
        makeField("По горизонтали", offsetX.wrap),
        makeField("По вертикали", offsetY.wrap),
    );

    const moveSection = el("div", "ccs-section");
    moveSection.append(el("div", "ccs-section-label", "Порядок"));
    const moveGrid = el("div", "ccs-action-grid");
    const leftButton = el("button", "ccs-btn ccs-btn--small", "Влево");
    const rightButton = el("button", "ccs-btn ccs-btn--small", "Вправо");
    const copyImageButton = el("button", "ccs-btn ccs-btn--small", "Копировать ссылку на изображение");
    const clearAllButton = el("button", "ccs-btn ccs-btn--small ccs-btn--danger", "Очистить ячейку");
    leftButton.type = "button";
    rightButton.type = "button";
    copyImageButton.type = "button";
    clearAllButton.type = "button";
    moveGrid.append(leftButton, rightButton, copyImageButton, clearAllButton);
    moveSection.append(moveGrid);

    pane.append(mediaSection, contentSection, cropSection, moveSection);


    Object.assign(ui, {
        previewImage,
        previewEmpty,
        replaceButton,
        clearButton,
        lockButton,
        labelInput,
        roleSelect,
        promptArea,
        fitSelect,
        zoomRange: zoom.input,
        zoomValue: zoom.value,
        offsetXRange: offsetX.input,
        offsetXValue: offsetX.value,
        offsetYRange: offsetY.input,
        offsetYValue: offsetY.value,
        leftButton,
        rightButton,
        copyImageButton,
        clearAllButton,
    });

    replaceButton.addEventListener("click", () => openFilePicker(ui, ui.selectedIndex));
    clearButton.addEventListener("click", () => updateSelectedSlot(ui, (slot) => {
        slot.image = "";
        slot.subfolder = "";
    }, true));
    clearAllButton.addEventListener("click", () => updateSelectedSlot(ui, (slot) => {
        slot.image = "";
        slot.subfolder = "";
        slot.prompt = "";
    }, true));
    lockButton.addEventListener("click", () => updateSelectedSlot(ui, (slot) => {
        slot.lockIdentity = !slot.lockIdentity;
    }, true));
    labelInput.addEventListener("input", () => updateSelectedSlot(ui, (slot) => {
        slot.label = labelInput.value;
    }, false));
    roleSelect.addEventListener("change", () => updateSelectedSlot(ui, (slot) => {
        slot.role = roleSelect.value;
    }, false));
    promptArea.addEventListener("input", () => updateSelectedSlot(ui, (slot) => {
        slot.prompt = promptArea.value;
    }, false));
    fitSelect.addEventListener("change", () => updateSelectedSlot(ui, (slot) => {
        slot.fit = fitSelect.value;
    }, false));
    zoom.input.addEventListener("input", () => updateSelectedSlot(ui, (slot) => {
        slot.zoom = Number(zoom.input.value);
    }, false));
    offsetX.input.addEventListener("input", () => updateSelectedSlot(ui, (slot) => {
        slot.offsetX = Number(offsetX.input.value);
    }, false));
    offsetY.input.addEventListener("input", () => updateSelectedSlot(ui, (slot) => {
        slot.offsetY = Number(offsetY.input.value);
    }, false));
    leftButton.addEventListener("click", () => moveSelected(ui, -1));
    rightButton.addEventListener("click", () => moveSelected(ui, 1));
    copyImageButton.addEventListener("click", () => {
        const slot = selectedSlot(ui);
        if (!slot?.image) {
            ui.showToast("В ячейке нет изображения", true);
            return;
        }
        const target = ui.state.slots.find((item) => !item.image);
        if (!target) {
            ui.showToast("Нет свободных ячеек", true);
            return;
        }
        target.image = slot.image;
        target.subfolder = slot.subfolder;
        target.fit = slot.fit;
        target.zoom = slot.zoom;
        target.offsetX = slot.offsetX;
        target.offsetY = slot.offsetY;
        commitUi(ui, { board: true, inspector: true, library: true });
        ui.showToast("Скопировано в следующую пустую ячейку");
    });
}

function buildRange(min, max, step) {
    const wrap = el("div", "ccs-range-row");
    const input = document.createElement("input");
    input.type = "range";
    input.className = "ccs-range";
    input.min = String(min);
    input.max = String(max);
    input.step = String(step);
    input.value = String(min <= 0 && max >= 0 ? 0 : (min + max) / 2);
    const value = el("div", "ccs-range-value");
    const sync = () => {
        value.textContent = Number(input.value).toFixed(step < 0.1 ? 2 : 1);
    };
    input.addEventListener("input", sync);
    wrap.append(input, value);
    sync();
    return { wrap, input, value };
}

function appendGlobalText(ui, parent, label, key, rows = 4) {
    const area = makeTextarea(rows);
    area.addEventListener("input", () => {
        ui.state[key] = area.value;
        queueStateSync(ui.node, ui.state);
    });
    parent.append(makeField(label, area, true));
    return area;
}

function buildGlobalPane(ui) {
    const pane = ui.globalPane;
    const state = ui.state;

    const identitySection = el("div", "ccs-section");
    identitySection.append(el("div", "ccs-section-label", "Сеттинг персонажа"));
    const titleInput = el("input", "ccs-input");
    const subtitleInput = el("input", "ccs-input");
    titleInput.addEventListener("input", () => {
        ui.state.title = titleInput.value;
        commitUi(ui, { board: true, sync: true });
    });
    subtitleInput.addEventListener("input", () => {
        ui.state.subtitle = subtitleInput.value;
        commitUi(ui, { board: true, sync: true });
    });
    identitySection.append(
        makeField("Название", titleInput),
        makeField("Подзаголовок", subtitleInput),
    );
    const identity = appendGlobalText(ui, identitySection, "Личность / тип сцены", "identity", 3);
    const appearance = appendGlobalText(ui, identitySection, "Внешность / структура сцены", "appearance", 4);
    const outfit = appendGlobalText(ui, identitySection, "Одежда / материалы окружения", "outfit", 4);
    const palette = appendGlobalText(ui, identitySection, "Фиксированная палитра", "palette", 2);

    const styleSection = el("div", "ccs-section");
    styleSection.append(el("div", "ccs-section-label is-teal", "Стиль вывода"));
    const style = appendGlobalText(ui, styleSection, "Единый стиль", "style", 3);
    const negative = appendGlobalText(ui, styleSection, "Негативный промпт", "negativePrompt", 3);

    const layoutSection = el("div", "ccs-section");
    layoutSection.append(el("div", "ccs-section-label", "Макет"));
    const widthInput = el("input", "ccs-input");
    const heightInput = el("input", "ccs-input");
    widthInput.type = "number";
    heightInput.type = "number";
    widthInput.min = "512";
    widthInput.max = "4096";
    heightInput.min = "512";
    heightInput.max = "4096";
    widthInput.step = "16";
    heightInput.step = "16";
    const dimensionWrap = el("div", "ccs-color-row");
    const swapBtn = el("button", "ccs-swap-btn", "⇄");
    swapBtn.type = "button";
    swapBtn.title = "Поменять ширину и высоту";
    swapBtn.addEventListener("click", () => {
        const w = ui.state.width;
        ui.state.width = ui.state.height;
        ui.state.height = w;
        widthInput.value = String(ui.state.width);
        heightInput.value = String(ui.state.height);
        commitUi(ui, { board: true, sync: true, header: true, inspector: true });
    });
    dimensionWrap.append(widthInput, swapBtn, heightInput);
    const writeDimension = () => {
        ui.state.width = roundDimension(widthInput.value);
        ui.state.height = roundDimension(heightInput.value);
        widthInput.value = String(ui.state.width);
        heightInput.value = String(ui.state.height);
        commitUi(ui, { board: true, sync: true, header: true });
    };
    widthInput.addEventListener("change", writeDimension);
    heightInput.addEventListener("change", writeDimension);
    const colorRow = el("div", "ccs-color-row");
    colorRow.append(
        makeColorField(state.background, (value) => {
            ui.state.background = value;
            commitUi(ui, { board: true, sync: true, inspector: true });
        }, "Фон"),
        makeColorField(state.accent, (value) => {
            ui.state.accent = value;
            commitUi(ui, { board: true, sync: true, inspector: true });
        }, "Акцент"),
    );
    const labelSwitch = makeSwitch(Boolean(state.showLabels), (next) => {
        ui.state.showLabels = next;
        commitUi(ui, { board: true, sync: true });
    }, "Показывать подписи ячеек на картинке");
    const labelRow = el("div", "ccs-check-row");
    labelRow.append(el("span", "", "Подписи ячеек"), labelSwitch);
    layoutSection.append(makeField("Размер холста", dimensionWrap), makeField("Фон / акцент", colorRow), labelRow);

    const actionSection = el("div", "ccs-section");
    actionSection.append(el("div", "ccs-section-label", "Действия"));
    const actions = el("div", "ccs-action-grid");
    const resetButton = el("button", "ccs-btn ccs-btn--small", "Сбросить содержимое макета");
    const selectAllIdentity = el("button", "ccs-btn ccs-btn--small", "Все в identity-референс");
    const copyButton = el("button", "ccs-btn ccs-btn--small", "Копировать JSON макета");
    const clearLibraryButton = el("button", "ccs-btn ccs-btn--small ccs-btn--danger", "Очистить библиотеку");
    resetButton.type = "button";
    selectAllIdentity.type = "button";
    copyButton.type = "button";
    clearLibraryButton.type = "button";
    actions.append(resetButton, selectAllIdentity, copyButton, clearLibraryButton);
    actionSection.append(actions);

    pane.append(identitySection, styleSection, layoutSection, actionSection);

    Object.assign(ui, {
        titleInput,
        subtitleInput,
        identityArea: identity,
        appearanceArea: appearance,
        outfitArea: outfit,
        paletteArea: palette,
        styleArea: style,
        negativeArea: negative,
        widthInput,
        heightInput,
        labelSwitch,
    });

    resetButton.addEventListener("click", () => {
        const template = templateFor(ui.state, ui.payload);
        const library = clone(ui.state.library);
        ui.state = defaultState(template, ui.payload);
        ui.state.library = library;
        ui.selectedIndex = 0;
        commitUi(ui, { board: true, inspector: true, library: true, header: true, sync: true });
        ui.showToast("Содержимое макета сброшено");
    });
    selectAllIdentity.addEventListener("click", () => {
        for (const item of ui.state.library) item.useForIdentity = true;
        for (const slot of ui.state.slots) slot.lockIdentity = true;
        queueStateSync(ui.node, ui.state);
        ui.showToast("Все референсы субъекта выбраны");
    });
    copyButton.addEventListener("click", () => copyState(ui));
    clearLibraryButton.addEventListener("click", () => {
        ui.state.library = [];
        queueStateSync(ui.node, ui.state);
        renderLibrary(ui);
        ui.showToast("Библиотека очищена");
    });
}

function selectedSlot(ui) {
    return ui.state.slots[ui.selectedIndex] || null;
}

function updateSelectedSlot(ui, updater, rerenderInspector) {
    const slot = selectedSlot(ui);
    if (!slot) return;
    updater(slot);
    commitUi(ui, { board: true, inspector: rerenderInspector, library: rerenderInspector });
}

function moveSelected(ui, direction) {
    const from = ui.selectedIndex;
    const to = from + direction;
    if (to < 0 || to >= ui.state.slots.length) return;
    moveSlot(ui, from, to);
}

function moveSlot(ui, from, to) {
    if (from === to) return;
    const [slot] = ui.state.slots.splice(from, 1);
    ui.state.slots.splice(to, 0, slot);
    ui.selectedIndex = to;
    commitUi(ui, { board: true, inspector: true, library: true, sync: true });
}

function assignImage(ui, imageIndex, targetIndex) {
    const item = ui.state.library[imageIndex];
    const slot = ui.state.slots[targetIndex];
    if (!item || !slot) return;
    slot.image = item.image;
    slot.subfolder = item.subfolder || "";
    ui.selectedIndex = targetIndex;
    setActiveTab(ui, "cell");
    commitUi(ui, { board: true, inspector: true, library: true, sync: true });
}

function commitUi(ui, options = {}) {
    if (options.board) renderBoard(ui);
    if (options.inspector) syncInspector(ui);
    if (options.library) renderLibrary(ui);
    if (options.header) { syncHeader(ui); renderTemplateStrip(ui); }
    if (options.sync !== false) queueStateSync(ui.node, ui.state);
    syncCellForm(ui);
}

function syncHeader(ui) {
    ui.templateSelect.value = ui.state.templateId;
    ui.dimensions.textContent = formatDimensions(ui.state);
    ui.stageMeta.textContent = `${templateFor(ui.state, ui.payload).name} · ${ui.state.slots.length} яч.`;
    ui.widthInput.value = String(ui.state.width);
    ui.heightInput.value = String(ui.state.height);
    ui.root.classList.toggle("show-labels", Boolean(ui.state.showLabels));
    ui.board.style.setProperty("--ccs-board-accent", ui.state.accent);
}

function syncInspector(ui) {
    syncCellForm(ui);
    syncGlobalForm(ui);
}

function syncCellForm(ui) {
    const slot = selectedSlot(ui);
    ui.updating = true;
    if (!slot) {
        ui.updating = false;
        return;
    }
    const url = imageUrl(slot);
    if (url) {
        ui.previewImage.src = url;
        ui.previewImage.style.display = "block";
        ui.previewEmpty.style.display = "none";
    } else {
        ui.previewImage.removeAttribute("src");
        ui.previewImage.style.display = "none";
        ui.previewEmpty.style.display = "grid";
    }
    if (document.activeElement !== ui.labelInput) ui.labelInput.value = slot.label || "";
    if (document.activeElement !== ui.promptArea) ui.promptArea.value = slot.prompt || "";
    ui.roleSelect.value = slot.role || "custom";
    ui.fitSelect.value = slot.fit || "cover";
    ui.zoomRange.value = String(slot.zoom ?? 1);
    ui.zoomValue.textContent = Number(slot.zoom ?? 1).toFixed(2);
    ui.offsetXRange.value = String(slot.offsetX ?? 0);
    ui.offsetXValue.textContent = Number(slot.offsetX ?? 0).toFixed(2);
    ui.offsetYRange.value = String(slot.offsetY ?? 0);
    ui.offsetYValue.textContent = Number(slot.offsetY ?? 0).toFixed(2);
    ui.lockButton.title = slot.lockIdentity ? "Включено в identity-референс — нажмите, чтобы отключить" : "Не в identity-референсе — нажмите, чтобы включить";
    ui.lockButton.classList.toggle("ccs-btn--accent", Boolean(slot.lockIdentity));
    ui.leftButton.disabled = ui.selectedIndex <= 0;
    ui.rightButton.disabled = ui.selectedIndex >= ui.state.slots.length - 1;
    ui.updating = false;
}

function syncGlobalForm(ui) {
    const state = ui.state;
    ui.updating = true;
    if (document.activeElement !== ui.titleInput) ui.titleInput.value = state.title || "";
    if (document.activeElement !== ui.subtitleInput) ui.subtitleInput.value = state.subtitle || "";
    if (document.activeElement !== ui.identityArea) ui.identityArea.value = state.identity || "";
    if (document.activeElement !== ui.appearanceArea) ui.appearanceArea.value = state.appearance || "";
    if (document.activeElement !== ui.outfitArea) ui.outfitArea.value = state.outfit || "";
    if (document.activeElement !== ui.paletteArea) ui.paletteArea.value = state.palette || "";
    if (document.activeElement !== ui.styleArea) ui.styleArea.value = state.style || "";
    if (document.activeElement !== ui.negativeArea) ui.negativeArea.value = state.negativePrompt || "";
    if (document.activeElement !== ui.widthInput) ui.widthInput.value = String(state.width);
    if (document.activeElement !== ui.heightInput) ui.heightInput.value = String(state.height);
    ui.labelSwitch.classList.toggle("is-on", Boolean(state.showLabels));
    ui.updating = false;
}

function renderTemplateStrip(ui) {
    ui.templateStrip.textContent = "";
    for (const template of ui.payload.templates) {
        const card = el("button", `ccs-template-card${template.id === ui.state.templateId ? " is-active" : ""}`);
        card.type = "button";
        card.append(buildTemplateMini(template));
        const copy = el("div", "ccs-template-copy");
        copy.append(
            el("span", "ccs-template-name", template.name),
            el("span", "ccs-template-count", `${template.cells?.length || 0} яч.`),
        );
        card.append(copy);
        card.addEventListener("click", () => switchTemplate(ui, template.id));
        ui.templateStrip.append(card);
    }
}

function switchTemplate(ui, templateId) {
    const template = ui.payload.templates.find((item) => item.id === templateId);
    if (!template) return;
    ui.state = defaultState(template, ui.payload, ui.state);
    ui.state.width = roundDimension(template.width);
    ui.state.height = roundDimension(template.height);
    ui.selectedIndex = 0;
    commitUi(ui, { board: true, inspector: true, library: true, header: true, sync: true });
    ui.showToast(`Переключено на: ${template.name}`);
}

function renderBoard(ui) {
    const board = ui.board;
    board.textContent = "";
    board.style.setProperty("--ccs-board-accent", ui.state.accent);
    board.classList.toggle("show-labels", Boolean(ui.state.showLabels));

    const rule = el("div", "ccs-board-rule");
    board.append(rule);
    if (ui.state.showLabels) {
        board.append(
            el("div", "ccs-board-title", ui.state.title || "Безымянный персонаж"),
            el("div", "ccs-board-subtitle", ui.state.subtitle || ""),
        );
    }

    const template = templateFor(ui.state, ui.payload);
    template.cells.forEach((cell, index) => {
        const slot = ui.state.slots[index] || slotFromCell(cell, index);
        const isDisabled = slot.enabled === false;
        const cellNode = el("div", `ccs-cell${index === ui.selectedIndex ? " is-selected" : ""}${isDisabled ? " is-disabled" : ""}`);
        cellNode.style.left = `${cell.x * 100}%`;
        cellNode.style.top = `${cell.y * 100}%`;
        cellNode.style.width = `${cell.w * 100}%`;
        cellNode.style.height = `${cell.h * 100}%`;
        cellNode.draggable = true;
        cellNode.dataset.index = String(index);

        const media = el("div", `ccs-cell-media${slot.fit === "contain" ? " is-contain" : ""}`);
        if (slot.image) {
            const image = el("img");
            image.alt = "";
            image.src = imageUrl(slot);
            image.draggable = false;
            image.style.transform = `translate(${Number(slot.offsetX || 0) * 40}%, ${Number(slot.offsetY || 0) * 40}%) scale(${Number(slot.zoom || 1)})${cell.mirror ? " scaleX(-1)" : ""}`;
            media.append(image);
        } else {
            const empty = el("div", "ccs-cell-empty");
            empty.append(el("div", "ccs-cell-empty-plus", "+"), el("div", "ccs-cell-empty-label", slot.label || cell.label));
            media.append(empty);
        }

        const indexBadge = el("div", "ccs-cell-index", String(index + 1).padStart(2, "0"));
        const caption = el("div", "ccs-cell-caption", slot.label || cell.label);
        const quick = el("div", "ccs-cell-quick");
        const toggle = el("button", `ccs-cell-toggle${isDisabled ? " is-off" : ""}`, isDisabled ? "🚫" : "👁");
        const replace = el("button", "", "↻");
        const clear = el("button", "", "×");
        toggle.type = "button";
        replace.type = "button";
        clear.type = "button";
        toggle.title = isDisabled ? "Включить эту ячейку" : "Отключить эту ячейку";
        replace.title = "Заменить изображение";
        clear.title = "Очистить изображение";
        toggle.addEventListener("click", (event) => {
            event.stopPropagation();
            slot.enabled = slot.enabled === false;
            commitUi(ui, { board: true, inspector: true, sync: true });
        });
        replace.addEventListener("click", (event) => {
            event.stopPropagation();
            openFilePicker(ui, index);
        });
        clear.addEventListener("click", (event) => {
            event.stopPropagation();
            slot.image = "";
            slot.subfolder = "";
            ui.selectedIndex = index;
            commitUi(ui, { board: true, inspector: true, library: true, sync: true });
        });
        quick.append(toggle, replace, clear);
        cellNode.append(media, indexBadge, caption, quick);

        cellNode.addEventListener("click", () => {
            ui.selectedIndex = index;
            setActiveTab(ui, "cell");
            for (const item of board.querySelectorAll(".ccs-cell")) item.classList.remove("is-selected");
            cellNode.classList.add("is-selected");
            syncCellForm(ui);
        });
        cellNode.addEventListener("dblclick", () => openFilePicker(ui, index));
        cellNode.addEventListener("dragstart", (event) => {
            event.dataTransfer.effectAllowed = "move";
            event.dataTransfer.setData(SLOT_MIME, String(index));
            event.dataTransfer.setData("text/plain", String(index));
            cellNode.classList.add("is-dragging");
        });
        cellNode.addEventListener("dragend", () => {
            cellNode.classList.remove("is-dragging");
            for (const item of board.querySelectorAll(".ccs-cell")) item.classList.remove("is-drop-target");
        });
        cellNode.addEventListener("dragover", (event) => {
            if (!event.dataTransfer) return;
            event.preventDefault();
            cellNode.classList.add("is-drop-target");
        });
        cellNode.addEventListener("dragleave", () => cellNode.classList.remove("is-drop-target"));
        cellNode.addEventListener("drop", (event) => {
            event.preventDefault();
            cellNode.classList.remove("is-drop-target");
            const slotSource = event.dataTransfer?.getData(SLOT_MIME);
            const imageSource = event.dataTransfer?.getData(IMAGE_MIME);
            if (slotSource !== undefined && slotSource !== "") {
                moveSlot(ui, Number(slotSource), index);
                return;
            }
            if (imageSource !== undefined && imageSource !== "") {
                assignImage(ui, Number(imageSource), index);
            }
        });
        board.append(cellNode);
    });
    requestAnimationFrame(() => updateBoardFrame(ui));
}

function bindBoardResize(ui) {
    if (typeof ResizeObserver === "function") {
        ui.boardObserver = new ResizeObserver(() => updateBoardFrame(ui));
        ui.boardObserver.observe(ui.boardWrap);
    }
}

function updateBoardFrame(ui) {
    const wrap = ui.boardWrap;
    if (!wrap || !ui.board) return;
    const compact = (ui.root?.clientWidth || 0) < 980;
    ui.root?.classList.toggle("is-compact", compact);
    const availableW = Math.max(120, wrap.clientWidth - 24);
    const availableH = Math.max(100, wrap.clientHeight - 24);
    const ratio = Math.max(0.2, Number(ui.state.width) / Math.max(1, Number(ui.state.height)));
    let width = availableW;
    let height = width / ratio;
    if (height > availableH) {
        height = availableH;
        width = height * ratio;
    }
    ui.board.style.width = `${Math.max(80, Math.floor(width))}px`;
    ui.board.style.height = `${Math.max(80, Math.floor(height))}px`;
}

function renderLibrary(ui) {
    ui.libraryMeta.textContent = `${ui.state.library.length} шт.`;
    ui.libraryList.textContent = "";
    if (!ui.state.library.length) {
        ui.libraryList.append(el("div", "ccs-library-empty", "Библиотека пуста"));
        return;
    }
    ui.state.library.forEach((item, index) => {
        const thumb = el("div", "ccs-thumb");
        thumb.draggable = true;
        thumb.title = item.name || item.image;
        const image = el("img");
        image.alt = "";
        image.src = imageUrl(item);
        image.draggable = false;
        const meta = el("div", "ccs-thumb-meta", item.name || item.image.split("/").pop() || item.image);
        const remove = el("button", "ccs-thumb-remove", "×");
        remove.type = "button";
        remove.title = "Удалить из библиотеки";
        remove.addEventListener("click", (event) => {
            event.stopPropagation();
            ui.state.library.splice(index, 1);
            queueStateSync(ui.node, ui.state);
            renderLibrary(ui);
        });
        thumb.append(image, meta, remove);
        thumb.addEventListener("click", () => {
            if (ui.selectedIndex >= 0) assignImage(ui, index, ui.selectedIndex);
        });
        thumb.addEventListener("dragstart", (event) => {
            event.dataTransfer.effectAllowed = "copy";
            event.dataTransfer.setData(IMAGE_MIME, String(index));
            event.dataTransfer.setData("text/plain", String(index));
        });
        ui.libraryList.append(thumb);
    });
}

function openFilePicker(ui, slotIndex) {
    if (slotIndex !== null && slotIndex !== undefined) {
        ui.fileInput.dataset.slotIndex = String(slotIndex);
    } else {
        delete ui.fileInput.dataset.slotIndex;
    }
    ui.fileInput.click();
}

async function uploadFiles(ui, files, targetIndex = null) {
    ui.uploadButton.disabled = true;
    ui.libraryUpload.disabled = true;
    let uploaded = 0;
    const uploadedItems = [];
    try {
        for (const file of files) {
            if (!file?.type?.startsWith("image/")) continue;
            const item = await uploadImageFile(file);
            if (!item) continue;
            const key = `${item.subfolder}\u0000${item.image}`;
            const exists = ui.state.library.some((entry) => `${entry.subfolder}\u0000${entry.image}` === key);
            if (!exists) ui.state.library.push(item);
            uploadedItems.push(item);
            uploaded += 1;
        }
        if (uploaded && targetIndex !== null && Number.isInteger(Number(targetIndex))) {
            const first = uploadedItems[0];
            const key = `${first.subfolder}\u0000${first.image}`;
            const libraryIndex = ui.state.library.findIndex(
                (entry) => `${entry.subfolder}\u0000${entry.image}` === key,
            );
            if (libraryIndex >= 0) assignImage(ui, libraryIndex, Number(targetIndex));
        } else if (uploaded) {
            fillEmptySlots(ui, true);
        }
        renderLibrary(ui);
        syncCellForm(ui);
        queueStateSync(ui.node, ui.state);
        ui.showToast(uploaded ? `Добавлено ${uploaded} ассетов` : "Нет подходящих изображений", !uploaded);
    } catch (error) {
        console.error("[CharacterCardStudio] Upload failed", error);
        ui.showToast("Ошибка загрузки изображения", true);
    } finally {
        ui.uploadButton.disabled = false;
        ui.libraryUpload.disabled = false;
    }
}

async function uploadImageFile(file) {
    const form = new FormData();
    form.append("image", file, file.name);
    form.append("type", "input");
    form.append("overwrite", "false");
    const response = await api.fetchApi("/upload/image", { method: "POST", body: form });
    if (!response.ok) throw new Error(`Upload failed: HTTP ${response.status}`);
    const data = await response.json();
    const name = String(data.name || file.name);
    return {
        image: name,
        subfolder: String(data.subfolder || ""),
        name: name.split("/").pop() || file.name,
        useForIdentity: true,
    };
}

function fillEmptySlots(ui, quiet = false) {
    let libraryIndex = 0;
    let filled = 0;
    for (const slot of ui.state.slots) {
        if (slot.image) continue;
        while (libraryIndex < ui.state.library.length && !ui.state.library[libraryIndex].image) libraryIndex += 1;
        if (libraryIndex >= ui.state.library.length) break;
        const item = ui.state.library[libraryIndex];
        slot.image = item.image;
        slot.subfolder = item.subfolder || "";
        libraryIndex += 1;
        filled += 1;
    }
    commitUi(ui, { board: true, inspector: true, library: true, sync: true });
    if (!quiet) ui.showToast(filled ? `Заполнено ${filled} ячеек` : "Нет пустых ячеек для заполнения", !filled);
}

async function copyState(ui) {
    const text = JSON.stringify(ui.state, null, 2);
    try {
        await navigator.clipboard.writeText(text);
        ui.showToast("JSON макета скопирован");
    } catch (error) {
        const area = document.createElement("textarea");
        area.value = text;
        area.style.position = "fixed";
        area.style.left = "-9999px";
        document.body.append(area);
        area.select();
        try {
            document.execCommand("copy");
            ui.showToast("JSON макета скопирован");
        } catch (copyError) {
            ui.showToast("Не удалось скопировать", true);
        }
        area.remove();
    }
}

function resizeNode(node) {
    const width = Math.max(Number(node.size?.[0]) || 0, 1080);
    const height = Math.max(Number(node.size?.[1]) || 0, 820);
    if (Math.abs(width - (node.size?.[0] || 0)) > 1 || Math.abs(height - (node.size?.[1] || 0)) > 1) {
        node.setSize?.([width, height]);
    }
}

async function setupNode(node) {
    if (!node || node.__ccsSetupStarted) return node.__ccsSetupPromise;
    node.__ccsSetupStarted = true;
    node.__ccsSetupPromise = (async () => {
        await ensureStyle();
        const payload = await loadPayload();
        const state = stateFromWidget(node, payload);
        hideNativeWidgets(node);
        const ui = buildUi(node, payload, state);
        node.__ccsUi = ui;

        if (typeof node.addDOMWidget === "function") {
            const domWidget = node.addDOMWidget("character_card_studio", "character_card_studio", ui.root, {
                serialize: false,
                getMinHeight: () => 760,
                afterResize: () => updateBoardFrame(ui),
            });
            if (domWidget) {
                domWidget.serialize = false;
                domWidget.type = "character_card_studio";
                node.__ccsDomWidget = domWidget;
            }
        }

        resizeNode(node);
        refreshVueWidgets(node);
        refreshNode(node);
        setTimeout(() => {
            updateBoardFrame(ui);
            resizeNode(node);
        }, 0);
        setTimeout(() => {
            updateBoardFrame(ui);
            resizeNode(node);
        }, 350);
        return ui;
    })();
    return node.__ccsSetupPromise;
}

function hideNativeWidgets(node) {
    for (const name of [STATE_WIDGET, WIDTH_WIDGET, HEIGHT_WIDGET]) {
        const widget = widgetOf(node, name);
        markWidgetHidden(widget);
    }
    refreshVueWidgets(node);
}

function reloadStateFromWidget(node, payload) {
    const ui = node.__ccsUi;
    if (!ui) return;
    const next = stateFromWidget(node, payload);
    ui.state = next;
    ui.selectedIndex = Math.max(0, Math.min(ui.selectedIndex, next.slots.length - 1));
    ui.renderAll();
    queueStateSync(node, next);
}

function installNode(nodeType, nodeData) {
    if (nodeData?.name !== NODE_ID) return;
    autoHideWidgets(nodeType, [STATE_WIDGET, WIDTH_WIDGET, HEIGHT_WIDGET]);

    const chain = (name, after) => {
        const original = nodeType.prototype[name];
        nodeType.prototype[name] = function (...args) {
            const result = original?.apply(this, args);
            try {
                after(this, args);
            } catch (error) {
                console.error("[CharacterCardStudio]", error);
            }
            return result;
        };
    };

    chain("onNodeCreated", (node) => {
        setupNode(node);
    });
    chain("onAdded", (node) => {
        setupNode(node);
    });
    chain("onConfigure", (node) => {
        setupNode(node).then(async () => {
            const payload = await loadPayload();
            reloadStateFromWidget(node, payload);
        });
        setTimeout(async () => {
            try {
                const payload = await loadPayload();
                reloadStateFromWidget(node, payload);
            } catch (error) {
                console.error("[CharacterCardStudio] Configure reload failed", error);
            }
        }, 120);
    });
    chain("onResize", (node) => {
        setTimeout(() => {
            updateBoardFrame(node.__ccsUi);
            refreshNode(node);
        }, 0);
    });
}

app.registerExtension({
    name: "AICG3D.CharacterCardStudio",
    setup() {
        ensureStyle();
        loadPayload();
    },
    beforeRegisterNodeDef(nodeType, nodeData) {
        installNode(nodeType, nodeData);
    },
    nodeCreated(node) {
        if (String(node?.comfyClass || node?.type || "") === NODE_ID) setupNode(node);
    },
    loadedGraphNode(node) {
        if (String(node?.comfyClass || node?.type || "") === NODE_ID) setupNode(node);
    },
});
