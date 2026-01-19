// WAF Plus 前端JavaScript逻辑

// 全局变量
let currentView = 'dashboard';
let dashboardRefreshInterval = null;

// API封装
const WafApi = {
    async post(method, args = {}) {
        try {
            const response = await $.post('/plugins/run', {
                name: 'waf_plus',
                func: method,
                args: JSON.stringify(args)
            });
            
            if (!response.status) {
                throw new Error(response.msg);
            }
            
            return response;
        } catch (error) {
            console.error('API调用失败:', error);
            layer.msg(error.message || '请求失败', {icon: 2});
            throw error;
        }
    }
};

// 视图管理
const ViewManager = {
    show(viewName) {
        // 隐藏所有视图
        $('.soft-man-con > div').hide();
        
        // 显示指定视图
        $(`#${viewName}-view`).show();
        currentView = viewName;
        
        // 加载对应数据
        switch(viewName) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'logs':
                this.loadLogs();
                break;
            case 'rules':
                this.loadRules();
                break;
            case 'intel':
                this.loadThreatIntel();
                break;
            case 'settings':
                this.loadSettings();
                break;
        }
    },
    
    async loadDashboard() {
        try {
            showLoading();
            const response = await WafApi.post('dashboard');
            DashboardRenderer.render(response.data);
            this.startAutoRefresh();
        } catch (error) {
            console.error('加载仪表板失败:', error);
        } finally {
            hideLoading();
        }
    },
    
    async loadLogs(page = 1, pageSize = 20, search = '') {
        try {
            showLoading();
            const response = await WafApi.post('logs', { 
                page, 
                page_size: pageSize, 
                search 
            });
            LogsRenderer.render(response.data);
        } catch (error) {
            console.error('加载日志失败:', error);
        } finally {
            hideLoading();
        }
    },
    
    async loadRules() {
        try {
            showLoading();
            const response = await WafApi.post('rules');
            RulesRenderer.render(response.data);
        } catch (error) {
            console.error('加载规则失败:', error);
        } finally {
            hideLoading();
        }
    },
    
    async loadThreatIntel() {
        try {
            showLoading();
            const response = await WafApi.post('threat_intel');
            ThreatIntelRenderer.render(response.data);
        } catch (error) {
            console.error('加载威胁情报失败:', error);
        } finally {
            hideLoading();
        }
    },
    
    async loadSettings() {
        try {
            showLoading();
            const response = await WafApi.post('get_settings');
            SettingsRenderer.render(response.data);
        } catch (error) {
            console.error('加载设置失败:', error);
        } finally {
            hideLoading();
        }
    },
    
    startAutoRefresh() {
        if (dashboardRefreshInterval) {
            clearInterval(dashboardRefreshInterval);
        }
        
        dashboardRefreshInterval = setInterval(async () => {
            if (currentView === 'dashboard') {
                try {
                    const response = await WafApi.post('dashboard');
                    DashboardRenderer.updateRealTimeStats(response.data.real_time_stats);
                } catch (error) {
                    console.error('自动刷新失败:', error);
                }
            }
        }, 30000); // 30秒刷新一次
    },
    
    stopAutoRefresh() {
        if (dashboardRefreshInterval) {
            clearInterval(dashboardRefreshInterval);
            dashboardRefreshInterval = null;
        }
    }
};

// 仪表板渲染器
const DashboardRenderer = {
    render(data) {
        this.updateStats(data.real_time_stats);
        this.renderAttackTrend(data.attack_trends);
        this.renderThreatIntel(data.threat_intel);
        this.renderSystemStatus(data.system_status);
    },
    
    updateStats(stats) {
        $('#attack-count').text(this.formatNumber(stats.recent_attacks));
        $('#connection-count').text(stats.active_connections);
        $('#qps-count').text(this.formatNumber(stats.current_qps));
        $('#blocked-ip-count').text(stats.blocked_ips);
        $('#total-rules').text(stats.total_rules);
    },
    
    updateRealTimeStats(stats) {
        // 只更新关键实时数据
        $('#attack-count').text(this.formatNumber(stats.recent_attacks));
        $('#connection-count').text(stats.active_connections);
        $('#qps-count').text(this.formatNumber(stats.current_qps));
    },
    
    renderAttackTrend(trends) {
        const chartContainer = $('#attack-trend-chart');
        let chartHtml = '<div style="padding:20px;">';
        
        trends.forEach((trend, index) => {
            const percentage = (trend.attacks / 200) * 100;
            chartHtml += `
                <div style="margin-bottom:15px;display:flex;align-items:center;gap:12px;">
                    <div style="width:80px;font-size:12px;color:#718096;">${trend.date}</div>
                    <div style="flex:1;height:24px;background:#e2e8f0;border-radius:12px;overflow:hidden;">
                        <div style="height:100%;width:${percentage}%;background:linear-gradient(90deg,#4299e1,#3182ce);border-radius:12px;
                             display:flex;align-items:center;justify-content:flex-end;padding-right:8px;color:white;font-size:10px;">
                            ${trend.attacks}
                        </div>
                    </div>
                </div>
            `;
        });
        
        chartHtml += '</div>';
        chartContainer.html(chartHtml);
    },
    
    renderThreatIntel(intel) {
        const intelList = $('#threat-intel-list');
        const html = `
            <div style="padding:16px 0;">
                <div style="margin-bottom:20px;">
                    <div style="font-weight:500;margin-bottom:8px;color:#4a5568;">今日恶意IP</div>
                    <div style="font-size:28px;font-weight:700;color:#e53e3e;">${intel.malicious_ips_today}</div>
                    <div style="font-size:12px;color:#718096;margin-top:4px;">较昨日 ${intel.malicious_ips_change >= 0 ? '+' : ''}${intel.malicious_ips_change}%</div>
                </div>
                
                <div style="margin-bottom:20px;">
                    <div style="font-weight:500;margin-bottom:8px;color:#4a5568;">新增威胁</div>
                    <div style="font-size:28px;font-weight:700;color:#ed8936;">${intel.new_threats_detected}</div>
                </div>
                
                <div>
                    <div style="font-weight:500;margin-bottom:12px;color:#4a5568;">高危来源</div>
                    <div style="display:flex;gap:8px;flex-wrap:wrap;">
                        ${intel.high_risk_countries.map(country => 
                            `<span style="background:#fed7d7;color:#c53030;padding:6px 12px;border-radius:16px;font-size:12px;font-weight:500;">${country}</span>`
                        ).join('')}
                    </div>
                </div>
            </div>
        `;
        intelList.html(html);
    },
    
    renderSystemStatus(status) {
        const statusElement = $('#system-status');
        const html = `
            <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:16px;">
                <div>
                    <div style="font-size:12px;color:#718096;margin-bottom:4px;">CPU使用率</div>
                    <div style="font-size:18px;font-weight:600;color:#4a5568;">${status.cpu_usage.toFixed(1)}%</div>
                    <div style="width:100%;height:6px;background:#e2e8f0;border-radius:3px;margin-top:6px;overflow:hidden;">
                        <div style="height:100%;width:${status.cpu_usage}%;background:${this.getStatusColor(status.cpu_usage)};border-radius:3px;"></div>
                    </div>
                </div>
                
                <div>
                    <div style="font-size:12px;color:#718096;margin-bottom:4px;">内存使用率</div>
                    <div style="font-size:18px;font-weight:600;color:#4a5568;">${status.memory_usage.toFixed(1)}%</div>
                    <div style="width:100%;height:6px;background:#e2e8f0;border-radius:3px;margin-top:6px;overflow:hidden;">
                        <div style="height:100%;width:${status.memory_usage}%;background:${this.getStatusColor(status.memory_usage)};border-radius:3px;"></div>
                    </div>
                </div>
                
                <div>
                    <div style="font-size:12px;color:#718096;margin-bottom:4px;">磁盘使用率</div>
                    <div style="font-size:18px;font-weight:600;color:#4a5568;">${status.disk_usage.toFixed(1)}%</div>
                    <div style="width:100%;height:6px;background:#e2e8f0;border-radius:3px;margin-top:6px;overflow:hidden;">
                        <div style="height:100%;width:${status.disk_usage}%;background:${this.getStatusColor(status.disk_usage)};border-radius:3px;"></div>
                    </div>
                </div>
                
                <div>
                    <div style="font-size:12px;color:#718096;margin-bottom:4px;">运行时间</div>
                    <div style="font-size:18px;font-weight:600;color:#4a5568;">${status.uptime}</div>
                </div>
            </div>
        `;
        statusElement.html(html);
    },
    
    getStatusColor(value) {
        if (value < 50) return '#48bb78';
        if (value < 80) return '#ed8936';
        return '#e53e3e';
    },
    
    formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }
};

// 日志渲染器
const LogsRenderer = {
    render(data) {
        this.renderTable(data.logs);
        this.renderPagination(data.total, data.page, data.pages, data.page_size);
    },
    
    renderTable(logs) {
        const tbody = $('#logs-table-body');
        tbody.empty();
        
        if (logs.length === 0) {
            tbody.html('<tr><td colspan="6" style="text-align:center;padding:40px;color:#718096;">暂无攻击日志</td></tr>');
            return;
        }
        
        logs.forEach(log => {
            const row = $(`
                <tr>
                    <td>${this.formatDateTime(log.attack_time)}</td>
                    <td>
                        <div style="display:flex;align-items:center;gap:8px;">
                            <span>${log.ip}</span>
                            <button class="btn-copy-ip" data-ip="${log.ip}" style="background:none;border:none;color:#4299e1;cursor:pointer;font-size:12px;">📋</button>
                        </div>
                    </td>
                    <td>${log.rule_name}</td>
                    <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${log.uri || ''}">
                        ${log.uri || '-'}
                    </td>
                    <td>
                        <span class="badge ${this.getRiskBadgeClass(log.risk_level)}">
                            ${this.getRiskText(log.risk_level)}
                        </span>
                    </td>
                    <td>${log.action_taken}</td>
                </tr>
            `);
            
            // 绑定复制IP事件
            row.find('.btn-copy-ip').click((e) => {
                e.preventDefault();
                this.copyToClipboard($(e.target).data('ip'));
            });
            
            tbody.append(row);
        });
    },
    
    renderPagination(total, currentPage, totalPages, pageSize) {
        const pagination = $('#logs-pagination');
        pagination.empty();
        
        if (totalPages <= 1) return;
        
        // 上一页
        if (currentPage > 1) {
            const prevBtn = $(`<button class="page-btn">上一页</button>`);
            prevBtn.click(() => ViewManager.loadLogs(currentPage - 1, pageSize));
            pagination.append(prevBtn);
        }
        
        // 页码
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, currentPage + 2);
        
        for (let i = startPage; i <= endPage; i++) {
            const pageBtn = $(`<button class="page-btn ${i === currentPage ? 'active' : ''}">${i}</button>`);
            pageBtn.click(() => ViewManager.loadLogs(i, pageSize));
            pagination.append(pageBtn);
        }
        
        // 下一页
        if (currentPage < totalPages) {
            const nextBtn = $(`<button class="page-btn">下一页</button>`);
            nextBtn.click(() => ViewManager.loadLogs(currentPage + 1, pageSize));
            pagination.append(nextBtn);
        }
    },
    
    formatDateTime(timestamp) {
        const date = new Date(timestamp * 1000);
        return date.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    },
    
    getRiskBadgeClass(level) {
        const classes = {
            'high': 'badge-high',
            'medium': 'badge-medium', 
            'low': 'badge-low'
        };
        return classes[level] || 'badge-medium';
    },
    
    getRiskText(level) {
        const texts = {
            'high': '高危',
            'medium': '中危',
            'low': '低危'
        };
        return texts[level] || '未知';
    },
    
    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            layer.msg('IP已复制到剪贴板', {icon: 1});
        }).catch(err => {
            layer.msg('复制失败', {icon: 2});
        });
    }
};

// 规则渲染器
const RulesRenderer = {
    render(rules) {
        const tbody = $('#rules-table-body');
        tbody.empty();
        
        if (rules.length === 0) {
            tbody.html('<tr><td colspan="5" style="text-align:center;padding:40px;color:#718096;">暂无防护规则</td></tr>');
            return;
        }
        
        rules.forEach(rule => {
            const row = $(`
                <tr>
                    <td>${rule.name}</td>
                    <td>
                        <span class="badge badge-rule-type">${this.getRuleTypeText(rule.type)}</span>
                    </td>
                    <td>${rule.priority}</td>
                    <td>
                        <div style="display:flex;align-items:center;gap:8px;">
                            <div class="status-dot ${rule.status === 'enabled' ? 'status-active' : 'status-inactive'}"></div>
                            <span>${rule.status === 'enabled' ? '启用' : '禁用'}</span>
                        </div>
                    </td>
                    <td>
                        <button class="btn-secondary btn-sm" onclick="RuleManager.edit(${rule.id})">编辑</button>
                        <button class="btn-secondary btn-sm" onclick="RuleManager.toggle(${rule.id}, '${rule.status}')">
                            ${rule.status === 'enabled' ? '禁用' : '启用'}
                        </button>
                        <button class="btn-danger btn-sm" onclick="RuleManager.delete(${rule.id})">删除</button>
                    </td>
                </tr>
            `);
            tbody.append(row);
        });
    },
    
    getRuleTypeText(type) {
        const types = {
            'sql_injection': 'SQL注入',
            'xss': '跨站脚本',
            'rce': '远程执行',
            'file_upload': '文件上传',
            'path_traversal': '路径遍历',
            'csrf': 'CSRF攻击'
        };
        return types[type] || type;
    }
};

// 威胁情报渲染器
const ThreatIntelRenderer = {
    render(data) {
        // 实现威胁情报渲染逻辑
    }
};

// 设置渲染器
const SettingsRenderer = {
    render(data) {
        // 填充表单数据
        Object.keys(data).forEach(key => {
            const element = $(`[name="${key}"]`);
            if (element.length) {
                if (element.attr('type') === 'checkbox') {
                    element.prop('checked', data[key] === 'true');
                } else {
                    element.val(data[key]);
                }
            }
        });
    }
};

// 规则管理器
const RuleManager = {
    async add() {
        const ruleData = this.getRuleFormData();
        if (!this.validateRuleData(ruleData)) return;
        
        try {
            showLoading();
            await WafApi.post('add_rule', ruleData);
            layer.msg('规则添加成功', {icon: 1});
            ViewManager.show('rules');
        } catch (error) {
            console.error('添加规则失败:', error);
        } finally {
            hideLoading();
        }
    },
    
    async edit(ruleId) {
        // 实现编辑逻辑
    },
    
    async toggle(ruleId, currentStatus) {
        try {
            showLoading();
            const newStatus = currentStatus === 'enabled' ? 'disabled' : 'enabled';
            await WafApi.post('update_rule', { 
                id: ruleId, 
                status: newStatus 
            });
            layer.msg(`规则已${newStatus === 'enabled' ? '启用' : '禁用'}`, {icon: 1});
            ViewManager.loadRules();
        } catch (error) {
            console.error('切换规则状态失败:', error);
        } finally {
            hideLoading();
        }
    },
    
    async delete(ruleId) {
        layer.confirm('确定要删除这个规则吗？', {icon: 3, title: '确认删除'}, async (index) => {
            try {
                showLoading();
                await WafApi.post('delete_rule', { id: ruleId });
                layer.msg('规则删除成功', {icon: 1});
                ViewManager.loadRules();
            } catch (error) {
                console.error('删除规则失败:', error);
            } finally {
                hideLoading();
                layer.close(index);
            }
        });
    },
    
    getRuleFormData() {
        return {
            name: $('#rule-name').val(),
            type: $('#rule-type').val(),
            pattern: $('#rule-pattern').val(),
            action: $('#rule-action').val(),
            priority: parseInt($('#rule-priority').val()) || 100,
            description: $('#rule-description').val()
        };
    },
    
    validateRuleData(data) {
        if (!data.name) {
            layer.msg('请输入规则名称', {icon: 2});
            return false;
        }
        if (!data.pattern) {
            layer.msg('请输入匹配模式', {icon: 2});
            return false;
        }
        return true;
    }
};

// 工具函数
function showLoading() {
    layer.load(1, {shade: [0.3, '#000']});
}

function hideLoading() {
    layer.closeAll('loading');
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 搜索防抖
const debouncedSearch = debounce((searchTerm) => {
    ViewManager.loadLogs(1, 20, searchTerm);
}, 500);

// 事件绑定
$(document).ready(function() {
    // 导航菜单点击事件
    $('.bt-w-menu p').click(function() {
        const viewName = $(this).attr('onclick').replace(/[()']/g, '');
        ViewManager.show(viewName);
        $('.bt-w-menu p').removeClass('bgw');
        $(this).addClass('bgw');
    });
    
    // 搜索框输入事件
    $('#log-search').on('input', function() {
        debouncedSearch($(this).val());
    });
    
    // 表单提交事件
    $('#basic-settings-form').submit(async function(e) {
        e.preventDefault();
        try {
            showLoading();
            const formData = $(this).serializeArray();
            const settings = {};
            formData.forEach(item => {
                settings[item.name] = item.value;
            });
            await WafApi.post('save_settings', settings);
            layer.msg('设置保存成功', {icon: 1});
        } catch (error) {
            console.error('保存设置失败:', error);
        } finally {
            hideLoading();
        }
    });
    
    // 默认显示仪表板
    ViewManager.show('dashboard');
});