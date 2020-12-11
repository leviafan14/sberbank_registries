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
from PyQt5.QtWidgets import QTextEdit,QApplication

#Описание переменных программы

#Описание условных обозначений услуг
service_internet = '02'
service_tv = '01'

#Описание путей к папкам для работы программы

#Папка из которой загружаем архив с реестром
zip_path = "/home/k/reesters_python_17_2/download_zip/"
#Папка в которую распаковываем реестр
unzip_path = '/home/k/reesters_python_17_3/reesters/'
#Папка обработанных архивов
zip_complate_path = '/home/k/reesters_python_17_3/complate_zip/'
#Папка обработанных реестров
path_complate = '/home/k/reesters_python_17_3/complate_reesters/'
#Папка из которой берётся реестр для обработки
path_reesters = '/home/k/reesters_python_17_3/reesters/'
#Папка для результатов обработки реестра
path_result = '/home/k/reesters_python_17_3/result_registries/'
#Список путей к каталогам
folders_list = [zip_path,unzip_path,path_complate,zip_complate_path,path_result]

#Описание функций программы

#Функция проверки существования необходимых папок и их создание при необходимости
def check_exists_folders(folders_list):
    for folder in folders_list:
        folder_name = '/' + folder.split('/')[-2]
        if os.path.exists(folder):
            print(folder_name + ' папка уже существет')
        else:
            try:
                os.mkdir(folder)
            except Exception as e:
                error_message = 'Не удалось создать папку '+folder_name
                messagebox.showerror('Ошибка', error_message)

        
#Функция вывода результата обработки реестра на принтер
def reg_printer(result_txt):
    app = Qt.QApplication([])
    te = QTextEdit()
    te.setHtml(result_txt.get(1.0,END).replace(';','<br>'))
    text = te.toPlainText()
    if(text == ''):
      messagebox.showerror('Ошибка', 'Не выбран реестр')
      return 3
    printer = Qt.QPrinter()
    print_dialog = Qt.QPrintDialog(printer)
    if print_dialog.exec() == Qt.QDialog.Accepted:
        te.print(printer)

        
# Функция теста платежа
def pay_test(abonent,pay_sum,trans_num):
    return int(0)


#Функция определяет успешно добавлен платеж или нет
def type_pay(abonent, pay_sum, trans_num, date_transaction, date_check, action_pay):
    global state_pay,pay_sum_fall,abonent_count_fall

    # Если сумма платежа предположительно за ТВ
    if action_pay == 123:
        state_pay = ' Attention!'
        pay_sum_fall += pay_sum #Сумма не проведенных платежей
        abonent_count_fall += 1 #Увеличить количество не прошедших платежей на 1
        return pay_sum_fall, abonent_count_fall, state_pay

    #Если сумма платежа за ТВ больше или равна 420 р. то делается пометка
    elif action_pay == 124:
        state_pay = ' check!'
        return state_pay

    #Если платеж не прошёл
    elif(action_pay != 0): 
        state_pay = ' FALL' #Если платёж не прошёл, то при выводе инфо добавляется FALL
        pay_sum_fall += pay_sum #Сумма не проведенных платежей
        abonent_count_fall += 1 #Увеличить количество не прошедших платежей на 1
        return pay_sum_fall, abonent_count_fall
    else:
        state_pay = ''
        return state_pay


#Функция обработки архива с реестром
def archive():
    reester_rename = ''
    arch = filedialog.askopenfilename(initialdir =zip_path,filetypes=[('zip files','*.zip')],title = "Укажите реестр")
    #Если архив не выбран
    if(not arch): 
        return 0
    try:
        zip_name = os.path.basename(arch)
        r_zip = zipfile.ZipFile(zip_path+zip_name)
        
        #Если архив за интернет
        if(zip_name[0:2] == service_internet):
            for name in r_zip.namelist():
                f = r_zip.extract(name,unzip_path)
                reester_rename = str('_internet_'+name)
                new_name = os.rename(unzip_path+name,unzip_path+reester_rename)

        #Если архив за ТВ
        elif(zip_name[0:2] == service_tv):
            for name in r_zip.namelist():
                f = r_zip.extract(name,unzip_path)
                reester_rename = ('_TV_'+name)
                new_name = os.rename(unzip_path+name,unzip_path+reester_rename)
        else:
            messagebox.showerror('Ошибка', 'Неизвестный тип архива')
            return False
        r_zip.close()
        shutil.move(arch,zip_complate_path+'complate'+zip_name)
        z_name = str(zip_name[0:2])
        r_list = [str(reester_rename),str(z_name)]
        return r_list
    except Exception as e:
          messagebox.showerror('Ошибка', 'Не удалось распаковать архив')
          print(e)
          return  False
    return reester_rename

     
#Функция внесения платежей за интернет в биллинг UTM5
def internet_pay(abonent,pay_sum,trans_num):
    pay_string = '/home/k/Dropbox/java/sberbankFX/utm5_payment_tool/utm5_payment_tool -a %d -b %s -e %s -C /netup/utm5/utm5_payment_tool.cfg' % (abonent, pay_sum, trans_num)#Внесение платежей за интернет в UTM5
    out = subprocess.call(pay_string,shell=True,stdout=PIPE)
    return out


#Обработка платежей за ТВ
def tv_pay(abonent,pay_sum,trans_num):
    pay_string = 'http://192.168.0.10/tv_sber_reesters.php?command=pay&account=%d&sum=%s&txn_id=%s' % (abonent, pay_sum, trans_num)#внесение платежей за тв в Atirra
    response = urllib.request.urlopen(pay_string)
    content = response.read().decode('UTF-8')
    n_cont = content.replace('\ufeff',' ').split()
    return int(n_cont[0])


#Функция обработки платежей    
def get_pay(result_txt):
    global pay_sum_fall, pay_sum_amount, abonent_count_fall
    state_reester = 'complate_' # подпись добавляется к названию реестра, если он успешно обработан

    #Если реестр не выбран, то функция завершается
    r_name_list = archive()
    if(not r_name_list):
        return 0
    name_list = r_name_list[0]
    fd=str(path_reesters+name_list)

    #Если реестр не выбран
    if(not fd):
        return 0
    try:
        #Открытите реестра
        reester = dbf.Table(fd) 
        reester.open()
        reester_name = os.path.basename(fd)# Имя реестра
    except:
        messagebox.showerror('Ошибка', 'Не удалось открыть реестр')
        return 0
    reester_len = int(len(reester))-1 # Убрать из реестра последнюю строку
    abonent_all = reester_len # Количество платежей в реестре для вывода вывода на экран
    count_payments = 'Количество платежей в реестре: ' + str(reester_len) # Подсчет количества платежей в реестре
    result_txt.configure(state='normal')#Разрешить запись в поле вывода платежей
    pay_sum_amount = 0 #Сумма успешных платежей
    pay_sum_fall = 0 #Сумма не прошедших платежей
    abonent_count_fall = 0 #Количество не проведенных платежей
    i = 0 # Установка счетчика цикла
    result_txt.delete(1.0,END)# Очистка поля вывода платежей

    #Если реестр за интернет
    if(str(r_name_list[1]) == service_internet):
        result_txt.insert(END,'Реестр: '+reester_name+' услуга: Интернет'+';'+'\n')
        
        while reester_len>0: #Пока длина реестра больше 0, на каждой итерации цикла reester_len уменьшается на 1

          try:
              trans_num = reester[i][0] #Номер транзакции
              date_transaction = reester[i][1] #Дата транзакции
              abonent = int(reester[i][2]) #Лицевой счёт абонента
              pay_sum = float(reester[i][3]) #Сумма платежа
              date_check = reester[i][5] #Дата получения платежа

          except ValueError:
              trans_num = reester[i][0] #Номер транзакции
              date_transaction = reester[i][1] #Дата транзакции
              abonent = reester[i][2] #Лицевой счёт абонента
              pay_sum = reester[i][3] #Сумма платежа
              date_check = reester[i][5] #Дата получения платежа
              action_pay = 1

          else:
              #Проверка, если сумма платежа предположительно за ТВ

              if (pay_sum == 140 or pay_sum == 280 or pay_sum == 420 or pay_sum == 560 or pay_sum == 720 or pay_sum == 860):
                  action_pay = 123

              else:
                  try:
                      action_pay = internet_pay(abonent,pay_sum,trans_num)#Результат выполнения функции
                      #action_pay = pay_test(abonent,pay_sum,trans_num)#Запуск функции эмитации платежа за интернет
                  except:
                      messagebox.showerror('Ошибка','Не удалось внести платёж')
                      return 3

          finally:
                print ('Результат: '+str(action_pay))
                type_pay(abonent, pay_sum, trans_num, date_transaction, date_check, action_pay)
                result_row = '№:'+str(trans_num).strip()+' дата платежа:'+str(date_transaction)+' л/с:'+str(abonent).rstrip()+' сумма:'+str(pay_sum)+' дата получения:'+str(date_transaction)+state_pay+';'
                result_txt.insert(INSERT,str(result_row)+'\n')
                pay_sum_amount += pay_sum #Сумма платежей в реестре  
                i += 1 #Увеличить счетчик цикла while на 1
                reester_len -= 1 # Уменьшить счетчик количества реестров на 1

    #Если реестр за телевидение    
    elif(str(r_name_list[1]) == service_tv):

    #Проверка соединения с сервером FireBird 2.5 - ATIRRA
        try:
            atirra_connection_test= fdb.connect(dsn='192.168.0.13:ATIRRA', user='SYSDBA', password='masterkey') #Подключение к серверу Atirra

        except:
            messagebox.showerror('Ошибка', 'Не удалось подключиться к серверу ATIRRA')
            return

        result_txt.insert(END,'Реестр: '+reester_name+' услуга: ТВ '+';'+'\n')
        while reester_len > 0: #Пока длина реестра больше 0, на каждой итерации цикла reester_len уменьшается на 1

          try:
              trans_num = reester[i][0] #Номер транзакции
              date_transaction = reester[i][1] #Дата транзакции
              abonent = int(reester[i][2]) #Лицевой счёт абонента
              pay_sum = float(reester[i][3]) #Сумма платежа
              date_check = reester[i][5] #Дата получения платежа

          except ValueError:
              trans_num = reester[i][0] #Номер транзакции
              date_transaction = reester[i][1] #Дата транзакции
              abonent = reester[i][2]
              pay_sum = reester[i][3] #Сумма платежа
              date_check = reester[i][5] #Дата получения платежа
              action_pay = 1

          else:
              #Если сумма платежа больше или равна 420 р.
              if(pay_sum >= 420):

                #Проводим платеж и если платеж прошел, то отправляем код пометки - 124
                  try:
                      action_pay = tv_pay(abonent,pay_sum,trans_num)

                      if action_pay == 0:
                          action_pay = 124
                      else:
                         action_pay == 1

                  except Exception as e:
                      messagebox.showerror('Ошибка', 'Не удалось внести платёж')
                      return 3

              else:
                  try:
                      action_pay = tv_pay(abonent,pay_sum,trans_num)#Результат выполнения функции
                      #action_pay = pay_test(abonent,pay_sum,trans_num)
                  except:
                      messagebox.showerror('Ошибка', 'Не удалось внести платёж')
                      return 3

          finally:
              print ('Результат: '+str(action_pay))
              
              type_pay(abonent, pay_sum, trans_num, date_transaction, date_check, action_pay)
              
              result_row = '№:'+str(trans_num).strip()+' дата платежа:'+str(date_transaction)+' л/с:'+str(abonent).rstrip()+' сумма:'+str(pay_sum)+' дата получения:'+str(date_transaction)+state_pay+' ;' 
              result_txt.insert(INSERT,str(result_row)+'\n')
              #Сумма платежей в реестре 
              pay_sum_amount += pay_sum      
              #Увеличить счетчик цикла while на 1
              i += 1
              reester_len -= 1 # Уменьшить счетчик количества реестров на 1       

    else:
        messagebox.showerror('Ошибка', 'Неизвестный тип реестра')
        return False
    abonent_count = abonent_all - abonent_count_fall #Количество успешных платежей
    pay_sum_final = pay_sum_amount - pay_sum_fall #Сумма зачисленных платежей
    pay_sum_lost = pay_sum_amount - pay_sum_final # Сумма необработанных платежей
    result_txt.insert(END,'\n'+count_payments+' Платежей успешно проведено: '+str(abonent_count)+' не проведено платежей: '+str(abonent_count_fall)+'; '+'\n')
    result_txt.insert(END,'\n'+'Сумма в реестре: '+str(pay_sum_amount)+'р. Разнесено по счетам: '+str(pay_sum_final)+'р.'+' Разница: '+str(pay_sum_lost)+'р.' )

    #Создание папки по дате реестра
    
    #Запись результата обработки реестра в файл в созданной папке
    folder_name = 'registries_from_' + str(date_check) #название создаваемой папки с датой из реестра
    folder_path = path_result + folder_name #Путь к создаваемой папке

    #Если папка с таким названием не создана, то создаем её
    if os.path.exists(folder_path):
        print('папка ',folder_name,' существует')
    else:
        try:
            os.mkdir(folder_path)
        except Exception as e:
            messagebox.showerror('Ошибка','Не удалось создать папку для резульатов обработки реестра')

    #Проверка наличия файлов в папке с результатами обработки реестра
    files_count = len(os.listdir(path=folder_path))
    
    #Дописываем к имени файла результата номер взятый по количеству
    #файлов в папке для исключения замены файлов с одинаковыми именами
    name_list=str(files_count + 1)+name_list

    #Записываем результат обработки в файл
    with open(path_result+folder_name+'/'+name_list,'w') as file:
        file.write(result_txt.get(1.0,END))
        
    reester.close()
    result_txt.configure(state='disable')#Запретить редактирование поля вывода платежей
    shutil.move(fd, path_complate+state_reester+reester_name)# Перемещение реестра если он успешно обработан


#Функция открытия и просмотра реестра в окне программы
def open_register(result_txt):
    #Выбираем реестр из папки
    register_path = filedialog.askopenfilename(initialdir = path_result, title = "Укажите обработанный реестр для чтения")

    #Если реестр не выбран
    if(not register_path): 
        return 0
    try:
        result_txt.configure(state='normal') #Разрешаем запись в поле вывода
        result_txt.delete(1.0,END)# Очистка поля вывода платежей
        with open(str(register_path)) as file: #Открываем реестр
            line = file.read() #Читаем реестр
            result_txt.insert(END,str(line) + '\n') #Выводим реестр на экран
        result_txt.configure(state='disable')#Запрещаем редактирование поля вывода платежей
    except Exception as e:
        messagebox.showerror('Ошибка', 'Не удалось открыть реестр')
        print(e)
        


