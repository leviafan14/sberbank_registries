# -*- coding:utf-8 -*-
import os
import dbf
import fdb
import shutil
import subprocess
import urllib
from tkinter import *
from tkinter import filedialog
from tkinter import scrolledtext
from tkinter import messagebox
import urllib.request
import zipfile
from subprocess import Popen, PIPE
from PyQt5 import Qt
from PyQt5.QtWidgets import QMessageBox,QPushButton,QTextEdit,QApplication,QWidget
#-----------------------------------------------------------------
#Описание переменных проекта
zip_path="/home/k/reesters_python_17_2/download_zip/" #Откуда загружаем архив с реестром
unzip_path='/home/k/reesters_python_17_2/reesters/' # папка куда распаковываем реестр
zip_complate_path='/home/k/reesters_python_17_2/complate_zip/' # Папка обработанных архивов
path_complate='/home/k/reesters_python_17_2/complate_reesters/' # папка обработанных реестров
path_reesters='/home/k/reesters_python_17_2/reesters/' # папка откуда откуда берётся реестр для обработки
#-----------------------------------------------
#Описание функций проекта
#Функция вывода результата обработки реестра на принтер
def reg_printer(result_txt):
    app = Qt.QApplication([])
    te =QTextEdit()
    te.setHtml(result_txt.get(1.0,END).replace(';','<br>'))
    text = te.toPlainText()
    if(text==''):
      messagebox.showerror('Ошибка', 'Не выбран реестр')
      return 3
    try:
        printer = Qt.QPrinter()
        print_dialog = Qt.QPrintDialog(printer)
    except:
        messagebox.showerror('Ошибка', 'Ошибка QPrinter')
    try:    
        if print_dialog.exec() == Qt.QDialog.Accepted:
            try:
                te.print(printer)
            except:
                messagebox.showerror('Ошибка', 'Ошибка печати')
    except:
        messagebox.showerror('Ошибка', 'Не удалось рапечатать реестр')
def reg_printer_second(result_txt):
    class Print_reg(QWidget):
        def __init__(self):
            super().__init__()
            self.initUI()
        def initUI(self):
            self.btn = QPushButton('Печать', self)
            self.btn.resize(self.btn.sizeHint())
            self.btn.move(390,0) 
            self.te =QTextEdit(self)
            self.te.setHtml(result_txt.get(1.0,END).replace(';','<br>'))
            self.te.resize(800,550)
            self.te.move(0,30)
            self.te.show()
            self.setWindowTitle('Предварительный просмотр')
            self.setGeometry(800,600,800,600)
            self.btn.clicked.connect(self.print_dialog)
            self.show()
        def print_dialog(self,te):
            self.printer = Qt.QPrinter()
            self.print_dialog = Qt.QPrintDialog(self.printer)
            try:
                if self.print_dialog.exec() == Qt.QDialog.Accepted:
                    try:
                        self.te.print(self.printer)
                    except:
                        print('отмена печати')
            except:
               pass        
    if __name__ == '__main__':
        app = QApplication(sys.argv)
        ex = Print_reg()
        sys.exit(app.exec_())
# Функция эмитации платежа
def pay_test(abonent,pay_sum,trans_num):
    return int(0)
#Функция определяет успешно добавлен платеж или нет
def type_pay(abonent, pay_sum, trans_num, date_transaction, date_check, action_pay):
    global state_pay,pay_sum_fall,abonent_count_fall
    if (action_pay==123):# Если сумма платежа предположительно за ТВ
        state_pay='_Attention!'
        pay_sum_fall+=pay_sum #Сумма не проведенных платежей
        abonent_count_fall+=1#Увеличить количество не прошедших платежей на 1
        return pay_sum_fall, abonent_count_fall,state_pay
    elif(action_pay!=0): #Если платеж не прошёл
        state_pay=' FALL' #Если платёж не прошёл, то при выводе инфо добавляется FALL
        pay_sum_fall+=pay_sum #Сумма не проведенных платежей
        abonent_count_fall+=1#Увеличить количество не прошедших платежей на 1
        return pay_sum_fall, abonent_count_fall
    else:
        state_pay=''
        return state_pay
#-----------------------------------------------
#Функция обработки архива с реестром
def archive():
    arch=filedialog.askopenfilename(initialdir =zip_path,filetypes=[('zip files','*.zip')],title = "Укажите реестр")
    if(not arch): #Если архив не выбран
        return 0
    try:
        zip_name=os.path.basename(arch)
        r_zip = zipfile.ZipFile(zip_path+zip_name)
        if(zip_name[0:2]=='02'):#Если реестр на интернет
            for name in r_zip.namelist():
                f=r_zip.extract(name,unzip_path)
                reester_rename=str('internet_'+name)
                new_name=os.rename(unzip_path+name,unzip_path+reester_rename)
        elif(zip_name[0:2]=='01'):#Если реестр за ТВ
            for name in r_zip.namelist():
                f=r_zip.extract(name,unzip_path)
                reester_rename=('TV_'+name)
                new_name=os.rename(unzip_path+name,unzip_path+reester_rename)
        else:
            messagebox.showerror('Ошибка', 'Неизвестный тип архива')
            return False
        r_zip.close()
        shutil.move(arch,zip_complate_path+'complate_'+zip_name)
        z_name=str(zip_name[0:2])
        r_list=[str(reester_rename),str(z_name)]
        return r_list
    except:
          messagebox.showerror('Ошибка', 'Не удалось распаковать архив')
          return  False
#----------------------------------        
#Функция внесения платежей за интернет в биллинг UTM5
def internet_pay(abonent,pay_sum,trans_num):
    #pay_string='/home/k/Dropbox/java/sberbankFX/utm5_payment_tool/utm5_payment_tool -a %d -b %s -e %s -C /netup/utm5/utm5_payment_tool.cfg' % (abonent, pay_sum, trans_num)#Внесение платежей за интернет в UTM5
    out=subprocess.call(pay_string,shell=True,stdout=PIPE)
    return out
#----------------------------------
#Обработка платежей за ТВ
def tv_pay(abonent,pay_sum,trans_num):
    #pay_string='http://192.168.0.10/tv_sber_reesters.php?command=pay&account=%d&sum=%s&txn_id=%s' % (abonent, pay_sum, trans_num)#внесение платежей за тв в Atirra
    response=urllib.request.urlopen(pay_string)
    content=response.read().decode('UTF-8')
    n_cont=content.replace('\ufeff',' ').split()
    return int(n_cont[0])
#---------------------------------- 
#Функция обработки платежей    
def get_pay():
    global pay_sum_fall, pay_sum_amount, abonent_count_fall
    state_reester='complate_' # подпись добавляется к названию реестра, если он успешно обработан
    #Если реестр не выбран, то функция завершается
    r_name_list=archive()
    if(not r_name_list):
        return 0
    name_list=r_name_list[0]
    print (str(name_list))
    fd=str(path_reesters+name_list)
    if(not fd):#Если реестр не выбран
        return 0
    try:
        reester=dbf.Table(fd) #Открытите реестра
        reester.open()
        reester_name=os.path.basename(fd)# Имя реестра
    except:
        messagebox.showerror('Ошибка', 'Не удалось открыть реестр')
        return 0
    reester_len=int(len(reester))-1 # Убрать из реестра последнюю строку
    abonent_all=reester_len # Количество платежей в реестре для вывода вывода на экран
    count_payments='Количество платежей в реестре: '+str(reester_len) # Подсчет количества платежей в реестре
    result_txt.configure(state='normal')#Разрешить запись в поле вывода платежей
    pay_sum_amount=0 #Сумма успешных платежей
    pay_sum_fall=0 #Сумма не прошедших платежей
    abonent_count_fall=0 #Количество не проведенных платежей
    i=0 # Установка счетчика цикла
    result_txt.delete(1.0,END)# Очистка поля вывода платежей
    if(str(r_name_list[1])=='02'):
        result_txt.insert(END,'Реестр: '+reester_name+' услуга: Интернет'+';'+'\n')
        while reester_len>0: #Пока длина реестра больше 0, на каждой итерации цикла reester_len уменьшается на 1
          try:
              trans_num=reester[i][0] #Номер транзакции
              date_transaction=reester[i][1] #Дата транзакции
              abonent=int(reester[i][2]) #Лицевой счёт абонента
              pay_sum=float(reester[i][3]) #Сумма платежа
              date_check=reester[i][5] #Дата получения платежа
          except ValueError:
              trans_num=reester[i][0] #Номер транзакции
              date_transaction=reester[i][1] #Дата транзакции
              abonent=reester[i][2] #Лицевой счёт абонента
              pay_sum=reester[i][3] #Сумма платежа
              date_check=reester[i][5] #Дата получения платежа
              action_pay=1
          else:
              if (pay_sum==140 or pay_sum==280 or pay_sum==420 or pay_sum==560 or pay_sum==720 or pay_sum==860):#Проверка, если сумма платежа предположительно за ТВ
                  action_pay=123
              else:
                  #action_pay=internet_pay(abonent,pay_sum,trans_num)#Результат выполнения функции
                  action_pay=pay_test(abonent,pay_sum,trans_num)#Запуск функции эмитации платежа за интернет
          finally:
                print ('Результат: '+str(action_pay))
                type_pay(abonent, pay_sum, trans_num, date_transaction, date_check, action_pay)
                result_row='№:'+str(trans_num).strip()+' дата платежа:'+str(date_transaction)+' л/с:'+str(abonent).rstrip()+' сумма:'+str(pay_sum)+' дата получения:'+str(date_transaction)+state_pay+';'
                result_txt.insert(INSERT,str(result_row)+'\n')
                pay_sum_amount+=pay_sum #Сумма платежей в реестре  
                i+=1 #Увеличить счетчик цикла while на 1
                reester_len-=1 # Уменьшить счетчик количества реестров на 1
    elif(str(r_name_list[1])=='01'):
        try:#Проверка соединения с сервером FireBird 2.5 - ATIRRA
            atirra_connection_test= fdb.connect(dsn='192.168.0.13:ATIRRA', user='SYSDBA', password='masterkey') #Подключение к серверу Atirra
        except:
            messagebox.showerror('Ошибка', 'Не удалось подключиться к серверу ATIRRA')
            return
        result_txt.insert(END,'Реестр: '+reester_name+' услуга: ТВ '+';'+'\n')
        while reester_len>0: #Пока длина реестра больше 0, на каждой итерации цикла reester_len уменьшается на 1
          try:
              trans_num=reester[i][0] #Номер транзакции
              date_transaction=reester[i][1] #Дата транзакции
              abonent=int(reester[i][2]) #Лицевой счёт абонента
              pay_sum=float(reester[i][3]) #Сумма платежа
              date_check=reester[i][5] #Дата получения платежа
          except ValueError:
              trans_num=reester[i][0] #Номер транзакции
              date_transaction=reester[i][1] #Дата транзакции
              abonent=reester[i][2]
              pay_sum=reester[i][3] #Сумма платежа
              date_check=reester[i][5] #Дата получения платежа
              action_pay=1
          else:
              #action_pay=tv_pay(abonent,pay_sum,trans_num)#Результат выполнения функции
              action_pay=pay_test(abonent,pay_sum,trans_num)
          finally:
              print ('Результат: '+str(action_pay))
              type_pay(abonent, pay_sum, trans_num, date_transaction, date_check, action_pay) 
              result_row='№:'+str(trans_num).strip()+' дата платежа:'+str(date_transaction)+' л/с:'+str(abonent).rstrip()+' сумма:'+str(pay_sum)+' дата получения:'+str(date_transaction)+state_pay+' ;' 
              result_txt.insert(INSERT,str(result_row)+'\n')
              pay_sum_amount+=pay_sum #Сумма платежей в реестре      
              i+=1 #Увеличить счетчик цикла while на 1
              reester_len-=1 # Уменьшить счетчик количества реестров на 1       
    else:
        messagebox.showerror('Ошибка', 'Неизвестный тип реестра')
        return False
    abonent_count=abonent_all-abonent_count_fall #Количество успешных платежей
    pay_sum_final=pay_sum_amount-pay_sum_fall #Сумма зачисленных платежей
    pay_sum_lost=pay_sum_amount-pay_sum_final # Сумма необработанных платежей
    result_txt.insert(END,'\n'+count_payments+' Платежей успешно проведено: '+str(abonent_count)+' не проведено платежей: '+str(abonent_count_fall)+'; '+'\n')
    result_txt.insert(END,'\n'+'Сумма в реестре: '+str(pay_sum_amount)+'р. Разнесено по счетам: '+str(pay_sum_final)+'р.'+' Разница: '+str(pay_sum_lost)+'р.' )
    reester.close()
    result_txt.configure(state='disable')#Запретить редактирование поля вывода платежей
    shutil.move( fd, path_complate+state_reester+reester_name)# Перемещение реестра если он успешно обработан
#----------------------------------
#Конфигурация окна
window = Tk()
window.geometry('800x600')
window.title("Сбербанк реестры")# Заголовок окна
#----------------------------------    
#Описание виджетов
#----------------------------------
#Button
btn_inet= Button(window, text="Загрузить реестр",width=15,command=get_pay)
btn_print_reg= Button(window, text="Печать",width=15,command=lambda:reg_printer(result_txt))
#----------------------------------
#Label
lbl_zip_path= Label(window, text="Путь к архиву: "+zip_path)
lbl_zip_complate_path= Label(window, text="Путь к обработанным архивам: "+zip_complate_path)
lbl_unzip_path= Label(window, text="Путь к реестрам после распаковки: "+unzip_path)
lbl_path_complate=Label(window, text="Путь к обработанным реестрам: "+path_complate)
#Виджет вывода на экран
result_txt=scrolledtext.ScrolledText(window,state='disable')
#----------------------------------
#Размещение виджетов в окне программы
btn_inet.pack()
btn_print_reg.pack()
lbl_zip_path.pack()
lbl_unzip_path.pack()
lbl_path_complate.pack()
lbl_zip_complate_path.pack()
result_txt.pack(expand = True, fill=BOTH)
#----------------------------------
#Вызов окна
window.mainloop()
