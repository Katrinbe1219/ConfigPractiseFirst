import tkinter as tk
from tkinter import scrolledtext, ttk, Tk
import os
import pwd
import argparse

class EmulatorGUI:

    def __init__(self, root: Tk):
        hostname = os.uname()[1]
        uid = os.getuid()

        user = pwd.getpwuid(uid).pw_name
        HEADER = "Эмулятор: " + user + "@" + hostname

        #self.protected_text=""
        
        self.root = root
        self.root.title(HEADER)
        self.root.geometry("800x600")
        self.prompt = user + "@" + hostname + ": "

        self.command_history = []

        
        #создаетс виджет gui
        self.setup_ui()
        self.setup_text_tags()

        #анализируются параметры запуска эмулятора
        self.config = self.parse_arguments()
        self.show_parsed_arguments()
        self.show_prompt()
        self.execute_startup_script()

        #начинается обычная работа эмулятора
        

        self.terminal_text.focus_set() # проверка фокуса на текстовом поле----------------------------------------------
        
    # building setup --------------------------
    def parse_arguments (self):
        parser = argparse.ArgumentParser(
            description="Эмултор с VFS и стартовым скриптом",
            epilog= "Пример python first_practise.py --vsf ./vfs.xml --script ./start.txt"
        )


        parser.add_argument(
            '--vfs',
            type=str,
            required= False,
            help = 'Путь до VFS - xml файл'
        )

        parser.add_argument(
            '--script',
            type=str,
            required= False,
            help = 'Путь до стартового скрипта'
        )

        return vars(parser.parse_args())

    def show_parsed_arguments(self):
        text = "Parametrs:\n"
        text += "-" * 50
        items = self.config.items()
        print(items)

        for key, value in self.config.items():
            text += f"\n--{key:15}: {value}"
        
        text += '\n'
        text += "-" * 50
        text += '\n'

        self.terminal_text.insert(tk.END, text)

    # start script 
    def execute_startup_script (self):
        script_path = self.config['script']

        if not script_path:
            return
        
        try:
            if not os.path.exists(script_path):
                self.show_prompt()
                self.show_startup_script_command(script_path)
                self.show_error('File does not exist')
                return
            
            #with open авто закрывает файл после выхода из блока
            with open(script_path, 'r', encoding='utf-8') as f:
                script_content = f.read().splitlines()

            self.run_startup_commands(script_content)

        except Exception as e:
            print(f"Ошибка при выполнении стартового скрипта: {e}")
    
    def show_startup_script_command(self, command, tag='output'):
        command += '\n'
        self.terminal_text.insert(tk.END, command, tag)
        self.terminal_text.see(tk.END)
    
    def run_startup_commands(self, commands):

        for i, command in enumerate(commands,1):
            command = command.strip()

            if not command or command.startswith('#'):
                continue

            self.show_startup_script_command(command)
            self.check_any_command(command)
            


    # ui setup----------------------------------------------------------

    def setup_ui(self):
        self.terminal_text = scrolledtext.ScrolledText(
            self.root,
            width = 80,
            height = 25,
            font = ("Consolas", 11),
            bg = "black",
            fg = 'white',
            insertbackground = 'white' #цвет курсора
        )
        self.terminal_text.pack(fill = tk.BOTH, # if parent widget grows, how does will this  widget react
                                expand= True, padx = 10, pady = 10)
        
        #Регулировка нажатия клавиш
        self.set_up_bindings()
    
    def setup_text_tags(self):
        self.terminal_text.tag_config('prompt', foreground=  'green')
        self.terminal_text.tag_config('command', foreground='cyan')
        self.terminal_text.tag_config('error', foreground='red')
        self.terminal_text.tag_config('output', foreground='white')

    def show_prompt(self):
        self.terminal_text.insert(tk.END, #speacial index indicating on the position after last symbol in line
                                   self.prompt,  #text
                                   'prompt' # tag for formating
                                   )
        
        self.terminal_text.see(tk.END) # auto scroll to the place of the inputing
    
    #binding---------------------

    def set_up_bindings(self):
        events = ['<Button-1>','<Button-2>','<Button-3>',
                  '<Double-Button-1>','<Triple-Button-1>',
                  '<B1-Motion>','<B2-Motion>','<B3-Motion>']
        
        for event in events:
            self.terminal_text.bind(event, self.on_mouse_events)
        
        self.terminal_text.bind('<Key>', self.on_key_press)
        #self.terminal_text.bind('<KeyRelease>', self.on_key_release)
        self.terminal_text.bind('<BackSpace>', self.on_backspace)
        self.terminal_text.bind('<Delete>', self.on_backspace)
        self.terminal_text.bind('<Return>', self.on_enter)


        arrow_keys = ['<Left>', '<Right>', '<Up>', '<Down>', '<Home>', '<End>']
        for key in arrow_keys:
            self.terminal_text.bind(key, self.on_arrow_key)
    
    def on_mouse_events(self, event):
        #backspace
        #return - enter
        #key?
        self.forse_end()
        return "break"
    
    def on_backspace(self, event):
        current_position = self.terminal_text.index(tk.INSERT)
        prompt_start = self.get_current_prompt_position()

        if  self.terminal_text.compare(current_position, "<", prompt_start):
            return "break"
        
        if  self.terminal_text.compare(current_position, "==", prompt_start):
            return "break"
        
        return None
        
    def on_delete(self, event):
        current_position = self.terminal_text.index(tk.INSERT)
        prompt_start = self.get_current_prompt_position()

        if  self.terminal_text.compare(current_position, "<", prompt_start):
            return "break"
        return None

    def on_enter (self, event):
        self.insert_new_line()

        current_input_position = self.terminal_text.index('insert')
        current_line = current_input_position.split('.')[0]
        prompt_line = self.get_current_prompt_line()


        command_start = f"{prompt_line}.{len(self.prompt)}"
        command_end = f"{current_line}.end"
        command_line_with_arguments = self.terminal_text.get(command_start, command_end).strip()

        self.check_any_command(command_line_with_arguments)
        
        return "break"


    def on_key_press(self, event):
        #Обраточик нажатия клавиш
        current_position = self.terminal_text.index(tk.INSERT)

        prompt_position = self.get_current_prompt_position()

        if self.terminal_text.compare(current_position, "<", prompt_position):
            
            self.terminal_text.mark_set(tk.INSERT, tk.END)
            self.terminal_text.see(tk.INSERT)
            return "break"
        
        return None

    def on_arrow_key(self, event):
        current_position = self.terminal_text.index(tk.INSERT)
        promt_pos = self.get_current_prompt_position()

        if self.terminal_text.compare(current_position, "<", promt_pos):
            self.terminal_text.mark_set(tk.INSERT, tk.END)
            return "break"
        
        return None


     # prompt position --------------------------------

    def get_current_prompt_position(self):
        # Получаем весь текст
        content = self.terminal_text.get('1.0', tk.END)
        lines = content.split('\n')
        
        #последняя строка с промптом
        for i in range(len(lines)-1, -1, -1):
            if lines[i].startswith(self.prompt) or lines[i].endswith('$ '):
                return f"{i+1}.{len(self.prompt)}"
        
        return '1.0'  # Fallback

    def get_current_prompt_line(self):
        text = self.terminal_text.get('1.0', tk.END)
        lines = text.split('\n')

        for i in range(len(lines)-1,-1,-1):
            if (lines[i].startswith(self.prompt)):
                return str(i  +  1)
        return '1'

    # command analyze ------------------------------------------------

    def parser( self, inputLine: str):

        if not inputLine.strip():
            return "", []
        

        spliting = inputLine.split(' ')
        command = spliting[0] if spliting else  ""
        arguments = spliting[1::] if len(spliting) > 1 else []

        return command, arguments

    def checking_command (self, command : str):

        commands  = ['ls' , 'cd' , 'exit', 
                 'head', 'uname', 'history' ,
                 'rmdir']

        if command not in commands:
            return False

            
        return True
    
    def checking_arguments (self, command : str, arguments : list):
        args  = {'ls' : [], 'cd' : [], 'exit': [], 
                 'head':[], 'uname':[], 'history' :[],
                 'rmdir':[]}

        
        if len(arguments) > 0 and command not in args.keys():
            return False
        
        for arg in arguments:
            if arg not in args[command]:
                return False
            
        return True

    def execute_command(self,command, full_command):
        
        if command == "ls":
            self.execute_ls(full_command)

        elif command == "cd":
            self.execute_cd(full_command)
        elif command == "exit":
            self.execute_exit()
        elif command == "head":
            self.execute_head(full_command)


    def execute_ls (self, inputLine, tag='output'):
        inputLine += '\n'
        self.terminal_text.insert(tk.END, inputLine, tag)
        self.terminal_text.see(tk.END)
        self.show_prompt()
    
    def execute_head (self, inputLine, tag='output'):
        inputLine += '\n'
        self.terminal_text.insert(tk.END, inputLine, tag)
        self.terminal_text.see(tk.END)
        self.show_prompt()
        

    def execute_cd (self, inputLine, tag='output'):
        inputLine += '\n'
        self.terminal_text.insert(tk.END, inputLine, tag)
        self.terminal_text.see(tk.END)
        self.show_prompt()

    def execute_exit(self):
        self.root.destroy()

    def show_error(self, error, tag='error'):
        error += '\n'
        self.terminal_text.insert(tk.END, error, tag)
        self.terminal_text.see(tk.END)
        self.show_prompt()


    # base features  --------------------
    def forse_end(self):
        self.terminal_text.mark_set(tk.INSERT, tk.END)
        self.terminal_text.see(tk.END)

    def insert_new_line(self):
        self.terminal_text.insert(tk.END, '\n')
        self.terminal_text.see(tk.END)

    def check_any_command(self, command_line_with_arguments):
        command, args = self.parser(command_line_with_arguments)
        command_validation = self.checking_command(command=command)
        
        if not command_validation:
                self.show_error(f"{command} is incorrect")
                return "break"
        
        args_validation = True
        if (len(args)>0):
            args_validation = self.checking_arguments(command, args)
        
        if not args_validation:
                self.show_error(f"arguments are incorrect")
                return "break"
        
        
        if command:
            self.command_history.append(command_line_with_arguments)
            self.execute_command(command, command_line_with_arguments)
        else:
            self.show_prompt()


if __name__ == "__main__":
    root = tk.Tk()
    terminal = EmulatorGUI(root)
    root.mainloop()