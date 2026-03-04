# performance-optimizer

性能优化诊断技能，定位瓶颈并给出针对性优化方案。

## 覆盖领域

- 前端：首屏加载、打包体积、渲染性能、图片优化
- 后端：接口响应、内存泄漏、N+1 查询、连接池
- 数据库：EXPLAIN 分析、索引优化、分页优化、慢查询

## 文件结构

```
performance-optimizer/
├── SKILL.md                              行为指导
├── README.md                             说明文档
└── references/
    └── optimization-playbook.md          优化手册（诊断清单 + 模式参考）
```

## 使用方式

向 AI 描述你的性能问题，例如：
- "页面首屏加载太慢了"
- "这个接口响应要 3 秒"
- "帮我分析一下这条 SQL 为什么慢"
- "打包体积太大了怎么优化"
