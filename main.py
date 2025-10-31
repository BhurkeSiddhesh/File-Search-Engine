import PySimpleGUI as sg
import os
import sys
import configparser
import multiprocessing
import time
from indexing import create_index, save_index, load_index
from search import search
from llm_integration import summarize, get_embeddings
from file_processing import extract_text
from background import start_background_indexing

def create_main_window():
    """Creates the main window of the application."""

    layout = [
        [sg.Text("Welcome to your personal File Search Engine!", font=("Helvetica", 16))],
        [sg.Multiline(size=(100, 25), key="-RESULTS-", disabled=True, autoscroll=True, reroute_stdout=True, reroute_cprint=True)],
        [sg.Multiline(size=(80, 5), key="-QUERY-", enter_submits=True)],
        [sg.Button("Search", key="-SEARCH-", bind_return_key=True), sg.Button("Settings", key="-SETTINGS-"), sg.Button("Exit")]
    ]

    return sg.Window("File Search Engine", layout, finalize=True)

def create_settings_window(config):
    """Creates the settings window."""

    general_tab = [[sg.Text("Folder to Index:"), sg.Input(default_text=config.get('General', 'folder', fallback=''), key="-FOLDER-", enable_events=True), sg.FolderBrowse()],
                   [sg.Checkbox("Enable automatic background indexing", default=config.getboolean('General', 'auto_index', fallback=False), key="-AUTO-INDEX-")]]

    api_keys_tab = [[sg.Text("OpenAI API Key:"), sg.Input(default_text=config.get('APIKeys', 'openai_api_key', fallback=''), key="-OPENAI-API-KEY-", password_char='*')]]

    local_llm_tab = [[sg.Text("Local Model Path:"), sg.Input(default_text=config.get('LocalLLM', 'model_path', fallback=''), key="-LOCAL-MODEL-PATH-"), sg.FileBrowse()],
                     [sg.Text("LLM Provider:"), sg.Radio("OpenAI", "LLM_PROVIDER", key="-OPENAI-", default=config.get('LocalLLM', 'provider', fallback='openai') == 'openai'), sg.Radio("Local", "LLM_PROVIDER", key="-LOCAL-", default=config.get('LocalLLM', 'provider', fallback='openai') == 'local')]]

    layout = [[sg.TabGroup([[sg.Tab("General", general_tab),
                              sg.Tab("API Keys", api_keys_tab),
                              sg.Tab("Local LLM", local_llm_tab)]])],
              [sg.Button("Save"), sg.Button("Cancel")]]

    return sg.Window("Settings", layout, finalize=True)

def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config

def save_config(values):
    config = configparser.ConfigParser()
    config['General'] = {'folder': values['-FOLDER-'], 'auto_index': str(values['-AUTO-INDEX-'])}
    config['APIKeys'] = {'openai_api_key': values['-OPENAI-API-KEY-']}
    config['LocalLLM'] = {'model_path': values['-LOCAL-MODEL-PATH-'], 'provider': 'openai' if values['-OPENAI-'] else 'local'}
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def main():
    """Main application loop."""
    if '--screenshot' in sys.argv:
        config = load_config()
        main_window = create_main_window()
        time.sleep(1)
        main_window.save_window_screenshot_to_disk('jules-scratch/verification/main_window.png')
        settings_window = create_settings_window(config)
        time.sleep(1)
        settings_window.save_window_screenshot_to_disk('jules-scratch/verification/settings_window.png')
        main_window.close()
        settings_window.close()
        sys.exit(0)

    config = load_config()
    main_window = create_main_window()
    settings_window = None
    index = None
    docs = []
    tags = []
    conversation_history = []
    background_process = None

    if config.has_section('General') and config.get('General', 'folder'):
        folder = config.get('General', 'folder')
        provider = config.get('LocalLLM', 'provider', fallback='openai')
        api_key = config.get('APIKeys', 'openai_api_key', fallback=None)
        model_path = config.get('LocalLLM', 'model_path', fallback=None)

        try:
            if os.path.exists('index.faiss'):
                sg.popup_auto_close("Loading existing index...", title="Loading", auto_close_duration=2)
                index, docs, tags = load_index('index.faiss')
                print("Loaded existing index.")
            else:
                sg.popup_quick_message("Creating new index, this may take a while...", background_color='red', text_color='white')
                index, docs, tags = create_index(folder, provider, api_key, model_path)
                if index:
                    save_index(index, docs, tags, 'index.faiss')
                    print("Created and saved new index.")
                sg.popup("Index created successfully!")

        except Exception as e:
            sg.popup_error(f"Error loading index: {e}")

    if config.getboolean('General', 'auto_index', fallback=False):
        background_process = multiprocessing.Process(target=start_background_indexing)
        background_process.start()

    while True:
        window, event, values = sg.read_all_windows()

        if event == sg.WIN_CLOSED or event == "Exit":
            if background_process:
                background_process.terminate()
            break

        if window == main_window:
            if event == "-SETTINGS-":
                if not settings_window:
                    settings_window = create_settings_window(config)
            elif event == "-SEARCH-":
                query = values["-QUERY-"].strip()
                if query and index:
                    conversation_history.append(f"User: {query}")
                    context = "\n".join(conversation_history)

                    provider = config.get('LocalLLM', 'provider', fallback='openai')
                    api_key = config.get('APIKeys', 'openai_api_key', fallback=None)
                    model_path = config.get('LocalLLM', 'model_path', fallback=None)
                    embeddings_model = get_embeddings(provider, api_key, model_path)

                    results = search(context, index, docs, tags, embeddings_model)

                    main_window["-RESULTS-"].update("")
                    print(f"Found {len(results)} results for '{query}':\n")
                    for result in results:
                        summary = summarize(result['document'], provider, api_key, model_path)
                        print(f"Result:\n{result['document']}\n")
                        print(f"Summary:\n{summary}\n")
                        print(f"Tags: {result['tags']}\n")
                        conversation_history.append(f"System: {summary}")
                        print("-" * 50)

        if window == settings_window:
            if event == "Save":
                save_config(values)
                config = load_config()
                sg.popup("Settings saved!")
                settings_window.close()
                settings_window = None
            elif event == "Cancel":
                settings_window.close()
                settings_window = None

    main_window.close()
    if settings_window:
        settings_window.close()

if __name__ == "__main__":
    main()
