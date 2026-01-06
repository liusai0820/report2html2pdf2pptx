import React, { useState, useEffect, useMemo } from 'react';

const Admin = () => {
    const [key, setKey] = useState(localStorage.getItem('admin_key') || '');
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [users, setUsers] = useState([]);
    const [generations, setGenerations] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [selectedUser, setSelectedUser] = useState(null);
    const [activeTab, setActiveTab] = useState('users');
    const [searchTerm, setSearchTerm] = useState('');
    const [sortConfig, setSortConfig] = useState({ key: '注册时间', direction: 'desc' });

    const [planType, setPlanType] = useState('pass');
    const [quota, setQuota] = useState(10);
    const [validityDays, setValidityDays] = useState(90);
    const [message, setMessage] = useState('');

    const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8005/api';

    useEffect(() => {
        if (key && localStorage.getItem('admin_key')) {
            fetchAll();
        }
    }, []);

    const fetchAll = async () => {
        setLoading(true);
        await Promise.all([fetchUsers(), fetchGenerations()]);
        setLoading(false);
    };

    const fetchUsers = async () => {
        try {
            const res = await fetch(`${API_BASE}/admin/users?key=${key}&limit=1000`);
            if (res.status === 403) {
                setIsLoggedIn(false);
                setError('Access Key 错误');
                localStorage.removeItem('admin_key');
                return;
            }
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            setUsers(data.users || []);
            setIsLoggedIn(true);
            localStorage.setItem('admin_key', key);
        } catch (err) {
            setError('加载失败: ' + err.message);
        }
    };

    const fetchGenerations = async () => {
        try {
            const res = await fetch(`${API_BASE}/admin/generations?key=${key}&limit=1000`);
            if (res.ok) {
                const data = await res.json();
                setGenerations(data.generations || []);
            }
        } catch (err) {
            console.error('Failed to fetch generations:', err);
        }
    };

    const handleLogin = (e) => {
        e.preventDefault();
        fetchAll();
    };

    const handleLogout = () => {
        setIsLoggedIn(false);
        setKey('');
        localStorage.removeItem('admin_key');
    };

    const handleUpgrade = async () => {
        if (!selectedUser) return;
        setMessage('');

        try {
            const res = await fetch(`${API_BASE}/admin/upgrade`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    key,
                    user_id: selectedUser.id,
                    plan_type: planType,
                    quota: Number(quota),
                    validity_days: Number(validityDays)
                })
            });

            const data = await res.json();
            if (res.ok) {
                setMessage('操作成功');
                setTimeout(() => {
                    setSelectedUser(null);
                    setMessage('');
                    fetchUsers();
                }, 1200);
            } else {
                setMessage('失败: ' + data.detail);
            }
        } catch (err) {
            setMessage('网络错误');
        }
    };

    // 排序函数
    const handleSort = (key) => {
        setSortConfig(prev => ({
            key,
            direction: prev.key === key && prev.direction === 'desc' ? 'asc' : 'desc'
        }));
    };

    // 过滤和排序用户
    const processedUsers = useMemo(() => {
        let result = users.filter(u =>
            !searchTerm || (u.email && u.email.toLowerCase().includes(searchTerm.toLowerCase()))
        );

        result.sort((a, b) => {
            let aVal, bVal;
            switch (sortConfig.key) {
                case '注册时间':
                    aVal = new Date(a['注册时间'] || a.created_at || 0).getTime();
                    bVal = new Date(b['注册时间'] || b.created_at || 0).getTime();
                    break;
                case '已用':
                    aVal = a['已使用'] || a.generations_used || 0;
                    bVal = b['已使用'] || b.generations_used || 0;
                    break;
                case '邮箱':
                    aVal = a.email || '';
                    bVal = b.email || '';
                    break;
                default:
                    aVal = a[sortConfig.key] || '';
                    bVal = b[sortConfig.key] || '';
            }
            if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
            if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
            return 0;
        });

        return result;
    }, [users, searchTerm, sortConfig]);

    // 趋势数据计算 - 全部历史
    const trendData = useMemo(() => {
        // 获取日期范围
        const allDates = [
            ...users.map(u => u['注册时间'] || u.created_at),
            ...generations.map(g => g['生成时间(北京)'] || g.created_at)
        ].filter(Boolean).map(d => new Date(d));

        if (allDates.length === 0) return { userTrend: [], genTrend: [] };

        const minDate = new Date(Math.min(...allDates.map(d => d.getTime())));
        const maxDate = new Date();

        // 按天生成数据
        const days = [];
        const current = new Date(minDate.getFullYear(), minDate.getMonth(), minDate.getDate());
        const end = new Date(maxDate.getFullYear(), maxDate.getMonth(), maxDate.getDate());

        while (current <= end) {
            days.push(new Date(current));
            current.setDate(current.getDate() + 1);
        }

        // 统计每天的注册和生成
        const userTrend = days.map(day => {
            const dayEnd = new Date(day.getTime() + 86400000);
            const count = users.filter(u => {
                const d = new Date(u['注册时间'] || u.created_at);
                return d >= day && d < dayEnd;
            }).length;
            return { date: day, count };
        });

        const genTrend = days.map(day => {
            const dayEnd = new Date(day.getTime() + 86400000);
            const count = generations.filter(g => {
                const d = new Date(g['生成时间(北京)'] || g.created_at);
                return d >= day && d < dayEnd;
            }).length;
            return { date: day, count };
        });

        return { userTrend, genTrend };
    }, [users, generations]);

    // 基础统计
    const stats = useMemo(() => {
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const last7Days = new Date(today.getTime() - 7 * 86400000);

        const usersToday = users.filter(u => new Date(u['注册时间'] || u.created_at) >= today).length;
        const gensToday = generations.filter(g => new Date(g['生成时间(北京)'] || g.created_at) >= today).length;

        // 付费用户：plan_type 为 pass、team 或 deadline
        const paidUsers = users.filter(u => ['pass', 'team', 'deadline'].includes(u.plan_type)).length;

        // 活跃用户：最近7天有生成记录的用户
        const activeUserEmails = new Set(
            generations
                .filter(g => new Date(g['生成时间(北京)'] || g.created_at) >= last7Days)
                .map(g => g['用户邮箱'] || g.email)
                .filter(Boolean)
        );
        const activeUsers = activeUserEmails.size;

        return {
            total: users.length,
            paid: paidUsers,
            totalGen: generations.length,
            active: activeUsers,
            usersToday,
            gensToday
        };
    }, [users, generations]);

    // 折线图组件
    const LineChart = ({ data, color, label }) => {
        if (!data || data.length === 0) return <div style={{ color: '#94A3B8', padding: '20px' }}>暂无数据</div>;

        const maxVal = Math.max(...data.map(d => d.count), 1);
        const width = 800;
        const height = 200;
        const padding = { top: 10, right: 10, bottom: 30, left: 40 };
        const chartWidth = width - padding.left - padding.right;
        const chartHeight = height - padding.top - padding.bottom;

        // 生成路径
        const points = data.map((d, i) => ({
            x: padding.left + (i / (data.length - 1 || 1)) * chartWidth,
            y: padding.top + chartHeight - (d.count / maxVal) * chartHeight
        }));

        const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
        const areaD = pathD + ` L ${points[points.length - 1].x} ${padding.top + chartHeight} L ${padding.left} ${padding.top + chartHeight} Z`;

        // X轴标签（每隔几个显示一个）
        const step = Math.max(1, Math.floor(data.length / 8));
        const xLabels = data.filter((_, i) => i % step === 0 || i === data.length - 1);

        return (
            <svg width="100%" viewBox={`0 0 ${width} ${height}`} style={{ display: 'block' }}>
                {/* 网格线 */}
                {[0, 0.5, 1].map((ratio, i) => (
                    <line key={i}
                        x1={padding.left} y1={padding.top + chartHeight * (1 - ratio)}
                        x2={width - padding.right} y2={padding.top + chartHeight * (1 - ratio)}
                        stroke="#E2E8F0" strokeDasharray="4,4"
                    />
                ))}

                {/* Y轴标签 */}
                <text x={padding.left - 8} y={padding.top + 4} fontSize="10" fill="#94A3B8" textAnchor="end">{maxVal}</text>
                <text x={padding.left - 8} y={padding.top + chartHeight} fontSize="10" fill="#94A3B8" textAnchor="end">0</text>

                {/* 填充区域 */}
                <path d={areaD} fill={color} opacity="0.1" />

                {/* 折线 */}
                <path d={pathD} fill="none" stroke={color} strokeWidth="2" />

                {/* 数据点 */}
                {points.length <= 30 && points.map((p, i) => (
                    <circle key={i} cx={p.x} cy={p.y} r="3" fill={color} />
                ))}

                {/* X轴标签 */}
                {xLabels.map((d, i) => {
                    const idx = data.indexOf(d);
                    const x = padding.left + (idx / (data.length - 1 || 1)) * chartWidth;
                    return (
                        <text key={i} x={x} y={height - 8} fontSize="10" fill="#94A3B8" textAnchor="middle">
                            {`${d.date.getMonth() + 1}/${d.date.getDate()}`}
                        </text>
                    );
                })}
            </svg>
        );
    };

    // 登录页面
    if (!isLoggedIn) {
        return (
            <div style={{
                minHeight: '100vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: '#F1F5F9',
                fontFamily: "'Noto Sans SC', -apple-system, sans-serif"
            }}>
                <div style={{
                    background: '#fff',
                    padding: '48px 40px',
                    boxShadow: '0 20px 60px -20px rgba(15, 23, 42, 0.15)',
                    width: '100%',
                    maxWidth: '360px'
                }}>
                    <div style={{ fontSize: '10px', fontWeight: 700, letterSpacing: '2px', color: '#94A3B8', marginBottom: '24px' }}>
                        管理员入口
                    </div>
                    <h1 style={{ fontSize: '28px', fontWeight: 700, color: '#0F172A', marginBottom: '32px' }}>管理后台</h1>
                    <form onSubmit={handleLogin}>
                        <input
                            type="password"
                            value={key}
                            onChange={(e) => setKey(e.target.value)}
                            placeholder="输入管理密钥"
                            style={{ width: '100%', padding: '14px 16px', border: '1px solid #E2E8F0', background: '#F8FAFC', fontSize: '14px', marginBottom: '16px', outline: 'none' }}
                        />
                        <button type="submit" style={{ width: '100%', padding: '14px', background: '#0F172A', color: '#fff', border: 'none', fontSize: '13px', fontWeight: 600, cursor: 'pointer' }}>
                            登录
                        </button>
                        {error && <p style={{ color: '#DC2626', fontSize: '12px', marginTop: '16px' }}>{error}</p>}
                    </form>
                </div>
            </div>
        );
    }

    const SortHeader = ({ label, sortKey }) => (
        <th
            onClick={() => handleSort(sortKey)}
            style={{
                padding: '14px 16px',
                textAlign: 'left',
                fontWeight: 600,
                fontSize: '11px',
                color: sortConfig.key === sortKey ? '#0F172A' : '#64748B',
                cursor: 'pointer',
                userSelect: 'none'
            }}
        >
            {label} {sortConfig.key === sortKey && (sortConfig.direction === 'desc' ? '↓' : '↑')}
        </th>
    );

    return (
        <div style={{ minHeight: '100vh', background: '#F1F5F9', fontFamily: "'Noto Sans SC', -apple-system, sans-serif", color: '#0F172A' }}>
            {/* 顶栏 */}
            <div style={{ background: '#fff', borderBottom: '1px solid #E2E8F0', padding: '16px 32px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', position: 'sticky', top: 0, zIndex: 100 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <span style={{ fontWeight: 900, fontSize: '14px' }}>SlideCraft Dashboard</span>
                    <span style={{ fontSize: '10px', color: '#64748B', background: '#F1F5F9', padding: '4px 8px' }}>管理后台</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
                    <span style={{ fontSize: '16px', fontWeight: 700, color: '#2563EB', letterSpacing: '0.5px' }}>Build · Ship · Profit</span>
                    <button onClick={fetchAll} style={{ padding: '8px 16px', border: '1px solid #E2E8F0', background: '#fff', fontSize: '12px', cursor: 'pointer' }}>刷新</button>
                    <button onClick={handleLogout} style={{ padding: '8px 16px', border: 'none', background: 'transparent', fontSize: '12px', cursor: 'pointer', color: '#64748B' }}>退出</button>
                </div>
            </div>

            <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '32px' }}>
                {/* 数据概览 */}
                <div style={{ marginBottom: '32px' }}>
                    <div style={{ fontSize: '10px', fontWeight: 700, letterSpacing: '2px', color: '#94A3B8', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                        数据概览 <span style={{ flex: 1, height: '1px', background: '#E2E8F0' }}></span>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1px', background: '#E2E8F0', border: '1px solid #E2E8F0' }}>
                        {[
                            { label: '总用户', value: stats.total, sub: `今日 +${stats.usersToday}`, color: '#0F172A' },
                            { label: '付费用户', value: stats.paid, sub: `含 deadline/pass/team`, color: '#2563EB' },
                            { label: '总生成次数', value: stats.totalGen, sub: `今日 +${stats.gensToday}`, color: '#0F172A' },
                            { label: '7日活跃', value: stats.active, sub: `近7天有生成`, color: '#059669' }
                        ].map((stat, i) => (
                            <div key={i} style={{ background: '#fff', padding: '24px 20px' }}>
                                <div style={{ fontSize: '32px', fontWeight: 700, color: stat.color, marginBottom: '4px' }}>{stat.value}</div>
                                <div style={{ fontSize: '12px', color: '#64748B', marginBottom: '4px' }}>{stat.label}</div>
                                <div style={{ fontSize: '11px', color: '#94A3B8' }}>{stat.sub}</div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* 趋势图 */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '32px' }}>
                    <div style={{ background: '#fff', border: '1px solid #E2E8F0', padding: '20px' }}>
                        <div style={{ fontSize: '10px', fontWeight: 700, letterSpacing: '1px', color: '#94A3B8', marginBottom: '16px' }}>
                            用户注册趋势
                        </div>
                        <LineChart data={trendData.userTrend} color="#2563EB" label="注册" />
                    </div>
                    <div style={{ background: '#fff', border: '1px solid #E2E8F0', padding: '20px' }}>
                        <div style={{ fontSize: '10px', fontWeight: 700, letterSpacing: '1px', color: '#94A3B8', marginBottom: '16px' }}>
                            生成次数趋势
                        </div>
                        <LineChart data={trendData.genTrend} color="#059669" label="生成" />
                    </div>
                </div>

                {/* 标签页 */}
                <div style={{ display: 'flex', gap: '0', marginBottom: '24px', borderBottom: '1px solid #E2E8F0' }}>
                    {[{ key: 'users', label: '用户管理' }, { key: 'generations', label: '生成记录' }].map(tab => (
                        <button key={tab.key} onClick={() => setActiveTab(tab.key)}
                            style={{ padding: '12px 24px', border: 'none', background: 'transparent', fontSize: '13px', fontWeight: 600, cursor: 'pointer', color: activeTab === tab.key ? '#0F172A' : '#94A3B8', borderBottom: activeTab === tab.key ? '2px solid #0F172A' : '2px solid transparent', marginBottom: '-1px' }}
                        >{tab.label}</button>
                    ))}
                </div>

                {/* 搜索 */}
                <div style={{ marginBottom: '24px' }}>
                    <input type="text" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} placeholder="搜索邮箱..."
                        style={{ width: '300px', padding: '10px 16px', border: '1px solid #E2E8F0', background: '#fff', fontSize: '13px', outline: 'none' }}
                    />
                </div>

                {loading ? (
                    <div style={{ padding: '60px', textAlign: 'center', color: '#94A3B8' }}>加载中...</div>
                ) : activeTab === 'users' ? (
                    <div style={{ background: '#fff', border: '1px solid #E2E8F0' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                            <thead>
                                <tr style={{ borderBottom: '1px solid #E2E8F0' }}>
                                    <SortHeader label="邮箱" sortKey="邮箱" />
                                    <th style={{ padding: '14px 16px', textAlign: 'left', fontWeight: 600, fontSize: '11px', color: '#64748B' }}>身份</th>
                                    <th style={{ padding: '14px 16px', textAlign: 'left', fontWeight: 600, fontSize: '11px', color: '#64748B' }}>套餐</th>
                                    <SortHeader label="已用 / 总额" sortKey="已用" />
                                    <th style={{ padding: '14px 16px', textAlign: 'left', fontWeight: 600, fontSize: '11px', color: '#64748B' }}>状态</th>
                                    <SortHeader label="注册时间" sortKey="注册时间" />
                                    <th style={{ padding: '14px 16px', textAlign: 'right', fontWeight: 600, fontSize: '11px', color: '#64748B' }}></th>
                                </tr>
                            </thead>
                            <tbody>
                                {processedUsers.map(user => {
                                    const used = user['已使用'] ?? user.generations_used ?? 0;
                                    const total = user['总额度'] ?? user.generation_quota ?? 0;
                                    const status = user['额度状态'] ?? '—';
                                    const isPaid = user.plan_type === 'pass' || user.plan_type === 'team';
                                    const occupationLabels = {
                                        student: '学生', teacher: '教师', researcher: '研究员',
                                        employee: '员工', manager: '高管', consultant: '顾问',
                                        freelancer: '自由职业', entrepreneur: '创业者', government: '政府', other: '其他'
                                    };
                                    const occupation = occupationLabels[user.occupation] || user.occupation || '—';

                                    return (
                                        <tr key={user.id} style={{ borderBottom: '1px solid #F1F5F9' }}>
                                            <td style={{ padding: '14px 16px', fontWeight: 500 }}>{user.email}</td>
                                            <td style={{ padding: '14px 16px', fontSize: '12px', color: '#64748B' }}>{occupation}</td>
                                            <td style={{ padding: '14px 16px' }}>
                                                <span style={{ display: 'inline-block', padding: '4px 10px', fontSize: '11px', fontWeight: 600, background: isPaid ? '#EFF6FF' : '#F8FAFC', color: isPaid ? '#2563EB' : '#64748B', borderLeft: isPaid ? '3px solid #2563EB' : '3px solid #CBD5E1' }}>
                                                    {user.plan_type || 'free'}
                                                </span>
                                            </td>
                                            <td style={{ padding: '14px 16px', fontFamily: 'monospace' }}>{used} / {total}</td>
                                            <td style={{ padding: '14px 16px', fontSize: '12px', color: status.includes('有效') ? '#059669' : status.includes('过期') ? '#DC2626' : '#94A3B8' }}>{status}</td>
                                            <td style={{ padding: '14px 16px', color: '#94A3B8', fontSize: '12px' }}>
                                                {user['注册时间'] ? new Date(user['注册时间']).toLocaleDateString('zh-CN') : '—'}
                                            </td>
                                            <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                                                <button onClick={() => { setSelectedUser(user); setPlanType(user.plan_type || 'pass'); setQuota(user['总额度'] || 10); setValidityDays(90); setMessage(''); }}
                                                    style={{ padding: '6px 14px', background: '#0F172A', color: '#fff', border: 'none', fontSize: '11px', cursor: 'pointer' }}
                                                >管理</button>
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                        <div style={{ padding: '14px 16px', borderTop: '1px solid #E2E8F0', fontSize: '12px', color: '#94A3B8' }}>
                            显示 {processedUsers.length} / {users.length} 位用户
                        </div>
                    </div>
                ) : (
                    <div style={{ background: '#fff', border: '1px solid #E2E8F0' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                            <thead>
                                <tr style={{ borderBottom: '1px solid #E2E8F0' }}>
                                    {['用户', '职业', '文档名称', '页数', '场景', '生成时间'].map((h, i) => (
                                        <th key={i} style={{ padding: '14px 16px', textAlign: 'left', fontWeight: 600, fontSize: '11px', color: '#64748B' }}>{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {generations.sort((a, b) => new Date(b['生成时间(北京)'] || b.created_at) - new Date(a['生成时间(北京)'] || a.created_at)).map((gen, idx) => {
                                    // 场景标签映射
                                    const scenarioLabels = {
                                        'annual_review': '年度报告', 'company_intro': '公司介绍', 'government': '政府公文',
                                        'consulting': '咨询报告', 'bid_proposal': '投标方案', 'thesis_proposal': '论文答辩',
                                        'party_building': '党建工作', 'corporate_training': '企业培训', 'tech_report': '技术报告'
                                    };
                                    const scenario = scenarioLabels[gen.scenario] || gen.scenario || gen['场景'] || '—';

                                    // 职业标签映射
                                    const occupationLabels = {
                                        student: '学生', teacher: '教师', researcher: '研究员',
                                        employee: '员工', manager: '高管', consultant: '顾问',
                                        freelancer: '自由职业', entrepreneur: '创业者', government: '政府', other: '其他'
                                    };
                                    const occupation = occupationLabels[gen.occupation] || gen.occupation || '—';

                                    // 时间转换为北京时间显示
                                    const formatBeijingTime = (dateStr) => {
                                        if (!dateStr) return '—';
                                        const date = new Date(dateStr);
                                        // 如果是 UTC 时间，加 8 小时转北京时间
                                        const beijingDate = new Date(date.getTime() + 8 * 60 * 60 * 1000);
                                        return beijingDate.toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' });
                                    };

                                    return (
                                        <tr key={gen.id || idx} style={{ borderBottom: '1px solid #F1F5F9' }}>
                                            <td style={{ padding: '14px 16px' }}>{gen['用户邮箱'] || gen.email || '—'}</td>
                                            <td style={{ padding: '14px 16px', color: '#64748B', fontSize: '12px' }}>{occupation}</td>
                                            <td style={{ padding: '14px 16px', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{gen['文档名'] || gen.document_name || '—'}</td>
                                            <td style={{ padding: '14px 16px', fontFamily: 'monospace' }}>{gen['页数'] || gen.actual_pages || '—'}</td>
                                            <td style={{ padding: '14px 16px', color: '#64748B' }}>{scenario}</td>
                                            <td style={{ padding: '14px 16px', color: '#94A3B8', fontSize: '12px', whiteSpace: 'nowrap' }}>
                                                {formatBeijingTime(gen['生成时间(北京)'] || gen.created_at)}
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                        <div style={{ padding: '14px 16px', borderTop: '1px solid #E2E8F0', fontSize: '12px', color: '#94A3B8' }}>
                            共 {generations.length} 条记录
                        </div>
                    </div>
                )}
            </div>

            {/* 弹窗 */}
            {selectedUser && (
                <div style={{ position: 'fixed', inset: 0, background: 'rgba(15, 23, 42, 0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px', zIndex: 200 }}>
                    <div style={{ background: '#fff', width: '100%', maxWidth: '400px', boxShadow: '0 40px 100px -20px rgba(15, 23, 42, 0.3)' }}>
                        <div style={{ padding: '24px', borderBottom: '1px solid #E2E8F0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span style={{ fontSize: '11px', fontWeight: 700, letterSpacing: '1px', color: '#94A3B8' }}>用户管理</span>
                            <button onClick={() => setSelectedUser(null)} style={{ border: 'none', background: 'transparent', cursor: 'pointer', color: '#94A3B8', fontSize: '18px' }}>×</button>
                        </div>

                        <div style={{ padding: '24px' }}>
                            <div style={{ background: '#F8FAFC', padding: '16px', marginBottom: '24px', borderLeft: '3px solid #2563EB' }}>
                                <div style={{ fontSize: '11px', color: '#94A3B8', marginBottom: '4px' }}>用户邮箱</div>
                                <div style={{ fontWeight: 600 }}>{selectedUser.email}</div>
                            </div>

                            <div style={{ marginBottom: '20px' }}>
                                <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: '#64748B', marginBottom: '8px' }}>套餐类型</label>
                                <select value={planType} onChange={(e) => setPlanType(e.target.value)} style={{ width: '100%', padding: '12px', border: '1px solid #E2E8F0', background: '#fff', fontSize: '14px' }}>
                                    <option value="free">free</option>
                                    <option value="deadline">deadline (¥9.9)</option>
                                    <option value="pass">pass (¥39)</option>
                                    <option value="team">team (¥79)</option>
                                </select>
                            </div>

                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '24px' }}>
                                <div>
                                    <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: '#64748B', marginBottom: '8px' }}>额度（次）</label>
                                    <input type="number" value={quota} onChange={(e) => setQuota(e.target.value)} style={{ width: '100%', padding: '12px', border: '1px solid #E2E8F0', fontSize: '14px' }} />
                                </div>
                                <div>
                                    <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: '#64748B', marginBottom: '8px' }}>有效期（天）</label>
                                    <input type="number" value={validityDays} onChange={(e) => setValidityDays(e.target.value)} style={{ width: '100%', padding: '12px', border: '1px solid #E2E8F0', fontSize: '14px' }} />
                                </div>
                            </div>

                            {message && (
                                <div style={{ padding: '14px', marginBottom: '20px', fontSize: '12px', background: message.includes('成功') ? '#F0FDF4' : '#FEF2F2', color: message.includes('成功') ? '#166534' : '#DC2626', borderLeft: `3px solid ${message.includes('成功') ? '#22C55E' : '#EF4444'}` }}>
                                    {message}
                                </div>
                            )}

                            <div style={{ display: 'flex', gap: '12px' }}>
                                <button onClick={() => setSelectedUser(null)} style={{ flex: 1, padding: '14px', border: '1px solid #E2E8F0', background: '#fff', fontSize: '13px', cursor: 'pointer' }}>取消</button>
                                <button onClick={handleUpgrade} style={{ flex: 1, padding: '14px', border: 'none', background: '#0F172A', color: '#fff', fontSize: '13px', fontWeight: 600, cursor: 'pointer' }}>确认修改</button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Admin;
