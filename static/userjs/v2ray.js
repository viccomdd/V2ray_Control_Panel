var v2rayObj = new Object();
var localv2rayObj = new Object();

if(getCookie('session')!==undefined){
    get_v2rayInfo();
    get_serverConfig();
    creat_v2ray_apps_table();
    get_logs();
}

var ping_status_ret= setInterval(function(){
    get_v2rayInfo();
},60000);


function makeid() {
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
    for (var i = 0; i < 5; i++)
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    return text;
}

function guid1() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8);
        return v.toString(16);
    });
}

function guid2() {
    function S4() {
       return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
    }
    return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
}

function utf8_to_b64(str) {
   return window.btoa(unescape(encodeURIComponent(str)));
}

function b64_to_utf8(str) {
   return decodeURIComponent(escape(window.atob(str)));
}



/**
 *    get_logs-get-/api/logs/{id}
 */
function get_logs(id) {
    if (id === undefined || id === '') {
        id = 'console';
    }
    $.ajax({
        url: '/api/logs/' + id,
        headers: {
            Accept: "application/json; charset=utf-8",
        },
        type: 'get',
        contentType: "application/json; charset=utf-8",
        dataType: 'json',
        success: function (req) {
            // console.log(req);
            if (req.message) {
                var obj=JSON.parse(req.message);
                var log_html = "";
                $.each(obj, function (i, val) {
                    // console.log(i,val);
                    log_html = log_html + '<tr>' +
                        '<td>' + val + '</td>' +
                        '</tr>';

                });

                $("table." + id + " tbody").empty();
                $("table." + id + " tbody").append(log_html + '</tr>');

            }
        },
        error: function (req) {
            console.log(req);
        }
    });
}

/**
 *    creat_v2rayInfo_table
 */
function get_v2rayInfo() {
    $.ajax({
        url: '/api/v2rayInfo',
        headers: {
            Accept: "application/json; charset=utf-8",
        },
        type: 'get',
        contentType: "application/json; charset=utf-8",
        dataType: 'json',
        success: function (req) {
            // console.log(req);
            var v2rayinfoObj = req.message;
            var status_color = "mdui-text-color-red";
            if(v2rayinfoObj.status==='running'){
                status_color = "mdui-text-color-green";
            }
            var info_html = '<tr>' +
                '<td class="mdui-hidden-sm mdui-hidden-xs">服务器IP:</td><td>' + v2rayinfoObj.publicip + '</td>' +
                '<td class="mdui-hidden-sm mdui-hidden-xs">安装版本:</td><td>' + v2rayinfoObj.version + '</td>' +
                '<td class="mdui-hidden-sm mdui-hidden-xs">运行状态:</td><td class="' + status_color + '">' + v2rayinfoObj.status + '</td>' +
                '</tr>';

            $("table.v2rayInfo tbody").empty();
            $("table.v2rayInfo tbody").append(info_html+ '</tr>');

        },
        error: function (req) {
            console.log(req);
        }
    });
}

/**
 *	creat_config_table
 */
function creat_config_table(obj, tableobj) {
    var html = '';
    if (obj.hasOwnProperty('listen')) {
        html = html + '<tr>' +
            '<td>绑定IP</td>' +
            '<td>' + obj.listen + '</td>' +
            '</tr>'
    }
    if (obj.hasOwnProperty('port')) {
        html = html + '<tr>' +
            '<td>端口</td>' +
            '<td>' + obj.port + '</td>' +
            '</tr>'
    }
    if (obj.hasOwnProperty('protocol')) {
        html = html + '<tr>' +
            '<td>协议类型</td>' +
            '<td>' + obj.protocol + '</td>' +
            '</tr>'
    }
    if (obj.hasOwnProperty('streamSettings')) {
        html = html + '<tr>' +
            '<td>传输方式</td>' +
            '<td>' + obj.streamSettings.network + '</td>' +
            '</tr>';
        html = html + '<tr>' +
            '<td>访问路径</td>' +
            '<td>' + obj.streamSettings.wsSettings.path + '</td>' +
            '</tr>'
    }

    tableobj.empty();
    tableobj.append(html);
}

/**
 *	creat_users_table
 */
function creat_users_table(obj, tableobj) {
    var trhtml = '';
    var current_user = getCookie('username');
    var extracode = undefined;
    if(getCookie('extracode')!==undefined){
        extracode = getCookie('extracode');
    }

    if (current_user === 'dajiji') {
        if (extracode !== undefined) {
            var userstat = '';
            if (val.hasOwnProperty('uplink')) {
                if(parseInt(val.downlink) > 1000000){
                    userstat = (Math.ceil(parseInt(val.uplink)/1000000)).toString() + " MB / " + (Math.ceil(parseInt(val.downlink)/1000000)).toString() + " MB";
                }else{
                    userstat = (Math.ceil(parseInt(val.uplink)/1000)).toString() + " KB / " + (Math.ceil(parseInt(val.downlink)/1000)).toString() + " KB";
                }
            }
            $.each(obj, function (i, val) {
                if (extracode === val.desc) {
                    trhtml = trhtml + '<tr>' +
                        '<td  width="35%">' + extracode + '</td>' +
                        '<td  width="40%">' + userstat + '</td>' +
                        '<td  width="25%">' +
                        '<button class="mdui-btn mdui-btn-icon usershare"  mdui-tooltip="{content: \'查看用户配置\'}" data-user = "' + extracode + '" data-uuid="' + val.id + '"><i class="mdui-icon material-icons">share</i></button>' +
                        '<button class="mdui-btn mdui-btn-icon useredit"  mdui-tooltip="{content: \'修改用户信息\'}" data-user = "' + extracode + '" data-uuid="' + val.id + '"><i class="mdui-icon material-icons">edit</i></button>' +
                        '<button class="mdui-btn mdui-btn-icon userdelete"  mdui-tooltip="{content: \'删除用户\'}" data-uuid="' + val.id + '"><i class="mdui-icon material-icons">delete</i></button>' +
                        '</td>' +
                        '</tr>'
                }
            });
        }
    } else {
        $.each(obj, function (i, val) {
            var user = '';
            if (val.hasOwnProperty('email')) {
                user = val.email;
            }
            var userstat = '';
            if (val.hasOwnProperty('uplink')) {
                if(parseInt(val.downlink) > 1000000){
                    userstat = (Math.ceil(parseInt(val.uplink)/1000000)).toString() + " MB / " + (Math.ceil(parseInt(val.downlink)/1000000)).toString() + " MB";
                }else{
                    userstat = (Math.ceil(parseInt(val.uplink)/1000)).toString() + " KB / " + (Math.ceil(parseInt(val.downlink)/1000)).toString() + " KB";
                }            }
            trhtml = trhtml + '<tr>' +
                '<td  width="35%">' + user + '</td>' +
                '<td  width="40%">' + userstat + '</td>' +
                '<td  width="25%">' +
                '<button class="mdui-btn mdui-btn-icon usershare"  mdui-tooltip="{content: \'查看用户配置\'}" data-user = "' + user + '" data-uuid="' + val.id + '"><i class="mdui-icon material-icons">share</i></button>' +
                '<button class="mdui-btn mdui-btn-icon useredit"  mdui-tooltip="{content: \'修改用户信息\'}" data-user = "' + user + '" data-uuid="' + val.id + '"><i class="mdui-icon material-icons">edit</i></button>' +
                '<button class="mdui-btn mdui-btn-icon userdelete"  mdui-tooltip="{content: \'删除用户\'}" data-uuid="' + val.id + '"><i class="mdui-icon material-icons">delete</i></button>' +
                '</td>' +
                '</tr>'
        });

    }

    tableobj.empty();
    tableobj.append(trhtml);


    $('button.useredit').click(function () {
        var curent_user = $(this).data('user');
        var curent_uuid = $(this).data('uuid');
        mdui.dialog({
            title: '标题',
            modal: true,
            content: '<div class="mdui-textfield">\n' +
                '<div class="mdui-col-md-11">' +
                '  <i class="mdui-icon material-icons">account_circle</i>\n' +
                '  <input class="mdui-textfield-input" name="newuser" type="text" value="' + curent_user + '" placeholder="UserName"/>\n' +
                '</div>\n' +
                '</div>\n' +
                '<div class="mdui-textfield">\n' +
                '<div class="mdui-col-md-11">' +
                '  <i class="mdui-icon material-icons">fingerprint</i>\n' +
                '  <input class="mdui-textfield-input" name="newuuid" type="text" value="' + curent_uuid + '" placeholder="UUID" readonly/>\n' +
                '</div>\n' +
                '</div>\n',
            buttons: [
                {
                    text: '取消'
                },
                {
                    text: '确认',
                    onClick: function (inst) {
                        // mdui.alert('点击确认按钮的回调');
                        var v1 = $("input[name='newuuid']").val();
                        var v2 = $("input[name='newuser']").val();
                        var userObj = {
                            "id": v1,
                            "desc": v2,
                            "email": v2,
                            "alterId": 64
                        };
                        $.each(localv2rayObj.clients, function (i, val) {
                            // console.log(i, val);
                            if (val.id === curent_uuid) {
                                console.log("delete:: ", i, val);
                                localv2rayObj.clients.splice(i, 1, userObj);
                                return false;
                            }
                        });
                        // localv2rayObj.clients.push(userObj);
                        // console.log(localv2rayObj);
                        var clients  = localv2rayObj.clients;
                        var clientstable = $("table.v2ray-clients tbody");
                        creat_users_table(clients, clientstable);
                    }
                }
            ]
        });

    });

    $('button.userdelete').click(function () {
        var curent_uuid = $(this).data('uuid');

        mdui.confirm('确定删除', undefined, function () {
            // mdui.alert('点击了确认按钮');
            // console.log(curent_uuid);
            $.each(localv2rayObj.clients, function (i, val) {
                // console.log(i, val);
                if(val.id===curent_uuid){
                    console.log("delete:: ", i, val);
                    localv2rayObj.clients.splice(i, 1);
                    return false;
                }
            });
            // console.log(localv2rayObj.clients);
            var clients  = localv2rayObj.clients;
            var clientstable = $("table.v2ray-clients tbody");
            creat_users_table(clients, clientstable);
        }, undefined, {      confirmText: '确定', cancelText: '取消', modal: true});

    });

    $('button.usershare').click(function () {
        var curent_uuid = $(this).data('uuid');
        var curent_user = $(this).data('user');
        var curent_host = window.document.location.hostname
        var vmess_json = {
            "v": "2",
            "ps": curent_user,
            "add": curent_host,
            "port": "443",
            "id": curent_uuid,
            "aid": "64",
            "net": "ws",
            "type": "auto",
            "host": curent_host,
            "path": localv2rayObj.streamSettings.wsSettings.path,
            "tls": "tls"
        };
        var raw_vmess_link = utf8_to_b64(JSON.stringify(vmess_json));
        var vmess_link = "vmess://"+ raw_vmess_link;
        // console.log("vmess_link:::", vmess_link);
        mdui.dialog({
            content: '<div class="mdui-col-md-6 mdui-col-sm-12 mdui-center mdui-typo" style="padding-top: 0px; padding-bottom: 0px; padding-left: 20px"><pre>' + vmess_link + '</pre></div><div id="vmess_qrcode" class="mdui-col-md-6 mdui-col-sm-12 mdui-text-center mdui-center" style="padding-left: 10px; padding-top: 10px; height: 250px"></div>',
            buttons: [
                {
                    text: '复制',
                    onClick: function (inst) {
                        // console.log(vmess_link);
                        $("#vmessContent").val(vmess_link);
                        $("button.vmess-copy").trigger("click");
                    }
                },
                {
                    text: '关闭'
                }
            ]
        });
        $('#vmess_qrcode').qrcode({
            render: "canvas",
            width:250,
            height:250,
            text: vmess_link
        });

    });


}


/**
 *	creat_v2ray_apps_table-get
 */
function creat_v2ray_apps_table() {
        $.ajax({
        url: '/api/v2rayApps',
        headers: {
            Accept: "application/json; charset=utf-8",
        },
        type: 'get',
        contentType: "application/json; charset=utf-8",
        dataType:'json',
        success: function (req) {
            // console.log(req);
            if(req.message){
                var v2rayAppsFiles = req.message;
                var apps_html = '';
                $.each(v2rayAppsFiles, function(i, app){
                    // console.log(i ,app);
                    apps_html = apps_html + '<tr>\n' +
                        '                        <td><i class="mdui-icon material-icons">' + app.platform + '</i> '+ app.platform.toUpperCase() + '</td>\n' +
                        '                        <td>\n' +
                        '                            <div class="mdui-chip"\n' +
                        '                                 onclick="window.open(\''+ app.filename +'\'); ">\n' +
                        '                                <span class="mdui-chip-icon mdui-color-green"><i class="mdui-icon material-icons">file_download</i></span>\n' +
                        '                                <span class="mdui-chip-title">'+ app.appName + ' </span>\n' +
                        '                            </div>\n' +
                        '                        </td>\n' +
                        '                    </tr>'
                });

            $("table.v2ray-apps tbody").empty();
            $("table.v2ray-apps tbody").append(apps_html);

            }

        },
        error:function(req){
            console.log(req);
        }
    });

}

/**
 *	load_defaultConfig-get
 */
function load_defaultConfig() {
    $.ajax({
        url: '/api/defaultConfig',
        headers: {
            Accept: "application/json; charset=utf-8",
        },
        type: 'get',
        contentType: "application/json; charset=utf-8",
        dataType:'json',
        success: function (req) {
            console.log(req);
            mdui.snackbar({
              message: '读取初始化配置成功'
            });
            if (req.message) {
                $(".v2rayAction").prop('disabled', false);
                v2rayObj = req.message;
                var tempv2rayObj = req.message;
                if (tempv2rayObj.hasOwnProperty('inbounds')) {
                    var inbounds = tempv2rayObj.inbounds;
                    if (inbounds.length > 0) {
                        var inbound = inbounds[0];
                        localv2rayObj.streamSettings = inbound.streamSettings;
                        // $.each(inbound, function(k, v){
                        //     console.log(k ,v);
                        // });
                        var configtable = $("table.v2ray-config tbody")
                        creat_config_table(inbound, configtable);

                        if (inbound.hasOwnProperty('settings')) {
                            localv2rayObj.clients = inbound.settings.clients;
                            var clients = inbound.settings.clients;
                            var clientstable = $("table.v2ray-clients tbody");
                            creat_users_table(clients, clientstable);
                        }

                    }
                }
            }else{
                $(".v2rayAction").prop('disabled', true);
            }
        },
        error:function(req){
            console.log(req);
            mdui.snackbar({
              message: '读取初始化配置失败'
            });
        }
    });
}


/**
 *	get_serverConfig-get
 */
function get_serverConfig() {
    $.ajax({
        url: '/api/serverConfig',
        headers: {
            Accept: "application/json; charset=utf-8",
        },
        type: 'get',
        contentType: "application/json; charset=utf-8",
        dataType:'json',
        success: function (req) {
            // console.log(req);
            if (req.message) {
                $(".v2rayAction").prop('disabled', false);
                v2rayObj = req.message;
                var tempv2rayObj = req.message;
                if (tempv2rayObj.hasOwnProperty('inbounds')) {
                    var inbounds = tempv2rayObj.inbounds;
                    if (inbounds.length > 0) {
                        var inbound = inbounds[0];
                        localv2rayObj.streamSettings = inbound.streamSettings;
                        // $.each(inbound, function(k, v){
                        //     console.log(k ,v);
                        // });
                        var configtable = $("table.v2ray-config tbody")
                        creat_config_table(inbound, configtable);

                        if (inbound.hasOwnProperty('settings')) {
                            localv2rayObj.clients = inbound.settings.clients;
                            var clients = inbound.settings.clients;
                            var clients_new = new Array();
                            if(req.stats.length > 0){
                                var stats = req.stats;
                                $.each(clients, function (i, val) {
                                    var clientname = val.email;
                                    $.each(stats, function (j, s) {
                                        if(s[0] === 'user' && s[1] === clientname){
                                            val[s[3]] =s[4];
                                        }
                                    })
                                    clients_new.push(val);
                                });


                            }
                            // console.log("clients_new::", clients_new);
                            var clientstable = $("table.v2ray-clients tbody");
                            creat_users_table(clients_new, clientstable);
                        }

                    }
                }
            }else{
                $(".v2rayAction").prop('disabled', true);
            }
        },
        error:function(req){
            console.log(req);
        }
    });
}

/**
 *	post_serverConfig-post
 */
function post_serverConfig(postdata) {
    $.ajax({
        url: '/api/serverConfig',
        headers: {
            Accept: "application/json; charset=utf-8",
        },
        type: 'post',
        data: JSON.stringify({"config": postdata }),
        contentType: "application/json; charset=utf-8",
        dataType:'json',
        success:function(req){
            console.log('successful: ', req);
            mdui.snackbar({
              message: '保存成功'
            });
        },
        error:function(req){
            console.log('failed: ', req);
            mdui.snackbar({
              message: '保存失败'
            });
        }
    });
}

/**
 *	post_serverConfig-post
 */
function apply_serverConfig(postdata) {
    $.ajax({
        url: '/api/applyConfig',
        headers: {
            Accept: "application/json; charset=utf-8",
        },
        type: 'post',
        data: JSON.stringify({"config": postdata }),
        contentType: "application/json; charset=utf-8",
        dataType:'json',
        success:function(req){
            console.log('successful: ', req);
            mdui.snackbar({
              message: '应用成功'
            });
        },
        error:function(req){
            console.log('failed: ', req);
            mdui.snackbar({
              message: '应用失败'
            });
        }
    });
}

/**
 *	start_v2ray-post
 */
function start_v2ray() {
    if (!$.isEmptyObject(v2rayObj)) {
        $.ajax({
            url: '/api/v2rayStart',
            headers: {
                Accept: "application/json; charset=utf-8",
            },
            type: 'post',
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function (req) {
                console.log('successful: ', req);
                mdui.snackbar({
                  message: '启动成功'
                });
                get_v2rayInfo();
            },
            error: function (req) {
                console.log('failed: ', req);
                mdui.snackbar({
                  message: '启动失败'
                });
            }
        });
    }

}

/**
 *	stop_v2ray-post
 */
function stop_v2ray() {
    if (!$.isEmptyObject(v2rayObj)) {
        $.ajax({
            url: '/api/v2rayStop',
            headers: {
                Accept: "application/json; charset=utf-8",
            },
            type: 'post',
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function (req) {
                console.log('successful: ', req);
                mdui.snackbar({
                  message: '停止成功'
                });
                get_v2rayInfo();
            },
            error: function (req) {
                console.log('failed: ', req);
                mdui.snackbar({
                  message: '停止失败'
                });
            }
        });
    }

}

/**
 *	restart_v2ray-post
 */
function restart_v2ray() {
    if (!$.isEmptyObject(v2rayObj)) {
        $.ajax({
            url: '/api/v2rayRestart',
            headers: {
                Accept: "application/json; charset=utf-8",
            },
            type: 'post',
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function (req) {
                console.log('successful: ', req);
                mdui.snackbar({
                  message: '重启成功'
                });
                get_v2rayInfo();
            },
            error: function (req) {
                console.log('failed: ', req);
                mdui.snackbar({
                  message: '重启失败'
                });
            }
        });
    }

}


/**
 *	update_v2ray-post
 */
function update_v2ray() {
    $.ajax({
        url: '/api/v2rayUpdate',
        headers: {
            Accept: "application/json; charset=utf-8",
        },
        type: 'post',
        contentType: "application/json; charset=utf-8",
        dataType: 'json',
        success: function (req) {
            console.log('successful: ', req);
            mdui.snackbar({
              message: '升级任务进行中……'
            });
            setTimeout(function () {
                get_v2rayInfo();
            }, 6000);
        },
        error: function (req) {
            console.log('failed: ', req);
            mdui.snackbar({
              message: '升级任务失败……'
            });
        }
    });
}