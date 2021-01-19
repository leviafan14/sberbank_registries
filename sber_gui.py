import os
import dbf
import fdb
from PyQt5 import Qt
from PyQt5.QtWidgets import QTextEdit,QApplication
import shutil
import subprocess
from subprocess import Popen, PIPE
from tkinter import *
from tkinter import filedialog
from tkinter import scrolledtext
from tkinter import messagebox
import urllib
import urllib.request
import zipfile

# Описание переменных программы

# Описание условных обозначений услуг
service_internet = '02' # Интернет
service_tv = '01' # ТВ (телевидение)
service = str() # Переменная для извлечения типа услуги
os_name = os.name # Хранит тип ОС

# Описание путей к каталогам для работы программы

# Функция определяет тип ОС: WIN или POSIX

def get_os_type():
    # Определение разделителя каталогов
    # Если ОС Windows
    if os_name == 'nt':
        spliter = '\\'
    # Если ОС Linux
    elif os_name == 'posix':
        spliter = '/'
    else:
        print('Error. Не удалось определить операционную систему')
        exit()
    return spliter

# Функция получает путь к корневому каталогу проекта
def get_project_folder_path():
    # Получаем путь до каталога с скриптом
    path = os.getcwd()
    # Переменная для хранения пути к каталогу
    registries_folder_path = str()
    spliter = get_os_type()
    # Разделяем полученный путь полученным разделителем и отсекаем последний элемент
    path = path.split(spliter)[0:-1]
    # Собираем полученный путь до корневой папки проекта с отсечением папки скрипта
    for p in path:
        registries_folder_path += p + '/'
    return registries_folder_path



# Функция проверки существования необходимых папок и их создание при необходимости
def check_exists_folders(folders_list):
    spliter = get_os_type()
    for folder in folders_list:
        folder_name = spliter + folder.split(spliter)[-2]
        if os.path.exists(folder):
            print(folder_name + ' каталог уже существет')
        else:
            try:
                os.mkdir(folder)
            except Exception as e:
                error_message = 'Не удалось создать каталог '+folder_name
                messagebox.showerror('Ошибка', error_message)

        
# Функция вывода результата обработки реестра на принтер
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


# Функция определяет успешно добавлен платеж или нет
def type_pay(abonent, pay_sum, trans_num, date_transaction, date_check, action_pay):
    global state_pay,pay_sum_fall,abonent_count_fall

    # Если сумма платежа предположительно за ТВ
    if action_pay == 123:
        state_pay = ' Attention!'
        pay_sum_fall += pay_sum # Сумма не проведенных платежей
        abonent_count_fall += 1 # Увеличить количество не прошедших платежей на 1
        return pay_sum_fall, abonent_count_fall, state_pay

    # Если сумма платежа за ТВ больше или равна 420 р. то делается пометка
    elif action_pay == 124:
        state_pay = ' check!'
        return state_pay

    # Если платеж не прошёл
    elif(action_pay != 0): 
        state_pay = ' FALL' # Если платёж не прошёл, то при выводе инфо добавляется FALL
        pay_sum_fall += pay_sum # Сумма не проведенных платежей
        abonent_count_fall += 1 # Увеличить количество не прошедших платежей на 1
        return pay_sum_fall, abonent_count_fall
    else:
        state_pay = ''
        return state_pay


# Функция обработки архива с реестром
def archive(zip_path,unzip_path,zip_complate_path,
            path_complate,path_reesters,path_result):
    reester_rename = ''
    arch = filedialog.askopenfilename(initialdir =zip_path,filetypes=[('zip files','*.zip*')],title = "Укажите реестр")
    # Если архив не выбран
    if(not arch): 
        return 0
    # Определяем первый символ архива
    try:
        zip_name = os.path.basename(arch)
        r_zip = zipfile.ZipFile(zip_path+zip_name)
        # Если первый символ '_' , то берем срез с 1 по 3 символ
        if str(zip_name[0]) == '_':
            service = zip_name[1:3]
        # Если первый символ '0' , то берем срез с 0 по 2 символ
        elif str(zip_name[0]) == '0':
            service = zip_name[0:2]
        else:
            messagebox.showerror('Ошибка', 'Не удалось определить услугу')
            return
        
        # Если архив за интернет
        if(str(service) == service_internet):
            for name in r_zip.namelist():
                f = r_zip.extract(name,unzip_path)
                reester_rename = str('_internet_'+name)
                new_name = os.rename(unzip_path+name,unzip_path+reester_rename)

        # Если архив за ТВ
        elif(str(service) == service_tv):
            for name in r_zip.namelist():
                f = r_zip.extract(name,unzip_path)
                reester_rename = ('_TV_'+name)
                new_name = os.rename(unzip_path+name,unzip_path+reester_rename)
        else:
            messagebox.showerror('Ошибка', 'Неизвестный тип архива')
            return False
        r_zip.close()
        shutil.move(arch,zip_complate_path+'complate_'+zip_name)
        z_name = str(service)
        r_list = [str(reester_rename),str(z_name)]
        return r_list
    except Exception as e:
          messagebox.showerror('Ошибка', 'Не удалось распаковать архив')
          print(e)
          return  False
    return reester_rename

     
# Функция внесения платежей за интернет в биллинг UTM5
def internet_pay(abonent,pay_sum,trans_num):
    # Если posix система (Linux, Mac)
    if os_name == 'posix':
        print(os_name)
        pay_string = '/home/k/Dropbox/java/sberbankFX/utm5_payment_tool/utm5_payment_tool -a %d -b %s -e %s -C /netup/utm5/utm5_payment_tool.cfg' % (abonent, pay_sum, trans_num)
    # Если nt система (Windows)
    elif os_name == 'nt':
        print(os_name)
        pay_string = "C:\\Program Files\\NetUp\\UTM5\\utm5_payment_tool.exe -a %d -b %s -e %s -C C:\\Program Files\\NetUp\\UTM5\\utm5_payment_tool.cfg" % (abonent, pay_sum, trans_num)
        #pay_string = 'string pay'
    else:
        print('Error. Invalid OS name')
        return 1
    try:
        out = subprocess.call(pay_string,shell=True,stdout=PIPE)
        print('out ',out)
        return out
    except Exception as e:
        print('subprocess error ',e)
        out = 1
        return out


# Внесение платежей за ТВ в биллинг Atirra
def tv_pay(abonent,pay_sum,trans_num):
    # Внесение платежей за тв в Atirra
    pay_string = 'http://192.168.0.10/tv_sber_reesters.php?command=pay&account=%d&sum=%s&txn_id=%s' % (abonent, pay_sum, trans_num)
    response = urllib.request.urlopen(pay_string)
    content = response.read().decode('UTF-8')
    n_cont = content.replace('\ufeff',' ').split()
    return int(n_cont[0])


# Функция обработки платежей    
def get_pay(result_txt,zip_path,unzip_path,zip_complate_path,
            path_complate,path_reesters,path_result):
    global pay_sum_fall, pay_sum_amount, abonent_count_fall
    state_reester = 'complate_' # Подпись добавляется к названию реестра, если он успешно обработан

    # Если реестр не выбран, то функция завершается
    r_name_list = archive(zip_path,unzip_path,zip_complate_path,
                          path_complate,path_reesters,path_result)
    if(not r_name_list):
        return 0
    name_list = r_name_list[0]
    fd=str(path_reesters+name_list)

    # Если реестр не выбран
    if(not fd):
        return 0
    try:
        # Открытите реестра
        reester = dbf.Table(fd) 
        reester.open()
        reester_name = os.path.basename(fd)# Имя реестра
    except:
        messagebox.showerror('Ошибка', 'Не удалось открыть реестр')
        return 0
    reester_len = int(len(reester))-1 # Убрать из реестра последнюю строку
    abonent_all = reester_len # Количество платежей в реестре для вывода вывода на экран
    count_payments = 'Количество платежей в реестре: ' + str(reester_len) # Подсчет количества платежей в реестре
    result_txt.configure(state='normal')# Разрешить запись в поле вывода платежей
    pay_sum_amount = 0 # Сумма успешных платежей
    pay_sum_fall = 0 # Сумма не прошедших платежей
    abonent_count_fall = 0 # Количество не проведенных платежей
    # Установка счетчика цикла
    i = 0
    # Очистка поля вывода платежей
    result_txt.delete(1.0,END)

    # Если реестр за интернет
    if(str(r_name_list[1]) == service_internet):
        result_txt.insert(END,'Реестр: '+reester_name+' услуга: Интернет'+';'+'\n')
        # Пока длина реестра больше 0, на каждой итерации цикла reester_len уменьшается на 1
        while reester_len>0: 

          try:
              trans_num = reester[i][0] # Номер транзакции
              date_transaction = reester[i][1] # Дата транзакции
              abonent = int(reester[i][2]) # Лицевой счёт абонента
              pay_sum = float(reester[i][3]) # Сумма платежа
              date_check = reester[i][5] # Дата получения платежа

          except ValueError:
              trans_num = reester[i][0] # Номер транзакции
              date_transaction = reester[i][1] # Дата транзакции
              abonent = reester[i][2] # Лицевой счёт абонента
              pay_sum = reester[i][3] # Сумма платежа
              date_check = reester[i][5] # Дата получения платежа
              action_pay = 1

          else:
              # Проверка, если сумма платежа предположительно за ТВ

              if (pay_sum == 140 or pay_sum == 280 or pay_sum == 420 or pay_sum == 560 or pay_sum == 720 or pay_sum == 860):
                  action_pay = 123

              else:
                  try:
                      # Результат выполнения функции
                      action_pay = int()
                      action_pay = internet_pay(abonent,pay_sum,trans_num)
                      # Запуск функции эмитации платежа за интернет
                      #action_pay = pay_test(abonent,pay_sum,trans_num)
                  except:
                      messagebox.showerror('Ошибка','Не удалось внести платёж')
                      return 3                
          #finally:
          print ('Результат: '+str(action_pay))
          type_pay(abonent, pay_sum, trans_num, date_transaction, date_check, action_pay)
          result_row = '№:'+str(trans_num).strip()+' дата платежа:'+str(date_transaction)+' л/с:'+str(abonent).rstrip()+' сумма:'+str(pay_sum)+' дата получения:'+str(date_transaction)+state_pay+';'
          result_txt.insert(INSERT,str(result_row)+'\n')
          pay_sum_amount += pay_sum # Сумма платежей в реестре  
          i += 1 # Увеличить счетчик цикла while на 1
          reester_len -= 1 # Уменьшить счетчик количества платежей на 1
                
    # Если реестр за телевидение    
    elif(str(r_name_list[1]) == service_tv):

    # Проверка соединения с сервером FireBird 2.5 - ATIRRA
        try:
            # Подключение к серверу Atirra
            #atirra_connection_test= fdb.connect(dsn='192.168.0.13:ATIRRA', user='SYSDBA', password='masterkey')
            pass
        except:
            messagebox.showerror('Ошибка', 'Не удалось подключиться к серверу ATIRRA')
            return

        result_txt.insert(END,'Реестр: '+reester_name+' услуга: ТВ '+';'+'\n')
        while reester_len > 0: #Пока длина реестра больше 0, на каждой итерации цикла reester_len уменьшается на 1

          try:
              trans_num = reester[i][0] # Номер транзакции
              date_transaction = reester[i][1] # Дата транзакции
              abonent = int(reester[i][2]) # Лицевой счёт абонента
              pay_sum = float(reester[i][3]) # Сумма платежа
              date_check = reester[i][5] # Дата получения платежа

          except ValueError:
              trans_num = reester[i][0] # Номер транзакции
              date_transaction = reester[i][1] # Дата транзакции
              abonent = reester[i][2]
              pay_sum = reester[i][3] # Сумма платежа
              date_check = reester[i][5] # Дата получения платежа
              action_pay = 1

          else:
              # Если сумма платежа больше или равна 420 р.
              if(pay_sum >= 420):

                # Проводим платеж и если платеж прошел, то отправляем код пометки - 124
                  try:
                      action_pay = pay_test(abonent,pay_sum,trans_num)
                      #action_pay = tv_pay(abonent,pay_sum,trans_num)

                      if action_pay == 0:
                          action_pay = 124
                      else:
                         action_pay == 1

                  except Exception as e:
                      messagebox.showerror('Ошибка', 'Не удалось внести платёж')
                      return 3

              else:
                  try:
                      #action_pay = tv_pay(abonent,pay_sum,trans_num)#Результат выполнения функции
                      action_pay = pay_test(abonent,pay_sum,trans_num)
                  except:
                      messagebox.showerror('Ошибка', 'Не удалось внести платёж')
                      return 3

          #finally:
          print ('Результат: '+str(action_pay))
              
          type_pay(abonent, pay_sum, trans_num, date_transaction, date_check, action_pay)
              
          result_row = '№:'+str(trans_num).strip()+' дата платежа:'+str(date_transaction)+' л/с:'+str(abonent).rstrip()+' сумма:'+str(pay_sum)+' дата получения:'+str(date_transaction)+state_pay+' ;' 
          result_txt.insert(INSERT,str(result_row)+'\n')
          # Сумма платежей в реестре 
          pay_sum_amount += pay_sum      
          # Увеличить счетчик цикла while на 1
          i += 1
          reester_len -= 1 # Уменьшить счетчик количества реестров на 1       

    else:
        messagebox.showerror('Ошибка', 'Неизвестный тип реестра')
        return False
    abonent_count = abonent_all - abonent_count_fall # Количество успешных платежей
    pay_sum_final = pay_sum_amount - pay_sum_fall # Сумма зачисленных платежей
    pay_sum_lost = pay_sum_amount - pay_sum_final # Сумма необработанных платежей
    result_txt.insert(END,'\n'+count_payments+' Платежей успешно проведено: '+str(abonent_count)+' не проведено платежей: '+str(abonent_count_fall)+'; '+'\n')
    result_txt.insert(END,'\n'+'Сумма в реестре: '+str(pay_sum_amount)+'р. Разнесено по счетам: '+str(pay_sum_final)+'р.'+' Разница: '+str(pay_sum_lost)+'р.' )

    # Создание папки по дате реестра
    
    # Запись результата обработки реестра в файл в созданном каталоге
    folder_name = 'registries_from_' + str(date_check) # Название создаваемого каталога с датой из реестра
    folder_path = path_result + folder_name # Путь к создаваемому каталогу

    # Если папка с таким названием не создана, то создаем её
    if os.path.exists(folder_path):
        print('каталог ',folder_name,' существует')
    else:
        try:
            os.mkdir(folder_path)
        except Exception as e:
            messagebox.showerror('Ошибка','Не удалось создать каталог для резульатов обработки реестра')

    # Проверка наличия файлов в каталоге с результатами обработки реестра
    files_count = len(os.listdir(path=folder_path))
    
    # Дописываем к имени файла результата номер взятый по количеству
    # файлов в каталоге для исключения замены файлов с одинаковыми именами
    name_list=str(files_count + 1)+name_list

    # Записываем результат обработки в файл
    with open(path_result+folder_name+'/'+name_list,'w') as file:
        file.write(result_txt.get(1.0,END))
        
    reester.close()
    # Запретить редактирование поля вывода платежей
    result_txt.configure(state='disable')
    # Перемещение реестра если он успешно обработан
    shutil.move(fd, path_complate+state_reester+reester_name)


# Функция открытия и просмотра реестра в окне программы
def open_register(result_txt,path_result):
    # Выбираем реестр из папки
    register_path = filedialog.askopenfilename(initialdir = path_result, title = "Укажите обработанный реестр для чтения")

    # Если реестр не выбран
    if(not register_path): 
        return 0
    try:
        # Разрешаем запись в поле вывода
        result_txt.configure(state='normal')
        # Очистка поля вывода платежей
        result_txt.delete(1.0,END)
        # Открываем реестр
        with open(str(register_path)) as file:
            # Читаем реестр
            line = file.read() 
            # Выводим реестр на экран
            result_txt.insert(END,str(line) + '\n')
            # Запрещаем редактирование поля вывода платежей
        result_txt.configure(state='disable')
    except Exception as e:
        messagebox.showerror('Ошибка', 'Не удалось открыть реестр')
        print(e)
        


