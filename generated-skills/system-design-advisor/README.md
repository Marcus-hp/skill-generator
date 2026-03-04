# system-design-advisor

系统设计辅助技能，在架构决策点提供结构化分析和选型建议。

## 覆盖领域

- 服务架构：单体 vs 微服务 vs Serverless
- 缓存策略：本地缓存 / Redis / 多级缓存
- 消息队列选型：Redis Streams / RabbitMQ / Kafka
- 数据库选型：PostgreSQL / MySQL / MongoDB
- API 设计：REST / GraphQL / gRPC / WebSocket
- 高可用模式：限流、熔断、重试、降级

## 文件结构

```
system-design-advisor/
├── SKILL.md                          行为指导
├── README.md                         说明文档
└── references/
    └── design-patterns.md            架构模式与选型参考
```

## 使用方式

向 AI 描述你的系统需求或架构问题，例如：
- "这个系统应该用微服务还是单体？"
- "缓存该怎么设计？"
- "消息队列选 RabbitMQ 还是 Kafka？"
