 Фролова Екатерина
 Вариант 15:
 Разработать эмулятор для языка оболочки ОС. Необходимо сделать работу 
эмулятора как можно более похожей на работу в командной строке UNIX
 подобной ОС
 
 first_practice.py хранит класс EmulatorGUI, который отвечает за UI часть эмулятора:
- parse_argument - настройка аргументов, передаваемых через командную строку, при запуске файла
- show_parsed_arguments - вывод параметров на экран
- execute_startup_script -  обработка стартового скрипта
- show_startup_script_command - вывод команд стартового скрипта
- run_startup_commands - выполнение команд стартового скрипта
- setup_ui - настройка и запуск UI эмулятора
- setup_text_tags - настройка цвета текста в эмуляторе
- show_prompt - вывод промта на экран
- set_up_bindings - настройка работы кнопок, нажатий клавиш
- on_mouse_events - обработка нажатия мыши
- on_backspace - обработка нажатия backspace
- on_delete - обработка удаления текста
-  on_enter - обработка нажатия enter
- on_key_press - обработчик нажатия клавиш
- on_arrow_key - обработчик нажатия стрелочек
- get_current_prompt_position - получение позиции промпта в окне, созданным Tkinter
- get_current_prompt_line - получение строки промпта в окне, созданным Tkinter
- parser - парсинг команд-  checking_command - проверка введенных комманд
- checking_arguments - проверка введенных аргументов
-  execute_command - выполнение введенных комманд
- execute_vfs_info - выполнение команды vfs-info
- execute_head - выполнение команды head
-  execute_uname - выполнение команды uname
-   execute_ls - выполнение команды ls
- execute_cd - выполнение команды cd
- execute_rmdir - выполнение команды rmdir
-  execute_history - выполнение команды history
-   execute_exit - выполнение команды exit
-   show_error - вывод на экран ошибки
-   forse_end - перевод позиции на последную в окне Tkinter
-   insert_new_line - добавление новой строки в окно
-   update_prompt - обновление промпта

  vfs_part.py содержит класс VFS по работе с файловой системой
  -load_from_xml_file - загрузка структуры файловой системы
  - process_directory - обработка директории
  - ensure_path - проверка пути до папки/ файла
  - calculate_vfs_hash - создание хеша всей файловой системы
  - hash_node - создание хеша для нода файловой системы
  - hash_metadate - хегирование метаданных нода
  - hash_content - хеширование файлового содержания
  - hash_children - хеширование вложенных нодов
  - get_current_node_children - получение текущей директории
  - execute_cd - выполнение команд cd
  - execute_head - выполнение команды head
  - execute_ls - выполнение команды ls
  - execute_rmdir - выполнение команды rmdir
