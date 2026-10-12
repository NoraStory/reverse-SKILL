# Resilience Patterns

The `openclaw_sdk.resilience` module provides three local resilience patterns for wrapping async operations. These patterns do not call the gateway directly; they wrap other operations (such as gateway calls) with resilience logic.

## RetryPolicy

Wraps async operations with exponential backoff retry logic.

```python
from openclaw_sdk.resilience.retry import RetryPolicy
```

### Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_retries` | `int` | `3` | Maximum retry attempts (0–50) |
| `backoff_base` | `float` | `1.0` | Base delay in seconds for exponential backoff |
| `backoff_max` | `float` | `60.0` | Maximum delay cap |
| `jitter` | `bool` | `True` | Add random jitter to backoff |
| `retryable_exceptions` | `tuple[type[Exception], ...]` | `(GatewayError, TimeoutError)` | Exception types eligible for retry |

### `execute(fn, *args, **kwargs)`

Executes an async callable with retry logic.

```python
policy = RetryPolicy(max_retries=3, backoff_base=1.0, backoff_max=60.0)

result = await policy.execute(some_async_fn, arg1, kwarg1="value")
```

- Retries on retryable exceptions with exponential backoff: `min(backoff_base * 2^attempt, backoff_max)`
- When `jitter=True`, delay is uniformly distributed between `0` and the computed value
- Raises the last exception if all retries are exhausted
- Raises immediately if the exception is not retryable

### `as_decorator()`

Returns a decorator that wraps async functions with this retry policy.

```python
policy = RetryPolicy(max_retries=5)

@policy.as_decorator()
async def fragile_call():
    ...
```

### `_is_retryable(exc)`

Determines whether an exception should be retried.

Resolution order:
1. If the exception's own class (not a base class) explicitly overrides `is_retryable`, that value takes precedence. This lets subclasses such as `AuthenticationError` (`False`) or `RateLimitError` (`True`) control retry behaviour directly.
2. Otherwise, retries when the exception is an instance of one of the configured `retryable_exceptions`.

### `_compute_delay(attempt)`

Computes the backoff delay for a given attempt (0-indexed).

```
delay = min(backoff_base * 2^attempt, backoff_max)
```

When `jitter=True`, returns a random value between `0` and the computed delay.

### Standalone Decorator: `retry_async`

Convenience decorator factory with inline configuration.

```python
from openclaw_sdk.resilience.retry import retry_async

@retry_async(max_retries=3, backoff_base=0.5, backoff_max=30.0, jitter=True)
async def fetch_data():
    ...
```

## CircuitBreaker

Prevents cascading failures by tracking consecutive errors and short-circuiting calls when a failure threshold is exceeded.

```python
from openclaw_sdk.resilience.circuit_breaker import CircuitBreaker
```

### States

| State | Description |
|-------|-------------|
| `closed` | Normal operation; calls pass through |
| `open` | Failure threshold exceeded; calls are rejected immediately with `CircuitOpenError` |
| `half_open` | Recovery timeout elapsed; limited probe calls allowed to test recovery |

### Constructor

```python
breaker = CircuitBreaker(
    failure_threshold=5,    # consecutive failures to trip
    recovery_timeout=30.0,  # seconds to wait before probing recovery
    half_open_max_calls=1,  # probe calls allowed in half-open state
)
```

### `execute(fn, *args, **kwargs)`

Executes an async callable through the circuit breaker.

```python
result = await breaker.execute(some_async_fn, arg1, kwarg1="value")
```

- In `closed` state: executes normally; resets failure counter on success, increments on failure
- In `open` state: raises `CircuitOpenError` immediately
- In `half_open` state: allows up to `half_open_max_calls` probe calls; re-opens on failure, closes on success

Raises `CircuitOpenError` when the circuit is open.

### `state` property

Returns the current circuit breaker state as a string: `"closed"`, `"open"`, or `"half_open"`.

Automatically transitions from `open` to `half_open` when the recovery timeout has elapsed.

```python
if breaker.state == "open":
    print("Circuit is open, calls are being rejected")
```

### `reset()`

Manually resets the circuit breaker to the closed state, clearing all failure counters and timestamps.

```python
breaker.reset()
```

## RateLimiter

Token bucket rate limiter that limits the number of calls within a rolling time window.

```python
from openclaw_sdk.resilience.rate_limiter import RateLimiter
```

### Constructor

```python
limiter = RateLimiter(
    max_calls=60,   # maximum calls per period
    period=60.0,    # time window in seconds
)
```

### `acquire()`

Asynchronously waits until a call slot is available under the rate limit.

- Blocks if the call budget for the current window has been exhausted
- Automatically resumes once a slot becomes available (when the oldest timestamp falls outside the window)

```python
await limiter.acquire()
```

### `execute(fn, *args, **kwargs)`

Executes an async callable after acquiring a rate limit slot.

```python
result = await limiter.execute(some_async_fn, arg1, kwarg1="value")
```

Equivalent to calling `await acquire()` followed by `await fn(*args, **kwargs)`.

### `remaining` property

Returns the number of calls still available in the current window.

```python
print(f"Calls remaining: {limiter.remaining}")
```

Automatically purges expired timestamps before computing.
