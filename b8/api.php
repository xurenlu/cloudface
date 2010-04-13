<?php
/**  vim: fdm=marker  
 * */
require "./b8.php";
define("PREFIX","b8php.");
define("MEM_HOST","localhost");
define("MEM_PORT",11211);
define("TIME",time());
/*** {{{ _gettokens 
*/ 
function _gettokens($text)
{
    $cws = scws_open("utf8");
    scws_send_text($cws, $text);
    $raw_tokens=array();
    while ($res = scws_get_result($cws))
    {
        foreach ($res as $tmp)
        {
            if ($tmp['len'] == 1 && $tmp['word'] == "\r")
                continue;
            if ($tmp['len'] == 1 && $tmp['word'] == "\n")
                continue;
            else		
                $raw_tokens[$tmp['word']]++;
        }
    }
    scws_close($cws);
    return $raw_tokens;
}
/** }}} */
/*** {{{  _getmem 
*/ 
function _getmem()
{
    $mem=new Memcache();
    $mem->addServer(MEM_HOST,MEM_PORT);
    return $mem;
}
/** }}} */
/*** {{{  _getb8 
*/ 
function _getb8()
{
    $b8=new b8; 
	if(!$b8->constructed) {
        error_log("Could not initialize b8. Truncating.");
        return NULL;
    }
    return $b8;
}
/** }}} */
/*** {{{  learn_spam 
*/ 
function api_learn_spam($text)
{
    $b8=_getb8();
    if(is_null($b8))
        return false;
    $b8->learn($text,"spam");
    return true;
}
/** }}} */
/*** {{{  learn_ham 
*/ 
function api_learn_ham($text)
{
    $b8=_getb8();
    if(is_null($b8))
        return false;
    $b8->learn($text,"ham");

}
/** }}} */
/*** {{{  unlearn_spam 
*/ 
function api_unlearn_spam($text)
{
    $b8=_getb8();
    if(is_null($b8))
        return false;
    $b8->unlearn($text,"spam");
    return true;
}
/** }}} */
/*** {{{  unlearn_ham 
*/ 
function api_unlearn_ham($text)
{
    $b8=_getb8();
    if(is_null($b8))
        return false;
    $b8->unlearn($text,"ham");

}
/** }}} */
/*** {{{  api_classify 
*/ 
function api_classify($text)
{
    $b8=_getb8();
    if(is_null($b8))
        return false;
    return $b8->classify($text); 
}
/** }}} */
/*** {{{ api_test_comment 
 * return 0 means somefield is in the whitelist;
 * return 1 means somefield is in the blacklist; 
 *
 * */
function api_test_comment($comment){
    $mem=_getmem();
    if(!empty($comment["ip"]))
    {
        //testing if the source ip is in the whitelist or the blacklist;
        $ip_expire=$mem->get(PREFIX."ipwhitelist.".$comment["ip"]);
        if($ip_expire && $ip_expire>TIME)
            return 0;
        unset($ip_expire);

        $ip_expire=$mem->get(PREFIX."ipblacklist.".$comment["ip"]);
        if($ip_expire && $ip_expire>TIME)
            return 1;
        unset($ip_expire);
        //testing if the urls were in the blacklist;
        foreach($comment["urls"] as $url){
            if(!empty($url)){
                $url_expire=$mem->get(PREFIX."urlblacklist.".$url);
                if($url_expire && $url_expire>TIME)
                    return 1;
                unset($url_expire);
            }
        }
        $words=_gettokens($comment["text"]);
        foreach($words as $w=>$count){
            if(!empty($w)){
                $w_expire=$mem->get(PREFIX."wordblacklist.".$w);
                if($w_expire && $w_expire>TIME)
                    return 1;
            }
        }
        //now return the b8 score:
        return array("score"=>api_classify($comment['text']),"code"=>200,"data"=>$comment);

    }  
}
/*** }}} */
/*** {{{  api_execute 
*/ 
function api_execute($func,$args)
{
    $ret=call_user_func_array($func,$args); 
    if(is_array($ret)){
        return array_merge(array("code"=>200),$ret);
    }
    else{
        return array("code"=>200,"data"=>$ret);
    }
}
/** }}} */

/**
 * testing
 * @example:
$comment=array(
    "ip"=>"127.0.0.1",
    "text"=>"本处招聘兼职",
    "urls"=>array("http://www.sohu.com")
);
(api_test_comment($comment));
 */
include('phprpc/phprpc_server.php');
$server = new PHPRPC_Server();
$funcs=get_defined_functions();
foreach($funcs["user"] as $f){
    if(preg_match("/^api_/i",$f)){
        $server->add($f);
    }
}
$server->start();
//var_dump( api_test_comment(array("ip"=>"127.0.0.1","text"=>"我们")));
