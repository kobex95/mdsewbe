function sqlitePost(method, args, callback){
    var loadT = layer.msg('正在处理...', { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'sqlite', func:method, args:JSON.stringify(args)}, function(data) {
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

function sqlitePluginService(_name, version){
    var data = {name:_name, func:'status'}
    if ( typeof(version) != 'undefined' ){
        data['version'] = version;
    } else {
        version = '';
    }

    sqlitePost('status', data, function(data){
        if (data.data == 'start'){
            sqlitePluginSetService(_name, true, version);
        } else {
            sqlitePluginSetService(_name, false, version);
        }
    });
}

function sqlitePluginSetService(_name ,status, version){
    var serviceCon ='<p class="status">当前状态：<span>'+(status ? '运行中' : '已停止' )+
        '</span><span style="color: '+
        (status?'#20a53a;':'red;')+
        ' margin-left: 3px;" class="glyphicon ' + (status?'glyphicon glyphicon-play':'glyphicon-pause')+'"></span></p><div class="sfm-opt">\
            <button class="btn btn-default btn-sm" onclick="sqliteOp(\''+_name+'\',\''+version+'\')">'+(status?'停止':'启动')+'</button>\
            <button class="btn btn-default btn-sm" onclick="sqliteOp(\''+_name+'\',\''+version+'\',\'restart\')">重启</button>\
        </div>';
    $(".soft-man-con").html(serviceCon);
}

function sqliteOp(_name, version, type='start'){
    var title = '';
    if (type == 'start'){
        title = '启动';
    } else if (type == 'stop'){
        title = '停止';
    } else if (type == 'restart'){
        title = '重启';
    }

    layer.confirm('您真的要'+title+'SQLite服务吗?', {icon:3,closeBtn: 1}, function() {
        var loadT = layer.msg('正在'+title+',请稍候...', {icon: 16,time: 0,shade: 0.3});
        var data = {name:_name, func:type}
        if ( typeof(version) != 'undefined' ){
            data['version'] = version;
        }
        
        sqlitePost(type, data, function(rdata){
            layer.close(loadT);
            layer.msg(rdata.msg,{icon:rdata.status?1:2});
            if(rdata.status){
                sqlitePluginService(_name, version);
            }
        });
    });
}

function sqliteDatabaseList(){
    sqlitePost('get_databases', {}, function(data){
        var databases = data.data;
        var con = '<div class="sqlite-db-management">';
        con += '<div style="margin-bottom:15px;">';
        con += '<button class="btn btn-success btn-sm" onclick="sqliteCreateDatabase()">创建数据库</button>';
        con += '</div>';
        
        if (databases.length === 0) {
            con += '<div style="text-align:center;padding:50px;color:#999;">暂无数据库</div>';
        } else {
            for(var i=0; i<databases.length; i++){
                var db = databases[i];
                con += '<div class="sqlite-db-item">';
                con += '<div class="sqlite-db-name">' + db.name + '</div>';
                con += '<div class="sqlite-db-info">路径: ' + db.path + '</div>';
                con += '<div class="sqlite-db-info">大小: ' + formatFileSize(db.size) + '</div>';
                con += '<div class="sqlite-db-info">表数量: ' + db.tables_count + '</div>';
                con += '<div class="sqlite-db-info">创建时间: ' + db.created_time + '</div>';
                con += '<div style="margin-top:10px;">';
                con += '<button class="btn btn-primary btn-xs" onclick="sqliteUseDatabase('+db.id+')">使用</button> ';
                con += '<button class="btn btn-info btn-xs" onclick="sqliteViewTables('+db.id+')">查看表</button> ';
                con += '<button class="btn btn-warning btn-xs" onclick="sqliteBackupDatabase('+db.id+')">备份</button> ';
                con += '<button class="btn btn-danger btn-xs" onclick="sqliteDeleteDatabase('+db.id+',\''+db.name+'\')">删除</button>';
                con += '</div>';
                con += '</div>';
            }
        }
        con += '</div>';
        $(".soft-man-con").html(con);
    });
}

function sqliteCreateDatabase(){
    var index = layer.open({
        type: 1,
        title: '创建新数据库',
        area: ['500px', '300px'],
        content: '<div style="padding:20px;">\
                    <div class="line">\
                        <span class="tname">数据库名称</span>\
                        <div class="info-r">\
                            <input type="text" id="db_name" class="bt-input-text mr5" placeholder="请输入数据库名称" style="width:300px;">\
                        </div>\
                    </div>\
                    <div class="line" style="margin-top:15px;">\
                        <span class="tname">描述</span>\
                        <div class="info-r">\
                            <input type="text" id="db_description" class="bt-input-text mr5" placeholder="数据库描述(可选)" style="width:300px;">\
                        </div>\
                    </div>\
                    <div class="submit-btn" style="margin-top:20px;text-align:right;">\
                        <button class="btn btn-danger btn-sm mr5" onclick="layer.closeAll()">取消</button>\
                        <button class="btn btn-success btn-sm" onclick="sqliteDoCreateDatabase()">创建</button>\
                    </div>\
                </div>'
    });
}

function sqliteDoCreateDatabase(){
    var name = $("#db_name").val().trim();
    var description = $("#db_description").val().trim();
    
    if (!name) {
        layer.msg('请输入数据库名称', {icon: 2});
        return;
    }
    
    sqlitePost('add_database', {name:name, description:description}, function(data){
        layer.msg(data.msg, {icon: data.status?1:2});
        if (data.status) {
            layer.closeAll();
            sqliteDatabaseList();
        }
    });
}

function sqliteDeleteDatabase(db_id, db_name){
    layer.confirm('确定要删除数据库 "' + db_name + '" 吗？此操作不可恢复！', {icon:3,title:'删除数据库'}, function(){
        sqlitePost('delete_database', {id:db_id}, function(data){
            layer.msg(data.msg, {icon: data.status?1:2});
            if (data.status) {
                sqliteDatabaseList();
            }
        });
    });
}

function sqliteQueryEditor(){
    var con = '<div class="sqlite-query-interface">';
    con += '<div style="margin-bottom:15px;">';
    con += '<select id="query_db_select" class="bt-input-text mr10" style="width:200px;">';
    con += '<option value="">请选择数据库</option>';
    con += '</select>';
    con += '<button class="btn btn-info btn-sm" onclick="sqliteLoadDatabasesForQuery()">刷新列表</button>';
    con += '</div>';
    
    con += '<textarea id="sql_query_editor" class="sqlite-query-editor" placeholder="请输入SQL查询语句..."></textarea>';
    con += '<div style="margin-top:10px;">';
    con += '<button class="btn btn-success btn-sm" onclick="sqliteExecuteQuery()">执行查询</button> ';
    con += '<button class="btn btn-warning btn-sm" onclick="sqliteClearQuery()">清空</button>';
    con += '</div>';
    con += '<div id="query_result_container" class="sqlite-query-result"></div>';
    con += '</div>';
    
    $(".soft-man-con").html(con);
    sqliteLoadDatabasesForQuery();
}

function sqliteLoadDatabasesForQuery(){
    sqlitePost('get_databases', {}, function(data){
        var databases = data.data;
        var selectHtml = '<option value="">请选择数据库</option>';
        for(var i=0; i<databases.length; i++){
            var db = databases[i];
            selectHtml += '<option value="'+db.id+'">'+db.name+'</option>';
        }
        $("#query_db_select").html(selectHtml);
    });
}

function sqliteExecuteQuery(){
    var db_id = $("#query_db_select").val();
    var query = $("#sql_query_editor").val().trim();
    
    if (!db_id) {
        layer.msg('请选择数据库', {icon: 2});
        return;
    }
    
    if (!query) {
        layer.msg('请输入SQL查询语句', {icon: 2});
        return;
    }
    
    sqlitePost('execute_query', {db_id:db_id, query:query}, function(data){
        if (data.status) {
            var result = data.data;
            var resultHtml = '<div style="margin-top:15px;">';
            resultHtml += '<div>执行时间: ' + result.execution_time + '秒</div>';
            resultHtml += '<div>影响行数: ' + result.rows_count + '</div>';
            
            if (result.data && result.data.length > 0) {
                resultHtml += '<table class="sqlite-result-table">';
                // 表头
                resultHtml += '<thead><tr>';
                for(var col in result.data[0]){
                    resultHtml += '<th>' + col + '</th>';
                }
                resultHtml += '</tr></thead>';
                // 数据行
                resultHtml += '<tbody>';
                for(var i=0; i<result.data.length; i++){
                    resultHtml += '<tr>';
                    for(var col in result.data[i]){
                        resultHtml += '<td>' + result.data[i][col] + '</td>';
                    }
                    resultHtml += '</tr>';
                }
                resultHtml += '</tbody>';
                resultHtml += '</table>';
            } else {
                resultHtml += '<div style="margin-top:10px;color:#666;">查询执行成功，无数据返回</div>';
            }
            resultHtml += '</div>';
            
            $("#query_result_container").html(resultHtml);
        } else {
            $("#query_result_container").html('<div style="color:red;margin-top:15px;">错误: ' + data.msg + '</div>');
        }
    });
}

function sqliteClearQuery(){
    $("#sql_query_editor").val('');
    $("#query_result_container").html('');
}

function sqliteViewTables(db_id){
    sqlitePost('get_tables', {db_id:db_id}, function(data){
        var tables = data.data;
        var con = '<div class="sqlite-tables-view">';
        con += '<h4>数据库表结构</h4>';
        
        if (tables.length === 0) {
            con += '<div style="text-align:center;padding:30px;color:#999;">该数据库中没有表</div>';
        } else {
            for(var i=0; i<tables.length; i++){
                var table = tables[i];
                con += '<div class="sqlite-table-item">';
                con += '<div style="font-weight:bold;margin-bottom:5px;">表名: ' + table.name + '</div>';
                con += '<div style="font-size:12px;color:#666;">列数: ' + table.columns_count + '</div>';
                con += '<div style="font-size:12px;color:#666;">行数: ' + table.rows_count + '</div>';
                con += '</div>';
            }
        }
        con += '</div>';
        $(".soft-man-con").html(con);
    });
}

function sqliteBackupManager(){
    var con = '<div class="sqlite-backup-manager">';
    con += '<div style="margin-bottom:15px;">';
    con += '<button class="btn btn-info btn-sm" onclick="sqliteDatabaseListForBackup()">选择数据库备份</button>';
    con += '</div>';
    con += '<div id="backup_list_container"></div>';
    con += '</div>';
    $(".soft-man-con").html(con);
}

function sqliteDatabaseListForBackup(){
    sqlitePost('get_databases', {}, function(data){
        var databases = data.data;
        var content = '<div style="max-height:400px;overflow-y:auto;">';
        for(var i=0; i<databases.length; i++){
            var db = databases[i];
            content += '<div style="padding:10px;border:1px solid #eee;margin-bottom:5px;">';
            content += '<div style="font-weight:bold;">' + db.name + '</div>';
            content += '<div style="font-size:12px;color:#666;">路径: ' + db.path + '</div>';
            content += '<button class="btn btn-warning btn-xs" style="margin-top:5px;" onclick="sqliteBackupDatabase('+db.id+')">立即备份</button>';
            content += '</div>';
        }
        content += '</div>';
        
        layer.open({
            type: 1,
            title: '选择要备份的数据库',
            area: ['500px', '400px'],
            content: content
        });
    });
}

function sqliteBackupDatabase(db_id){
    sqlitePost('backup_database', {db_id:db_id}, function(data){
        layer.msg(data.msg, {icon: data.status?1:1});
        if (data.status) {
            console.log('备份文件:', data.data.backup_path);
        }
    });
}

function sqliteQueryHistory(){
    sqlitePost('get_history', {}, function(data){
        var history = data.data;
        var con = '<div class="sqlite-query-history">';
        con += '<h4>查询历史</h4>';
        
        if (history.length === 0) {
            con += '<div style="text-align:center;padding:30px;color:#999;">暂无查询历史</div>';
        } else {
            for(var i=0; i<history.length; i++){
                var item = history[i];
                con += '<div class="sqlite-history-item">';
                con += '<div class="sqlite-history-query">' + item.query_text + '</div>';
                con += '<div style="font-size:12px;color:#666;">';
                con += '执行时间: ' + item.executed_time + ' | ';
                con += '耗时: ' + item.execution_time + '秒 | ';
                con += '结果行数: ' + item.result_rows;
                con += '</div>';
                con += '</div>';
            }
        }
        con += '</div>';
        $(".soft-man-con").html(con);
    });
}

function sqliteSettings(){
    sqlitePost('get_config', {}, function(data){
        var config = data.data;
        var con = '<div class="sqlite-settings">';
        con += '<h4>SQLite插件设置</h4>';
        con += '<div style="margin:20px 0;">';
        con += '<div style="margin-bottom:15px;">';
        con += '<label>默认数据库路径:</label>';
        con += '<input type="text" id="default_path" class="bt-input-text" style="width:300px;margin-left:10px;" value="' + (config.default_path || '') + '">';
        con += '</div>';
        con += '<div style="margin-bottom:15px;">';
        con += '<label>最大数据库大小(字节):</label>';
        con += '<input type="text" id="max_db_size" class="bt-input-text" style="width:200px;margin-left:10px;" value="' + (config.max_db_size || '') + '">';
        con += '</div>';
        con += '<button class="btn btn-success btn-sm" onclick="sqliteSaveSettings()">保存设置</button>';
        con += '</div>';
        con += '</div>';
        $(".soft-man-con").html(con);
    });
}

function sqliteSaveSettings(){
    var defaultPath = $("#default_path").val();
    var maxSize = $("#max_db_size").val();
    
    // 保存默认路径
    sqlitePost('set_config', {key:'default_path', value:defaultPath}, function(){
        // 保存最大大小
        sqlitePost('set_config', {key:'max_db_size', value:maxSize}, function(data){
            layer.msg(data.msg, {icon: data.status?1:2});
        });
    });
}

// 工具函数
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    var k = 1024;
    var sizes = ['Bytes', 'KB', 'MB', 'GB'];
    var i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}