import streamlit as st
import pandas as pd
from urllib.parse import urlencode
from datetime import datetime
import re

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

st.set_page_config(page_title="Генератор нейминга и UTM", page_icon="🏷️", layout="wide")

st.title("🏷️ Генератор нейминга кампании и UTM")

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

# Прогресс-бар
completed, total = get_progress(
    current_product, current_stream, current_expense, current_source,
    current_campaign_types, current_client_geo, current_targeting, current_goal
)
st.progress(completed / total, text=f"Прогресс: {completed} из {total} шагов")

# Превью нейминга в реальном времени
preview = build_preview(
    current_product, current_stream, current_expense, current_source,
    current_campaign_types, current_client_geo, current_targeting, current_goal
)
if preview:
    st.markdown(f'<div style="background-color: #E3F2FD; padding: 10px; border-radius: 5px; margin-bottom: 15px;"><b>Превью:</b> <code>{preview}</code></div>', unsafe_allow_html=True)

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

# Кнопка генерации нейминга
if st.button("🚀 GENERATE NAME", type="primary", use_container_width=True):
    parts = []
    
    # Строгий набор
    if product:
        parts.append(product)
    if stream:
        parts.append(stream)
    if expense:
        parts.append(expense)
    if source:
        parts.append(source)
    
    # Вариативный набор
    if campaign_types:
        # Соединяем несколько типов кампании через &
        parts.append("&".join(campaign_types))
    if client_geo:
        parts.append(client_geo)
    if targeting:
        parts.append(targeting)
    if goal:
        parts.append(goal)
    
    st.session_state.campaign_name = "_".join(parts)
    
    # Добавляем в историю
    if st.session_state.campaign_name:
        st.session_state.history.append({
            'datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'type': 'Нейминг',
            'value': st.session_state.campaign_name
        })

# Отображение результата нейминга
if st.session_state.campaign_name:
    st.success(f"**Нейминг кампании:**")
    
    # Контейнер с кодом и кнопкой копирования
    col_code, col_copy = st.columns([5, 1])
    with col_code:
        st.code(st.session_state.campaign_name, language=None)
    with col_copy:
        # JavaScript для копирования в буфер обмена
        copy_js = f"""
        <button onclick="navigator.clipboard.writeText('{st.session_state.campaign_name}').then(function() {{
            alert('Скопировано!');
        }});" style="
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            margin-top: 5px;
        ">📋 Копировать</button>
        """
        st.markdown(copy_js, unsafe_allow_html=True)

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
    # utm_campaign - автозаполнение, активен после utm_medium
    utm_campaign_disabled = not bool(utm_medium)
    if utm_campaign_disabled:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #9E9E9E; margin-bottom: 5px;">utm_campaign <span style="font-size: 12px;">🔒</span></p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #6B4C9A; margin-bottom: 5px;">utm_campaign</p>', unsafe_allow_html=True)
    utm_campaign = st.text_input("Кампания", 
                                 value=st.session_state.campaign_name,
                                 key="utm_campaign",
                                 help="Автоматически заполняется из нейминга выше",
                                 disabled=utm_campaign_disabled)
    
    # utm_content - активен после utm_campaign
    utm_content_disabled = not bool(utm_campaign)
    if utm_content_disabled:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #9E9E9E; margin-bottom: 5px;">utm_content <span style="font-size: 12px;">🔒</span></p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #6B4C9A; margin-bottom: 5px;">utm_content</p>', unsafe_allow_html=True)
    utm_content = select_with_add("контент", "utm_content", select_key="utm_content_select", disabled=utm_content_disabled)

with utm_cols[2]:
    # utm_term - активен после utm_content
    utm_term_disabled = not bool(utm_content)
    if utm_term_disabled:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #9E9E9E; margin-bottom: 5px;">utm_term <span style="font-size: 12px;">🔒</span></p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #6B4C9A; margin-bottom: 5px;">utm_term</p>', unsafe_allow_html=True)
    utm_term = select_with_add("ключевое слово", "utm_term", select_key="utm_term_select", disabled=utm_term_disabled)
    
    # utm_vacancy - активен после utm_term
    utm_vacancy_disabled = not bool(utm_term)
    if utm_vacancy_disabled:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #9E9E9E; margin-bottom: 5px;">utm_vacancy <span style="font-size: 12px;">🔒</span></p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size: 18px; font-weight: 600; color: #6B4C9A; margin-bottom: 5px;">utm_vacancy</p>', unsafe_allow_html=True)
    utm_vacancy = select_with_add("ID вакансии", "utm_vacancy", select_key="utm_vacancy_select", disabled=utm_vacancy_disabled)

# Кнопка генерации UTM ссылки
if st.button("🔗 GENERATE LINK + UTM", type="primary", use_container_width=True):
    if not base_link:
        st.error("⚠️ Введите базовую ссылку!")
    elif not validate_url(base_link):
        st.error("⚠️ Введите корректную ссылку (начинается с http:// или https://)")
    else:
        # Собираем UTM параметры
        utm_params = {}
        if utm_source:
            utm_params["utm_source"] = utm_source
        if utm_medium:
            utm_params["utm_medium"] = utm_medium
        if utm_campaign:
            utm_params["utm_campaign"] = utm_campaign
        if utm_content:
            utm_params["utm_content"] = utm_content
        if utm_term:
            utm_params["utm_term"] = utm_term
        if utm_vacancy:
            utm_params["utm_vacancy"] = utm_vacancy
        
        # Формируем финальную ссылку
        if utm_params:
            # Используем ручную сборку для сохранения специальных символов типа {ad_id}
            utm_string = "&".join([f"{k}={v}" for k, v in utm_params.items()])
            separator = "&" if "?" in base_link else "?"
            st.session_state.final_link = f"{base_link}{separator}{utm_string}"
        else:
            st.session_state.final_link = base_link
        
        # Добавляем в историю
        if st.session_state.final_link:
            st.session_state.history.append({
                'datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'type': 'UTM ссылка',
                'value': st.session_state.final_link
            })

# Отображение результата
if st.session_state.final_link:
    st.success(f"**Готовая ссылка с UTM:**")
    
    col_code, col_copy = st.columns([5, 1])
    with col_code:
        st.code(st.session_state.final_link, language=None)
    with col_copy:
        copy_js_link = f"""
        <button onclick="navigator.clipboard.writeText('{st.session_state.final_link}').then(function() {{
            alert('Скопировано!');
        }});" style="
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            margin-top: 5px;
        ">📋 Копировать</button>
        """
        st.markdown(copy_js_link, unsafe_allow_html=True)

st.divider()

# ============================================================
# ИСТОРИЯ ГЕНЕРАЦИЙ
# ============================================================

st.header("📜 История генераций")

if st.session_state.history:
    # Кнопки управления историей
    col_export, col_clear_hist = st.columns([1, 1])
    
    with col_export:
        # Формируем текст для экспорта
        export_text = "История генераций\n" + "=" * 50 + "\n\n"
        for item in st.session_state.history:
            export_text += f"[{item['datetime']}] {item['type']}:\n{item['value']}\n\n"
        
        st.download_button(
            label="📥 Скачать историю (.txt)",
            data=export_text,
            file_name=f"naming_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col_clear_hist:
        if st.button("🗑️ Очистить историю", use_container_width=True):
            st.session_state.history = []
            st.rerun()
    
    # Отображение истории (от новых к старым)
    for i, item in enumerate(reversed(st.session_state.history)):
        with st.container():
            col_info, col_copy_hist = st.columns([5, 1])
            with col_info:
                badge_color = "#1E5AA8" if item['type'] == 'Нейминг' else "#6B4C9A"
                st.markdown(f'''
                <div style="background-color: #f5f5f5; padding: 10px; border-radius: 5px; margin-bottom: 10px; border-left: 4px solid {badge_color};">
                    <small style="color: #666;">📅 {item['datetime']} | <span style="color: {badge_color}; font-weight: bold;">{item['type']}</span></small><br>
                    <code style="font-size: 12px; word-break: break-all;">{item['value']}</code>
                </div>
                ''', unsafe_allow_html=True)
            with col_copy_hist:
                # Экранируем кавычки в значении для JavaScript
                escaped_value = item['value'].replace("'", "\\'")
                copy_hist_js = f"""
                <button onclick="navigator.clipboard.writeText('{escaped_value}').then(function() {{
                    alert('Скопировано!');
                }});" style="
                    background-color: #757575;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 12px;
                    margin-top: 15px;
                ">📋</button>
                """
                st.markdown(copy_hist_js, unsafe_allow_html=True)
else:
    st.info("История пуста. Сгенерируйте нейминг или UTM-ссылку.")

st.divider()

# ============================================================
# ЭКСПОРТ ТЕКУЩИХ РЕЗУЛЬТАТОВ
# ============================================================

if st.session_state.campaign_name or st.session_state.final_link:
    st.header("📤 Экспорт результатов")
    
    export_current = ""
    if st.session_state.campaign_name:
        export_current += f"Нейминг кампании:\n{st.session_state.campaign_name}\n\n"
    if st.session_state.final_link:
        export_current += f"UTM ссылка:\n{st.session_state.final_link}\n"
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        st.download_button(
            label="📥 Скачать результаты (.txt)",
            data=export_current,
            file_name=f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col_exp2:
        # Копировать оба значения
        both_values = f"{st.session_state.campaign_name}\n{st.session_state.final_link}".strip()
        escaped_both = both_values.replace("'", "\\'").replace("\n", "\\n")
        copy_both_js = f"""
        <button onclick="navigator.clipboard.writeText('{escaped_both}').then(function() {{
            alert('Скопировано оба значения!');
        }});" style="
            background-color: #1976D2;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            width: 100%;
        ">📋 Копировать всё</button>
        """
        st.markdown(copy_both_js, unsafe_allow_html=True)

st.divider()

# ============================================================
# ПОДСКАЗКА
# ============================================================

with st.expander("ℹ️ Справка по использованию"):
    st.markdown("""
    ### Как пользоваться:
    
    1. **Этап 1** - Выберите параметры нейминга кампании:
       - Заполняйте поля последовательно (следующее разблокируется после заполнения предыдущего)
       - В поле "Тип кампании" можно выбрать несколько значений (они объединятся через `&`)
       - Смотрите превью нейминга в реальном времени
       - Нажмите **GENERATE NAME**
    
    2. **Этап 2** - Создайте ссылку с UTM:
       - Введите базовую ссылку (должна начинаться с http:// или https://)
       - Выберите UTM параметры (utm_campaign заполнится автоматически)
       - Нажмите **GENERATE LINK + UTM**
    
    3. **Дополнительные функции:**
       - ➕ Добавляйте свои значения в любое поле
       - 📋 Копируйте результаты одним кликом
       - 📜 Просматривайте историю генераций
       - 📥 Скачивайте результаты в файл
       - 🔄 Сбросить всё — очистить все поля
    
    ### Пример нейминга:
    `adtech-b2c_lpv_cpa_telegram_mk_astrakhan_users_tresponse`
    
    ### Примечание для TG Ads:
    *Для отслеживания таргетированного отклика прописываем: utm_medium=cpc_yandex_direct и utm_vacancy={utm_vacancy}*
    """)
