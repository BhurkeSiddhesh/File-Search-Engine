import PySimpleGUI as sg
import os
import sys
import configparser
import multiprocessing
import time
import json
from indexing import create_index, save_index, load_index
from search import search
from llm_integration import summarize, get_embeddings
from file_processing import extract_text
from background import start_background_indexing

# Apple-style color scheme
APPLE_LIGHT_BG = '#f5f5f7'
APPLE_DARK_BG = '#1d1d1f'
APPLE_ACCENT_BLUE = '#007AFF'
APPLE_WHITE = '#FFFFFF'
APPLE_GRAY = '#8e8e93'
APPLE_DARK_TEXT = '#1d1d1f'
APPLE_LIGHT_TEXT = '#f2f2f7'
APPLE_SEPARATOR = '#d2d2d7'

def create_main_window(search_history=None):
    """Creates the main window of the application with Apple-style design."""
    
    # Set the theme to match Apple aesthetics
    sg.theme('SystemDefault')
    
    if search_history is None:
        search_history = []
    
    # Create the search input with rounded corners and padding
    search_layout = [
        [sg.Text("File Search Engine", font=("SF Pro Display", 24, "bold"), 
                 text_color=APPLE_DARK_TEXT, pad=((20, 20), (20, 10)))],
        [sg.HorizontalSeparator(color=APPLE_SEPARATOR)],
        [sg.Text("Enter your search query:", font=("SF Pro Text", 12), 
                 text_color=APPLE_GRAY, pad=((20, 20), (10, 5)))],
        [sg.Combo(search_history, key="-SEARCH-HISTORY-", 
                  size=(50, 5), font=("SF Pro Text", 12),
                  pad=((20, 10), (5, 5)),
                  background_color=APPLE_WHITE,
                  text_color=APPLE_DARK_TEXT,
                  enable_events=True),
         sg.Button("🔄", key="-REFRESH-HISTORY-", 
                   button_color=(APPLE_WHITE, APPLE_GRAY),
                   pad=((0, 0), (5, 5)),
                   border_width=0,
                   font=("SF Pro Text", 10))],
        [sg.InputText(key="-QUERY-", size=(60, 1), font=("SF Pro Text", 14),
                      pad=((20, 20), (5, 15)), 
                      background_color=APPLE_WHITE,
                      border_width=1,
                      text_color=APPLE_DARK_TEXT)],
        [sg.Button("🔍 Search", key="-SEARCH-", font=("SF Pro Text", 12), 
                   button_color=(APPLE_WHITE, APPLE_ACCENT_BLUE),
                   pad=((20, 10), (0, 15)), 
                   border_width=0,
                   focus=True),
         sg.Button("🌙 Dark Mode", key="-DARK-MODE-", font=("SF Pro Text", 12),
                   button_color=(APPLE_WHITE, APPLE_GRAY),
                   pad=((0, 10), (0, 15)),
                   border_width=0),
         sg.Button("⚙️ Settings", key="-SETTINGS-", font=("SF Pro Text", 12),
                   button_color=('white', APPLE_GRAY),
                   pad=((0, 10), (0, 15)),
                   border_width=0),
         sg.Button("✕ Exit", key="Exit", font=("SF Pro Text", 12),
                   button_color=('white', '#ff3b30'),
                   pad=((0, 20), (0, 15)),
                   border_width=0)],
        [sg.HorizontalSeparator(color=APPLE_SEPARATOR)],
        [sg.Text("Search Results:", font=("SF Pro Text", 14, "bold"), 
                 text_color=APPLE_DARK_TEXT, pad=((20, 20), (15, 5)))],
        [sg.Multiline(size=(90, 30), key="-RESULTS-", disabled=True, 
                      autoscroll=True, reroute_stdout=False, reroute_cprint=False,
                      font=("SF Pro Text", 11),
                      background_color=APPLE_WHITE,
                      text_color=APPLE_DARK_TEXT,
                      pad=((20, 20), (5, 20)),
                      border_width=1)]
    ]

    return sg.Window("File Search Engine", search_layout, finalize=True, 
                     size=(800, 700),
                     background_color=APPLE_LIGHT_BG)

def create_settings_window(config):
    """Creates the settings window with Apple-style design."""
    
    # General tab with Apple-style layout
    general_tab = [
        [sg.Text("Folder to Index:", font=("SF Pro Text", 12), text_color=APPLE_DARK_TEXT, pad=((10, 5), (10, 5)))],
        [sg.Input(default_text=config.get('General', 'folder', fallback=''), 
                  key="-FOLDER-", 
                  font=("SF Pro Text", 11),
                  size=(50, 1),
                  pad=((10, 5), (5, 15)),
                  enable_events=True, 
                  background_color=APPLE_WHITE,
                  text_color=APPLE_DARK_TEXT), 
         sg.FolderBrowse(button_text="Browse", 
                         button_color=(APPLE_WHITE, APPLE_ACCENT_BLUE),
                         pad=((5, 10), (5, 15)),
                         font=("SF Pro Text", 11))],
        [sg.Checkbox("Enable automatic background indexing", 
                     default=config.getboolean('General', 'auto_index', fallback=False), 
                     key="-AUTO-INDEX-",
                     font=("SF Pro Text", 12),
                     text_color=APPLE_DARK_TEXT,
                     pad=((10, 5), (10, 15)))]
    ]

    # API Keys tab
    api_keys_tab = [
        [sg.Text("OpenAI API Key:", font=("SF Pro Text", 12), text_color=APPLE_DARK_TEXT, pad=((10, 5), (10, 5)))],
        [sg.Input(default_text=config.get('APIKeys', 'openai_api_key', fallback=''), 
                  key="-OPENAI-API-KEY-", 
                  password_char='*',
                  font=("SF Pro Text", 11),
                  size=(50, 1),
                  pad=((10, 10), (5, 15)),
                  background_color=APPLE_WHITE,
                  text_color=APPLE_DARK_TEXT)]
    ]

    # Local LLM tab
    local_llm_tab = [
        [sg.Text("Local Model Path:", font=("SF Pro Text", 12), text_color=APPLE_DARK_TEXT, pad=((10, 5), (10, 5)))],
        [sg.Input(default_text=config.get('LocalLLM', 'model_path', fallback=''), 
                  key="-LOCAL-MODEL-PATH-", 
                  font=("SF Pro Text", 11),
                  size=(50, 1),
                  pad=((10, 5), (5, 10)),
                  background_color=APPLE_WHITE,
                  text_color=APPLE_DARK_TEXT), 
         sg.FileBrowse(button_text="Browse", 
                       button_color=(APPLE_WHITE, APPLE_ACCENT_BLUE),
                       pad=((5, 10), (5, 10)),
                       font=("SF Pro Text", 11))],
        [sg.Text("LLM Provider:", font=("SF Pro Text", 12), text_color=APPLE_DARK_TEXT, pad=((10, 5), (10, 5)))],
        [sg.Radio("OpenAI", "LLM_PROVIDER", 
                  key="-OPENAI-", 
                  default=config.get('LocalLLM', 'provider', fallback='openai') == 'openai',
                  font=("SF Pro Text", 11),
                  text_color=APPLE_DARK_TEXT,
                  pad=((10, 10), (5, 5))), 
         sg.Radio("Local", "LLM_PROVIDER", 
                  key="-LOCAL-", 
                  default=config.get('LocalLLM', 'provider', fallback='openai') == 'local',
                  font=("SF Pro Text", 11),
                  text_color=APPLE_DARK_TEXT,
                  pad=((10, 10), (5, 15)))]
    ]

    layout = [
        [sg.TabGroup([[sg.Tab("General", general_tab, font=("SF Pro Text", 12), title_color=APPLE_DARK_TEXT),
                       sg.Tab("API Keys", api_keys_tab, font=("SF Pro Text", 12), title_color=APPLE_DARK_TEXT),
                       sg.Tab("Local LLM", local_llm_tab, font=("SF Pro Text", 12), title_color=APPLE_DARK_TEXT)]], 
                     font=("SF Pro Text", 12),
                     selected_row_colors=APPLE_ACCENT_BLUE)],
        [sg.Button("Save", button_color=(APPLE_WHITE, APPLE_ACCENT_BLUE), 
                   font=("SF Pro Text", 12),
                   pad=((10, 10), (15, 15)),
                   border_width=0),
         sg.Button("Cancel", button_color=(APPLE_WHITE, '#8e8e93'), 
                   font=("SF Pro Text", 12),
                   pad=((0, 10), (15, 15)),
                   border_width=0)]
    ]

    return sg.Window("Settings", layout, finalize=True, 
                     size=(600, 500),
                     background_color=APPLE_LIGHT_BG)

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

def format_search_results(results, query):
    """Format search results in an Apple-style card-like format."""
    formatted_output = f"🔍 Search Results for: '{query}'\n"
    formatted_output += "="*60 + "\n\n"
    
    for i, result in enumerate(results, 1):
        formatted_output += f"📄 Result {i}\n"
        formatted_output += "-" * 30 + "\n"
        formatted_output += f"Document Preview:\n{result['document'][:300]}...\n\n"
        formatted_output += f"💡 Summary:\n{result['summary']}\n\n"
        formatted_output += f"🏷️  Tags: {', '.join(result['tags'])}\n"
        formatted_output += "="*60 + "\n\n"
    
    return formatted_output

def load_search_history():
    """Load search history from file."""
    try:
        with open('search_history.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_search_history(history):
    """Save search history to file."""
    with open('search_history.json', 'w') as f:
        json.dump(history, f)

def main():
    """Main application loop."""
    if '--screenshot' in sys.argv:
        config = load_config()
        search_history = load_search_history()
        main_window = create_main_window(search_history)
        time.sleep(1)
        main_window.save_window_screenshot_to_disk('jules-scratch/verification/main_window.png')
        settings_window = create_settings_window(config)
        time.sleep(1)
        settings_window.save_window_screenshot_to_disk('jules-scratch/verification/settings_window.png')
        main_window.close()
        settings_window.close()
        sys.exit(0)

    config = load_config()
    search_history = load_search_history()
    main_window = create_main_window(search_history)
    settings_window = None
    index = None
    docs = []
    tags = []
    conversation_history = []
    background_process = None
    dark_mode = False  # Track dark mode state

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
            if event == "-DARK-MODE-":
                # Toggle dark mode
                dark_mode = not dark_mode
                if dark_mode:
                    # Apply dark mode colors
                    main_window['-RESULTS-'].update(background_color=APPLE_DARK_BG, text_color=APPLE_LIGHT_TEXT)
                    main_window['-QUERY-'].update(background_color=APPLE_DARK_BG, text_color=APPLE_LIGHT_TEXT)
                    main_window.BackgroundColor = APPLE_DARK_BG
                    # Update all text elements to use light text
                    for element in main_window.element_list():
                        if isinstance(element, sg.Text):
                            element.update(text_color=APPLE_LIGHT_TEXT)
                else:
                    # Apply light mode colors
                    main_window['-RESULTS-'].update(background_color=APPLE_WHITE, text_color=APPLE_DARK_TEXT)
                    main_window['-QUERY-'].update(background_color=APPLE_WHITE, text_color=APPLE_DARK_TEXT)
                    main_window.BackgroundColor = APPLE_LIGHT_BG
                    # Update all text elements to use dark text
                    for element in main_window.element_list():
                        if isinstance(element, sg.Text):
                            element.update(text_color=APPLE_DARK_TEXT)
                            
                # Update the button text
                button_text = "☀️ Light Mode" if dark_mode else "🌙 Dark Mode"
                main_window["-DARK-MODE-"].update(button_text)
                
            elif event == "-SEARCH-HISTORY-":
                # Update the query field when a history item is selected
                selected_query = values["-SEARCH-HISTORY-"]
                if selected_query:
                    main_window["-QUERY-"].update(selected_query)
                    
            elif event == "-REFRESH-HISTORY-":
                # Refresh the search history dropdown
                search_history = load_search_history()
                main_window["-SEARCH-HISTORY-"].update(values=search_history)
                
            elif event == "-SETTINGS-":
                if not settings_window:
                    settings_window = create_settings_window(config)
            elif event == "-SEARCH-":
                query = values["-QUERY-"].strip()
                if query and index:
                    # Add to search history if not already present
                    if query not in search_history:
                        search_history.insert(0, query)
                        # Limit history to 20 items
                        search_history = search_history[:20]
                        save_search_history(search_history)
                        # Update the history dropdown
                        main_window["-SEARCH-HISTORY-"].update(values=search_history)
                    
                    conversation_history.append(f"User: {query}")
                    context = "\n".join(conversation_history)

                    provider = config.get('LocalLLM', 'provider', fallback='openai')
                    api_key = config.get('APIKeys', 'openai_api_key', fallback=None)
                    model_path = config.get('LocalLLM', 'model_path', fallback=None)
                    embeddings_model = get_embeddings(provider, api_key, model_path)

                    results = search(context, index, docs, tags, embeddings_model)

                    # Prepare results with summaries
                    processed_results = []
                    for result in results:
                        summary = summarize(result['document'], provider, api_key, model_path)
                        processed_results.append({
                            'document': result['document'],
                            'summary': summary,
                            'tags': result['tags']
                        })

                    # Format and display results
                    formatted_output = format_search_results(processed_results, query)
                    main_window["-RESULTS-"].update(formatted_output)
                    
                    # Add to conversation history
                    for result in processed_results:
                        conversation_history.append(f"System: {result['summary']}")

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
