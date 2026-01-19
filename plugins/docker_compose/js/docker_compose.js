function dockerComposePost(method, args, callback){
    var loadT = layer.msg('正在处理...', { icon: 16, time: 0, shade: 0.3 });
    $.post('/plugins/run', {name:'docker_compose', func:method, args:JSON.stringify(args)}, function(data) {
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

function dockerComposePluginService(_name, version){
    var data = {name:_name, func:'status'}
    if ( typeof(version) != 'undefined' ){
        data['version'] = version;
    } else {
        version = '';
    }

    dockerComposePost('status', data, function(data){
        if (data.data == 'start'){
            dockerComposePluginSetService(_name, true, version);
        } else {
            dockerComposePluginSetService(_name, false, version);
        }
    });
}

function dockerComposePluginSetService(_name ,status, version){
    var serviceCon ='<p class="status">当前状态：<span>'+(status ? '运行中' : '已停止' )+
        '</span><span style="color: '+
        (status?'#20a53a;':'red;')+
        ' margin-left: 3px;" class="glyphicon ' + (status?'glyphicon glyphicon-play':'glyphicon-pause')+'"></span></p><div class="sfm-opt">\
            <button class="btn btn-default btn-sm" onclick="dockerComposeOp(\''+_name+'\',\''+version+'\')">'+(status?'停止':'启动')+'</button>\
            <button class="btn btn-default btn-sm" onclick="dockerComposeOp(\''+_name+'\',\''+version+'\',\'restart\')">重启</button>\
        </div>';
    $(".soft-man-con").html(serviceCon);
}

function dockerComposeOp(_name, version, type='start'){
    var title = '';
    if (type == 'start'){
        title = '启动';
    } else if (type == 'stop'){
        title = '停止';
    } else if (type == 'restart'){
        title = '重启';
    }

    layer.confirm('您真的要'+title+'Docker Compose服务吗?', {icon:3,closeBtn: 1}, function() {
        var loadT = layer.msg('正在'+title+',请稍候...', {icon: 16,time: 0,shade: 0.3});
        var data = {name:_name, func:type}
        if ( typeof(version) != 'undefined' ){
            data['version'] = version;
        }
        
        dockerComposePost(type, data, function(rdata){
            layer.close(loadT);
            layer.msg(rdata.msg,{icon:rdata.status?1:2});
            if(rdata.status){
                dockerComposePluginService(_name, version);
            }
        });
    });
}

function dockerComposeProjectList(){
    dockerComposePost('get_projects', {}, function(data){
        var projects = data.data;
        var con = '<div class="docker-project-management">';
        con += '<div style="margin-bottom:15px;">';
        con += '<button class="btn btn-success btn-sm" onclick="dockerComposeCreateProject()">创建项目</button> ';
        con += '<button class="btn btn-info btn-sm" onclick="dockerComposeRefreshProjects()">刷新</button>';
        con += '</div>';
        
        if (projects.length === 0) {
            con += '<div style="text-align:center;padding:50px;color:#999;">暂无项目</div>';
        } else {
            for(var i=0; i<projects.length; i++){
                var project = projects[i];
                con += '<div class="docker-project-item">';
                con += '<div class="docker-project-name">' + project.name + '</div>';
                con += '<div class="docker-project-info">路径: ' + project.path + '</div>';
                con += '<div class="docker-project-info">服务数量: ' + project.services_count + '</div>';
                con += '<div class="docker-project-info">创建时间: ' + project.created_time + '</div>';
                con += '<div class="docker-project-info">状态: ';
                con += '<span class="docker-service-status ' + (project.status=='running'?'docker-status-running':'docker-status-stopped') + '">';
                con += project.status=='running'?'运行中':'已停止';
                con += '</span></div>';
                con += '<div style="margin-top:10px;">';
                con += '<button class="btn btn-primary btn-xs" onclick="dockerComposeManageProject('+project.id+')">管理</button> ';
                con += '<button class="btn btn-success btn-xs" onclick="dockerComposeStartProject('+project.id+')" '+(project.status=='running'?'disabled':'')+'>启动</button> ';
                con += '<button class="btn btn-warning btn-xs" onclick="dockerComposeStopProject('+project.id+')" '+(project.status=='stopped'?'disabled':'')+'>停止</button> ';
                con += '<button class="btn btn-info btn-xs" onclick="dockerComposeViewServices('+project.id+')">服务</button> ';
                con += '<button class="btn btn-danger btn-xs" onclick="dockerComposeDeleteProject('+project.id+',\''+project.name+'\')">删除</button>';
                con += '</div>';
                con += '</div>';
            }
        }
        con += '</div>';
        $(".soft-man-con").html(con);
    });
}

function dockerComposeCreateProject(){
    dockerComposePost('get_templates', {}, function(templateData){
        var templates = templateData.data;
        var templateOptions = '<option value="">空白项目</option>';
        for(var i=0; i<templates.length; i++){
            var template = templates[i];
            templateOptions += '<option value="'+template.id+'">'+template.name+' ('+template.category+')</option>';
        }
        
        var index = layer.open({
            type: 1,
            title: '创建新项目',
            area: ['600px', '400px'],
            content: '<div style="padding:20px;">\
                        <div class="line">\
                            <span class="tname">项目名称</span>\
                            <div class="info-r">\
                                <input type="text" id="project_name" class="bt-input-text mr5" placeholder="请输入项目名称" style="width:300px;">\
                            </div>\
                        </div>\
                        <div class="line" style="margin-top:15px;">\
                            <span class="tname">选择模板</span>\
                            <div class="info-r">\
                                <select id="template_select" class="bt-input-text mr5" style="width:300px;">' + templateOptions + '</select>\
                            </div>\
                        </div>\
                        <div class="line" style="margin-top:15px;">\
                            <span class="tname">描述</span>\
                            <div class="info-r">\
                                <input type="text" id="project_description" class="bt-input-text mr5" placeholder="项目描述(可选)" style="width:300px;">\
                            </div>\
                        </div>\
                        <div class="submit-btn" style="margin-top:20px;text-align:right;">\
                            <button class="btn btn-danger btn-sm mr5" onclick="layer.closeAll()">取消</button>\
                            <button class="btn btn-success btn-sm" onclick="dockerComposeDoCreateProject()">创建</button>\
                        </div>\
                    </div>'
        });
    });
}

function dockerComposeDoCreateProject(){
    var name = $("#project_name").val().trim();
    var templateId = $("#template_select").val();
    var description = $("#project_description").val().trim();
    
    if (!name) {
        layer.msg('请输入项目名称', {icon: 2});
        return;
    }
    
    dockerComposePost('create_project', {name:name, template_id:templateId, description:description}, function(data){
        layer.msg(data.msg, {icon: data.status?1:2});
        if (data.status) {
            layer.closeAll();
            dockerComposeProjectList();
        }
    });
}

function dockerComposeDeleteProject(project_id, project_name){
    layer.confirm('确定要删除项目 "' + project_name + '" 吗？此操作将删除所有相关文件！', {icon:3,title:'删除项目'}, function(){
        dockerComposePost('delete_project', {id:project_id}, function(data){
            layer.msg(data.msg, {icon: data.status?1:2});
            if (data.status) {
                dockerComposeProjectList();
            }
        });
    });
}

function dockerComposeManageProject(project_id){
    // 项目管理详情页面
    var con = '<div class="docker-project-detail">';
    con += '<h4>项目管理</h4>';
    con += '<div id="project_detail_content"></div>';
    con += '</div>';
    $(".soft-man-con").html(con);
    
    // 加载项目详情
    dockerComposeViewServices(project_id);
}

function dockerComposeViewServices(project_id){
    dockerComposePost('get_services', {project_id:project_id}, function(data){
        var services = data.data;
        var con = '<div class="docker-services-view">';
        con += '<h5>服务列表</h5>';
        
        if (services.length === 0) {
            con += '<div style="text-align:center;padding:30px;color:#999;">该项目中没有服务</div>';
        } else {
            for(var i=0; i<services.length; i++){
                var service = services[i];
                var actualStatus = service.actual_status || 'unknown';
                var statusClass = actualStatus == 'running' ? 'docker-status-running' : 'docker-status-stopped';
                
                con += '<div class="docker-service-item">';
                con += '<div>';
                con += '<div class="docker-service-name">' + service.service_name + '</div>';
                con += '<div style="font-size:12px;color:#666;">镜像: ' + service.image + '</div>';
                con += '</div>';
                con += '<div>';
                con += '<span class="docker-service-status ' + statusClass + '">' + actualStatus + '</span>';
                con += '</div>';
                con += '</div>';
            }
        }
        con += '</div>';
        
        if ($("#project_detail_content").length > 0) {
            $("#project_detail_content").html(con);
        } else {
            $(".soft-man-con").html(con);
        }
    });
}

function dockerComposeStartProject(project_id){
    dockerComposePost('start_project', {project_id:project_id}, function(data){
        layer.msg(data.msg, {icon: data.status?1:1});
        if (data.status) {
            setTimeout(function(){
                dockerComposeProjectList();
            }, 1000);
        }
    });
}

function dockerComposeStopProject(project_id){
    dockerComposePost('stop_project', {project_id:project_id}, function(data){
        layer.msg(data.msg, {icon: data.status?1:2});
        if (data.status) {
            setTimeout(function(){
                dockerComposeProjectList();
            }, 1000);
        }
    });
}

function dockerComposeTemplateList(){
    dockerComposePost('get_templates', {}, function(data){
        var templates = data.data;
        var con = '<div class="docker-template-center">';
        con += '<h4>模板中心</h4>';
        
        if (templates.length === 0) {
            con += '<div style="text-align:center;padding:50px;color:#999;">暂无模板</div>';
        } else {
            for(var i=0; i<templates.length; i++){
                var template = templates[i];
                con += '<div class="docker-template-item" onclick="dockerComposeShowTemplate('+template.id+')">';
                con += '<div class="docker-template-header">';
                con += '<div class="docker-template-name">' + template.name + '</div>';
                con += '<div class="docker-template-category">' + template.category + '</div>';
                con += '</div>';
                con += '<div style="color:#666;font-size:14px;">' + template.description + '</div>';
                con += '<div style="margin-top:8px;font-size:12px;color:#999;">下载量: ' + template.downloads + '</div>';
                con += '</div>';
            }
        }
        con += '</div>';
        $(".soft-man-con").html(con);
    });
}

function dockerComposeShowTemplate(template_id){
    // 显示模板详情（可扩展功能）
    layer.msg('模板详情功能开发中...', {icon: 6});
}

function dockerComposeServiceMonitor(){
    // 服务监控页面
    var con = '<div class="docker-monitor-dashboard">';
    con += '<h4>服务监控</h4>';
    con += '<div class="docker-stats-grid">';
    con += '<div class="docker-stat-card">';
    con += '<div class="docker-stat-number" id="total_projects">-</div>';
    con += '<div class="docker-stat-label">项目总数</div>';
    con += '</div>';
    con += '<div class="docker-stat-card">';
    con += '<div class="docker-stat-number" id="running_projects">-</div>';
    con += '<div class="docker-stat-label">运行中项目</div>';
    con += '</div>';
    con += '<div class="docker-stat-card">';
    com += '<div class="docker-stat-number" id="total_services">-</div>';
    con += '<div class="docker-stat-label">服务总数</div>';
    con += '</div>';
    con += '<div class="docker-stat-card">';
    con += '<div class="docker-stat-number" id="running_services">-</div>';
    con += '<div class="docker-stat-label">运行中服务</div>';
    con += '</div>';
    con += '</div>';
    con += '<button class="btn btn-info btn-sm" onclick="dockerComposeRefreshMonitor()">刷新数据</button>';
    con += '</div>';
    $(".soft-man-con").html(con);
    
    dockerComposeRefreshMonitor();
}

function dockerComposeRefreshMonitor(){
    dockerComposePost('get_projects', {}, function(data){
        var projects = data.data;
        var totalProjects = projects.length;
        var runningProjects = projects.filter(p => p.status === 'running').length;
        var totalServices = projects.reduce((sum, p) => sum + parseInt(p.services_count || 0), 0);
        
        $("#total_projects").text(totalProjects);
        $("#running_projects").text(runningProjects);
        $("#total_services").text(totalServices);
        
        // 计算运行中的服务数量（需要进一步实现）
        $("#running_services").text('-');
    });
}

function dockerComposeLogs(){
    var con = '<div class="docker-logs-view">';
    con += '<div style="margin-bottom:15px;">';
    con += '<select id="logs_project_select" class="bt-input-text mr10" style="width:200px;">';
    con += '<option value="">选择项目查看日志</option>';
    con += '</select>';
    con += '<button class="btn btn-info btn-sm" onclick="dockerComposeLoadProjectsForLogs()">刷新列表</button>';
    con += '</div>';
    con += '<div id="logs_display_area" class="docker-logs-container">请选择项目查看日志</div>';
    con += '</div>';
    $(".soft-man-con").html(con);
    dockerComposeLoadProjectsForLogs();
}

function dockerComposeLoadProjectsForLogs(){
    dockerComposePost('get_projects', {}, function(data){
        var projects = data.data;
        var selectHtml = '<option value="">选择项目查看日志</option>';
        for(var i=0; i<projects.length; i++){
            var project = projects[i];
            selectHtml += '<option value="'+project.id+'">'+project.name+'</option>';
        }
        $("#logs_project_select").html(selectHtml);
        
        $("#logs_project_select").change(function(){
            var projectId = $(this).val();
            if (projectId) {
                dockerComposeShowProjectLogs(projectId);
            } else {
                $("#logs_display_area").html('请选择项目查看日志');
            }
        });
    });
}

function dockerComposeShowProjectLogs(project_id){
    dockerComposePost('get_logs', {project_id:project_id, limit:50}, function(data){
        var logs = data.data;
        var logContent = '';
        if (logs.length === 0) {
            logContent = '暂无日志记录';
        } else {
            for(var i=0; i<logs.length; i++){
                var log = logs[i];
                logContent += '[' + log.timestamp + '] ';
                logContent += (log.service_name ? log.service_name + ': ' : '');
                logContent += log.message + '\n';
            }
        }
        $("#logs_display_area").html(logContent);
    });
}

function dockerComposeSettings(){
    dockerComposePost('get_config', {}, function(data){
        var config = data.data;
        var con = '<div class="docker-settings">';
        con += '<h4>Docker Compose插件设置</h4>';
        con += '<div style="margin:20px 0;">';
        con += '<div style="margin-bottom:15px;">';
        con += '<label>项目存储路径:</label>';
        con += '<input type="text" id="projects_path" class="bt-input-text" style="width:300px;margin-left:10px;" value="' + (config.projects_path || '') + '">';
        con += '</div>';
        con += '<div style="margin-bottom:15px;">';
        con += '<label>模板存储路径:</label>';
        con += '<input type="text" id="templates_path" class="bt-input-text" style="width:300px;margin-left:10px;" value="' + (config.templates_path || '') + '">';
        con += '</div>';
        con += '<div style="margin-bottom:15px;">';
        con += '<label>docker-compose路径:</label>';
        con += '<input type="text" id="docker_compose_path" class="bt-input-text" style="width:300px;margin-left:10px;" value="' + (config.docker_compose_path || '') + '">';
        con += '</div>';
        con += '<button class="btn btn-success btn-sm" onclick="dockerComposeSaveSettings()">保存设置</button>';
        con += '</div>';
        con += '</div>';
        $(".soft-man-con").html(con);
    });
}

function dockerComposeSaveSettings(){
    var projectsPath = $("#projects_path").val();
    var templatesPath = $("#templates_path").val();
    var dockerComposePath = $("#docker_compose_path").val();
    
    // 保存配置
    dockerComposePost('set_config', {key:'projects_path', value:projectsPath}, function(){
        dockerComposePost('set_config', {key:'templates_path', value:templatesPath}, function(){
            dockerComposePost('set_config', {key:'docker_compose_path', value:dockerComposePath}, function(data){
                layer.msg(data.msg, {icon: data.status?1:2});
            });
        });
    });
}

function dockerComposeRefreshProjects(){
    dockerComposeProjectList();
}