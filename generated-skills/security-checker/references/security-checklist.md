# 安全检查清单

## 上线前必检项

### 认证与授权

- [ ] 密码使用 bcrypt / argon2 哈希，不是 MD5/SHA1
- [ ] JWT 有合理的过期时间（建议 ≤ 7 天）
- [ ] Refresh Token 存在 HttpOnly Cookie 中，不在 LocalStorage
- [ ] API 端点有权限检查，不只是登录检查
- [ ] 管理员接口有独立的权限验证
- [ ] 密码强度策略：≥ 8 位，包含大小写+数字
- [ ] 登录失败有速率限制（如 5 次/分钟）
- [ ] 敏感操作要求二次验证

### 输入验证

- [ ] 所有用户输入有服务端验证（不只靠前端）
- [ ] SQL 查询使用参数化 / ORM，不拼接字符串
- [ ] HTML 输出做了转义（防 XSS）
- [ ] 文件上传检查了文件类型、大小和内容
- [ ] URL 参数和 path 参数有做验证
- [ ] JSON 请求体有 Schema 验证（Zod / Pydantic）

### 敏感数据

- [ ] `.env` 在 `.gitignore` 中
- [ ] Git 历史中没有泄漏过密钥（用 `git log --all -S "password"` 检查）
- [ ] 日志中不打印密码、token 等敏感信息
- [ ] 错误信息不暴露堆栈或内部路径给用户
- [ ] 数据库连接字符串不硬编码在代码中
- [ ] 前端代码不包含后端密钥

### HTTP 安全

- [ ] 使用 HTTPS（生产环境强制）
- [ ] 设置了 `Content-Security-Policy` 头
- [ ] 设置了 `X-Frame-Options: DENY`（防 clickjacking）
- [ ] 设置了 `X-Content-Type-Options: nosniff`
- [ ] Cookie 设置了 `Secure`, `HttpOnly`, `SameSite=Strict`
- [ ] CORS 没有使用 `*`（或至少在认证接口不用）

### 依赖安全

- [ ] 运行了 `npm audit` / `pip-audit` 并修复高危漏洞
- [ ] 没有使用已废弃的包
- [ ] 锁文件（package-lock.json / poetry.lock）已提交
- [ ] 依赖来源可信（npm / PyPI 官方源）

---

## 常见漏洞修复模式

### SQL 注入

```typescript
// ❌ 危险
const query = `SELECT * FROM users WHERE email = '${email}'`;

// ✅ 参数化
const query = 'SELECT * FROM users WHERE email = $1';
const result = await db.query(query, [email]);

// ✅ ORM
const user = await prisma.user.findUnique({ where: { email } });
```

```python
# ❌ 危险
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")

# ✅ 参数化
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))

# ✅ ORM
user = await User.get_or_none(email=email)
```

### XSS 防护

```typescript
// ❌ 危险（React 中少见，但需注意）
<div dangerouslySetInnerHTML={{ __html: userContent }} />

// ✅ 如果必须渲染 HTML，先 sanitize
import DOMPurify from 'dompurify';
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userContent) }} />

// ✅ 大多数情况直接渲染文本
<div>{userContent}</div>  // React 自动转义
```

### 路径穿越

```typescript
// ❌ 危险
const filePath = path.join('/uploads', req.params.filename);

// ✅ 验证路径
const safeName = path.basename(req.params.filename); // 去掉 ../
const filePath = path.join('/uploads', safeName);

// ✅ 进一步检查
const resolved = path.resolve('/uploads', req.params.filename);
if (!resolved.startsWith('/uploads/')) {
  throw new ForbiddenError('Invalid path');
}
```

### 密码哈希

```typescript
// ❌ 危险
const hash = crypto.createHash('md5').update(password).digest('hex');

// ✅ bcrypt
import bcrypt from 'bcrypt';
const hash = await bcrypt.hash(password, 12);
const isValid = await bcrypt.compare(inputPassword, hash);
```

```python
# ❌ 危险
import hashlib
hash = hashlib.md5(password.encode()).hexdigest()

# ✅ bcrypt
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"])
hash = pwd_context.hash(password)
is_valid = pwd_context.verify(input_password, hash)
```

### 速率限制

```typescript
// Express + rate-limiter
import rateLimit from 'express-rate-limit';

const loginLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 5,
  message: { error: '登录尝试过多，请稍后再试' },
  standardHeaders: true,
});

app.post('/api/auth/login', loginLimiter, loginHandler);
```

```python
# FastAPI + slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/auth/login")
@limiter.limit("5/minute")
async def login(request: Request):
    ...
```

### CORS 配置

```typescript
// ❌ 过于宽松
app.use(cors({ origin: '*', credentials: true }));

// ✅ 指定允许的域名
app.use(cors({
  origin: ['https://myapp.com', 'https://admin.myapp.com'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}));
```

---

## 安全响应头模板

```
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self' https://api.myapp.com; frame-ancestors 'none';
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 0
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```
