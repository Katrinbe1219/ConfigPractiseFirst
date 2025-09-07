import tkinter as tk
from tkinter import scrolledtext, ttk, Tk
import os
import pwd

class EmulatorGUI:

    def __init__(self, root: Tk):
        hostname = os.uname()[1]
        uid = os.getuid()

        user = pwd.getpwuid(uid).pw_name
        HEADER = "Эмулятор: " + user + "@" + hostname

        self.protected_text=""
        
        self.root = root
        self.root.title(HEADER)
        self.root.geometry("800x600")
        self.prompt = user + "@" + hostname + ": "

        self.command_history = []

        self.setup_ui()
        self.setup_text_tags()
        self.show_prompt()

        self.terminal_text.focus_set() # проверка фокуса на текстовом поле----------------------------------------------


        
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
        # self.terminal_text.bind('<Return>', self.on_enter) # enter
        # self.terminal_text.bind('<Button-1>', self.on_click) # left btn
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
    
    def on_enter(self, event):
        print("here")
        pass


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

    # def on_key_release(self, event):
    #         self.forse_end()

    def on_arrow_key(self, event):
        current_position = self.terminal_text.index(tk.INSERT)
        promt_pos = self.get_current_prompt_position()

        if self.terminal_text.compare(current_position, "<", promt_pos):
            self.terminal_text.mark_set(tk.INSERT, tk.END)
            return "break"
        
        return None

    
    def forse_end(self):
        self.terminal_text.mark_set(tk.INSERT, tk.END)
        self.terminal_text.see(tk.END)

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


    def execute_ls (self, inputLine, tag='output'):
        inputLine += '\n'
        self.terminal_text.insert(tk.END, inputLine, tag)
        self.terminal_text.see(tk.END)
        self.show_prompt()
        

    def execute_cd (self, inputLine, tag='output'):
        inputLine += '\n'
        self.terminal_text.insert(tk.END, inputLine, tag)
        self.terminal_text.see(tk.END)
        self.show_prompt()

    def execute_exit(self): #self.root.destroy()
        root.destroy()

    def show_error(self, error, tag='error'):
        error += '\n'
        self.terminal_text.insert(tk.END, error, tag)
        self.terminal_text.see(tk.END)
        self.show_prompt()

    def insert_new_line(self):
        self.terminal_text.insert(tk.END, '\n')
        self.terminal_text.see(tk.END)







root = Tk()




def parser( inputLine: str):

    if not inputLine.strip():
        return "", []
    

    spliting = inputLine.split(' ')
    command = spliting[0] if spliting else  ""
    arguments = spliting[1::] if len(spliting) > 1 else []

    return command, arguments


def checking_command (command : str, arguments: list):

    args  = {'ls' : [], 'cd' : [], 'exit': []}

    if command not in args.keys():
        return False
    
    if len(arguments) > 0 and command not in args.keys():
        return False
    
    for arg in arguments:
        if arg not in args[command]:
            return False
        
    return True

def execute_command(inputLine):
    if not inputLine:
        # вывести на экран ошибку
        return
    
    command, args = parser(inputLine)
    checking = checking_command(command, args)

    if not checking:
        # вывести на экран ошибку
        return
    
    if command == "ls":
        execute_ls(inputLine)

    elif command == "cd":
        execute_cd(inputLine)
    elif command == "exit":
        execute_exit()


def execute_ls (inputLine):
    #вывести команду inputLine
    pass

def execute_cd (inputLine):
    #вывести команду inputLine
    pass

def execute_exit(): #self.root.destroy()
    root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    terminal = EmulatorGUI(root)
    root.mainloop()