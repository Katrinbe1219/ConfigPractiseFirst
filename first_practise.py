from tkinter import *
import os
import pwd

root = Tk()


hostname = os.uname()[1]
uid = os.getuid()
user = pwd.getpwuid(uid).pw_name
HEADER = user + "@" + hostname

def parser( inputLine: str):

    if not inputLine.strip():
        return "", []
    

    spliting = inputLine.split(' ')
    command = spliting[0] if spliting else  ""
    arguments = spliting[1::] if len(spliting) > 1 else []

    return command, arguments


def checking_command (command : str, arguments: list):
    commands = ['ls', 'cd', 'exit']
    args  = {'ls' : []}

    if command not in commands:
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
