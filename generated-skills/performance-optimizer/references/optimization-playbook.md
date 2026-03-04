# 性能优化手册

## 前端性能

### 核心指标（Web Vitals）

| 指标 | 好 | 需改善 | 差 | 含义 |
|------|------|--------|------|------|
| LCP | < 2.5s | 2.5~4s | > 4s | 最大内容绘制（加载速度） |
| FID/INP | < 100ms | 100~300ms | > 300ms | 交互延迟（响应速度） |
| CLS | < 0.1 | 0.1~0.25 | > 0.25 | 布局偏移（视觉稳定性） |
| TTFB | < 800ms | 800ms~1.8s | > 1.8s | 首字节时间（服务端速度） |
| FCP | < 1.8s | 1.8~3s | > 3s | 首次内容绘制 |

### 打包体积优化清单

| 检查项 | 操作 | 预期收益 |
|--------|------|---------|
| 未使用的依赖 | `npx depcheck`，移除未引用包 | 减少 10~50% |
| 大型依赖替代 | moment→dayjs、lodash→lodash-es 按需引入 | 减少 50~200KB |
| 动态导入路由 | `React.lazy()` / `defineAsyncComponent()` | 首屏减少 30~60% |
| 图片未压缩 | WebP/AVIF 格式 + 响应式尺寸 | 减少 50~80% |
| Source Map 泄漏 | 生产构建关闭 source map | 减少 50%+ |
| CSS 未 Tree-shake | PurgeCSS / Tailwind 的 content 配置 | 减少 80%+ 未使用 CSS |

### React 渲染优化

```
性能问题 → 先用 React DevTools Profiler 定位

组件重复渲染？
├── props 引用变化 → useMemo / useCallback 包裹
├── Context 变化导致全树渲染 → 拆分 Context 或用 selector
├── 父组件渲染带动子组件 → React.memo 包裹子组件
└── 列表未用 key / key 是 index → 使用稳定唯一 key

大列表渲染卡顿？
├── > 100 项 → 虚拟列表（react-window / tanstack-virtual）
└── 筛选/排序 → 在 useMemo 中计算，不在 render 中
```

---

## 后端性能

### 接口响应优化清单

| 瓶颈类型 | 诊断方法 | 优化方案 |
|---------|---------|---------|
| N+1 查询 | 日志中看到大量重复 SQL | ORM eager loading / JOIN / DataLoader |
| 序列化慢 | 返回数据字段过多 | 只返回需要的字段，分页 |
| 外部调用阻塞 | 接口中调其他服务 | 异步化 / 并行请求 / 缓存结果 |
| 计算密集 | CPU 占用高 | 缓存计算结果 / 后台任务 / Worker |
| 连接池耗尽 | 等待连接超时 | 增大池大小 / 检查连接泄漏 |

### 内存泄漏常见原因

**Node.js / TypeScript：**
- 全局变量无限增长（Map/Set 未清理）
- 事件监听器未移除（EventEmitter.on 没有 off）
- 闭包引用大对象（定时器回调中引用外部大数组）
- 缓存无上限（应设 maxSize + TTL）

**Python：**
- 循环引用 + `__del__` 方法（阻止 GC 回收）
- 全局列表/字典不断追加
- 未关闭的文件句柄/数据库连接
- 线程局部变量未清理

### 并发模型选择

| 场景 | Node.js | Python |
|------|---------|--------|
| IO 密集（API 网关） | 天然异步，直接用 | asyncio / FastAPI |
| CPU 密集（数据处理） | Worker Threads | multiprocessing / Celery |
| 混合负载 | 主线程 IO + Worker 计算 | asyncio + ProcessPool |

---

## 数据库性能

### EXPLAIN 结果解读

```sql
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';
```

| 关键字 | 含义 | 是否需要优化 |
|--------|------|------------|
| Seq Scan | 全表扫描 | ⚠️ 大表需要加索引 |
| Index Scan | 索引扫描 | ✅ 正常 |
| Index Only Scan | 覆盖索引 | ✅ 最优 |
| Bitmap Heap Scan | 位图扫描 | ✅ 多条件查询正常 |
| Nested Loop | 嵌套循环 JOIN | ⚠️ 大表可能慢 |
| Hash Join | 哈希 JOIN | ✅ 大表 JOIN 正常 |
| Sort | 排序 | ⚠️ 检查是否可用索引排序 |

### 索引优化原则

```
何时加索引？
├── WHERE 条件中的列
├── JOIN 条件中的列
├── ORDER BY 的列
└── 高基数列（如 email、user_id），低基数列（如 status、gender）索引效果差

何时用复合索引？
├── 查询经常一起用的列 → (user_id, created_at)
├── 遵循最左前缀原则
└── 把选择性高的列放前面

何时不加索引？
├── 表很小（< 1000 行）
├── 写多读少的表
└── 频繁更新的列
```

### 分页优化

```sql
-- ❌ OFFSET 分页（越深越慢）
SELECT * FROM orders ORDER BY id LIMIT 20 OFFSET 100000;

-- ✅ 游标分页（恒定速度）
SELECT * FROM orders WHERE id > :last_id ORDER BY id LIMIT 20;

-- ✅ 如果必须支持跳页
SELECT * FROM orders WHERE id >= (
  SELECT id FROM orders ORDER BY id LIMIT 1 OFFSET 100000
) ORDER BY id LIMIT 20;
```

---

## 性能优化优先级矩阵

| 收益 ╲ 成本 | 低成本 | 中成本 | 高成本 |
|-------------|--------|--------|--------|
| **高收益** | 🟢 立即做 | 🟢 排期做 | 🟡 评估 ROI |
| **中收益** | 🟢 顺手做 | 🟡 看情况 | 🔴 暂不做 |
| **低收益** | 🟡 有空做 | 🔴 暂不做 | 🔴 不做 |
