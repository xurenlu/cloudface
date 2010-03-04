<?php
class CLogger
{
	const TRACE		= 0;
	const DEBUG		= 1;
	const INFO		= 2;
	const WARN		= 3;
	const ERR		= 4;
	static public $level= 0;
	static private $defaultLevel = self::ERR;

	static private function Log($msg, $objs, $file, $line, $level) 
	{
		if(self::getLevel() <= $level) {
			switch($level) {
				case self::TRACE:
					$header = '[0;32;1m[TRACE] ';
					break;
				case self::DEBUG:
					$header = '[0;33;1m[DEBUG] ';
					break;
				case self::INFO:
					$header = '[0;36;1m[INFO ] ';
					break;
				case self::WARN:
					$header = '[0;35;1m[WARN ] ';
					break;
				case self::ERR:
					$header = '[0;31;1m[ERROR] ';
					break;
				default:
					return;
			}
			if($file) {
				$header .= "__ $file __ , ";
			}
			if($line) {
				$header .= "__ $line __ : ";
			}
			//error_log($header . $msg . print_r($objs, TRUE) . '[0;0;0m');
			echo ($header . $msg . print_r($objs, TRUE) . '[0;0;0m');
		}
	}

	static function SetLevel($level)
	{
		self::$level = $level;	
	}

	static function GetLevel()
	{
		if(isset(self::$level)) {
			return self::$level;
		} 
		return self::$defaultLevel;
	}

	static function Trace($msg, $objs = NULL, $file=NULL, $line=NULL)
	{
		self::Log($msg, $objs, $file, $line, self::TRACE);
	}
	
	static function Debug($msg, $objs = NULL, $file=NULL, $line=NULL)
	{
		self::Log($msg, $objs, $file, $line, self::DEBUG);
	}

	static function Info($msg, $objs = NULL, $file=NULL, $line=NULL)
	{
		self::Log($msg, $objs, $file, $line, self::INFO);
	}
	
	static function Warn($msg, $objs = NULL, $file=NULL, $line=NULL)
	{
		self::Log($msg, $objs, $file, $line, self::WARN);
	}
	
	static function Err($msg, $objs = NULL, $file=NULL, $line=NULL)
	{
		self::Log($msg, $objs, $file, $line, self::ERR);
	}
	
}
/*
CLogger::setLevel(CLogger::TRACE);
CLogger::trace('i want to trace', __FILE__, __LINE__);
CLogger::debug('i want to debug', __FILE__, __LINE__);
CLogger::info('i want print info', __FILE__, __LINE__);
CLogger::warn('i want print warn', __FILE__, __LINE__);
CLogger::err('i want print err', __FILE__, __LINE__);

error_log("_________");
CLogger::trace('i want to trace');
CLogger::debug('i want to debug');
CLogger::info('i want print info');
CLogger::warn('i want print warn');
CLogger::err('i want print err');
*/
?>
