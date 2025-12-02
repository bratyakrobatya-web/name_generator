import streamlit as st
import pandas as pd
from urllib.parse import urlencode
from datetime import datetime
import re
import html

# ============================================================
# НАСТРОЙКА СТРАНИЦЫ (должна быть первой командой Streamlit)
# ============================================================

st.set_page_config(
    page_title="Генератор нейминга и UTM",
    page_icon="🏷️",
    layout="wide"
)

# ============================================================
# ПОДКЛЮЧЕНИЕ ШРИФТА GOLOS TEXT
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Golos+Text:wght@400;500;600;700&display=swap');

/* Применяем Golos Text только к текстовым элементам */
.stMarkdown p, .stMarkdown li, .stMarkdown span {
    font-family: 'Golos Text', sans-serif;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Golos Text', sans-serif;
}

.stSelectbox label, .stMultiSelect label, .stTextInput label {
    font-family: 'Golos Text', sans-serif;
}

/* Исключение для code блоков */
code, pre, .stCode {
    font-family: 'Courier New', monospace !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# КОНФИГУРАЦИЯ ДАННЫХ (дефолтные значения)
# ============================================================

DEFAULT_STRICT_NAMING = {
    "Продукт": ["adtech-b2b", "adtech-b2c"],
    "Стрим": ["magnitsupergeo", "lpv", "vebinar", "multi", "clickme", "client", "cobrand",
              "omnikanalnost", "brandlift", "vr", "career", "retargeting", "reactiv",
              "adtech", "meetup", "onedayoffer"],
    "Статья расхода": ["vr", "cpa", "nch", "lpv", "career"],
    "Источник": ["yandex", "telegram", "vk", "tgads", "rockettelegram", "gooroo", "vc", "yandexpromopages"],
}

DEFAULT_VARIABLE_NAMING = {
    "Тип кампании": ["cpcepkall", "mk", "inapp", "media", "leadform", "telegram", "feed",
                     "autofeed", "epkrsya", "cpaepkall", "post", "search", "article",
                     "resumes", "common", "vacancy", "banner300x600", "banner100x250",
                     "employer", "text", "video", "banner", "image"],
    "Клиент/гео": ["rostelecomoperatorcallcenter", "astrakhan", "voditel", "b2c", "multigeo",
                   "supergeo", "vit", "special", "remote", "common", "efes", "february",
                   "multycallcentre", "multyvoditel", "podrabotka", "5napravleniy", "bezopyta",
                   "vakhta", "obnoviresume", "kaknenado", "statyasovetirezume", "kartavacanse",
                   "RTK-operatorkc", "RTK-seller", "periodmart", "yandex-storekeeper",
                   "vkusnoitochka", "webinarkobrend"],
    "Таргетинг": ["channel", "users", "bdhh", "msk2km", "joblisting", "bigdata",
                  "segment6-12", "segment12-24", "segment24-60", "chatbot", "key-autotarget",
                  "segmenteconomist", "segment-themes-t1", "segment-channel-t1",
                  "segment1224-themes-t1", "segment1224-channel-t1", "segmentcallcentre",
                  "channel-t1", "channel-t2", "channel-t3", "channel-t4", "channel-themes-t1",
                  "segment612-themes-t1", "segment612-channel-t1", "segmenthh", "segment-t1", "segment-t2"],
    "Цель": ["response", "tresponse", "reg", "regb2c", "install", "reginstall", "leadform",
             "lead", "response-tresponse", "clickredlk-clicksohranitizmeneniyalk", "cuerresponse",
             "zapolnenyekontaktnihdanih", "impressions"],
}

DEFAULT_UTM_PARAMS = {
    "utm_source": ["yandex", "tgads", "clickme", "vk", "gooroo", "tg", "vc", "yandexpromopages"],
    "utm_medium": ["cpc", "cpm", "cpa", "post", "posev", "cpc_yandex_direct"],
    "utm_content": ["ad1", "{ad_id}", "ad2", "t1", "t2", "t3", "v1", "v2", "v3", "i1"],
    "utm_term": ["none", "{keyword}", "kartavacanse", "5obraztsov", "sovetirezume", "kaknenado",
                 "posadkavacancy", "statyaudalenka", "statya5napravleniy", "obshayabezopyta",
                 "obshayaposadkavacancy", "posadkaresume", "obshayapodrabotka", "podrabotka",
                 "vakhta", "remote", "obnoviresume", "multy_callcentre", "seller", "waiter",
                 "multyvoditel", "statyamyths", "rosteloperatorcc", "bezopyta", "RTK-seller",
                 "yandex-storekeeper", "msk", "yandexeda-courier"],
    "utm_vacancy": ["116482958", "114556060", "{utm_vacancy}", "121286221", "33086", "125468351"],
}

# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def validate_url(url):
    """Проверяет валидность URL"""
    pattern = re.compile(
        r'^https?://'  # http:// или https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # домен
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # или IP
        r'(?::\d+)?'  # порт
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(pattern.match(url))

def get_progress(product, stream, expense, source, campaign_types, client_geo, targeting, goal):
    """Вычисляет прогресс заполнения"""
    steps = [
        bool(product),
        bool(stream),
        bool(expense),
        bool(source),
        bool(campaign_types),
        bool(client_geo),
        bool(targeting),
        bool(goal)
    ]
    return sum(steps), len(steps)

def build_preview(product, stream, expense, source, campaign_types, client_geo, targeting, goal):
    """Строит превью нейминга в реальном времени"""
    parts = []
    if product:
        parts.append(product)
    if stream:
        parts.append(stream)
    if expense:
        parts.append(expense)
    if source:
        parts.append(source)
    if campaign_types:
        parts.append("&".join(campaign_types))
    if client_geo:
        parts.append(client_geo)
    if targeting:
        parts.append(targeting)
    if goal:
        parts.append(goal)
    return "_".join(parts) if parts else ""

def clear_all():
    """Очищает все поля"""
    keys_to_clear = ['product', 'stream', 'expense', 'source', 'campaign_types',
                     'client_geo', 'targeting', 'goal', 'base_link', 'utm_source_select',
                     'utm_medium_select', 'utm_campaign', 'utm_content_select',
                     'utm_term_select', 'utm_vacancy_select']
    for key in keys_to_clear:
        if key in st.session_state:
            if key == 'campaign_types':
                st.session_state[key] = []
            else:
                st.session_state[key] = ""
    st.session_state.campaign_name = ""
    st.session_state.final_link = ""

# ============================================================
# STREAMLIT UI
# ============================================================

st.title("🏷️ Генератор нейминга кампании и UTM")

# Справка в раскрывающемся блоке
with st.expander("ℹ️ Справка по использованию"):
    st.markdown("""
    **Этап 1** — Нейминг кампании:
    - Заполняйте поля последовательно (следующее разблокируется после заполнения предыдущего)
    - "Тип кампании" — можно выбрать несколько значений (объединятся через `&`)
    - Нейминг генерируется автоматически — смотрите панель внизу экрана
    - Нажмите **Сохранить в историю** для сохранения результата
    
    **Этап 2** — UTM ссылка:
    - Введите базовую ссылку (должна начинаться с http:// или https://)
    - Выберите UTM параметры (utm_campaign заполнится автоматически из нейминга)
    - Нажмите **GENERATE LINK + UTM**
    
    **Функции:** ➕ Добавить своё значение | 📋 Копировать результат | 📜 История генераций | 📥 Скачать в файл
    
    **Пример нейминга:** `adtech-b2c_lpv_cpa_telegram_mk_astrakhan_users_tresponse`
    
    **TG Ads:** utm_medium=cpc_yandex_direct, utm_vacancy={utm_vacancy}
    """)

# Кнопка сброса в правом верхнем углу
col_title, col_reset = st.columns([5, 1])
with col_reset:
    if st.button("🔄 Сбросить всё", type="secondary", use_container_width=True):
        clear_all()
        st.rerun()

# ============================================================
# ИНИЦИАЛИЗАЦИЯ SESSION STATE
# ============================================================

if 'campaign_name' not in st.session_state:
    st.session_state.campaign_name = ""
if 'final_link' not in st.session_state:
    st.session_state.final_link = ""
if 'history' not in st.session_state:
    st.session_state.history = []  # Список словарей: {datetime, type, value}

# Инициализация кастомных списков (копия дефолтных)
for key in DEFAULT_STRICT_NAMING:
    state_key = f"list_{key}"
    if state_key not in st.session_state:
        st.session_state[state_key] = DEFAULT_STRICT_NAMING[key].copy()

for key in DEFAULT_VARIABLE_NAMING:
    state_key = f"list_{key}"
    if state_key not in st.session_state:
        st.session_state[state_key] = DEFAULT_VARIABLE_NAMING[key].copy()

for key in DEFAULT_UTM_PARAMS:
    state_key = f"list_{key}"
    if state_key not in st.session_state:
        st.session_state[state_key] = DEFAULT_UTM_PARAMS[key].copy()

# ============================================================
# ФУНКЦИЯ ДЛЯ СОЗДАНИЯ ПОЛЯ С ВОЗМОЖНОСТЬЮ ДОБАВЛЕНИЯ
# ============================================================

# Подсказки для полей
FIELD_HINTS = {
    "Продукт": "Основной продукт/направление бизнеса",
    "Стрим": "Поток или категория кампании",
    "Статья расхода": "Категория бюджета/расходов",
    "Источник": "Рекламная платформа/источник трафика",
    "Тип кампании": "Тип рекламной кампании в системе",
    "Клиент/гео": "Клиент, профиль или география",
    "Таргетинг": "Настройки таргетирования аудитории",
    "Цель": "Целевое действие кампании",
    "utm_source": "Источник трафика (google, yandex, telegram...)",
    "utm_medium": "Тип трафика (cpc, cpm, email, social...)",
    "utm_content": "Идентификатор объявления/креатива",
    "utm_term": "Ключевое слово или тема",
    "utm_vacancy": "ID вакансии для отслеживания",
}

def select_with_add(label, list_key, multiselect=False, select_key=None, disabled=False):
    """Создаёт selectbox/multiselect с возможностью добавить своё значение"""
    
    options = st.session_state[f"list_{list_key}"]
    hint = FIELD_HINTS.get(list_key, "")
    
    # Основной селект
    if multiselect:
        selected = st.multiselect(f"Выберите {label.lower()}", options, key=select_key, disabled=disabled, help=hint)
    else:
        selected = st.selectbox(f"Выберите {label.lower()}", [""] + options, key=select_key, disabled=disabled, help=hint)
    
    # Поле для добавления нового значения (всегда активно)
    col_input, col_btn = st.columns([3, 1])
    with col_input:
        new_value = st.text_input(
            "Добавить своё",
            key=f"new_{list_key}",
            placeholder="Добавить значение...",
            label_visibility="collapsed"
        )
    with col_btn:
        if st.button("➕", key=f"add_btn_{list_key}", help="Добавить значение в список"):
            if new_value and new_value.strip():
                new_val = new_value.strip()
                if new_val not in st.session_state[f"list_{list_key}"]:
                    st.session_state[f"list_{list_key}"].append(new_val)
                    st.rerun()
                else:
                    st.toast("Значение уже есть в списке", icon="⚠️")
    
    return selected

# ============================================================
# ЭТАП 1: СОЗДАНИЕ НЕЙМИНГА КАМПАНИИ
# ============================================================

st.header("Этап 1: Создаём нейминг кампании")

# Получаем текущие значения для прогресса и превью
current_product = st.session_state.get('product', '')
current_stream = st.session_state.get('stream', '')
current_expense = st.session_state.get('expense', '')
current_source = st.session_state.get('source', '')
current_campaign_types = st.session_state.get('campaign_types', [])
current_client_geo = st.session_state.get('client_geo', '')
current_targeting = st.session_state.get('targeting', '')
current_goal = st.session_state.get('goal', '')

# Вычисляем прогресс и превью
completed, total = get_progress(
    current_product, current_stream, current_expense, current_source,
    current_campaign_types, current_client_geo, current_targeting, current_goal
)

preview = build_preview(
    current_product, current_stream, current_expense, current_source,
    current_campaign_types, current_client_geo, current_targeting, current_goal
)

# Автоматически обновляем campaign_name из превью
if preview:
    st.session_state.campaign_name = preview

col1, col2 = st.columns(2)

with col1:
    st.subheader("📌 Строгий набор нейминга")
    
    # 1. Продукт - всегда активен
    st.markdown('<p style="font-size: 18px; font-weight: 600; color: #1E5AA8; margin-bottom: 5px;">1. Продукт</p>', unsafe_allow_html=True)
    product = select_with_add("продукт", "Продукт", select_key="product", disabled=False)
    
    # 2. Стрим - активен после выбора Продукта
    step2_disabled = not bool(product)
    if step2_disabled:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #9E9E9E; margin-bottom: 5px;">2. Стрим <span style="font-size: 12px;">🔒</span></p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #1E5AA8; margin-bottom: 5px;">2. Стрим</p>', unsafe_allow_html=True)
    stream = select_with_add("стрим", "Стрим", select_key="stream", disabled=step2_disabled)
    
    # 3. Статья расхода - активен после выбора Стрима
    step3_disabled = not bool(stream)
    if step3_disabled:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #9E9E9E; margin-bottom: 5px;">3. Статья расхода <span style="font-size: 12px;">🔒</span></p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #1E5AA8; margin-bottom: 5px;">3. Статья расхода</p>', unsafe_allow_html=True)
    expense = select_with_add("статью расхода", "Статья расхода", select_key="expense", disabled=step3_disabled)
    
    # 4. Источник - активен после выбора Статьи расхода
    step4_disabled = not bool(expense)
    if step4_disabled:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #9E9E9E; margin-bottom: 5px;">4. Источник <span style="font-size: 12px;">🔒</span></p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #1E5AA8; margin-bottom: 5px;">4. Источник</p>', unsafe_allow_html=True)
    source = select_with_add("источник", "Источник", select_key="source", disabled=step4_disabled)

with col2:
    st.subheader("🔄 Вариативный набор нейминга")
    
    # 5. Тип кампании - активен после выбора Источника
    step5_disabled = not bool(source)
    if step5_disabled:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #9E9E9E; margin-bottom: 5px;">5. Тип кампании <span style="font-weight: 400; font-size: 14px;">(можно несколько)</span> <span style="font-size: 12px;">🔒</span></p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #2E7D32; margin-bottom: 5px;">5. Тип кампании <span style="font-weight: 400; font-size: 14px;">(можно несколько)</span></p>', unsafe_allow_html=True)
    campaign_types = select_with_add("тип(ы) кампании", "Тип кампании", multiselect=True, select_key="campaign_types", disabled=step5_disabled)
    
    # 6. Клиент/гео - активен после выбора Типа кампании
    step6_disabled = not bool(campaign_types)
    if step6_disabled:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #9E9E9E; margin-bottom: 5px;">6. Клиент/профроль/гео <span style="font-size: 12px;">🔒</span></p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #2E7D32; margin-bottom: 5px;">6. Клиент/профроль/гео</p>', unsafe_allow_html=True)
    client_geo = select_with_add("клиента/гео", "Клиент/гео", select_key="client_geo", disabled=step6_disabled)
    
    # 7. Таргетинг - активен после выбора Клиента/гео
    step7_disabled = not bool(client_geo)
    if step7_disabled:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #9E9E9E; margin-bottom: 5px;">7. Таргетинг <span style="font-size: 12px;">🔒</span></p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #2E7D32; margin-bottom: 5px;">7. Таргетинг</p>', unsafe_allow_html=True)
    targeting = select_with_add("таргетинг", "Таргетинг", select_key="targeting", disabled=step7_disabled)
    
    # 8. Цель - активен после выбора Таргетинга
    step8_disabled = not bool(targeting)
    if step8_disabled:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #9E9E9E; margin-bottom: 5px;">8. Цель <span style="font-size: 12px;">🔒</span></p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #2E7D32; margin-bottom: 5px;">8. Цель</p>', unsafe_allow_html=True)
    goal = select_with_add("цель", "Цель", select_key="goal", disabled=step8_disabled)

st.divider()

# ============================================================
# ЭТАП 2: СОЗДАНИЕ UTM
# ============================================================

st.header("Этап 2: Создаём ссылку с UTM")

# Поле для ввода базовой ссылки
base_link = st.text_input("🔗 Введите базовую ссылку",
                          placeholder="https://expert.hh.ru/webinar/...",
                          key="base_link")

# Валидация URL
if base_link and not validate_url(base_link):
    st.warning("⚠️ Ссылка должна начинаться с http:// или https://")

# Проверка готовности нейминга для UTM
naming_ready = bool(st.session_state.campaign_name)

st.subheader("🎯 UTM параметры")

if not naming_ready:
    st.info("⬆️ Сначала сгенерируйте нейминг кампании")

utm_cols = st.columns(3)

with utm_cols[0]:
    # utm_source - активен после генерации нейминга
    if not naming_ready:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #9E9E9E; margin-bottom: 5px;">utm_source <span style="font-size: 12px;">🔒</span></p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #6B4C9A; margin-bottom: 5px;">utm_source</p>', unsafe_allow_html=True)
    utm_source = select_with_add("источник", "utm_source", select_key="utm_source_select", disabled=not naming_ready)
    
    # utm_medium - активен после выбора utm_source
    utm_medium_disabled = not bool(utm_source)
    if utm_medium_disabled:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #9E9E9E; margin-bottom: 5px;">utm_medium <span style="font-size: 12px;">🔒</span></p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #6B4C9A; margin-bottom: 5px;">utm_medium</p>', unsafe_allow_html=True)
    utm_medium = select_with_add("канал", "utm_medium", select_key="utm_medium_select", disabled=utm_medium_disabled)

with utm_cols[1]:
    # utm_campaign - автозаполнение, всегда активен после utm_medium (не блокирует другие)
    utm_campaign_disabled = not bool(utm_medium)
    if utm_campaign_disabled:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #9E9E9E; margin-bottom: 5px;">utm_campaign <span style="font-size: 12px;">🔒</span></p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #6B4C9A; margin-bottom: 5px;">utm_campaign <span style="font-size: 12px; color: #888;">(авто)</span></p>', unsafe_allow_html=True)
    utm_campaign = st.text_input("Кампания",
                                 value=st.session_state.campaign_name,
                                 key="utm_campaign",
                                 help="Автоматически заполняется из нейминга выше",
                                 disabled=utm_campaign_disabled)
    
    # utm_content - активен после utm_medium (не зависит от utm_campaign)
    utm_content_disabled = not bool(utm_medium)
    if utm_content_disabled:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #9E9E9E; margin-bottom: 5px;">utm_content <span style="font-size: 12px;">🔒</span></p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #6B4C9A; margin-bottom: 5px;">utm_content</p>', unsafe_allow_html=True)
    utm_content = select_with_add("контент", "utm_content", select_key="utm_content_select", disabled=utm_content_disabled)

with utm_cols[2]:
    # utm_term - активен после utm_medium
    utm_term_disabled = not bool(utm_medium)
    if utm_term_disabled:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #9E9E9E; margin-bottom: 5px;">utm_term <span style="font-size: 12px;">🔒</span></p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #6B4C9A; margin-bottom: 5px;">utm_term</p>', unsafe_allow_html=True)
    utm_term = select_with_add("ключевое слово", "utm_term", select_key="utm_term_select", disabled=utm_term_disabled)
    
    # utm_vacancy - активен после utm_medium
    utm_vacancy_disabled = not bool(utm_medium)
    if utm_vacancy_disabled:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #9E9E9E; margin-bottom: 5px;">utm_vacancy <span style="font-size: 12px;">🔒</span></p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #6B4C9A; margin-bottom: 5px;">utm_vacancy</p>', unsafe_allow_html=True)
    utm_vacancy = select_with_add("ID вакансии", "utm_vacancy", select_key="utm_vacancy_select", disabled=utm_vacancy_disabled)

st.divider()

# Отступ внизу страницы чтобы контент не перекрывался фиксированной панелью
st.markdown("<div style='height: 160px;'></div>", unsafe_allow_html=True)

# ============================================================
# ФИКСИРОВАННАЯ ПАНЕЛЬ ВНИЗУ
# ============================================================

preview_display = html.escape(preview) if preview else "Заполните поля выше..."
naming_color = "#00ff88" if preview else "#888"

# Формируем превью UTM ссылки
current_base_link = st.session_state.get('base_link', '')
current_utm_source = st.session_state.get('utm_source_select', '')
current_utm_medium = st.session_state.get('utm_medium_select', '')
current_utm_campaign = st.session_state.get('utm_campaign', '') or preview
current_utm_content = st.session_state.get('utm_content_select', '')
current_utm_term = st.session_state.get('utm_term_select', '')
current_utm_vacancy = st.session_state.get('utm_vacancy_select', '')

# Собираем UTM строку для превью
utm_parts = []
if current_utm_source:
    utm_parts.append(f"utm_source={current_utm_source}")
if current_utm_medium:
    utm_parts.append(f"utm_medium={current_utm_medium}")
if current_utm_campaign:
    utm_parts.append(f"utm_campaign={current_utm_campaign}")
if current_utm_content:
    utm_parts.append(f"utm_content={current_utm_content}")
if current_utm_term:
    utm_parts.append(f"utm_term={current_utm_term}")
if current_utm_vacancy:
    utm_parts.append(f"utm_vacancy={current_utm_vacancy}")

utm_preview = ""
if current_base_link and utm_parts:
    separator = "&" if "?" in current_base_link else "?"
    utm_preview = f"{current_base_link}{separator}{'&'.join(utm_parts)}"
elif current_base_link:
    utm_preview = current_base_link
elif utm_parts:
    utm_preview = f"?{'&'.join(utm_parts)}"

utm_display = html.escape(utm_preview) if utm_preview else "Введите ссылку и UTM параметры..."
utm_color = "#64B5F6" if utm_preview else "#888"

# CSS для фиксированной панели и JavaScript для копирования
st.markdown(f'''
<style>
.fixed-panel {{
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    padding: 18px 30px;
    box-shadow: 0 -6px 30px rgba(0,0,0,0.4);
    z-index: 9999;
    border-top: 4px solid #4CAF50;
}}
.panel-inner {{
    max-width: 1600px;
    margin: 0 auto;
}}
.panel-row {{
    display: flex;
    align-items: center;
    margin-bottom: 12px;
    gap: 15px;
}}
.panel-row:last-child {{
    margin-bottom: 0;
}}
.panel-label {{
    color: #ccc;
    font-size: 14px;
    min-width: 80px;
    font-weight: 600;
}}
.panel-code {{
    background: #2d2d44;
    padding: 12px 18px;
    border-radius: 6px;
    font-size: 16px;
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-family: monospace;
}}
.copy-btn {{
    min-width: 160px;
    padding: 14px 28px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 16px;
    font-weight: 600;
    border: none;
    color: #fff;
    transition: all 0.2s;
}}
.copy-btn:hover {{
    transform: scale(1.03);
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}}
.copy-btn-green {{
    background: #4CAF50;
}}
.copy-btn-green:hover {{
    background: #45a049;
}}
.copy-btn-blue {{
    background: #2196F3;
}}
.copy-btn-blue:hover {{
    background: #1976D2;
}}
.copy-btn-disabled {{
    background: #555;
    opacity: 0.5;
    cursor: not-allowed;
}}
</style>

<script>
function copyToClipboard(text, buttonId) {{
    var textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.left = '-9999px';
    document.body.appendChild(textarea);
    textarea.select();
    try {{
        document.execCommand('copy');
        var btn = document.getElementById(buttonId);
        if (btn) {{
            btn.innerText = '✓ Скопировано';
            setTimeout(function() {{
                btn.innerText = '📋 Копировать';
            }}, 1500);
        }}
    }} catch (err) {{
        console.error('Ошибка копирования:', err);
    }} finally {{
        document.body.removeChild(textarea);
    }}
}}
</script>

<div class="fixed-panel">
    <div class="panel-inner">
        <div class="panel-row">
            <span class="panel-label">Нейминг:</span>
            <code class="panel-code" style="color:{naming_color};">{preview_display}</code>
            {"<button id='btnNaming' class='copy-btn copy-btn-green' onclick='copyToClipboard(`" + preview + "`, `btnNaming`)'>📋 Копировать</button>" if preview else "<div class='copy-btn copy-btn-disabled'>📋 Копировать</div>"}
        </div>
        <div class="panel-row">
            <span class="panel-label">UTM:</span>
            <code class="panel-code" style="color:{utm_color};">{utm_display}</code>
            {"<button id='btnUtm' class='copy-btn copy-btn-blue' onclick='copyToClipboard(`" + utm_preview + "`, `btnUtm`)'>📋 Копировать</button>" if utm_preview else "<div class='copy-btn copy-btn-disabled'>📋 Копировать</div>"}
        </div>
    </div>
</div>
''', unsafe_allow_html=True)
