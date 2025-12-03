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
# ПОДКЛЮЧЕНИЕ ШРИФТА GOLOS TEXT + КОМПАКТНЫЕ СТИЛИ
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

.stSelectbox label, .stMultiSelect label, .stTextInput label, .stRadio label {
    font-family: 'Golos Text', sans-serif;
}

code, pre, .stCode {
    font-family: 'Courier New', monospace !important;
}

/* Компактные отступы */
.block-container {
    padding-top: 2rem;
    padding-bottom: 8rem;
}

/* Уменьшаем отступы между элементами */
.stButton button {
    margin: 2px;
    padding: 8px 16px;
    font-size: 14px;
}

/* Стили для кнопок-чипсов */
.chip-button {
    display: inline-block;
    margin: 4px;
}

/* Секции полей */
.field-section {
    margin-bottom: 1.5rem;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 8px;
}

.field-label {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 8px;
    color: #1E5AA8;
}

.field-label-disabled {
    color: #9E9E9E;
}

/* Фиксированная панель */
.fixed-panel {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    padding: 18px 30px;
    box-shadow: 0 -6px 30px rgba(0,0,0,0.4);
    z-index: 9999;
    border-top: 4px solid #4CAF50;
}

.panel-inner {
    max-width: 1600px;
    margin: 0 auto;
}

.panel-row {
    display: flex;
    align-items: center;
    margin-bottom: 12px;
    gap: 15px;
}

.panel-row:last-child {
    margin-bottom: 0;
}

.panel-label {
    color: #ccc;
    font-size: 14px;
    min-width: 80px;
    font-weight: 600;
}

.panel-code {
    background: #2d2d44;
    padding: 12px 18px;
    border-radius: 6px;
    font-size: 15px;
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-family: 'Courier New', monospace;
}

.btn-placeholder {
    min-width: 160px;
    height: 52px;
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

# Избранные значения (топ-5 для длинных списков)
FAVORITES = {
    "Клиент/гео": ["astrakhan", "b2c", "multigeo", "supergeo", "voditel"],
    "Таргетинг": ["users", "channel", "bigdata", "segment6-12", "bdhh"],
}

# Умные дефолты: source → utm параметры
SMART_DEFAULTS = {
    "telegram": {"utm_source": "tgads", "utm_medium": "cpc_yandex_direct"},
    "tgads": {"utm_source": "tgads", "utm_medium": "cpc_yandex_direct"},
    "yandex": {"utm_source": "yandex", "utm_medium": "cpc"},
    "vk": {"utm_source": "vk", "utm_medium": "cpc"},
}

# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def validate_url(url):
    """Проверяет валидность URL"""
    pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(pattern.match(url))

def build_preview(product, stream, expense, source, campaign_types, client_geo, targeting, goal):
    """Строит превью нейминга"""
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

def apply_smart_defaults(source):
    """Применяет умные дефолты для UTM на основе источника"""
    if source in SMART_DEFAULTS:
        defaults = SMART_DEFAULTS[source]
        if 'utm_source_select' not in st.session_state or not st.session_state.utm_source_select:
            st.session_state.utm_source_select = defaults.get('utm_source', '')
        if 'utm_medium_select' not in st.session_state or not st.session_state.utm_medium_select:
            st.session_state.utm_medium_select = defaults.get('utm_medium', '')

# ============================================================
# ИНИЦИАЛИЗАЦИЯ SESSION STATE
# ============================================================

if 'campaign_name' not in st.session_state:
    st.session_state.campaign_name = ""
if 'final_link' not in st.session_state:
    st.session_state.final_link = ""
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

def render_button_field(label, options, state_key, disabled=False, columns=4):
    """Рендерит поле с кнопками в виде сетки"""
    st.markdown(f'<p class="field-label {"field-label-disabled" if disabled else ""}">{label}</p>', unsafe_allow_html=True)
    
    if disabled:
        st.info("🔒 Заполните предыдущее поле")
        return
    
    cols = st.columns(columns)
    current_value = st.session_state.get(state_key, "")
    
    for i, option in enumerate(options):
        with cols[i % columns]:
            button_type = "primary" if option == current_value else "secondary"
            if st.button(option, key=f"{state_key}_{option}", type=button_type, use_container_width=True):
                st.session_state[state_key] = option
                st.rerun()

def render_checkbox_field(label, options, state_key, disabled=False, columns=4):
    """Рендерит поле с чекбоксами для множественного выбора"""
    st.markdown(f'<p class="field-label {"field-label-disabled" if disabled else ""}">{label}</p>', unsafe_allow_html=True)
    
    if disabled:
        st.info("🔒 Заполните предыдущее поле")
        return
    
    cols = st.columns(columns)
    current_values = st.session_state.get(state_key, [])
    
    for i, option in enumerate(options):
        with cols[i % columns]:
            is_checked = option in current_values
            if st.checkbox(option, value=is_checked, key=f"{state_key}_cb_{option}"):
                if option not in current_values:
                    current_values.append(option)
                    st.session_state[state_key] = current_values
            else:
                if option in current_values:
                    current_values.remove(option)
                    st.session_state[state_key] = current_values

def render_favorite_field(label, all_options, favorites, state_key, disabled=False):
    """Рендерит поле с избранными кнопками + dropdown для остальных"""
    st.markdown(f'<p class="field-label {"field-label-disabled" if disabled else ""}">{label}</p>', unsafe_allow_html=True)
    
    if disabled:
        st.info("🔒 Заполните предыдущее поле")
        return
    
    # Избранные кнопки
    st.markdown("⭐ **Избранное:**")
    fav_cols = st.columns(len(favorites))
    current_value = st.session_state.get(state_key, "")
    
    for i, fav in enumerate(favorites):
        with fav_cols[i]:
            button_type = "primary" if fav == current_value else "secondary"
            if st.button(fav, key=f"{state_key}_fav_{fav}", type=button_type, use_container_width=True):
                st.session_state[state_key] = fav
                st.rerun()
    
    # Dropdown для остальных
    other_options = [opt for opt in all_options if opt not in favorites]
    selected = st.selectbox(
        "Все остальные:",
        [""] + other_options,
        key=f"{state_key}_dropdown",
        index=0 if not current_value or current_value in favorites else other_options.index(current_value) + 1 if current_value in other_options else 0
    )
    
    if selected and selected != current_value:
        st.session_state[state_key] = selected
        st.rerun()

# ============================================================
# STREAMLIT UI
# ============================================================

st.title("🏷️ Генератор нейминга кампании и UTM")

# Кнопка сброса
col_title, col_reset = st.columns([5, 1])
with col_reset:
    if st.button("🔄 Сбросить всё", type="secondary", use_container_width=True):
        clear_all()
        st.rerun()

st.divider()

# ============================================================
# ЭТАП 1: НЕЙМИНГ
# ============================================================

st.header("📌 Этап 1: Нейминг кампании")

# Получаем текущие значения
current_product = st.session_state.get('product', '')
current_stream = st.session_state.get('stream', '')
current_expense = st.session_state.get('expense', '')
current_source = st.session_state.get('source', '')
current_campaign_types = st.session_state.get('campaign_types', [])
current_client_geo = st.session_state.get('client_geo', '')
current_targeting = st.session_state.get('targeting', '')
current_goal = st.session_state.get('goal', '')

# Применяем умные дефолты при выборе источника
if current_source:
    apply_smart_defaults(current_source)

# Строим превью
preview = build_preview(
    current_product, current_stream, current_expense, current_source,
    current_campaign_types, current_client_geo, current_targeting, current_goal
)

if preview:
    st.session_state.campaign_name = preview

# ПОЛЯ НЕЙМИНГА

# 1. Продукт (всегда активен)
render_button_field("1. Продукт", DEFAULT_STRICT_NAMING["Продукт"], "product", columns=2)

st.markdown("---")

# 2. Стрим
step2_disabled = not bool(current_product)
render_button_field("2. Стрим", DEFAULT_STRICT_NAMING["Стрим"], "stream", disabled=step2_disabled, columns=4)

st.markdown("---")

# 3. Статья расхода
step3_disabled = not bool(current_stream)
render_button_field("3. Статья расхода", DEFAULT_STRICT_NAMING["Статья расхода"], "expense", disabled=step3_disabled, columns=5)

st.markdown("---")

# 4. Источник
step4_disabled = not bool(current_expense)
render_button_field("4. Источник", DEFAULT_STRICT_NAMING["Источник"], "source", disabled=step4_disabled, columns=4)

st.markdown("---")

# 5. Тип кампании (множественный выбор)
step5_disabled = not bool(current_source)
render_checkbox_field("5. Тип кампании (можно несколько)", DEFAULT_VARIABLE_NAMING["Тип кампании"], "campaign_types", disabled=step5_disabled, columns=4)

st.markdown("---")

# 6. Клиент/гео (с избранным)
step6_disabled = not bool(current_campaign_types)
render_favorite_field("6. Клиент/профиль/гео", DEFAULT_VARIABLE_NAMING["Клиент/гео"], FAVORITES["Клиент/гео"], "client_geo", disabled=step6_disabled)

st.markdown("---")

# 7. Таргетинг (с избранным)
step7_disabled = not bool(current_client_geo)
render_favorite_field("7. Таргетинг", DEFAULT_VARIABLE_NAMING["Таргетинг"], FAVORITES["Таргетинг"], "targeting", disabled=step7_disabled)

st.markdown("---")

# 8. Цель
step8_disabled = not bool(current_targeting)
render_button_field("8. Цель", DEFAULT_VARIABLE_NAMING["Цель"], "goal", disabled=step8_disabled, columns=4)

st.divider()

# ============================================================
# ЭТАП 2: UTM
# ============================================================

st.header("🎯 Этап 2: UTM ссылка")

# Базовая ссылка
base_link = st.text_input("🔗 Базовая ссылка", 
                          placeholder="https://expert.hh.ru/webinar/...",
                          key="base_link")

if base_link and not validate_url(base_link):
    st.warning("⚠️ Ссылка должна начинаться с http:// или https://")

# Проверка готовности нейминга
naming_ready = bool(st.session_state.campaign_name)

if not naming_ready:
    st.info("⬆️ Сначала сгенерируйте нейминг кампании")

# UTM параметры
st.subheader("UTM параметры")

# utm_source
utm_source_disabled = not naming_ready
render_button_field("utm_source", DEFAULT_UTM_PARAMS["utm_source"], "utm_source_select", disabled=utm_source_disabled, columns=4)

st.markdown("---")

# utm_medium
current_utm_source = st.session_state.get('utm_source_select', '')
utm_medium_disabled = not bool(current_utm_source)
render_button_field("utm_medium", DEFAULT_UTM_PARAMS["utm_medium"], "utm_medium_select", disabled=utm_medium_disabled, columns=3)

st.markdown("---")

# utm_campaign (автозаполнение)
current_utm_medium = st.session_state.get('utm_medium_select', '')
utm_campaign_disabled = not bool(current_utm_medium)

if utm_campaign_disabled:
    st.markdown('<p class="field-label field-label-disabled">utm_campaign (авто) 🔒</p>', unsafe_allow_html=True)
    st.info("🔒 Заполните utm_medium")
else:
    st.markdown('<p class="field-label">utm_campaign <span style="color: #888;">(автозаполнение)</span></p>', unsafe_allow_html=True)
    utm_campaign = st.text_input(
        "Кампания", 
        value=st.session_state.campaign_name,
        key="utm_campaign",
        disabled=utm_campaign_disabled,
        label_visibility="collapsed"
    )

st.markdown("---")

# utm_content, utm_term, utm_vacancy (dropdown)
utm_other_disabled = not bool(current_utm_medium)

col_utm1, col_utm2, col_utm3 = st.columns(3)

with col_utm1:
    if utm_other_disabled:
        st.markdown('<p class="field-label field-label-disabled">utm_content 🔒</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="field-label">utm_content</p>', unsafe_allow_html=True)
    st.selectbox("Контент", [""] + DEFAULT_UTM_PARAMS["utm_content"], key="utm_content_select", disabled=utm_other_disabled, label_visibility="collapsed")

with col_utm2:
    if utm_other_disabled:
        st.markdown('<p class="field-label field-label-disabled">utm_term 🔒</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="field-label">utm_term</p>', unsafe_allow_html=True)
    st.selectbox("Термин", [""] + DEFAULT_UTM_PARAMS["utm_term"], key="utm_term_select", disabled=utm_other_disabled, label_visibility="collapsed")

with col_utm3:
    if utm_other_disabled:
        st.markdown('<p class="field-label field-label-disabled">utm_vacancy 🔒</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="field-label">utm_vacancy</p>', unsafe_allow_html=True)
    st.selectbox("Вакансия", [""] + DEFAULT_UTM_PARAMS["utm_vacancy"], key="utm_vacancy_select", disabled=utm_other_disabled, label_visibility="collapsed")

st.divider()

# Отступ для фиксированной панели
st.markdown("<div style='height: 180px;'></div>", unsafe_allow_html=True)

# ============================================================
# ФИКСИРОВАННАЯ ПАНЕЛЬ
# ============================================================

preview_display = preview if preview else "Заполните поля выше..."
naming_color = "#00ff88" if preview else "#888"

# Формируем UTM ссылку
current_base_link = st.session_state.get('base_link', '')
current_utm_content = st.session_state.get('utm_content_select', '')
current_utm_term = st.session_state.get('utm_term_select', '')
current_utm_vacancy = st.session_state.get('utm_vacancy_select', '')
current_utm_campaign = st.session_state.get('utm_campaign', '') or preview

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

utm_display = utm_preview if utm_preview else "Введите ссылку и UTM параметры..."
utm_color = "#64B5F6" if utm_preview else "#888"

# Экранирование для JS
escaped_naming = preview.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"').replace('\n', '').replace('\r', '') if preview else ""
escaped_utm = utm_preview.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"').replace('\n', '').replace('\r', '') if utm_preview else ""

# Фиксированная панель (CSS)
st.markdown(f'''
<div class="fixed-panel">
<div class="panel-inner">
<div class="panel-row">
<span class="panel-label">Нейминг:</span>
<code class="panel-code" style="color:{naming_color};">{preview_display}</code>
<div class="btn-placeholder" id="btn-naming-slot"></div>
</div>
<div class="panel-row">
<span class="panel-label">UTM:</span>
<code class="panel-code" style="color:{utm_color};">{utm_display}</code>
<div class="btn-placeholder" id="btn-utm-slot"></div>
</div>
</div>
</div>
''', unsafe_allow_html=True)

# Кнопки копирования
import streamlit.components.v1 as components

st.markdown("### 📋 Копирование результатов")
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if preview:
        btn_html = f'''
        <html><head><style>
        * {{ margin: 0; padding: 0; }}
        body {{ background: transparent; }}
        .copy-btn {{
            width: 100%;
            padding: 12px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 15px;
            font-weight: 600;
            border: none;
            color: #fff;
            background: #4CAF50;
            transition: all 0.2s;
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
        components.html(btn_html, height=50)
    else:
        st.button("📋 Копировать нейминг", disabled=True, use_container_width=True)

with col_btn2:
    if utm_preview:
        btn_html = f'''
        <html><head><style>
        * {{ margin: 0; padding: 0; }}
        body {{ background: transparent; }}
        .copy-btn {{
            width: 100%;
            padding: 12px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 15px;
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
        components.html(btn_html, height=50)
    else:
        st.button("📋 Копировать UTM", disabled=True, use_container_width=True)
