# 测试模式参考

## TypeScript（Jest / Vitest）

### 基础结构

```typescript
describe('模块名或函数名', () => {
  // 共享 setup
  beforeEach(() => { /* 每个 test 前执行 */ });
  afterEach(() => { /* 每个 test 后清理 */ });

  describe('正常路径', () => {
    it('should 做什么 when 什么条件', () => {
      // Arrange → Act → Assert
    });
  });

  describe('边界条件', () => { /* ... */ });
  describe('异常路径', () => { /* ... */ });
});
```

### 常见测试模式

**纯函数测试：**
```typescript
describe('calculateTotal', () => {
  it('should sum item prices correctly', () => {
    const items = [{ price: 10 }, { price: 20 }];
    expect(calculateTotal(items)).toBe(30);
  });

  it('should return 0 for empty array', () => {
    expect(calculateTotal([])).toBe(0);
  });

  it('should handle negative prices', () => {
    const items = [{ price: 10 }, { price: -5 }];
    expect(calculateTotal(items)).toBe(5);
  });
});
```

**异步函数测试：**
```typescript
describe('fetchUser', () => {
  it('should return user data', async () => {
    const user = await fetchUser('123');
    expect(user).toMatchObject({ id: '123', name: expect.any(String) });
  });

  it('should throw on non-existent user', async () => {
    await expect(fetchUser('nonexistent')).rejects.toThrow('Not found');
  });
});
```

**Mock 外部依赖：**
```typescript
// mock 整个模块
vi.mock('./api', () => ({
  fetchData: vi.fn(),
}));

// mock 单个函数
const mockFetch = vi.spyOn(api, 'fetchData').mockResolvedValue({ data: [] });

// 验证调用
expect(mockFetch).toHaveBeenCalledWith('/users', expect.objectContaining({ page: 1 }));
expect(mockFetch).toHaveBeenCalledTimes(1);
```

**React 组件测试（Testing Library）：**
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

describe('LoginForm', () => {
  it('should show error on empty submit', async () => {
    render(<LoginForm />);
    fireEvent.click(screen.getByRole('button', { name: '登录' }));
    await waitFor(() => {
      expect(screen.getByText('请输入用户名')).toBeInTheDocument();
    });
  });

  it('should call onSubmit with form data', async () => {
    const onSubmit = vi.fn();
    render(<LoginForm onSubmit={onSubmit} />);
    
    fireEvent.change(screen.getByLabelText('用户名'), { target: { value: 'admin' } });
    fireEvent.change(screen.getByLabelText('密码'), { target: { value: '123456' } });
    fireEvent.click(screen.getByRole('button', { name: '登录' }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({ username: 'admin', password: '123456' });
    });
  });
});
```

---

## Python（pytest）

### 基础结构

```python
import pytest

class TestCalculateTotal:
    """测试 calculate_total 函数"""

    def test_sums_prices_correctly(self):
        items = [{"price": 10}, {"price": 20}]
        assert calculate_total(items) == 30

    def test_returns_zero_for_empty_list(self):
        assert calculate_total([]) == 0

    def test_raises_on_invalid_input(self):
        with pytest.raises(TypeError):
            calculate_total(None)
```

### 常见测试模式

**Fixture 共享数据：**
```python
@pytest.fixture
def sample_user():
    return User(name="张三", email="zhangsan@example.com", role="admin")

@pytest.fixture
def db_session():
    session = create_test_session()
    yield session
    session.rollback()
    session.close()

def test_user_display_name(sample_user):
    assert sample_user.display_name == "张三"
```

**Parametrize 批量测试：**
```python
@pytest.mark.parametrize("input_val,expected", [
    ("hello", "HELLO"),
    ("", ""),
    ("Hello World", "HELLO WORLD"),
    ("123abc", "123ABC"),
])
def test_to_uppercase(input_val, expected):
    assert to_uppercase(input_val) == expected
```

**异步测试：**
```python
import pytest

@pytest.mark.asyncio
async def test_fetch_user():
    user = await fetch_user("123")
    assert user["id"] == "123"

@pytest.mark.asyncio
async def test_fetch_nonexistent_user():
    with pytest.raises(NotFoundError):
        await fetch_user("nonexistent")
```

**Mock 外部依赖：**
```python
from unittest.mock import patch, MagicMock, AsyncMock

def test_send_email(mocker):
    mock_smtp = mocker.patch("myapp.email.smtplib.SMTP")
    send_email("test@example.com", "Hello")
    mock_smtp.return_value.send_message.assert_called_once()

@patch("myapp.services.httpx.AsyncClient.get")
async def test_external_api(mock_get):
    mock_get.return_value = MagicMock(status_code=200, json=lambda: {"ok": True})
    result = await call_external_api()
    assert result["ok"] is True
```

**FastAPI 端点测试：**
```python
from httpx import AsyncClient, ASGITransport
from myapp.main import app

@pytest.mark.asyncio
async def test_create_user():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/users", json={"name": "张三", "email": "z@example.com"})
    assert response.status_code == 201
    assert response.json()["name"] == "张三"
```

---

## 通用测试原则

### 命名规范

```
test_<行为描述>_when_<条件>
should_<行为描述>_when_<条件>
```

好的命名：
- `test_returns_empty_list_when_no_results`
- `should show error message when password is too short`

差的命名：
- `test_function1`
- `test_it_works`

### 每个测试用例覆盖的维度

| 维度 | 示例 |
|------|------|
| 正常输入 | 标准参数，预期返回 |
| 空值 | null / undefined / None / "" / [] / {} |
| 边界值 | 0, -1, MAX_INT, 超长字符串 |
| 类型错误 | 传错误类型的参数 |
| 并发 | 多个请求同时操作同一资源 |
| 幂等性 | 同一操作执行两次结果一致 |
| 权限 | 无权限用户尝试操作 |

### 什么不该 Mock

- 被测函数本身的逻辑
- 纯数据转换函数
- 项目内部的工具函数（除非有副作用）

### 什么该 Mock

- 外部 HTTP 请求
- 数据库操作（单元测试层面）
- 文件系统读写
- 时间相关（Date.now / time.time）
- 随机数（Math.random / random）
