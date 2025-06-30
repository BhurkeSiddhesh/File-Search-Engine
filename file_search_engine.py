'''
  Index and search for local files with this GUI based search engine
  
  Author:     Israel Dryer
  Email:      israel.dryer@gmail.com
  Modified:   2020-01-14
  
'''
import os
import pickle
import PySimpleGUI as sg
from typing import Dict

# Support both old and new PySimpleGUI theme APIs so that the tests, which
# monkeypatch ``ChangeLookAndFeel``, work regardless of the installed
# version. Prefer the modern call when available.
if hasattr(sg, 'change_look_and_feel'):
    sg.change_look_and_feel('Black')
elif hasattr(sg, 'ChangeLookAndFeel'):
    sg.ChangeLookAndFeel('Black')

class Gui:
    ''' Create a GUI object '''
    
    def __init__(self):
        self.layout: list = [
            [sg.Text('Search Term', size=(11,1)), 
             sg.Input(size=(40,1), focus=True, key="TERM"), 
             sg.Radio('Contains', size=(10,1), group_id='choice', key="CONTAINS", default=True), 
             sg.Radio('StartsWith', size=(10,1), group_id='choice', key="STARTSWITH"), 
             sg.Radio('EndsWith', size=(10,1), group_id='choice', key="ENDSWITH")],
            [sg.Text('Root Path', size=(11,1)), 
             sg.Input('/..', size=(40,1), key="PATH"), 
             sg.FolderBrowse('Browse', size=(10,1)), 
             sg.Button('Re-Index', size=(10,1), key="_INDEX_"), 
             sg.Button('Search', size=(10,1), bind_return_key=True, key="_SEARCH_")],
            [sg.Output(size=(100,30))]]
        
        self.window: object = sg.Window('File Search Engine', self.layout, element_justification='left')


class SearchEngine:
    ''' Create a search engine object '''

    def __init__(self):
        self.file_index = [] # directory listing returned by os.walk()
        self.results = [] # search results returned from search method
        self.matches = 0 # count of records matched
        self.records = 0 # count of records searched


    def create_new_index(self, values: Dict[str, str], show_cli_progress: bool = False) -> None:
        '''Create a new file index of the root path with progress information.

        A progress meter is displayed using PySimpleGUI while directories are
        traversed. When ``show_cli_progress`` is ``True`` a simple text based
        progress indicator is also printed to the console. The resulting index
        is stored on ``self.file_index`` and written to ``file_index.pkl``.
        '''
        root_path = values['PATH']

        # Determine the total number of directories so the progress meter can
        # report the correct percentage completed.
        total_dirs = sum(1 for _ in os.walk(root_path)) or 1

        self.file_index = []
        current_dir = 0
        for root, _, files in os.walk(root_path):
            current_dir += 1
            # update the GUI progress meter
            sg.one_line_progress_meter(
                'Indexing Files',
                current_dir,
                total_dirs,
                'INDEX_PROGRESS',
                'Scanning directories...',
            )

            # optional CLI progress for non-GUI callers
            if show_cli_progress:
                percent = int(current_dir / total_dirs * 100)
                print(f'Indexing: {percent:3d}% ({current_dir}/{total_dirs})', end='\r')

            if files:
                self.file_index.append((root, files))

        # ensure the progress meter is closed and the CLI progress line is reset
        sg.one_line_progress_meter(
            'Indexing Files',
            total_dirs,
            total_dirs,
            'INDEX_PROGRESS',
        )
        if show_cli_progress:
            print()

        # save index to file
        with open('file_index.pkl', 'wb') as f:
            pickle.dump(self.file_index, f)


    def load_existing_index(self) -> None:
        ''' Load an existing file index into the program '''
        try:
            with open('file_index.pkl','rb') as f:
                self.file_index = pickle.load(f)
        except:
            self.file_index = []


    def search(self, values: Dict[str, str]) -> None:
        ''' Search for the term based on the type in the index; the types of search
            include: contains, startswith, endswith; save the results to file '''
        self.results.clear()
        self.matches = 0
        self.records = 0
        term = values['TERM']

        # search for matches and count results
        for path, files in self.file_index:
            for file in files:
                self.records +=1
                if (values['CONTAINS'] and term.lower() in file.lower() or 
                    values['STARTSWITH'] and file.lower().startswith(term.lower()) or 
                    values['ENDSWITH'] and file.lower().endswith(term.lower())):

                    result = path.replace('\\','/') + '/' + file
                    self.results.append(result)
                    self.matches +=1
                else:
                    continue 
        
        # save results to file
        with open('search_results.txt','w') as f:
            for row in self.results:
                f.write(row + '\n')

def main():
    ''' The main loop for the program '''
    g = Gui()
    s = SearchEngine()
    s.load_existing_index() # load if exists, otherwise return empty list

    while True:
        event, values = g.window.read()

        if event is None:
            break
        if event == '_INDEX_':
            s.create_new_index(values)
            print()
            print(">> New index created")
            print()
        if event == '_SEARCH_':
            s.search(values)

            # print the results to output element
            print()
            for result in s.results:
                print(result)
            
            print()
            print(">> Searched {:,d} records and found {:,d} matches".format(s.records, s.matches))
            print(">> Results saved in working directory as search_results.txt.")


if __name__ == '__main__':
    print('Starting program...')
    main()            
