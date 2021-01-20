# -*- coding:utf-8 -*-
from sber_gui import *

#global registries_folder_path,zip_path,unzip_path,path_complate,zip_complate_path,path_result,folder_list,path_reesters,folders_list

def main():
    # Корневой путь к каталогу проекта
    registries_folder_path = get_project_folder_path()
    # Каталог из которого загружаем архив с реестром
    zip_path = registries_folder_path+'download_zip/'
    # Каталог в который распаковываем реестр
    unzip_path = registries_folder_path+'reesters/'
    # Каталог обработанных архивов
    zip_complate_path = registries_folder_path+'complate_zip/'
    # Каталог обработанных реестров
    path_complate = registries_folder_path+'complate_reesters/'
    # Каталог из которого берётся реестр для обработки
    path_reesters = registries_folder_path+'reesters/'
    # Каталог для результатов обработки реестра
    path_result = registries_folder_path+'result_registries/'
    # Список путей к каталогам
    folders_list = [zip_path,unzip_path,path_complate,zip_complate_path,path_result]

    # Конфигурация окна
    window = Tk()
    window.geometry('800x600')
    window.title("Сбербанк реестры")
    
    # Описание виджетов
    
    # Виджет вывода на экран
    result_txt=scrolledtext.ScrolledText(window,state='disable')
    
    # Button
    btn_inet = Button(window, text="Обработать реестр",width=15,command=lambda:get_pay(result_txt,zip_path,unzip_path,zip_complate_path,
                                                                                       path_complate,path_reesters,path_result))
    btn_print_reg = Button(window, text="Печать",width=15,command=lambda:reg_printer(result_txt))
    btn_open_register = Button(window, text="Открыть реестр",width=15,command=lambda:open_register(result_txt,path_result))

    # Label
    lbl_zip_path = Label(window, text="Путь к архиву: "+zip_path)
    lbl_zip_complate_path = Label(window, text="Путь к обработанным архивам: "+zip_complate_path)
    lbl_unzip_path = Label(window, text="Путь к реестрам после распаковки: "+unzip_path)
    lbl_path_complate = Label(window, text="Путь к обработанным реестрам: "+path_complate)
    lbl_path_result_registries = Label(window, text="Путь к результату :"+path_result)

    
    # Размещение виджетов в окне программы
    btn_inet.pack()
    btn_print_reg.pack()
    btn_open_register.pack()
    lbl_zip_path.pack()
    lbl_unzip_path.pack()
    lbl_path_complate.pack()
    lbl_zip_complate_path.pack()
    lbl_path_result_registries.pack()
    result_txt.pack(expand = True, fill=BOTH)

    # Вызов окна
    check_exists_folders(folders_list)#Вызов функции проверки сущестования необхидимых папок
    window.mainloop()
if __name__ == '__main__':
    main()
    
