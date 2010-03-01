<?php
/**
 * library for accessing  psearch
 *
 * @author renlu <xurenlu@gmail.com>
 * @version $Id$
 * @copyright renlu <xurenlu@gmail.com>, 01 三月, 2010
 * @package default
 **/

/**
 * Define DocBlock
 *//
/**
 * openapi client
 **/
class psearchClient 
{
    private $dbpath;
    private $apiurl; 
    /**
     * 构造函数;
     * @param $apiurl :openapi的接口地址
     * @dbpath 搜索
     *
     * @return void
     * @author renlu <xurenlu@gmail.com>
     **/
    function __construct($apiurl,$dbpath)
    {
        $this->changeurl($apiurl);
        $this->changedbpath($dbpath);
    }
    /**
     * generate a PHPRPC_Client object
     * 构造一个PHPRPC_Client对象;
     *
     * @return void
     * @author renlu <xurenlu@gmail.com>
     **/
    private function _get_rpc()
    {
        global $rpc_client;
        if(empty($rpc_client)){
            $rpc_client = new PHPRPC_Client();
            $rpc_client->setProxy(NULL);
            $rpc_client->useService($this->apiurl);
        }
        return $rpc_client;
    }
    /**
     * change the apiurl
     *
     * @return void
     * @author renlu <xurenlu@gmail.com>
     **/
    public function changeurl($apiurl)
    {
        $this->apiurl=$apiurl;
    }
    /**
     * change the dbpath of the psearch database;
     *
     * @return void
     * @author renlu <xurenlu@gmail.com>
     **/
    public function changedbpath($dbpath)
    {
        $this->dbpath=$dbpath;
    }
    /**
     * return the count of the generic search result;
     *
     * @return void
     * @author renlu <xurenlu@gmail.com>
     **/
    public function generic_search_count($queries){
        $rpc=$this->_get_rpc();
        return $rpc->api_generic_search_count($this->dbpath,$queries);
    }
    /**
     * return the generic search result;
     * @param $queries :an array to query in the database;
     * @return void
     * @author renlu <xurenlu@gmail.com>
     **/
    public function generic_search($queries,$offset=0,$size=10){
        $rpc=$this->_get_rpc();
        return $rpc->api_generic_search($this->dbpath,$queries,$offset,$size);
    }
    /**
     * index generic data to the database
     * @param $key:key of the data,一般用来标识这条数据,通常是数据库主键之类;
     *
     * @return void
     * @author renlu <xurenlu@gmail.com>
     **/
    public function generic_index($key,$data){
        $rpc=$this->_get_rpc();
        return $rpc->api_generic_index($this->dbpath,$key,$data);
    } 
    /**
     * return the result count of simple search 
     *
     * @param $keyword: keyword to search
     * @return void
     * @author renlu <xurenlu@gmail.com>
     **/
    public function simple_search_count($keyword)
    {
        $rpc=$this->_get_rpc();
        return $rpc->api_simple_search_count($this->dbpath,$keyword);
    }
    /**
     * execute simple search  to the database
     *
     * @return void
     * @author renlu <xurenlu@gmail.com>
     **/
    public function simple_search($keyword,$offset=0,$size=10){
        $rpc=$this->_get_rpc();
        return $rpc->api_simple_search_count($this->dbpath,$keyword,$offset,$size);
    }
    /**
     * execute simple indexing operation  to the database
     *
     * @return void
     * @author renlu <xurenlu@gmail.com>
     **/
    public function simple_index($key,$text)
    {
        $rpc=$this->_get_rpc();
        return $rpc->api_simple_index($this->dbpath,$key,$text);
    }
    /**
     * get  the total documents number of the database
     *
     * @return void
     * @author renlu <xurenlu@gmail.com>
     **/
    public function get_documents_count()
    {
        $rpc=$this->_get_rpc();
        return $rpc->api_get_documents_count($this->dbpath);
    }
    /**
     * remove a document from the database
     *
     * @return void
     * @author renlu <xurenlu@gmail.com>
     **/
    public function remove_document($docid)
    {
        $rpc=$this->_get_rpc();
        return $rpc->api_remove_document($this->dbpath,$docid);  
    }
    /**
     * init a generic db
     *
     * @return void
     * @author renlu <xurenlu@gmail.com>
     * @example:
     * generic_init(
     *  array(
     *      "author"=>array("prefix"=>"A","segment"=>False),
     *      "text"=>array("prefix"=>"T","segment"=>True),
     *      "date"=>array("prefix"=>"D","segment"=>False)
     *      )
     *  );
     **/
    public function generic_init($dict){
        $rpc=$this->_get_rpc();
        return $rpc->api_generic_init($this->dbpath,$dict);
    }
    /**
     * init a simple db:
     *
     * @return void
     * @author renlu <xurenlu@gmail.com>
     * 
     **/
    public function simple_init()
    {
        $rpc=$this->_get_rpc();
        return $rpc->api_simple_init($this->dbpath);
    }
}
