# security-checker

安全检查技能，识别代码和配置中的安全漏洞并给出修复方案。

## 覆盖领域

- OWASP Top 10 风险检查
- 认证与授权审查
- 输入验证与注入防护
- 敏感数据防泄漏
- HTTP 安全头配置
- 依赖漏洞扫描

## 文件结构

```
security-checker/
├── SKILL.md                            行为指导
├── README.md                           说明文档
└── references/
    └── security-checklist.md           安全检查清单 + 漏洞修复代码示例
```

## 使用方式

向 AI 描述你的安全需求，例如：
- "帮我检查这个项目的安全问题"
- "上线前做一下安全审查"
- "这段代码有 XSS 风险吗"
- "帮我配置安全响应头"
