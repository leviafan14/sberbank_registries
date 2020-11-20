<?PHP                                                                                     	
/*
инструкция: 
необходимо для работы: 

1. apache + php5(с модулем поддержки Interbase/Firebird)
2. копируем в удобную папочку apache 
3. расширение .php или любое другое в зависимости от настроек 
4. в скрипте меняем параметры 
	
	atirra_host     = "192.168.0.94"         // IP сервера Ашкуишкв
	atirra_db       = "/opt/db/atirra_fdb";  // база данных
	atirra_user     = "SYSDBA";              // пользователь БД
	atirra_password = "masterkey";           // пароль БД 
	paysource_id    = 0;   
	log_file        = "/var/www/atirra_osmp.log"; // куда пишем лог 
	
	на ваши данные 

5. даем ссылку в OSMP и тестируемся, все тесты должны пройти на 100%. 

0   ОК    
1   Временная ошибка. Повторите запрос позже
4   Неверный формат идентификатора  абонента
5   Идентификатор абонента не найден ( Ошиблись номером )
7   Прием  платежа запрещен  провайдером
8   Прием  платежа запрещен  по техническим  причинам
79  Счет абонента не активен
90  Проведение платежа  не окончено
241 Сумма слишком мала
242 Сумма слишком велика
243 Невозможно проверить состояние счета
300 Другая ошибка провайдера

*/

define('atirra_host',       '192.168.0.13');          // сервер Firebird 192.168.0.13
define('atirra_db',         '/var/lib/firebird/data/ATIRRA_DB.FDB');                 // бд 
define('atirra_user',       'AMIGO');             // пользователь БД
define('atirra_password',   '8845svma');          // пароль БД 
define('paysource_id',      29595);                    // ID источника платежа для системы ОСМП из таблицы 
define('LOG_FILE',          'var/log/atirra_reesters.log'); // куда пишем лог 
function LogWrite($str) {
    $file = fopen(LOG_FILE,"a-");
    fputs($file, date("Y-m-d G:i:s")." - ".$str.PHP_EOL);
    fclose($file);
};

function EchoAnswer($answer) {
    LogWrite('answer: '.$answer);
    echo $answer;
    return $answer;
}

function EchoErrorCheck($code) {
    global $txn_id;
    $s = 1;  
    EchoAnswer($s);
}

function EchoErrorPay($code) {
    global $txn_id;
    $s = 1;   
    EchoAnswer($s);
}

function CheckAccount($value) {
    if (preg_match('/^\d+$/', $value)) 
        return True;
    else 
        return False;
}

function CheckSum($sum) {
    if (is_numeric($sum)) 
        if ($sum > 0) 
            return True;
        else {
            EchoErrorPay('241');
            return False;
        }
    else { 
        EchoErrorPay('300');
        return False;
    }
}

function CheckTxnID($value) {
    if (preg_match('/^\d+$/', $value))
        return True;
    else 
        return False;
}

function GetUserInfo($account) {
    $fb_ses = @ibase_pconnect(atirra_host.':'.atirra_db, atirra_user, atirra_password, "UTF8"); 
    if ($fb_ses) { 
        $customer_id = -1; 
        $balance     = 0; 
        #$sql = "SELECT CUSTOMER_ID, (DEBT_SUM*(-1)) DEBT_SUM, c.surname||coalesce(' '||c.firstname||coalesce(' '||c.midlename,''),'') as FIO FROM CUSTOMER C WHERE C.ACCOUNT_NO = '$account'";
        $sql = "select CUSTOMER_ID, (DEBT_SUM * (-1)) DEBT_SUM, C.SURNAME || coalesce(' ' || C.FIRSTNAME || coalesce(' ' || C.MIDLENAME, ''), '') as FIO,
        s.street_short||s.street_name||' д.'||h.house_no||' кв.'||c.flat_no as ADR from CUSTOMER C inner join HOUSE H on (C.HOUSE_ID = H.HOUSE_ID) inner join street s on (s.street_id = h.street_id) where C.ACCOUNT_NO = '$account'";
        $fb_tr  = ibase_trans(IBASE_READ + IBASE_NOWAIT, $fb_ses);
        $fb_res = ibase_query($fb_tr, $sql);
        $row = ibase_fetch_assoc($fb_res);
        ibase_rollback($fb_tr);
        if ($row) {
            $s = '<?xml version="1.0" encoding="UTF-8"?>'.
                '<response>'.
                '<result>0</result>'.
                '<comment>'.$row["ADR"].'</comment>'.
                '</response> ';
            EchoAnswer($s);
        }
        else EchoErrorCheck('5'); // Абонент не найден
    }
    else EchoErrorCheck('8'); // Сервис не доступен
}

function MakePayment($account, $sum, $txn_id, $txn_date) {
    $fb_ses = @ibase_pconnect(atirra_host.':'.atirra_db, atirra_user, atirra_password, "UTF8"); 
    if ($fb_ses) { 
        $sql    = "select PAYMENT_ID from payment p inner join pay_doc pd on (p.pay_doc_id = pd.pay_doc_id) where pd.paysource_id = ".paysource_id." and p.ext_pay_id = '$txn_id'";
        $fb_tr  = ibase_trans(IBASE_READ + IBASE_NOWAIT, $fb_ses);
        $fb_res = ibase_query($fb_tr, $sql);
        $row    = ibase_fetch_assoc($fb_res);
        ibase_rollback($fb_tr);
        if (!$row){ 
            $sql = "SELECT CUSTOMER_ID  FROM CUSTOMER C WHERE C.ACCOUNT_NO = '$account'";
            $fb_tr  = ibase_trans(IBASE_READ + IBASE_NOWAIT, $fb_ses);
            $fb_res = ibase_query($fb_tr, $sql);
            $row = ibase_fetch_assoc($fb_res);
            ibase_rollback($fb_tr);
            if ($row){
                $date = date('Y-m-d');
                $sql    = "select coalesce(PAYMENT_ID,0) PAYMENT_ID from ADD_PAYMENT_FROM_EXT_SYSTEMS('$account', $sum, '$date', ".paysource_id.", '$txn_id', 'sberbank')";
                $fb_tr  = ibase_trans(IBASE_WRITE + IBASE_NOWAIT, $fb_ses);
                $fb_res = ibase_query($fb_tr, $sql);
                $row    = ibase_fetch_assoc($fb_res);
                ibase_commit($fb_tr);
                if ($row['PAYMENT_ID'] > 0) {
                    $s=0;
                    EchoAnswer($s);
                }
                else EchoErrorPay('7'); // Прием платежей для данного клиента невозможен
            }
            else EchoErrorPay('5'); // Клиент не найден
        }
        else { // Платеж уже существует
            $s=1;
            EchoAnswer($s);
        }
    }
    else EchoErrorPay('8'); // Сервис не доступен    
}
//header("Content-type: text/xml"); 

LogWrite('request: '.print_r($_GET, true));

if (array_key_exists('command', $_GET)) { // GET передача
    $command = $_GET["command"];
    if (array_key_exists('txn_id', $_GET))   $txn_id   = $_GET['txn_id'];   else $txn_id   = '';
    if (array_key_exists('account',$_GET))   $account  = $_GET['account'];  else $account  = '';    
    if (array_key_exists('sum',    $_GET))   $sum      = $_GET['sum'];      else $sum      = '';
    if (array_key_exists('txn_date', $_GET)) $txn_date = $_GET['txn_date']; else $txn_date = '';
}
else { 
    EchoErrorCheck('300');
    exit;
}

// Проверим формат лицевого
if (!CheckAccount($account)) {
    EchoErrorCheck('4');
    exit;
}

// Проверим формат txn_id
if (!CheckTxnID($txn_id) AND $command == "pay") {
	EchoErrorPay('300');
    exit;
}
        
switch ($command) {
    case 'check' :    // запрос информации про абонента, и проверка возможности оплаты (info); 
        GetUserInfo($account);
        break;
    case 'pay' :    // запрос на оплату платежа (pay); 
        if (CheckSum($sum)) {
            MakePayment($account, $sum, $txn_id, $txn_date);
        }
        break;
    default: 
        //EchoErrorCheck('300');
	
}

?>
