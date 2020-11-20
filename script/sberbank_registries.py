# -*- coding:utf-8 -*-
from sber_gui import *
def main():
    
    #Конфигурация окна
    window = Tk()
    window.geometry('800x600')
    window.title("Сбербанк реестры")# Заголовок окна
    
    #Описание виджетов
    
    #Виджет вывода на экран
    result_txt=scrolledtext.ScrolledText(window,state='disable')
    
    #Button
    btn_inet= Button(window, text="Обработать реестр",width=15,command=lambda:get_pay(result_txt))
    btn_print_reg= Button(window, text="Печать",width=15,command=lambda:reg_printer(result_txt))
    btn_open_register=Button(window, text="Открыть реестр",width=15,command=lambda:open_register(result_txt))

    #Label
    lbl_zip_path= Label(window, text="Путь к архиву: "+zip_path)
    lbl_zip_complate_path= Label(window, text="Путь к обработанным архивам: "+zip_complate_path)
    lbl_unzip_path= Label(window, text="Путь к реестрам после распаковки: "+unzip_path)
    lbl_path_complate=Label(window, text="Путь к обработанным реестрам: "+path_complate)
    lbl_path_result_registries=Label(window, text="Путь к результату :"+path_result)

    
    #Размещение виджетов в окне программы
    btn_inet.pack()
    btn_print_reg.pack()
    btn_open_register.pack()
    lbl_zip_path.pack()
    lbl_unzip_path.pack()
    lbl_path_complate.pack()
    lbl_zip_complate_path.pack()
    lbl_path_result_registries.pack()
    result_txt.pack(expand = True, fill=BOTH)

    #Вызов окна
    check_exists_folders(folders_list)#Вызов функции проверки сущестования необхидимых папок
    window.mainloop()
if __name__=='__main__':
    main()
    
