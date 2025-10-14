import TkEasyGUI as eg
import os
import sys
import configparser
from pathlib import Path
import json
import shutil
import threading
import queue
import tkinter as tk
from tkinter import filedialog

APP_VERSION = "1.00"

FORMAT = "utf-8"
INIT_FILE = "config.ini"
LANG_DIR = "lang"
# プロファイル管理
PROFILE_DIR = "profiles"

os.makedirs(PROFILE_DIR, exist_ok=True)

def get_profile_list():
    return [f.replace("config_","").replace(".ini","") for f in os.listdir(PROFILE_DIR) if f.startswith("config_") and f.endswith(".ini")]

def get_profile_config_path(profile_name):
    return os.path.join(PROFILE_DIR, f"config_{profile_name}.ini")

# 設定項目
mod_folder = ""
xml_folder = ""
sst_folder = ""
txt_folder = ""
skyrim_lang = ""
source_lang = ""
dest_lang = ""
trans_target = ""
trans_mode = ""
bat_list_max_num = ""
trans_source = ""
api_trans = ""
api_heuristic = ""
language = "ja"  # デフォルト言語
translations = {}

# パス履歴を保存するグローバル変数
mod_path_history = []
xml_path_history = []
sst_path_history = []
txt_path_history = []
mcm_interface_path_history = []

# 言語履歴を保存するグローバル変数
skyrim_lang_history = []
source_lang_history = []
dest_lang_history = []

# プロファイルの初期値
current_profile = "default"

LAST_PROFILE_FILE = os.path.join(PROFILE_DIR, "last_profile.txt")

def save_last_profile(profile_name):
    try:
        with open(LAST_PROFILE_FILE, "w", encoding="utf-8") as f:
            f.write(profile_name)
    except Exception:
        pass

def load_last_profile():
    try:
        with open(LAST_PROFILE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return None

def load_translations(lang):
    """指定された言語に基づいて JSON ファイルから翻訳を読み込む。"""
    global translations
    lang_file = os.path.join(LANG_DIR, f"{lang}.json")
    try:
        if os.path.exists(lang_file):
            with open(lang_file, 'r', encoding=FORMAT) as f:
                translations = json.load(f)
        else:
            translations = {}  # 翻訳ファイルがない場合は空の翻訳を返す
            print(f"翻訳ファイル {lang_file} が見つかりません。")
    except Exception as e:
        translations = {}
        print(f"翻訳の読み込みに失敗しました: {str(e)}")
    return translations

def list_files(directory, extensions, include_string=None, exclude_string=None):
    """
    指定されたフォルダから特定の拡張子のファイルパスをリストアップする。
    オプションで特定の文字列を含む/含まないファイルをフィルタリングする。
    """
    matching_files = []

    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = Path(root) / file
                file_name = file.lower()

                if include_string and include_string.lower() not in file_name:
                    continue

                if exclude_string and exclude_string.lower() in file_name:
                    continue

                matching_files.append(str(file_path))

    return matching_files

def load_init():
    global current_profile
    global mod_folder, xml_folder, sst_folder, txt_folder
    global skyrim_lang, source_lang, dest_lang
    global trans_target, trans_mode, bat_list_max_num
    global trans_source, api_trans, api_heuristic, language
    global mcm_interface_folder
    global mod_path_history, xml_path_history, sst_path_history, txt_path_history, mcm_interface_path_history
    global skyrim_lang_history, source_lang_history, dest_lang_history
    global current_profile

    config = configparser.ConfigParser()
    config_path = get_profile_config_path(current_profile)

    default_mod_folder = os.getcwd() + "\\mod"
    default_xml_folder = os.getcwd() + "\\xml"
    default_sst_folder = os.getcwd() + "\\sst"
    default_txt_folder = os.getcwd() + "\\output"
    default_mcm_interface_folder = os.getcwd() + "\\mcm_interface"  # 追加
    default_skyrim_lang = "japanese"
    default_source_lang = "english"
    default_dest_lang = "japanese"
    default_trans_target = "0"
    default_trans_mode = "0"
    default_bat_list_max_num = "100"
    default_trans_source = "0"
    default_api_trans = "0"
    default_api_heuristic = "0"
    
    # 過去のパス履歴のデフォルト値（空のリスト）
    default_mod_path_history = "[]"
    default_xml_path_history = "[]"
    default_sst_path_history = "[]"
    default_txt_path_history = "[]"
    default_mcm_interface_path_history = "[]"
    default_skyrim_lang_history = "[]"
    default_source_lang_history = "[]"
    default_dest_lang_history = "[]"
    default_language = "ja"

    try:
        if os.path.exists(config_path):
            config.read(config_path, encoding=FORMAT)

            mod_folder = config.get('FOLDER_SETTING', 'MOD_FOLDER', fallback=default_mod_folder)
            xml_folder = config.get('FOLDER_SETTING', 'XML_FOLDER', fallback=default_xml_folder)
            sst_folder = config.get('FOLDER_SETTING', 'SST_FOLDER', fallback=default_sst_folder)
            txt_folder = config.get('FOLDER_SETTING', 'TXT_FOLDER', fallback=default_txt_folder)
            mcm_interface_folder = config.get('FOLDER_SETTING', 'MCM_INTERFACE_FOLDER', fallback=default_mcm_interface_folder)

            # パス履歴の読み込み
            mod_path_history = json.loads(config.get('FOLDER_SETTING', 'MOD_PATH_HISTORY', fallback='[]'))
            xml_path_history = json.loads(config.get('FOLDER_SETTING', 'XML_PATH_HISTORY', fallback='[]'))
            sst_path_history = json.loads(config.get('FOLDER_SETTING', 'SST_PATH_HISTORY', fallback='[]'))
            txt_path_history = json.loads(config.get('FOLDER_SETTING', 'TXT_PATH_HISTORY', fallback='[]'))
            mcm_interface_path_history = json.loads(config.get('FOLDER_SETTING', 'MCM_INTERFACE_PATH_HISTORY', fallback='[]'))
            
            # 言語履歴の読み込み
            skyrim_lang_history = json.loads(config.get('LANG_SETTING', 'SKYRIM_LANG_HISTORY', fallback='[]'))
            source_lang_history = json.loads(config.get('LANG_SETTING', 'SOURCE_LANG_HISTORY', fallback='[]'))
            dest_lang_history = json.loads(config.get('LANG_SETTING', 'DEST_LANG_HISTORY', fallback='[]'))

            # 現在のパスを履歴に追加
            mod_path_history = update_path_history(mod_folder, mod_path_history)
            xml_path_history = update_path_history(xml_folder, xml_path_history)
            sst_path_history = update_path_history(sst_folder, sst_path_history)
            txt_path_history = update_path_history(txt_folder, txt_path_history)
            mcm_interface_path_history = update_path_history(mcm_interface_folder, mcm_interface_path_history)
            
            # 現在の言語を履歴に追加
            skyrim_lang_history = update_path_history(skyrim_lang, skyrim_lang_history)
            source_lang_history = update_path_history(source_lang, source_lang_history)
            dest_lang_history = update_path_history(dest_lang, dest_lang_history)
            skyrim_lang = config.get('TRANS_SETTING', 'SKYRIM_LANG', fallback=default_skyrim_lang)
            source_lang = config.get('TRANS_SETTING', 'SOURCE_LANG', fallback=default_source_lang)
            dest_lang = config.get('TRANS_SETTING', 'DEST_LANG', fallback=default_dest_lang)
            trans_target = config.get('TRANS_SETTING', 'TRANS_TARGET', fallback=default_trans_target)
            trans_mode = config.get('TRANS_SETTING', 'TRANS_MODE', fallback=default_trans_mode)
            bat_list_max_num = config.get('TRANS_SETTING', 'bat_list_max_num', fallback=default_bat_list_max_num)
            trans_source = config.get('TRANS_SETTING', 'trans_source', fallback=default_trans_source)
            api_trans = config.get('TRANS_SETTING', 'api_trans', fallback=default_api_trans)
            api_heuristic = config.get('TRANS_SETTING', 'api_heuristic', fallback=default_api_heuristic)
            language = config.get('GENERAL', 'LANGUAGE', fallback=default_language)
        else:
            mod_folder = default_mod_folder
            xml_folder = default_xml_folder
            sst_folder = default_sst_folder
            txt_folder = default_txt_folder
            mcm_interface_folder = default_mcm_interface_folder
            mod_path_history = [mod_folder]
            xml_path_history = [xml_folder]
            sst_path_history = [sst_folder]
            txt_path_history = [txt_folder]
            mcm_interface_path_history = [mcm_interface_folder]
            skyrim_lang = default_skyrim_lang
            source_lang = default_source_lang
            dest_lang = default_dest_lang
            trans_target = default_trans_target
            trans_mode = default_trans_mode
            bat_list_max_num = default_bat_list_max_num
            trans_source = default_trans_source
            api_trans = default_api_trans
            api_heuristic = default_api_heuristic
            language = default_language
    except Exception as e:
        print(translations.get("load_config_failed", "設定ファイルの読み込みに失敗しました: {error}").format(error=str(e)))
        mod_folder = default_mod_folder
        xml_folder = default_xml_folder
        sst_folder = default_sst_folder
        txt_folder = default_txt_folder
        mcm_interface_folder = default_mcm_interface_folder
        mod_path_history = [mod_folder]
        xml_path_history = [xml_folder]
        sst_path_history = [sst_folder]
        txt_path_history = [txt_folder]
        mcm_interface_path_history = [mcm_interface_folder]
        skyrim_lang = default_skyrim_lang
        source_lang = default_source_lang
        dest_lang = default_dest_lang
        trans_target = default_trans_target
        trans_mode = default_trans_mode
        bat_list_max_num = default_bat_list_max_num
        trans_source = default_trans_source
        api_trans = default_api_trans
        api_heuristic = default_api_heuristic
        language = default_language

    load_translations(language)

def update_path_history(path, history_list, max_history=10):
    """パス履歴を更新する"""
    if path and path not in history_list:
        history_list.insert(0, path)
        if len(history_list) > max_history:
            history_list.pop()
    return history_list

def save_init(values):
    global mod_path_history, xml_path_history, sst_path_history, txt_path_history, mcm_interface_path_history
    global skyrim_lang_history, source_lang_history, dest_lang_history
    global current_profile
    
    mod_folder = values['-mod_path-']
    xml_folder = values['-xml_path-']
    sst_folder = values['-sst_path-']
    txt_folder = values['-txt_path-']
    mcm_interface_folder = values['-mcm_interface_path-']
    skyrim_lang = values['-skyrim_lang-']
    source_lang = values['-s_lang-']
    dest_lang = values['-d_lang-']

    # パス履歴を更新
    mod_path_history = update_path_history(mod_folder, mod_path_history)
    xml_path_history = update_path_history(xml_folder, xml_path_history)
    sst_path_history = update_path_history(sst_folder, sst_path_history)
    txt_path_history = update_path_history(txt_folder, txt_path_history)
    mcm_interface_path_history = update_path_history(mcm_interface_folder, mcm_interface_path_history)
    
    # 言語履歴を更新
    skyrim_lang_history = update_path_history(skyrim_lang, skyrim_lang_history)
    source_lang_history = update_path_history(source_lang, source_lang_history)
    dest_lang_history = update_path_history(dest_lang, dest_lang_history)

    # ラジオボタンの値を取得
    # 選択されているキーから数字部分を抽出
    trans_target = next(key.replace("trans_target_", "") for key in values.keys() 
                       if key.startswith("trans_target_") and values[key] == True)
    trans_mode = next(key.replace("trans_mode_", "") for key in values.keys() 
                     if key.startswith("trans_mode_") and values[key] == True)
    trans_source = next(key.replace("trans_source_", "") for key in values.keys() 
                       if key.startswith("trans_source_") and values[key] == True)
    api_trans = next(key.replace("api_trans_", "") for key in values.keys() 
                    if key.startswith("api_trans_") and values[key] == True)
    bat_list_max_num = values['-bat_list_max_num-']
    language = values['-language-']

    if values['chk_api_heuristic']:
        api_heuristic = "1"
    else:
        api_heuristic = "0"

    config = configparser.ConfigParser()
    config_path = get_profile_config_path(current_profile)

    config['GENERAL'] = {
        'LANGUAGE': language
    }

    config['FOLDER_SETTING'] = {
        'MOD_FOLDER': mod_folder,
        'XML_FOLDER': xml_folder,
        'SST_FOLDER': sst_folder,
        'TXT_FOLDER': txt_folder,
        'MCM_INTERFACE_FOLDER': mcm_interface_folder,
        # パス履歴をJSON形式で保存
        'MOD_PATH_HISTORY': json.dumps(mod_path_history),
        'XML_PATH_HISTORY': json.dumps(xml_path_history),
        'SST_PATH_HISTORY': json.dumps(sst_path_history),
        'TXT_PATH_HISTORY': json.dumps(txt_path_history),
        'MCM_INTERFACE_PATH_HISTORY': json.dumps(mcm_interface_path_history)
    }

    config['TRANS_SETTING'] = {
        'SKYRIM_LANG': skyrim_lang,
        'SOURCE_LANG': source_lang,
        'DEST_LANG': dest_lang,
        'TRANS_TARGET': trans_target,
        'TRANS_MODE': trans_mode,
        'bat_list_max_num': bat_list_max_num,
        'trans_source': trans_source,
        'api_trans': api_trans,
        'api_heuristic': api_heuristic
    }

    config['LANG_SETTING'] = {
        'SKYRIM_LANG_HISTORY': json.dumps(skyrim_lang_history),
        'SOURCE_LANG_HISTORY': json.dumps(source_lang_history),
        'DEST_LANG_HISTORY': json.dumps(dest_lang_history)
    }

    try:
        with open(config_path, 'w', encoding=FORMAT) as configfile:
            config.write(configfile)
        print(translations.get("save_config_success", f"設定を{config_path}に保存しました。"))
    except Exception as e:
        print(translations.get("save_config_failed", f"設定ファイルの保存に失敗しました: {str(e)}"))

def normalize_filename(filename, remove_strings=None):
    """ファイル名を正規化する（拡張子除去、大文字小文字無視、スペースとアンダースコアを統一、特定文字列削除）"""
    if remove_strings is None or remove_strings == "":
        remove_strings = []
    if isinstance(remove_strings, str):
        remove_strings = [remove_strings] if remove_strings else []
    name = os.path.splitext(os.path.basename(filename))[0]
    name = name.lower()
    for string in remove_strings:
        name = name.replace(string.lower(), "")
    name = name.replace(" ", "_")
    return name

def compare_file_lists(list1, list2, remove_strings1=None, remove_strings2=None):
    """
    2つのフルパスファイル名リストを比較し、合致するファイル名のフルパスリストを返す
    """
    if remove_strings1 is None or remove_strings1 == "":
        remove_strings1 = []
    if isinstance(remove_strings1, str):
        remove_strings1 = [remove_strings1] if remove_strings1 else []
    
    if remove_strings2 is None or remove_strings2 == "":
        remove_strings2 = []
    if isinstance(remove_strings2, str):
        remove_strings2 = [remove_strings2] if remove_strings2 else []

    list1_normalized = {normalize_filename(path, remove_strings1): path for path in list1}
    list2_normalized = {normalize_filename(path, remove_strings2): path for path in list2}
    
    common_names = set(list1_normalized.keys()) & set(list2_normalized.keys())
    
    list1_matches = [list1_normalized[name] for name in common_names]
    list2_matches = [list2_normalized[name] for name in common_names]
    
    return list1_matches, list2_matches

def get_trans_list(values, mod_ext, trans_mod_str, trans_lang_str):
    """翻訳ファイルリスト取得"""
    mod_file_list = list_files(values['-mod_path-'], mod_ext)

    if values["trans_source"] == "trans_source_0":
        xml_ext = [".xml"]
        xml_file_list = list_files(values['-xml_path-'], xml_ext, trans_lang_str)
        mod_file_list, xml_file_list = compare_file_lists(mod_file_list, xml_file_list, trans_mod_str, trans_lang_str)
        data_str_list = create_trans_xml_batch_text_data(values, mod_file_list, xml_file_list)
    elif values["trans_source"] == "trans_source_1":
        sst_ext = [".sst"]
        sst_file_list = list_files(values['-sst_path-'], sst_ext, trans_lang_str)
        mod_file_list, sst_file_list = compare_file_lists(mod_file_list, sst_file_list, trans_mod_str, trans_lang_str)
        data_str_list = create_trans_sst_batch_text_data(values, mod_file_list, sst_file_list)
    elif values["trans_source"] == "trans_source_2":
        data_str_list = create_trans_api_batch_text_data(values, mod_file_list)

    return data_str_list

def check_input(window, values):
    """簡単な入力チェック"""
    if len(values["-mod_path-"]) <= 0:
        eg.popup(translations.get("error_mod_path_empty", "「modファイル保存パス」が未入力です。"))
        window["-mod_path-"].focus()
        return False

    if len(values["-txt_path-"]) <= 0:
        eg.popup(translations.get("error_txt_path_empty", "「翻訳バッチ用Txtファイル出力先パス」が未入力です。"))
        window["-txt_path-"].focus()
        return False
    
    if len(values["-skyrim_lang-"]) <= 0:
        eg.popup(translations.get("error_skyrim_lang_empty", "「Skyrim言語」が未入力です。"))
        window["-skyrim_lang-"].focus()
        return False

    if len(values["-s_lang-"]) <= 0:
        eg.popup(translations.get("error_source_lang_empty", "「元言語」が未入力です。"))
        window["-s_lang-"].focus()
        return False
    
    if len(values["-d_lang-"]) <= 0:
        eg.popup(translations.get("error_dest_lang_empty", "「翻訳先言語」が未入力です。"))
        window["-d_lang-"].focus()
        return False
    
    if len(values["-xml_path-"]) <= 0:
        eg.popup(translations.get("error_xml_path_empty", "「インポート翻訳XMLファイル保存パス」が未入力です。"))
        window["-xml_path-"].focus()
        return False
    
    if len(values["-sst_path-"]) <= 0:
        eg.popup(translations.get("error_sst_path_empty", "「インポート翻訳SSTファイル保存パス」が未入力です。"))
        window["-sst_path-"].focus()
        return False
    
    if len(values["-bat_list_max_num-"]) <= 0:
        eg.popup(translations.get("error_batch_max_items_empty", "「翻訳バッチ１ファイル内最大件数」が未入力です。"))
        window["-bat_list_max_num-"].focus()
        return False
    else:
        if values["-bat_list_max_num-"].isdigit() and int(values["-bat_list_max_num-"]) > 0:
            pass
        else:
            eg.popup(translations.get("error_batch_max_items_invalid", "「翻訳バッチ１ファイル内最大件数」には自然数を入力してください。"))
            window["-bat_list_max_num-"].focus()
            return False
    
    return True

def create_esp_trans_file(values):
    """esp,esm翻訳バッチ用ファイル作成"""
    s_lang = values['-s_lang-']
    d_lang = values['-d_lang-']
    trans_lang_str = "_" + s_lang + "_" + d_lang
    mod_ext = [".esp", ".esm"]
    data_str_list = get_trans_list(values, mod_ext, "", trans_lang_str)
    file_name = "esp_trans"
    if values["trans_source"] == "trans_source_0":
        file_name += "_xml"
    elif values["trans_source"] == "trans_source_1":
        file_name += "_sst"
    elif values["trans_source"] == "trans_source_2":
        file_name += "_api"
    file_num = split_list_to_files(data_str_list, values['-txt_path-'], int(values['-bat_list_max_num-']), file_name)
    data_num = len(data_str_list)
    return translations.get("batch_file_created", "バッチ用ファイル作成完了({data_num}件のデータ、{file_num}ファイル)").format(data_num=data_num, file_num=file_num)

def create_pex_trans_file(values):
    """PapyrusPex翻訳バッチ用ファイル作成"""
    s_lang = values['-s_lang-']
    d_lang = values['-d_lang-']
    trans_lang_str = "_pex_" + s_lang + "_" + d_lang
    mod_ext = [".pex"]
    data_str_list = get_trans_list(values, mod_ext, "", trans_lang_str)
    file_name = "pex_trans"
    if values["trans_source"] == "trans_source_0":
        file_name += "_xml"
    elif values["trans_source"] == "trans_source_1":
        file_name += "_sst"
    elif values["trans_source"] == "trans_source_2":
        file_name += "_api"
    file_num = split_list_to_files(data_str_list, values['-txt_path-'], int(values['-bat_list_max_num-']), file_name)
    data_num = len(data_str_list)
    return translations.get("batch_file_created", "バッチ用ファイル作成完了({data_num}件のデータ、{file_num}ファイル)").format(data_num=data_num, file_num=file_num)

def create_mcm_trans_file(values):
    """MCM翻訳バッチ用ファイル作成"""
    skyrim_lang = values['-skyrim_lang-']
    s_lang = values['-s_lang-']
    d_lang = values['-d_lang-']
    trans_lang_str = "_mcm_" + s_lang + "_" + d_lang
    trans_mod_str = "_" + skyrim_lang
    mod_ext = [".txt"]
    data_str_list = get_trans_list(values, mod_ext, trans_mod_str, trans_lang_str)
    file_name = "mcm_trans"
    if values["trans_source"] == "trans_source_0":
        file_name += "_xml"
    elif values["trans_source"] == "trans_source_1":
        file_name += "_sst"
    elif values["trans_source"] == "trans_source_2":
        file_name += "_api"
    file_num = split_list_to_files(data_str_list, values['-txt_path-'], int(values['-bat_list_max_num-']), file_name)
    data_num = len(data_str_list)
    return translations.get("batch_file_created", "バッチ用ファイル作成完了({data_num}件のデータ、{file_num}ファイル)").format(data_num=data_num, file_num=file_num)

def replace_mcm_interface_file(values):
    """MCMインターフェースファイル置換"""

    # 翻訳元ファイルは -mcm_interface_path- の interface/translations 以下で「_[skyrim_lang].txt」をすべて対象に
    src_dir = values['-mcm_interface_path-']
    dst_dir = values['-mod_path-']  # 置換先は-mod_path-のinterface/translations以下
    skyrim_lang = values['-skyrim_lang-'].lower()

    # interface/translations フォルダをサブフォルダも含めて検索し、_[skyrim_lang].txtで終わるファイルをすべて取得
    def find_src_files(base_dir, lang_suffix):
        result = []
        for root, _, files in os.walk(base_dir):
            norm_root = root.replace("\\", "/").lower()
            if "interface/translations" in norm_root:
                for file in files:
                    if file.lower().endswith(f"_{lang_suffix}.txt"):
                        result.append(os.path.join(root, file))
        return result

    # 置換先も同じファイル名をinterface/translations以下から探す
    def find_dst_file(base_dir, filename):
        for root, _, files in os.walk(base_dir):
            norm_root = root.replace("\\", "/").lower()
            if "interface/translations" in norm_root:
                for file in files:
                    if file.lower() == filename:
                        return os.path.join(root, file)
        return None

    # 置換元ファイルリスト
    src_files = find_src_files(src_dir, skyrim_lang)
    if not src_files:
        eg.popup("置換元ファイルが見つかりません。")
        return

    replaced_count = 0
    for src in src_files:
        filename = os.path.basename(src).lower()
        dst = find_dst_file(dst_dir, filename)
        if dst:
            try:
                shutil.copy2(src, dst)
                replaced_count += 1
            except Exception as e:
                eg.popup(f"{filename} の置換に失敗: {e}")

    if replaced_count == 0:
        eg.popup("置換先フォルダに同名ファイルがありません。")
    else:
        eg.popup(f"置換完了: {replaced_count}件のファイルを置換しました。")

def replace_mcm_interface_file_with_progress(values, window=None):
    """MCMインターフェースファイル置換（別スレッドで実行し、処理中ダイアログを表示、多言語対応）"""
    progress_window = None
    result_queue = queue.Queue()

    def task():
        src_dir = values['-mcm_interface_path-']
        dst_dir = values['-mod_path-']
        skyrim_lang = values['-skyrim_lang-'].lower()

        def find_src_files(base_dir, lang_suffix):
            result = []
            for root, _, files in os.walk(base_dir):
                norm_root = root.replace("\\", "/").lower()
                if "interface/translations" in norm_root:
                    for file in files:
                        if file.lower().endswith(f"_{lang_suffix}.txt"):
                            result.append(os.path.join(root, file))
            return result

        def find_dst_file(base_dir, filename):
            for root, _, files in os.walk(base_dir):
                norm_root = root.replace("\\", "/").lower()
                if "interface/translations" in norm_root:
                    for file in files:
                        if file.lower() == filename:
                            return os.path.join(root, file)
            return None

        src_files = find_src_files(src_dir, skyrim_lang)
        if not src_files:
            result_queue.put(("error", translations.get("error_mcm_src_not_found", "置換元ファイルが見つかりません。")))
            return

        replaced_count = 0
        errors = []
        for src in src_files:
            filename = os.path.basename(src).lower()
            dst = find_dst_file(dst_dir, filename)
            if dst:
                try:
                    shutil.copy2(src, dst)
                    replaced_count += 1
                except Exception as e:
                    errors.append(translations.get("error_mcm_replace_failed", "{filename} の置換に失敗: {error}").format(filename=filename, error=str(e)))

        if replaced_count == 0:
            result_queue.put(("error", translations.get("error_mcm_dst_not_found", "置換先フォルダに同名ファイルがありません。")))
        else:
            result_queue.put(("success", translations.get("mcm_replace_success", "置換完了: {count}件のファイルを置換しました。").format(count=replaced_count)))
        for err in errors:
            result_queue.put(("error", err))

    # ダイアログ表示（多言語対応）
    progress_window = eg.Window(
        translations.get("progress_title", "処理中"),
        [[eg.Text(translations.get("mcm_replace_progress", "MCM Interfaceファイル置換中です。しばらくお待ちください..."))]],
        modal=True, finalize=True
    )
    thread = threading.Thread(target=task, daemon=True)
    thread.start()
    # スレッド終了まで待機しつつ、結果をメインスレッドでポップアップ
    while True:
        event, _ = progress_window.read(timeout=100)
        try:
            msg_type, msg = result_queue.get_nowait()
            progress_window.close()
            eg.popup(msg)
            break
        except queue.Empty:
            pass
        if not thread.is_alive():
            # スレッド終了後もキューに何か残っていれば表示
            try:
                while True:
                    msg_type, msg = result_queue.get_nowait()
                    progress_window.close()
                    eg.popup(msg)
            except queue.Empty:
                pass
            break
        if event == eg.WINDOW_CLOSED:
            break
    progress_window.close()

def show_progress_with_worker(worker_func, args, msg="バッチファイル作成中です。しばらくお待ちください..."):
    result_queue = queue.Queue()
    def task():
        try:
            result = worker_func(*args)
            result_queue.put(("success", result))
        except Exception as e:
            result_queue.put(("error", str(e)))
    progress_window = eg.Window("処理中", [[eg.Text(msg)]], modal=True, finalize=True)
    thread = threading.Thread(target=task, daemon=True)
    thread.start()
    while True:
        event, _ = progress_window.read(timeout=100)
        try:
            msg_type, msg = result_queue.get_nowait()
            progress_window.close()
            if msg_type == "success":
                eg.popup(str(msg))
            else:
                eg.popup("エラー: " + str(msg))
            break
        except queue.Empty:
            pass
        if not thread.is_alive():
            break
        if event == eg.WINDOW_CLOSED:
            break
    progress_window.close()

def create_trans_xml_batch_text_data(values, mod_file_list, xml_file_list):
    """バッチ翻訳用テキストデータ作成"""
    data_str_list = []
    for mod_file, xml_file in zip(mod_file_list, xml_file_list):
        data_str = ""
        data_str += "StartRule\n"
        data_str += "LangSource=" + values['-s_lang-'] + "\n"
        data_str += "LangDest=" + values['-d_lang-'] + "\n"
        data_str += "usedatadir=0\n"
        data_str += "command=loadfile:" + mod_file + "\n"
        data_str += "command=importxml:" + values['trans_target'].replace("trans_target_", "") + ":" + values['trans_mode'].replace("trans_mode_", "") + ":" + xml_file + "\n"
        data_str += "command=finalize\n"
        data_str += "command=CloseFile\n"
        data_str += "EndRule\n\n"
        data_str_list.append(data_str)
    return data_str_list

def create_trans_sst_batch_text_data(values, mod_file_list, sst_file_list):
    """バッチ翻訳用テキストデータ作成"""
    data_str_list = []
    for mod_file, sst_file in zip(mod_file_list, sst_file_list):
        data_str = ""
        data_str += "StartRule\n"
        data_str += "LangSource=" + values['-s_lang-'] + "\n"
        data_str += "LangDest=" + values['-d_lang-'] + "\n"
        data_str += "usedatadir=0\n"
        data_str += "command=loadfile:" + mod_file + "\n"
        data_str += "command=importsst:" + values['trans_target'].replace("trans_target_", "") + ":" + values['trans_mode'].replace("trans_mode_", "") + ":" + sst_file + "\n"
        data_str += "command=finalize\n"
        data_str += "command=CloseFile\n"
        data_str += "EndRule\n\n"
        data_str_list.append(data_str)
    return data_str_list

def create_trans_api_batch_text_data(values, mod_file_list):
    """バッチ翻訳用テキストデータ作成"""
    data_str_list = []
    for mod_file in mod_file_list:
        data_str = ""
        data_str += "StartRule\n"
        data_str += "LangSource=" + values['-s_lang-'] + "\n"
        data_str += "LangDest=" + values['-d_lang-'] + "\n"
        data_str += "usedatadir=0\n"
        data_str += "command=loadfile:" + mod_file + "\n"
        data_str += "command=apitranslation:" + values['api_trans'].replace("api_trans_", "") + ":"
        if values['chk_api_heuristic']:
            data_str += "1\n"
        else:
            data_str += "0\n"
        data_str += "command=finalize\n"
        data_str += "command=CloseFile\n"
        data_str += "EndRule\n\n"
        data_str_list.append(data_str)
    return data_str_list

def split_list_to_files(data_list, output_dir, items_per_file, base_filename="output"):
    """
    リストの内容を指定件数で分割してファイルに書き込む
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    file_num = 0
    for i in range(0, len(data_list), items_per_file):
        chunk = data_list[i:i + items_per_file]
        file_number = i // items_per_file + 1
        filename = os.path.join(output_dir, f"{base_filename}_{file_number}.txt")
        file_num += 1
        with open(filename, 'w', encoding='utf-8') as f:
            for item in chunk:
                f.write(str(item) + '\n')
    return file_num

def main():
    global mod_folder, xml_folder, sst_folder, txt_folder
    global skyrim_lang, source_lang, dest_lang
    global trans_target, trans_mode, bat_list_max_num
    global trans_source, api_trans, api_heuristic, language
    global current_profile
    global translations
    load_translations(language)

    # 前回選択プロファイルを初期化
    current_profile = load_last_profile() or "default"

    # 利用可能な言語リスト（lang ディレクトリから取得）
    available_languages = []
    if os.path.exists(LANG_DIR):
        for file in os.listdir(LANG_DIR):
            if file.endswith(".json"):
                available_languages.append(os.path.splitext(file)[0])
    else:
        available_languages = ["ja", "en"]  # デフォルト言語

    profile_list = get_profile_list()
    if current_profile not in profile_list:
        current_profile = profile_list[0] if profile_list else "default"

    # プロファイル決定後、必ず設定内容をロード
    load_init()

    layout = [
        [eg.Text("プロファイル:"),
         eg.Combo(profile_list + ["新規作成..."], default_value=current_profile, size=(20, 1), key="-profile-", enable_events=True),
         eg.Text("　　"),
         eg.Text(translations.get("language_label", "言語：")),
         eg.Combo(available_languages, default_value=language, size=(20, 1), key="-language-", enable_events=True)],
        [eg.Text("　")],
        [eg.Text(translations.get("mod_path_label", "modファイル保存パス：")),
         eg.Combo(values=mod_path_history, default_value=mod_folder, size=(130, 1), key="-mod_path-"), eg.Button(translations.get("browse", "参照"), key="-mod_path_browse-")],
        [eg.Text(translations.get("txt_path_label", "翻訳バッチ用Txtファイル出力先パス：")),
         eg.Combo(values=txt_path_history, default_value=txt_folder, size=(130, 1), key="-txt_path-"), eg.Button(translations.get("browse", "参照"), key="-txt_path_browse-")],
        [eg.Text("　")],
        [eg.Text(translations.get("skyrim_lang_label", "Skyrim言語：")),
         eg.Combo(values=skyrim_lang_history, default_value=skyrim_lang, size=(30, 1), key="-skyrim_lang-")],
        [eg.Text(translations.get("source_lang_label", "元言語：")),
         eg.Combo(values=source_lang_history, default_value=source_lang, size=(30, 1), key="-s_lang-"),
         eg.Text("　　"),
         eg.Text(translations.get("dest_lang_label", "翻訳先言語：")),
         eg.Combo(values=dest_lang_history, default_value=dest_lang, size=(30, 1), key="-d_lang-")],
        [eg.Text("　")],
        [eg.Text(translations.get("trans_target_label", "翻訳対象：")),
         eg.Radio(translations.get("trans_target_all", "すべて"), group_id="trans_target", key="trans_target_0", default=True, enable_events=True),
         eg.Text("　"),
         eg.Radio(translations.get("trans_target_untranslated", "未翻訳"), group_id="trans_target", key="trans_target_1", enable_events=True),
         eg.Text("　"),
         eg.Radio(translations.get("trans_target_unverified_to_in_progress", "未検証→進行中"), group_id="trans_target", key="trans_target_2", enable_events=True),
         eg.Text("　"),
         eg.Radio(translations.get("trans_target_in_progress", "進行中"), group_id="trans_target", key="trans_target_3", enable_events=True)],
        [eg.Text(translations.get("trans_mode_label", "翻訳モード：")),
         eg.Radio(translations.get("trans_mode_formid", "フォームID"), group_id="trans_mode", key="trans_mode_0", default=True, enable_events=True),
         eg.Text("　"),
         eg.Radio(translations.get("trans_mode_strict", "StrictFormID+String"), group_id="trans_mode", key="trans_mode_1", enable_events=True),
         eg.Text("　"),
         eg.Radio(translations.get("trans_mode_relax", "relaxFormID+String"), group_id="trans_mode", key="trans_mode_2", enable_events=True),
         eg.Text("　"),
         eg.Radio(translations.get("trans_mode_string", "Stringのみ"), group_id="trans_mode", key="trans_mode_3", enable_events=True)],
        [eg.Text("　")],
        [eg.Text(translations.get("main_trans_source_label", "メイン翻訳ソース："))],
        [eg.Text("　"),
         eg.Radio(translations.get("xml_label", "XML"), group_id="trans_source", key="trans_source_0", default=True, enable_events=True)],
        [eg.Text("　　"),
         eg.Text(translations.get("xml_path_label", "インポート翻訳XMLファイル保存パス：")),
         eg.Combo(values=xml_path_history, default_value=xml_folder, size=(130, 1), key="-xml_path-"), eg.Button(translations.get("browse", "参照"), key="-xml_path_browse-")],
        [eg.Text("　"),
         eg.Radio(translations.get("sst_label", "SST"), group_id="trans_source", key="trans_source_1", enable_events=True)],
    [eg.Text("　　"), 
     eg.Text(translations.get("sst_path_label", "インポート翻訳SSTファイル保存パス：")), 
     eg.Combo(values=sst_path_history, default_value=sst_folder, size=(130, 1), key="-sst_path-"), eg.Button(translations.get("browse", "参照"), key="-sst_path_browse-")],
        [eg.Text("　"), 
         eg.Radio(translations.get("api_label", "API"), group_id="trans_source", key="trans_source_2", enable_events=True)],
        [eg.Text("　　"), 
         eg.Radio(translations.get("api_ms_translator", "MStranslator"), group_id="api_trans", key="api_trans_0", default=True, enable_events=True), 
         eg.Text("　"), 
         eg.Radio(translations.get("api_google", "Google"), group_id="api_trans", key="api_trans_5", enable_events=True), 
         eg.Text("　"), 
         eg.Radio(translations.get("api_deepl", "DeepL"), group_id="api_trans", key="api_trans_6", enable_events=True)],
        [eg.Text("　　"), 
         eg.Checkbox(translations.get("heuristic_label", "ヒューリスティックな文字列除外"), key="chk_api_heuristic")],
        [eg.Text("　")],
        [eg.Text("　")],
    [eg.Text(translations.get("mcm_interface_path_label", "MCM翻訳Interfaceファイル保存パス：")),
     eg.Combo(values=mcm_interface_path_history, default_value=mcm_interface_folder, size=(130, 1), key="-mcm_interface_path-"), eg.Button(translations.get("browse", "参照"), key="-mcm_interface_path_browse-")], 
        [eg.Text("　")],
        [eg.Text(translations.get("batch_max_items_label", "翻訳バッチ１ファイル内最大件数：")), 
         eg.InputText("100", size=(15, 1), key="-bat_list_max_num-")],
        [eg.Text("　")],
        [
            eg.Button(translations.get("create_esp_button", "esp,esm翻訳バッチ用ファイル作成"), key="-create_t_esp-"), 
            eg.Text("　　"),
            eg.Button(translations.get("create_pex_button", "PapyrusPex翻訳バッチ用ファイル作成"), key="-create_t_pex-"), 
            eg.Text("　　"),
            eg.Button(translations.get("create_mcm_button", "MCM翻訳バッチ用ファイル作成"), key="-create_t_mcm-"),
            eg.Text("　　"),
            eg.Button(translations.get("create_mcm_if_rep_button", "MCM Interfaceファイル置き換え処理"), key="-create_rep_mcm-")
        ]
    ]

    window = eg.Window(
        translations.get("window_title", "xTranslatorバッチプロセッサ用ファイル作成ツール") + "　" + 
        translations.get("version", "ver.") + APP_VERSION, 
        layout, finalize=True, resizable=True
    )

    # tkinter root for filedialog; keep hidden
    _tk_root = tk.Tk()
    _tk_root.withdraw()

    window["-mod_path-"].update(mod_folder)
    window["-xml_path-"].update(xml_folder)
    window["-sst_path-"].update(sst_folder)
    window["-txt_path-"].update(txt_folder)
    window["-mcm_interface_path-"].update(mcm_interface_folder)  # 追加
    window["-skyrim_lang-"].update(skyrim_lang)
    window["-s_lang-"].update(source_lang)
    window["-d_lang-"].update(dest_lang)
    window["trans_target_" + str(trans_target)].select()
    window["trans_mode_" + str(trans_mode)].select()
    window["-bat_list_max_num-"].update(bat_list_max_num)
    window["trans_source_" + str(trans_source)].select()
    window["api_trans_" + str(api_trans)].select()
    window["-language-"].update(language)
    if int(api_heuristic) == 1:
        window["chk_api_heuristic"].update(value=True)
    else:
        window["chk_api_heuristic"].update(value=False)

    while True:
        event, values = window.read()

        if event == eg.WINDOW_CLOSED:
            save_init(values)
            save_last_profile(current_profile)
            break

        elif event == "-profile-":
            selected_profile = values["-profile-"]
            if selected_profile == "新規作成...":
                new_profile = eg.popup_get_text("新しいプロファイル名を入力してください")
                if new_profile:
                    current_profile = new_profile
                    save_init(values)
                    save_last_profile(current_profile)
                    load_init()
                    window.close()
                    main()
                    break
            else:
                current_profile = selected_profile
                save_last_profile(current_profile)
                load_init()
                window.close()
                main()
                break
        # Browse button handlers: use current input text as initialdir if valid, otherwise cwd
        elif event == "-mod_path_browse-":
            current_path = values["-mod_path-"]
            init_dir = current_path if os.path.isdir(current_path) else os.path.dirname(current_path) if os.path.exists(current_path) else os.getcwd()
            selected = filedialog.askdirectory(parent=_tk_root, initialdir=init_dir, title=translations.get("mod_path_label", "Mod File Path:"))
            if selected:
                window["-mod_path-"].update(selected)

        elif event == "-txt_path_browse-":
            current_path = values["-txt_path-"]
            init_dir = current_path if os.path.isdir(current_path) else os.path.dirname(current_path) if os.path.exists(current_path) else os.getcwd()
            selected = filedialog.askdirectory(parent=_tk_root, initialdir=init_dir, title=translations.get("txt_path_label", "Translation Batch Text File Output Path:"))
            if selected:
                window["-txt_path-"].update(selected)

        elif event == "-xml_path_browse-":
            current_path = values["-xml_path-"]
            init_dir = current_path if os.path.isdir(current_path) else os.path.dirname(current_path) if os.path.exists(current_path) else os.getcwd()
            selected = filedialog.askdirectory(parent=_tk_root, initialdir=init_dir, title=translations.get("xml_path_label", "Import Translation XML File Path:"))
            if selected:
                window["-xml_path-"].update(selected)

        elif event == "-sst_path_browse-":
            current_path = values["-sst_path-"]
            init_dir = current_path if os.path.isdir(current_path) else os.path.dirname(current_path) if os.path.exists(current_path) else os.getcwd()
            selected = filedialog.askdirectory(parent=_tk_root, initialdir=init_dir, title=translations.get("sst_path_label", "Import Translation SST File Path:"))
            if selected:
                window["-sst_path-"].update(selected)

        elif event == "-mcm_interface_path_browse-":
            current_path = values["-mcm_interface_path-"]
            init_dir = current_path if os.path.isdir(current_path) else os.path.dirname(current_path) if os.path.exists(current_path) else os.getcwd()
            selected = filedialog.askdirectory(parent=_tk_root, initialdir=init_dir, title=translations.get("mcm_interface_path_label", "MCM translation interface file save path："))
            if selected:
                window["-mcm_interface_path-"].update(selected)

        elif event == "-create_t_esp-":
            if check_input(window, values) == False:
                continue
            show_progress_with_worker(create_esp_trans_file, (values,), "esp,esmバッチファイル作成中です。しばらくお待ちください...")

        elif event == "-create_t_pex-":
            if check_input(window, values) == False:
                continue
            show_progress_with_worker(create_pex_trans_file, (values,), "PapyrusPexバッチファイル作成中です。しばらくお待ちください...")

        elif event == "-create_t_mcm-":
            if check_input(window, values) == False:
                continue
            show_progress_with_worker(create_mcm_trans_file, (values,), "MCMバッチファイル作成中です。しばらくお待ちください...")

        elif event == "-create_rep_mcm-":
            if eg.popup_yes_no(translations.get("mcm_if_rep_confirm", "MCM Interfaceファイル置き換え処理を実行しますか？")) != "Yes":
                continue

            if check_input(window, values) == False:
                continue
            replace_mcm_interface_file_with_progress(values)
        elif event == "-language-":
            language = values["-language-"]
            save_init(values)
            load_translations(language)
            window.close()
            main()
            break

    window.close()

if __name__ == '__main__' and sys.executable:
    load_init()
    main()
