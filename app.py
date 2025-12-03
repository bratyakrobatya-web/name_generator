import streamlit as st
import pandas as pd
from urllib.parse import urlencode
from datetime import datetime
import re

# ============================================================
# НАСТРОЙКА СТРАНИЦЫ
# ============================================================

st.set_page_config(
    page_title="Генератор нейминга и UTM", 
    page_icon="🏷️", 
    layout="wide"
)

# ============================================================
# CSS СТИЛИ
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Golos+Text:wght@400;500;600;700&display=swap');

/* Применяем Golos Text */
.stMarkdown p, .stMarkdown li, .stMarkdown span {
    font-family: 'Golos Text', sans-serif;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Golos Text', sans-serif;
}

.stSelectbox label, .stMultiSelect label, .stTextInput label, .stRadio label, .stCheckbox label {
    font-family: 'Golos Text', sans-serif;
}

code, pre, .stCode {
    font-family: 'Courier New', monospace !important;
}

/* Компактные отступы */
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

/* КОМПАКТНЫЕ КНОПКИ */
.stButton button {
    margin: 3px;
    padding: 6px 12px;
    font-size: 13px;
    min-height: 36px;
    max-height: 36px;
}

/* Заголовки полей */
.field-label {
    font-size: 17px;
    font-weight: 700;
    margin-bottom: 10px;
    color: #1E5AA8;
    display: flex;
    align-items: center;
    gap: 8px;
}

.field-label-disabled {
    color: #9E9E9E;
}

/* Нумерация в кружках */
.field-number {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #1E5AA8;
    color: white;
    width: 26px;
    height: 26px;
    border-radius: 50%;
    font-weight: 700;
    font-size: 14px;
    flex-shrink: 0;
}

.field-number-disabled {
    background: #9E9E9E;
}

/* Прогресс-бар */
.progress-container {
    width: 100%;
    height: 6px;
    background: #e0e0e0;
    border-radius: 3px;
    margin-bottom: 20px;
    overflow: hidden;
}

.progress-bar {
    height: 6px;
    background: linear-gradient(90deg, #4CAF50, #2196F3);
    border-radius: 3px;
    transition: width 0.3s ease;
}

/* СТИЛИ САЙДБАРА */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
}

[data-testid="stSidebar"] .stMarkdown h3 {
    color: #ffffff;
    font-weight: 700;
    font-size: 20px;
}

[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown strong {
    color: #cccccc;
    font-size: 14px;
    font-weight: 600;
}

/* Код блоки в сайдбаре с красной окантовкой */
[data-testid="stSidebar"] code {
    background: #0d0d1a !important;
    border: 2px solid #ff3b3b !important;
    border-radius: 6px !important;
    padding: 12px !important;
    color: #00ff88 !important;
    font-family: 'Courier New', monospace !important;
    font-size: 13px !important;
    display: block !important;
    white-space: pre-wrap !important;
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
    max-width: 100% !important;
}

/* Убираем белый контейнер вокруг code в сайдбаре */
[data-testid="stSidebar"] [data-testid="stCodeBlock"] {
    background: transparent !important;
    padding: 0 !important;
}

[data-testid="stSidebar"] .stCodeBlock {
    background: transparent !important;
}

[data-testid="stSidebar"] pre {
    background: #0d0d1a !important;
    border: 2px solid #ff3b3b !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Красный текст для UTM ссылки */
[data-testid="stSidebar"] .utm-code code {
    color: #ff6b6b !important;
}

/* Разделитель в сайдбаре */
[data-testid="stSidebar"] hr {
    border-color: #333 !important;
    margin: 15px 0 !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# КОНФИГУРАЦИЯ ДАННЫХ
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
    pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(pattern.match(url))

def build_preview(product, stream, expense, source, campaign_types, client_geo, targeting, goal):
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

# ============================================================
# ИНИЦИАЛИЗАЦИЯ SESSION STATE
# ============================================================

if 'campaign_name' not in st.session_state:
    st.session_state.campaign_name = ""
if 'product' not in st.session_state:
    st.session_state.product = ""
if 'stream' not in st.session_state:
    st.session_state.stream = ""
if 'expense' not in st.session_state:
    st.session_state.expense = ""
if 'source' not in st.session_state:
    st.session_state.source = ""
if 'campaign_types' not in st.session_state:
    st.session_state.campaign_types = []
if 'client_geo' not in st.session_state:
    st.session_state.client_geo = ""
if 'targeting' not in st.session_state:
    st.session_state.targeting = ""
if 'goal' not in st.session_state:
    st.session_state.goal = ""

# ============================================================
# UI: ФУНКЦИИ ДЛЯ ПОЛЕЙ
# ============================================================

def render_field_header(label, field_number, disabled=False):
    number_class = "field-number-disabled" if disabled else "field-number"
    label_class = "field-label-disabled" if disabled else "field-label"
    lock_icon = " 🔒" if disabled else ""
    
    st.markdown(f'''
    <div class="{label_class}">
        <span class="{number_class}">{field_number}</span>
        <span>{label}{lock_icon}</span>
    </div>
    ''', unsafe_allow_html=True)

def render_button_field(label, field_number, options, state_key, disabled=False, columns=4):
    col_header, col_add = st.columns([6, 1])
    with col_header:
        render_field_header(label, field_number, disabled)
    with col_add:
        if not disabled and field_number:  # Показываем ➕ только для нейминга (где есть field_number)
            if st.button("➕", key=f"add_btn_{state_key}", help="Добавить своё значение", use_container_width=True):
                st.session_state[f"show_add_{state_key}"] = True
    
    if disabled:
        st.info("🔒 Заполните предыдущее поле")
        return
    
    if st.session_state.get(f"show_add_{state_key}", False):
        col_input, col_btn_add, col_btn_cancel = st.columns([4, 1, 1])
        with col_input:
            new_val = st.text_input("Новое значение:", key=f"new_input_{state_key}", placeholder="Введите значение...", label_visibility="collapsed")
        with col_btn_add:
            if st.button("✓", key=f"confirm_{state_key}", help="Добавить", use_container_width=True, type="primary"):
                if new_val and new_val.strip():
                    if new_val.strip() not in options:
                        options.append(new_val.strip())
                        st.session_state[f"show_add_{state_key}"] = False
                        st.rerun()
                    else:
                        st.toast("Значение уже есть в списке", icon="⚠️")
        with col_btn_cancel:
            if st.button("✗", key=f"cancel_{state_key}", help="Отмена", use_container_width=True):
                st.session_state[f"show_add_{state_key}"] = False
                st.rerun()
    
    cols = st.columns(columns)
    current_value = st.session_state.get(state_key, "")
    
    for i, option in enumerate(options):
        with cols[i % columns]:
            button_type = "primary" if option == current_value else "secondary"
            if st.button(option, key=f"{state_key}_{option}", type=button_type, use_container_width=True):
                st.session_state[state_key] = option
                st.rerun()

def render_multiselect_field(label, field_number, options, state_key, disabled=False, columns=4):
    col_header, col_add = st.columns([6, 1])
    with col_header:
        render_field_header(label, field_number, disabled)
    with col_add:
        if not disabled:
            if st.button("➕", key=f"add_btn_{state_key}", help="Добавить своё значение", use_container_width=True):
                st.session_state[f"show_add_{state_key}"] = True
    
    if disabled:
        st.info("🔒 Заполните предыдущее поле")
        return
    
    if st.session_state.get(f"show_add_{state_key}", False):
        col_input, col_btn_add, col_btn_cancel = st.columns([4, 1, 1])
        with col_input:
            new_val = st.text_input("Новое значение:", key=f"new_input_{state_key}", placeholder="Введите значение...", label_visibility="collapsed")
        with col_btn_add:
            if st.button("✓", key=f"confirm_{state_key}", help="Добавить", use_container_width=True, type="primary"):
                if new_val and new_val.strip():
                    if new_val.strip() not in options:
                        options.append(new_val.strip())
                        st.session_state[f"show_add_{state_key}"] = False
                        st.rerun()
                    else:
                        st.toast("Значение уже есть в списке", icon="⚠️")
        with col_btn_cancel:
            if st.button("✗", key=f"cancel_{state_key}", help="Отмена", use_container_width=True):
                st.session_state[f"show_add_{state_key}"] = False
                st.rerun()
    
    cols = st.columns(columns)
    current_values = st.session_state.get(state_key, [])
    
    for i, option in enumerate(options):
        with cols[i % columns]:
            button_type = "primary" if option in current_values else "secondary"
            if st.button(option, key=f"{state_key}_toggle_{option}", type=button_type, use_container_width=True):
                if option in current_values:
                    current_values.remove(option)
                else:
                    current_values.append(option)
                st.session_state[state_key] = current_values
                st.rerun()

def render_dropdown_with_add(label, options, state_key, disabled=False):
    col_label, col_add = st.columns([6, 1])
    with col_label:
        if disabled:
            st.markdown(f'<p class="field-label field-label-disabled">{label} 🔒</p>', unsafe_allow_html=True)
        else:
            st.markdown(f'<p class="field-label">{label}</p>', unsafe_allow_html=True)
    with col_add:
        if not disabled:
            if st.button("➕", key=f"add_btn_{state_key}", help="Добавить своё значение", use_container_width=True):
                st.session_state[f"show_add_{state_key}"] = True
    
    if st.session_state.get(f"show_add_{state_key}", False):
        col_input, col_btn_add, col_btn_cancel = st.columns([4, 1, 1])
        with col_input:
            new_val = st.text_input("Новое значение:", key=f"new_input_{state_key}", placeholder="Введите значение...", label_visibility="collapsed")
        with col_btn_add:
            if st.button("✓", key=f"confirm_{state_key}", help="Добавить", use_container_width=True, type="primary"):
                if new_val and new_val.strip():
                    if new_val.strip() not in options:
                        options.append(new_val.strip())
                        st.session_state[state_key] = new_val.strip()
                        st.session_state[f"show_add_{state_key}"] = False
                        st.rerun()
                    else:
                        st.toast("Значение уже есть в списке", icon="⚠️")
        with col_btn_cancel:
            if st.button("✗", key=f"cancel_{state_key}", help="Отмена", use_container_width=True):
                st.session_state[f"show_add_{state_key}"] = False
                st.rerun()
    
    current_value = st.session_state.get(state_key, "")
    selected = st.selectbox(
        label,
        [""] + options,
        key=f"{state_key}_dropdown",
        index=0 if not current_value else (options.index(current_value) + 1 if current_value in options else 0),
        disabled=disabled,
        label_visibility="collapsed"
    )
    
    if selected != current_value:
        st.session_state[state_key] = selected
        st.rerun()

# ============================================================
# ГЛАВНЫЙ UI
# ============================================================

st.title("🏷️ Генератор нейминга кампании и UTM")

# Кнопка сброса
col_title, col_reset = st.columns([5, 1])
with col_reset:
    if st.button("🔄 Сбросить всё", type="secondary", use_container_width=True):
        clear_all()
        st.rerun()

# Получаем текущие значения
current_product = st.session_state.get('product', '')
current_stream = st.session_state.get('stream', '')
current_expense = st.session_state.get('expense', '')
current_source = st.session_state.get('source', '')
current_campaign_types = st.session_state.get('campaign_types', [])
current_client_geo = st.session_state.get('client_geo', '')
current_targeting = st.session_state.get('targeting', '')
current_goal = st.session_state.get('goal', '')

# Прогресс-бар
completed_steps = sum([
    bool(current_product),
    bool(current_stream),
    bool(current_expense),
    bool(current_source),
    bool(current_campaign_types),
    bool(current_client_geo),
    bool(current_targeting),
    bool(current_goal)
])
total_steps = 8
progress_percent = (completed_steps / total_steps) * 100

st.markdown(f'''
<div class="progress-container">
    <div class="progress-bar" style="width: {progress_percent}%"></div>
</div>
<p style="text-align: center; color: #666; font-size: 13px; margin-top: -10px; margin-bottom: 15px;">
    {completed_steps} из {total_steps} завершено
</p>
''', unsafe_allow_html=True)

# ============================================================
# ЭТАП 1: НЕЙМИНГ
# ============================================================

st.header("📌 Этап 1: Нейминг кампании")

# ПОЛЯ НЕЙМИНГА
render_button_field("Продукт", "1", DEFAULT_STRICT_NAMING["Продукт"], "product", columns=2)

step2_disabled = not bool(current_product)
render_button_field("Стрим", "2", DEFAULT_STRICT_NAMING["Стрим"], "stream", disabled=step2_disabled, columns=4)

step3_disabled = not bool(current_stream)
render_button_field("Статья расхода", "3", DEFAULT_STRICT_NAMING["Статья расхода"], "expense", disabled=step3_disabled, columns=5)

step4_disabled = not bool(current_expense)
render_button_field("Источник", "4", DEFAULT_STRICT_NAMING["Источник"], "source", disabled=step4_disabled, columns=4)

step5_disabled = not bool(current_source)
render_multiselect_field("Тип кампании (можно несколько)", "5", DEFAULT_VARIABLE_NAMING["Тип кампании"], "campaign_types", disabled=step5_disabled, columns=4)

step6_disabled = not bool(current_campaign_types)
render_button_field("Клиент/профиль/гео", "6", DEFAULT_VARIABLE_NAMING["Клиент/гео"], "client_geo", disabled=step6_disabled, columns=5)

step7_disabled = not bool(current_client_geo)
render_button_field("Таргетинг", "7", DEFAULT_VARIABLE_NAMING["Таргетинг"], "targeting", disabled=step7_disabled, columns=5)

step8_disabled = not bool(current_targeting)
render_button_field("Цель", "8", DEFAULT_VARIABLE_NAMING["Цель"], "goal", disabled=step8_disabled, columns=4)

st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

# ============================================================
# ЭТАП 2: UTM
# ============================================================

st.header("🎯 Этап 2: UTM ссылка")

# Базовая ссылка
st.markdown("### 🔗 Базовая ссылка")
st.info("👇 **Вставьте сюда URL страницы** (должна начинаться с `https://`)")

base_link = st.text_input(
    "Базовая ссылка", 
    placeholder="https://expert.hh.ru/webinar/kobrending",
    key="base_link",
    label_visibility="collapsed"
)

if base_link:
    if validate_url(base_link):
        st.success("✓ Ссылка корректна")
    else:
        st.error("❌ Ссылка должна начинаться с http:// или https://")

st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

# Строим превью нейминга
preview = build_preview(
    current_product, current_stream, current_expense, current_source,
    current_campaign_types, current_client_geo, current_targeting, current_goal
)

if preview:
    st.session_state.campaign_name = preview

naming_ready = bool(preview)

st.subheader("UTM параметры")

if not naming_ready:
    st.info("⬆️ Сначала сгенерируйте нейминг кампании")

# utm_source
utm_source_disabled = not naming_ready
st.markdown('<p class="field-label">utm_source</p>' if not utm_source_disabled else '<p class="field-label field-label-disabled">utm_source 🔒</p>', unsafe_allow_html=True)
if not utm_source_disabled:
    render_button_field("", "", DEFAULT_UTM_PARAMS["utm_source"], "utm_source_select", columns=4)
else:
    st.info("🔒 Заполните нейминг")

# utm_medium
current_utm_source = st.session_state.get('utm_source_select', '')
utm_medium_disabled = not bool(current_utm_source)
st.markdown('<p class="field-label">utm_medium</p>' if not utm_medium_disabled else '<p class="field-label field-label-disabled">utm_medium 🔒</p>', unsafe_allow_html=True)
if not utm_medium_disabled:
    render_button_field("", "", DEFAULT_UTM_PARAMS["utm_medium"], "utm_medium_select", columns=3)
else:
    st.info("🔒 Выберите utm_source")

# utm_campaign
current_utm_medium = st.session_state.get('utm_medium_select', '')
utm_campaign_disabled = not bool(current_utm_medium)

if not utm_campaign_disabled:
    st.markdown('<div class="field-label"><span>utm_campaign <span style="color: #888; font-weight: 400;">(автозаполнение)</span></span></div>', unsafe_allow_html=True)
    utm_campaign = st.text_input(
        "Кампания", 
        value=preview,
        key="utm_campaign",
        disabled=False,
        label_visibility="collapsed"
    )
else:
    st.markdown('<div class="field-label field-label-disabled"><span>utm_campaign (автозаполнение) 🔒</span></div>', unsafe_allow_html=True)
    st.info("🔒 Заполните utm_medium")

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

# utm_content, utm_term, utm_vacancy
utm_other_disabled = not bool(current_utm_medium)

col_utm1, col_utm2, col_utm3 = st.columns(3)

with col_utm1:
    render_dropdown_with_add("utm_content", DEFAULT_UTM_PARAMS["utm_content"], "utm_content_select", disabled=utm_other_disabled)

with col_utm2:
    render_dropdown_with_add("utm_term", DEFAULT_UTM_PARAMS["utm_term"], "utm_term_select", disabled=utm_other_disabled)

with col_utm3:
    render_dropdown_with_add("utm_vacancy", DEFAULT_UTM_PARAMS["utm_vacancy"], "utm_vacancy_select", disabled=utm_other_disabled)

# ============================================================
# SIDEBAR: ПРЕВЬЮ РЕЗУЛЬТАТОВ
# ============================================================

import streamlit.components.v1 as components

with st.sidebar:
    st.markdown("### 📋 Результат")
    
    # Получаем все значения
    current_base_link = st.session_state.get('base_link', '')
    current_utm_source = st.session_state.get('utm_source_select', '')
    current_utm_medium = st.session_state.get('utm_medium_select', '')
    current_utm_campaign = st.session_state.get('utm_campaign', '') or preview
    current_utm_content = st.session_state.get('utm_content_select', '')
    current_utm_term = st.session_state.get('utm_term_select', '')
    current_utm_vacancy = st.session_state.get('utm_vacancy_select', '')
    
    # Собираем UTM строку
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
    
    # Отображение
    preview_display = preview if preview else "Заполните поля..."
    utm_display = utm_preview if utm_preview else "Введите ссылку и UTM..."
    
    # Нейминг (зеленый)
    st.markdown("**Нейминг:**")
    st.code(preview_display, language=None)
    
    if preview:
        escaped_naming = preview.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"').replace('\n', '').replace('\r', '')
        
        btn_html_naming = f'''
        <html><head><style>
        * {{ margin: 0; padding: 0; }}
        body {{ background: transparent; }}
        .copy-btn {{
            width: 100%;
            padding: 10px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            border: none;
            color: #fff;
            background: #4CAF50;
            transition: all 0.2s;
            margin-bottom: 10px;
        }}
        .copy-btn:hover {{ background: #45a049; transform: scale(1.02); }}
        </style></head><body>
        <button class="copy-btn" onclick="
            navigator.clipboard.writeText('{escaped_naming}').then(function() {{
                document.querySelector('.copy-btn').innerText = '✓ Скопировано!';
                setTimeout(function() {{ document.querySelector('.copy-btn').innerText = '📋 Копировать нейминг'; }}, 1500);
            }}).catch(function() {{
                var ta = document.createElement('textarea');
                ta.value = '{escaped_naming}';
                ta.style.position = 'fixed';
                ta.style.left = '-9999px';
                document.body.appendChild(ta);
                ta.select();
                document.execCommand('copy');
                document.body.removeChild(ta);
                document.querySelector('.copy-btn').innerText = '✓ Скопировано!';
                setTimeout(function() {{ document.querySelector('.copy-btn').innerText = '📋 Копировать нейминг'; }}, 1500);
            }});
        ">📋 Копировать нейминг</button>
        </body></html>
        '''
        components.html(btn_html_naming, height=50)
    
    st.markdown("---")
    
    # UTM (красный)
    st.markdown("**UTM ссылка:**")
    st.markdown('<div class="utm-code">', unsafe_allow_html=True)
    st.code(utm_display, language=None)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if utm_preview:
        escaped_utm = utm_preview.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"').replace('\n', '').replace('\r', '')
        
        btn_html_utm = f'''
        <html><head><style>
        * {{ margin: 0; padding: 0; }}
        body {{ background: transparent; }}
        .copy-btn {{
            width: 100%;
            padding: 10px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            border: none;
            color: #fff;
            background: #2196F3;
            transition: all 0.2s;
        }}
        .copy-btn:hover {{ background: #1976D2; transform: scale(1.02); }}
        </style></head><body>
        <button class="copy-btn" onclick="
            navigator.clipboard.writeText('{escaped_utm}').then(function() {{
                document.querySelector('.copy-btn').innerText = '✓ Скопировано!';
                setTimeout(function() {{ document.querySelector('.copy-btn').innerText = '📋 Копировать UTM'; }}, 1500);
            }}).catch(function() {{
                var ta = document.createElement('textarea');
                ta.value = '{escaped_utm}';
                ta.style.position = 'fixed';
                ta.style.left = '-9999px';
                document.body.appendChild(ta);
                ta.select();
                document.execCommand('copy');
                document.body.removeChild(ta);
                document.querySelector('.copy-btn').innerText = '✓ Скопировано!';
                setTimeout(function() {{ document.querySelector('.copy-btn').innerText = '📋 Копировать UTM'; }}, 1500);
            }});
        ">📋 Копировать UTM</button>
        </body></html>
        '''
        components.html(btn_html_utm, height=50)
