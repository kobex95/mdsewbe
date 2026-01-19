function nginxPost(method, args, callback){
    var loadT = layer.msg('正在获取...', { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'nginx', func:method, args:JSON.stringify(args)}, function(data) {
        layer.close(loadT);
        if (!data.status){
            layer.msg(data.msg,{icon:0,time:2000,shade: [0.3, '#000']});
            return;
        }

        if(typeof(callback) == 'function'){
            callback(data);
        }
    },'json'); 
}

function nginxPluginService(_name, version){
    var data = {name:_name, func:'status'}
    if ( typeof(version) != 'undefined' ){
        data['version'] = version;
    } else {
        version = '';
    }

    nginxPost('status', data, function(data){
        if (data.data == 'start'){
            nginxPluginSetService(_name, true, version);
        } else {
            nginxPluginSetService(_name, false, version);
        }
    });
}

function nginxPluginSetService(_name ,status, version){
    var serviceCon ='<p class="status">当前状态：<span>'+(status ? '开启' : '关闭' )+
        '</span><span style="color: '+
        (status?'#20a53a;':'red;')+
        ' margin-left: 3px;" class="glyphicon ' + (status?'glyphicon glyphicon-play':'glyphicon-pause')+'"></span></p><div class="sfm-opt">\
            <button class="btn btn-default btn-sm" onclick="nginxOp(\''+_name+'\',\''+version+'\')">'+(status?'停止':'启动')+'</button>\
            <button class="btn btn-default btn-sm" onclick="nginxOp(\''+_name+'\',\''+version+'\',\'restart\')">重启</button>\
            <button class="btn btn-default btn-sm" onclick="nginxOp(\''+_name+'\',\''+version+'\',\'reload\')">重载</button>\
        </div>';
    $(".soft-man-con").html(serviceCon);
}

function nginxOp(_name, version, type='start'){
    var title = '';
    if (type == 'start'){
        title = '启动';
    } else if (type == 'stop'){
        title = '停止';
    } else if (type == 'restart'){
        title = '重启';
    } else if (type == 'reload'){
        title = '重载';
    }

    layer.confirm('您真的要'+title+'Nginx服务吗?', {icon:3,closeBtn: 1}, function() {
        var loadT = layer.msg('正在'+title+',请稍候...', {icon: 16,time: 0,shade: 0.3});
        var data = {name:_name, func:type}
        if ( typeof(version) != 'undefined' ){
            data['version'] = version;
        }
        
        nginxPost(type, data, function(rdata){
            layer.close(loadT);
            layer.msg(rdata.msg,{icon:rdata.status?1:2});
            if(rdata.status){
                nginxPluginService(_name, version);
            }
        });
    });
}

function nginxConfig(){
    nginxPost('get_config', {}, function(data){
        var config = data.data;
        var mBody = '<div class="bingfa">\
                        <textarea style="width:100%;height:400px;" id="nginx_config">'+config+'</textarea>\
                        <button id="btn_save_config" class="btn btn-success btn-sm" style="margin-top:10px;">保存配置</button>\
                        <button id="btn_test_config" class="btn btn-warning btn-sm" style="margin-top:10px;margin-left:10px;">测试配置</button>\
                    </div>';
                    
        layer.open({
            type: 1,
            title: 'Nginx配置文件编辑',
            area: ['800px','550px'],
            content:mBody,
            cancel: function(){ 
                nginxPluginService('nginx',$('.plugin_version').attr('version'));
            }
        });

        $('#btn_save_config').click(function(){
            var newConfig = $('#nginx_config').val();
            nginxPost('set_config', {content:newConfig}, function(result){
                layer.msg(result.msg,{icon:result.status?1:2});
            });
        });

        $('#btn_test_config').click(function(){
            nginxPost('test_config', {}, function(result){
                layer.msg(result.msg,{icon:result.status?1:2});
            });
        });
    });
}

function nginxRunInfo(){
    nginxPost('run_info', {}, function(data){
        try {
            var rdata = $.parseJSON(data.data);
            if (!rdata.status){
                layer.msg(rdata.msg, {icon: 2});
                return;
            }

            var con = '<div class="nginx-status-info">';
            con += '<div class="nginx-status-item"><span class="nginx-status-label">运行状态:</span><span class="nginx-status-value">' + (rdata.status == 'running' ? '运行中' : '已停止') + '</span></div>';
            con += '<div class="nginx-status-item"><span class="nginx-status-label">进程PID:</span><span class="nginx-status-value">' + (rdata.pid || 'N/A') + '</span></div>';
            con += '<div class="nginx-status-item"><span class="nginx-status-label">Nginx版本:</span><span class="nginx-status-value">' + (rdata.version || 'N/A') + '</span></div>';
            con += '<div class="nginx-status-item"><span class="nginx-status-label">工作进程数:</span><span class="nginx-status-value">' + (rdata.worker_processes || 'N/A') + '</span></div>';
            
            if (rdata.listen_ports && rdata.listen_ports.length > 0) {
                con += '<div class="nginx-status-item"><span class="nginx-status-label">监听端口:</span><span class="nginx-status-value">' + rdata.listen_ports.join(', ') + '</span></div>';
            }
            
            con += '<div class="nginx-status-item"><span class="nginx-status-label">启动时间:</span><span class="nginx-status-value">' + (rdata.start_time || 'N/A') + '</span></div>';
            con += '</div>';

            $(".soft-man-con").html(con);
        } catch(e) {
            layer.msg('数据解析错误', {icon: 2});
        }
    });
}

function nginxErrorLogs(){
    nginxPost('error_logs', {}, function(data){
        var logs = data.data || '暂无错误日志';
        var con = '<div class="nginx-log-container">' + logs + '</div>';
        $(".soft-man-con").html(con);
    });
}

function nginxAccessLogs(){
    nginxPost('access_logs', {}, function(data){
        var logs = data.data || '暂无访问日志';
        var con = '<div class="nginx-log-container">' + logs + '</div>';
        $(".soft-man-con").html(con);
    });
}

function nginxVirtualHosts(){
    nginxPost('get_vhosts', {}, function(data){
        try {
            var vhosts = data.data;
            if (!Array.isArray(vhosts)) {
                vhosts = $.parseJSON(vhosts);
            }

            var con = '<div class="nginx-vhosts-list">';
            if (vhosts.length === 0) {
                con += '<div style="text-align:center;padding:50px;color:#999;">暂无虚拟主机配置</div>';
            } else {
                for(var i=0; i<vhosts.length; i++){
                    var vhost = vhosts[i];
                    con += '<div class="nginx-vhost-item">';
                    con += '<div class="nginx-vhost-domain">' + vhost.name + '</div>';
                    if (vhost.domains && vhost.domains.length > 0) {
                        con += '<div style="margin:5px 0;">域名: ' + vhost.domains.join(', ') + '</div>';
                    }
                    if (vhost.ports && vhost.ports.length > 0) {
                        con += '<div class="nginx-vhost-port">端口: ' + vhost.ports.join(', ') + '</div>';
                    }
                    con += '<div class="nginx-vhost-port">状态: ' + (vhost.status == 'active' ? '启用' : '禁用') + '</div>';
                    con += '</div>';
                }
            }
            con += '</div>';
            $(".soft-man-con").html(con);
        } catch(e) {
            layer.msg('虚拟主机数据解析错误', {icon: 2});
        }
    });
}

function nginxPerformance(){
    var con = '<div class="nginx-performance-tuning">\
                <div style="padding:20px;">\
                    <h4>Nginx性能调优建议</h4>\
                    <div style="margin:15px 0;">\
                        <strong>worker_processes:</strong>\
                        <p>建议设置为CPU核心数，可以通过命令 <code>nproc</code> 查看核心数</p>\
                    </div>\
                    <div style="margin:15px 0;">\
                        <strong>worker_connections:</strong>\
                        <p>每个工作进程的最大连接数，默认1024，可根据需求调整</p>\
                    </div>\
                    <div style="margin:15px 0;">\
                        <strong>keepalive_timeout:</strong>\
                        <p>保持连接超时时间，建议设置为15-30秒</p>\
                    </div>\
                    <div style="margin:15px 0;">\
                        <strong>gzip:</strong>\
                        <p>启用gzip压缩可以显著减少传输数据量</p>\
                    </div>\
                    <div style="margin:15px 0;">\
                        <strong>缓存配置:</strong>\
                        <p>合理配置静态资源缓存策略</p>\
                    </div>\
                    <button class="btn btn-primary btn-sm" onclick="nginxConfig()">编辑配置文件</button>\
                </div>\
            </div>';
    $(".soft-man-con").html(con);
}