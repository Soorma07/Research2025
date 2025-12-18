# System Design: Real-Time Payment Processing System

This is a common system design question for Capital One backend interviews. You'll be asked to design a system that processes credit card transactions in real-time.

## Problem Statement

Design a payment processing system that can handle millions of credit card transactions per day with the following requirements:

**Functional Requirements:**
1. Process credit card transactions in real-time (< 100ms latency)
2. Validate transactions (card validity, sufficient credit, fraud detection)
3. Support multiple payment methods (credit, debit, rewards)
4. Handle refunds and chargebacks
5. Generate transaction receipts and notifications

**Non-Functional Requirements:**
1. High availability (99.99% uptime)
2. Low latency (P99 < 100ms)
3. Strong consistency for financial transactions
4. PCI-DSS compliance
5. Scalable to 10,000+ TPS

## High-Level Architecture

```
                                    ┌─────────────────┐
                                    │   Load Balancer │
                                    │    (AWS ALB)    │
                                    └────────┬────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
           ┌────────▼────────┐      ┌────────▼────────┐      ┌────────▼────────┐
           │  API Gateway    │      │  API Gateway    │      │  API Gateway    │
           │   (Instance 1)  │      │   (Instance 2)  │      │   (Instance N)  │
           └────────┬────────┘      └────────┬────────┘      └────────┬────────┘
                    │                        │                        │
                    └────────────────────────┼────────────────────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
           ┌────────▼────────┐      ┌────────▼────────┐      ┌────────▼────────┐
           │ Transaction     │      │ Fraud Detection │      │ Notification    │
           │ Service         │      │ Service         │      │ Service         │
           └────────┬────────┘      └────────┬────────┘      └────────┬────────┘
                    │                        │                        │
                    │              ┌─────────▼─────────┐              │
                    │              │   ML Model        │              │
                    │              │   (SageMaker)     │              │
                    │              └───────────────────┘              │
                    │                                                 │
           ┌────────▼────────────────────────────────────────────────▼────────┐
           │                        Message Queue (Kafka)                      │
           └────────┬─────────────────────────┬───────────────────────────────┘
                    │                         │
           ┌────────▼────────┐       ┌────────▼────────┐
           │  PostgreSQL     │       │  Redis Cache    │
           │  (Primary)      │       │  (Cluster)      │
           │       │         │       └─────────────────┘
           │       ▼         │
           │  PostgreSQL     │
           │  (Replica)      │
           └─────────────────┘
```

## Component Deep Dive

### 1. API Gateway Layer

**Responsibilities:**
- Request authentication and authorization
- Rate limiting per merchant/customer
- Request validation and sanitization
- TLS termination
- Request routing

**Technology Choices:**
- AWS API Gateway or Kong
- JWT tokens for authentication
- OAuth 2.0 for merchant authorization

**Sample API Endpoints:**
```
POST /v1/transactions/authorize
POST /v1/transactions/capture
POST /v1/transactions/refund
GET  /v1/transactions/{id}
GET  /v1/transactions?merchant_id=xxx&date_range=xxx
```

### 2. Transaction Service

**Responsibilities:**
- Core transaction processing logic
- Card validation (Luhn check, expiry, CVV)
- Credit limit verification
- Transaction state management
- Idempotency handling

**Key Design Decisions:**

**Idempotency:**
```python
# Use idempotency key to prevent duplicate charges
class TransactionService:
    def process_transaction(self, request: TransactionRequest) -> TransactionResponse:
        # Check if we've seen this idempotency key
        existing = self.cache.get(f"idempotency:{request.idempotency_key}")
        if existing:
            return existing
        
        # Process transaction
        result = self._do_process(request)
        
        # Store result with TTL (24 hours)
        self.cache.set(
            f"idempotency:{request.idempotency_key}",
            result,
            ttl=86400
        )
        
        return result
```

**Two-Phase Commit for Distributed Transactions:**
```python
# Saga pattern for distributed transaction
class PaymentSaga:
    def execute(self, payment: Payment):
        try:
            # Step 1: Reserve funds
            reservation = self.account_service.reserve_funds(
                payment.account_id, 
                payment.amount
            )
            
            # Step 2: Process with card network
            network_result = self.card_network.process(payment)
            
            # Step 3: Confirm reservation
            self.account_service.confirm_reservation(reservation.id)
            
            return Success(network_result)
            
        except CardNetworkError as e:
            # Compensating transaction
            self.account_service.release_reservation(reservation.id)
            return Failure(e)
```

### 3. Fraud Detection Service

**Responsibilities:**
- Real-time fraud scoring
- Rule-based fraud detection
- ML model inference
- Velocity checks

**Key Features:**

**Rule Engine:**
```python
class FraudRuleEngine:
    rules = [
        # Transaction amount rules
        Rule("high_amount", lambda t: t.amount > 10000, score=30),
        Rule("round_amount", lambda t: t.amount % 100 == 0, score=5),
        
        # Velocity rules
        Rule("high_velocity", lambda t: t.txn_count_1hr > 10, score=40),
        Rule("new_merchant", lambda t: t.merchant_first_seen < 7, score=15),
        
        # Geographic rules
        Rule("foreign_txn", lambda t: t.country != t.home_country, score=20),
        Rule("impossible_travel", lambda t: t.travel_speed > 500, score=80),
    ]
    
    def evaluate(self, transaction: Transaction) -> FraudScore:
        total_score = sum(
            rule.score for rule in self.rules 
            if rule.condition(transaction)
        )
        
        return FraudScore(
            score=total_score,
            decision="DECLINE" if total_score > 70 else "APPROVE"
        )
```

**ML Model Integration:**
```python
class MLFraudDetector:
    def __init__(self):
        self.model = self.load_model("fraud_model_v2")
        self.feature_store = FeatureStore()
    
    def predict(self, transaction: Transaction) -> float:
        # Get real-time features
        features = self.feature_store.get_features(
            transaction.account_id,
            transaction.merchant_id
        )
        
        # Combine with transaction features
        input_vector = self.prepare_features(transaction, features)
        
        # Get prediction (probability of fraud)
        return self.model.predict_proba(input_vector)[0][1]
```

### 4. Data Layer

**Primary Database (PostgreSQL):**
- ACID transactions for financial data
- Partitioned by date for query performance
- Read replicas for reporting queries

**Schema Design:**
```sql
-- Transactions table (partitioned by month)
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idempotency_key VARCHAR(64) UNIQUE,
    account_id UUID NOT NULL,
    merchant_id UUID NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    currency CHAR(3) NOT NULL,
    status VARCHAR(20) NOT NULL,
    fraud_score INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Indexes for common queries
CREATE INDEX idx_transactions_account ON transactions(account_id, created_at);
CREATE INDEX idx_transactions_merchant ON transactions(merchant_id, created_at);
CREATE INDEX idx_transactions_status ON transactions(status) WHERE status = 'PENDING';
```

**Caching Strategy (Redis):**
```python
class CacheStrategy:
    # Cache layers
    ACCOUNT_CACHE_TTL = 300  # 5 minutes
    MERCHANT_CACHE_TTL = 3600  # 1 hour
    RATE_LIMIT_WINDOW = 60  # 1 minute
    
    def get_account_info(self, account_id: str) -> AccountInfo:
        # Try cache first
        cached = self.redis.get(f"account:{account_id}")
        if cached:
            return AccountInfo.from_json(cached)
        
        # Fetch from DB
        account = self.db.get_account(account_id)
        
        # Cache for future requests
        self.redis.setex(
            f"account:{account_id}",
            self.ACCOUNT_CACHE_TTL,
            account.to_json()
        )
        
        return account
```

## Scalability Considerations

### Horizontal Scaling
- Stateless services behind load balancer
- Database read replicas for read-heavy workloads
- Kafka partitioning by account_id for ordered processing

### Performance Optimizations
- Connection pooling for database connections
- Batch writes to reduce I/O
- Async processing for non-critical paths (notifications, analytics)

### Capacity Planning
```
Target: 10,000 TPS

API Gateway: 
  - 10 instances × 1,500 TPS each = 15,000 TPS capacity
  
Transaction Service:
  - 20 instances × 600 TPS each = 12,000 TPS capacity
  
Database:
  - Primary: 5,000 write TPS
  - 3 Read Replicas: 15,000 read TPS total
  
Redis Cluster:
  - 6 nodes: 100,000+ ops/sec
```

## Failure Handling

### Circuit Breaker Pattern
```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = "CLOSED"
        self.last_failure_time = None
    
    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise CircuitOpenError()
        
        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise
    
    def on_success(self):
        self.failure_count = 0
        self.state = "CLOSED"
    
    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
```

### Retry with Exponential Backoff
```python
def retry_with_backoff(func, max_retries=3, base_delay=0.1):
    for attempt in range(max_retries):
        try:
            return func()
        except RetryableError:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, 0.1)
            time.sleep(delay)
```

## Security Considerations

1. **PCI-DSS Compliance:**
   - Encrypt card data at rest and in transit
   - Tokenize card numbers (never store raw PANs)
   - Network segmentation for cardholder data environment
   - Regular security audits and penetration testing

2. **Data Encryption:**
   - TLS 1.3 for all communications
   - AES-256 for data at rest
   - HSM for key management

3. **Access Control:**
   - Role-based access control (RBAC)
   - Principle of least privilege
   - Audit logging for all data access

## Interview Tips

When presenting this design:

1. **Start with requirements clarification** - Ask about scale, latency requirements, and specific features needed

2. **Draw the high-level architecture first** - Show the main components and data flow

3. **Deep dive on critical paths** - Focus on the transaction processing flow and how you ensure consistency

4. **Discuss trade-offs** - Explain why you chose certain technologies and what alternatives exist

5. **Address failure scenarios** - Show you understand distributed systems challenges

6. **Mention monitoring and observability** - Metrics, logging, alerting, and tracing
