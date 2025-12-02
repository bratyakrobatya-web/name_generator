import streamlit as st
import pandas as pd
from urllib.parse import urlencode

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
# STREAMLIT UI
# ============================================================

st.set_page_config(page_title="Генератор нейминга и UTM", page_icon="🏷️", layout="wide")

st.title("🏷️ Генератор нейминга кампании и UTM")

# ============================================================
# ИНИЦИАЛИЗАЦИЯ SESSION STATE
# ============================================================

if 'campaign_name' not in st.session_state:
    st.session_state.campaign_name = ""
if 'final_link' not in st.session_state:
    st.session_state.final_link = ""

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

def select_with_add(label, list_key, multiselect=False, select_key=None, disabled=False):
    """Создаёт selectbox/multiselect с возможностью добавить своё значение"""
    
    options = st.session_state[f"list_{list_key}"]
    
    # Основной селект
    if multiselect:
        selected = st.multiselect(f"Выберите {label.lower()}", options, key=select_key, disabled=disabled)
    else:
        selected = st.selectbox(f"Выберите {label.lower()}", [""] + options, key=select_key, disabled=disabled)
    
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

# Отображение результата нейминга
if st.session_state.campaign_name:
    st.success(f"**Нейминг кампании:**")
    st.code(st.session_state.campaign_name, language=None)
    
    # Кнопка копирования
    st.button("📋 Копировать нейминг", 
              on_click=lambda: st.write(""),  # Placeholder
              help="Выделите и скопируйте текст выше")

st.divider()

# ============================================================
# ЭТАП 2: СОЗДАНИЕ UTM
# ============================================================

st.header("Этап 2: Создаём ссылку с UTM")

# Поле для ввода базовой ссылки
base_link = st.text_input("🔗 Введите базовую ссылку", 
                          placeholder="https://expert.hh.ru/webinar/...",
                          key="base_link")

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

# Отображение результата
if st.session_state.final_link:
    st.success(f"**Готовая ссылка с UTM:**")
    st.code(st.session_state.final_link, language=None)

st.divider()

# ============================================================
# ПОДСКАЗКА
# ============================================================

with st.expander("ℹ️ Справка по использованию"):
    st.markdown("""
    ### Как пользоваться:
    
    1. **Этап 1** - Выберите параметры нейминга кампании:
       - Раскройте нужные секции и выберите значения
       - В поле "Тип кампании" можно выбрать несколько значений (они объединятся через `&`)
       - Нажмите **GENERATE NAME**
    
    2. **Этап 2** - Создайте ссылку с UTM:
       - Введите базовую ссылку
       - Выберите UTM параметры (utm_campaign заполнится автоматически)
       - Нажмите **GENERATE LINK + UTM**
    
    ### Пример нейминга:
    `adtech-b2c_lpv_cpa_telegram_mk_astrakhan_users_tresponse`
    
    ### Примечание для TG Ads:
    *Для отслеживания таргетированного отклика прописываем: utm_medium=cpc_yandex_direct и utm_vacancy={utm_vacancy}*
    """)
