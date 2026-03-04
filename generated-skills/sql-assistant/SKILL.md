---
name: sql-assistant
description: |
  当用户需要编写、优化或解释 SQL 查询时使用此技能。
  支持从自然语言生成 SQL，也支持解释已有的复杂 SQL。
  同时支持 ORM 查询（Prisma / SQLAlchemy）。
  触发关键词：SQL、查询、数据库、query、select、join、
  prisma query、sqlalchemy、怎么查、数据怎么取、写个查询。
  即使用户只说"帮我查出所有过期订单"，也应使用此技能。
---

# sql-assistant

自然语言转 SQL，SQL 优化与解释，ORM 查询辅助。

## 输入

以下任意一种：
- 自然语言描述查询需求（"查出最近 7 天注册的活跃用户"）
- 已有的 SQL 需要优化或解释
- ORM 代码需要帮助（Prisma / SQLAlchemy）

## 输出

可执行的 SQL 或 ORM 代码，附带解释。

## 执行步骤

1. 确定使用场景：
   - 自然语言 → SQL/ORM 代码
   - SQL → 解释/优化
   - SQL ↔ ORM 互转
2. 如果项目中有 schema 定义，先读取以了解表结构：
   - Prisma: 读取 `prisma/schema.prisma`
   - SQLAlchemy: 读取 models 定义文件
   - 原生 SQL: 读取 migration 文件或 schema.sql
3. 根据需求生成查询：
   ```
   ## 查询需求
   [用户的需求描述]

   ## 原生 SQL
   ```sql
   SELECT ...
   ```

   ## Prisma 写法（如果项目使用 Prisma）
   ```typescript
   const result = await prisma.user.findMany({...})
   ```

   ## SQLAlchemy 写法（如果项目使用 SQLAlchemy）
   ```python
   result = session.query(User).filter(...)
   ```

   ## 说明
   - 查询逻辑解释
   - 预期返回的数据结构
   - 性能提示（是否需要索引）
   ```
4. 如果是优化场景，指出具体的性能问题和优化方案

## 注意事项

- 生成 SQL 时先确认数据库类型（PostgreSQL / MySQL / SQLite），语法有差异
- 涉及大量数据的查询要提醒分页
- JOIN 查询要提醒索引是否存在
- 写操作（UPDATE / DELETE）务必加 WHERE 条件，并提醒用户确认
- 优先使用项目中已有的 ORM，不要混用
