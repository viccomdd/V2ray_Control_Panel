isLogin();

/**
 *	判断是否登录
 */
function isLogin(){
    var noLoginArr = ['login']; // 排除无需登陆的页面板块
    var page_name = document.URL.split("/")[document.URL.split("/").length - 1];
    // console.log(page_name=='');
    // console.log($.inArray(page_name, noLoginArr))
    var us = $.cookie("session");
    console.log(us, us==undefined);
    if(us==undefined){
        if($.inArray(page_name, noLoginArr)!=-1){
            return false;
        }else{
            redirect('/login');
        }
    }else{
        ping();
        /**
         *	周期获取opcdaBRG状态
         */

        var ping_status_ret= setInterval(function(){
            ping();
        },600000);
    }

}

/**
 *	logout
 */
function logout() {
    $.ajax({
        url: '/logout',
        headers: {
            Accept: "application/json; charset=utf-8",
        },
        type: 'post',
        contentType: "application/json; charset=utf-8",
        dataType: 'json',
        success: function (req) {
            console.log('successful: ', req);
            redirect('/login');
        },
        error: function (req) {
            console.log('failed: ', req);
        }
    });

}

/**
 *	ping
 */
function ping() {
    var page_name = document.URL.split("/")[document.URL.split("/").length - 1];
    console.log(page_name);
    $.ajax({
        url: '/api/ping',
        headers: {
            Accept: "application/json; charset=utf-8",
        },
        type: 'get',
        contentType: "application/json; charset=utf-8",
        dataType:'json',
        success:function(req){
            console.log(req);
            var loginUser = $.cookie("username");
            console.log(loginUser, "已登录");
            if(loginUser==='dajiji'){
                if(page_name==='login' || page_name===''){
                    redirect('/user');
                }
            }else{
                if(page_name==='login' || page_name==='user'){
                    redirect('/');
                }
            }
        },
        error:function(req){
            console.log(page_name, page_name==='login', req.responseText);
            if(!(page_name==='login')){
                console.log('跳转登录页');
                redirect('/login');
            }else{
                console.log('不跳转');
            }
        }
    });
}

/**
 *	跳转
**/
function redirect(url){
	window.location.href=url;
}

/**
 *	获取cookie
**/
function getCookie(name){
	var value = $.cookie(name);
	if(value!=null) {
		value = decodeURI(value, "utf-8");
	}
	return value;
}