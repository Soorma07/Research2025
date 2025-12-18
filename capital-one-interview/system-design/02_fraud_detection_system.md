# System Design: Real-Time Fraud Detection System

This is another common system design question at Capital One, given their focus on security and fraud prevention.

## Problem Statement

Design a real-time fraud detection system that can analyze credit card transactions and flag potentially fraudulent activity within milliseconds.

**Functional Requirements:**
1. Analyze transactions in real-time (< 50ms latency for scoring)
2. Support rule-based and ML-based fraud detection
3. Maintain user behavior profiles
4. Handle false positive management
5. Support manual review workflow
6. Generate alerts and reports

**Non-Functional Requirements:**
1. Process 50,000+ transactions per second
2. P99 latency < 50ms for fraud scoring
3. High availability (99.99%)
4. Support model updates without downtime
5. Audit trail for all decisions

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Data Ingestion Layer                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│   │ Transaction  │    │ Card Network │    │ Third-Party  │                  │
│   │ API          │    │ Feed         │    │ Data Feeds   │                  │
│   └──────┬───────┘    └──────┬───────┘    └──────┬───────┘                  │
│          │                   │                   │                          │
│          └───────────────────┼───────────────────┘                          │
│                              │                                              │
│                    ┌─────────▼─────────┐                                    │
│                    │   Apache Kafka    │                                    │
│                    │   (Event Stream)  │                                    │
│                    └─────────┬─────────┘                                    │
│                              │                                              │
└──────────────────────────────┼──────────────────────────────────────────────┘
                               │
┌──────────────────────────────┼──────────────────────────────────────────────┐
│                              │     Real-Time Processing Layer               │
├──────────────────────────────┼──────────────────────────────────────────────┤
│                              │                                              │
│          ┌───────────────────┼───────────────────┐                          │
│          │                   │                   │                          │
│   ┌──────▼──────┐     ┌──────▼──────┐     ┌──────▼──────┐                   │
│   │ Feature     │     │ Rule        │     │ ML Model    │                   │
│   │ Engineering │     │ Engine      │     │ Service     │                   │
│   └──────┬──────┘     └──────┬──────┘     └──────┬──────┘                   │
│          │                   │                   │                          │
│          │            ┌──────▼──────┐            │                          │
│          │            │ Decision    │◄───────────┘                          │
│          └───────────►│ Aggregator  │                                       │
│                       └──────┬──────┘                                       │
│                              │                                              │
└──────────────────────────────┼──────────────────────────────────────────────┘
                               │
┌──────────────────────────────┼──────────────────────────────────────────────┐
│                              │     Data Storage Layer                       │
├──────────────────────────────┼──────────────────────────────────────────────┤
│                              │                                              │
│   ┌──────────────┐    ┌──────▼──────┐    ┌──────────────┐                   │
│   │ Feature      │    │ Transaction │    │ Time-Series  │                   │
│   │ Store        │    │ Database    │    │ Database     │                   │
│   │ (Redis)      │    │ (PostgreSQL)│    │ (InfluxDB)   │                   │
│   └──────────────┘    └─────────────┘    └──────────────┘                   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Component Deep Dive

### 1. Feature Engineering Service

Real-time feature computation is critical for fraud detection. Features fall into several categories:

**Transaction Features:**
```python
class TransactionFeatures:
    """Features derived from the current transaction."""
    
    @staticmethod
    def extract(txn: Transaction) -> Dict[str, float]:
        return {
            "amount": txn.amount,
            "amount_log": math.log1p(txn.amount),
            "is_round_amount": 1.0 if txn.amount % 100 == 0 else 0.0,
            "hour_of_day": txn.timestamp.hour,
            "day_of_week": txn.timestamp.weekday(),
            "is_weekend": 1.0 if txn.timestamp.weekday() >= 5 else 0.0,
            "is_night": 1.0 if txn.timestamp.hour < 6 or txn.timestamp.hour > 22 else 0.0,
            "merchant_category_code": float(txn.mcc),
            "is_card_present": 1.0 if txn.entry_mode == "chip" else 0.0,
            "is_international": 1.0 if txn.country != txn.card_country else 0.0,
        }
```

**Aggregated Features (from Feature Store):**
```python
class AggregatedFeatures:
    """Pre-computed features from historical data."""
    
    def __init__(self, feature_store: FeatureStore):
        self.store = feature_store
    
    def get_features(self, account_id: str, merchant_id: str) -> Dict[str, float]:
        # Account-level features
        account_features = self.store.get(f"account:{account_id}")
        
        # Merchant-level features
        merchant_features = self.store.get(f"merchant:{merchant_id}")
        
        return {
            # Velocity features
            "txn_count_1h": account_features.get("txn_count_1h", 0),
            "txn_count_24h": account_features.get("txn_count_24h", 0),
            "txn_count_7d": account_features.get("txn_count_7d", 0),
            "amount_sum_1h": account_features.get("amount_sum_1h", 0),
            "amount_sum_24h": account_features.get("amount_sum_24h", 0),
            
            # Behavioral features
            "avg_txn_amount_30d": account_features.get("avg_amount_30d", 0),
            "std_txn_amount_30d": account_features.get("std_amount_30d", 0),
            "unique_merchants_30d": account_features.get("unique_merchants_30d", 0),
            "most_common_mcc": account_features.get("most_common_mcc", 0),
            
            # Merchant features
            "merchant_fraud_rate": merchant_features.get("fraud_rate", 0),
            "merchant_avg_amount": merchant_features.get("avg_amount", 0),
            "merchant_txn_count_1h": merchant_features.get("txn_count_1h", 0),
            
            # Derived features
            "amount_vs_avg_ratio": self._safe_divide(
                account_features.get("current_amount", 0),
                account_features.get("avg_amount_30d", 1)
            ),
            "time_since_last_txn": account_features.get("time_since_last", 0),
        }
    
    def _safe_divide(self, a: float, b: float) -> float:
        return a / b if b != 0 else 0
```

**Feature Store Architecture:**
```python
class FeatureStore:
    """
    Redis-based feature store with sliding window aggregations.
    
    Uses Redis Sorted Sets for time-windowed aggregations.
    """
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.windows = {
            "1h": 3600,
            "24h": 86400,
            "7d": 604800,
            "30d": 2592000,
        }
    
    def update_features(self, account_id: str, txn: Transaction):
        """Update features after a transaction."""
        now = time.time()
        
        # Add to sorted set (score = timestamp)
        self.redis.zadd(
            f"txns:{account_id}",
            {txn.id: now}
        )
        
        # Update amount sum
        self.redis.hincrbyfloat(
            f"amounts:{account_id}",
            "total",
            txn.amount
        )
        
        # Update merchant set
        self.redis.sadd(
            f"merchants:{account_id}",
            txn.merchant_id
        )
        
        # Cleanup old entries (async)
        self._cleanup_old_entries(account_id, now)
    
    def get_velocity_features(self, account_id: str) -> Dict[str, int]:
        """Get transaction counts for different windows."""
        now = time.time()
        features = {}
        
        for window_name, window_seconds in self.windows.items():
            count = self.redis.zcount(
                f"txns:{account_id}",
                now - window_seconds,
                now
            )
            features[f"txn_count_{window_name}"] = count
        
        return features
```

### 2. Rule Engine

The rule engine provides interpretable, fast fraud detection:

```python
from dataclasses import dataclass
from typing import Callable, List
from enum import Enum


class RuleAction(Enum):
    APPROVE = "approve"
    DECLINE = "decline"
    REVIEW = "review"
    SCORE = "score"


@dataclass
class Rule:
    name: str
    condition: Callable[[Transaction, Dict], bool]
    action: RuleAction
    score: int = 0
    priority: int = 0
    enabled: bool = True


class RuleEngine:
    """
    Configurable rule engine for fraud detection.
    
    Rules are evaluated in priority order. First matching
    DECLINE or APPROVE rule wins. SCORE rules accumulate.
    """
    
    def __init__(self):
        self.rules: List[Rule] = []
        self._load_rules()
    
    def _load_rules(self):
        """Load rules from configuration."""
        self.rules = [
            # Hard decline rules (highest priority)
            Rule(
                name="blocked_merchant",
                condition=lambda t, f: t.merchant_id in self.blocked_merchants,
                action=RuleAction.DECLINE,
                priority=100
            ),
            Rule(
                name="blocked_country",
                condition=lambda t, f: t.country in self.blocked_countries,
                action=RuleAction.DECLINE,
                priority=100
            ),
            Rule(
                name="card_reported_stolen",
                condition=lambda t, f: f.get("card_status") == "stolen",
                action=RuleAction.DECLINE,
                priority=100
            ),
            
            # Velocity rules
            Rule(
                name="high_velocity_1h",
                condition=lambda t, f: f.get("txn_count_1h", 0) > 10,
                action=RuleAction.SCORE,
                score=40,
                priority=50
            ),
            Rule(
                name="high_amount_velocity",
                condition=lambda t, f: f.get("amount_sum_1h", 0) > 5000,
                action=RuleAction.SCORE,
                score=30,
                priority=50
            ),
            
            # Behavioral anomaly rules
            Rule(
                name="unusual_amount",
                condition=lambda t, f: (
                    t.amount > f.get("avg_txn_amount_30d", 0) * 5
                    and f.get("avg_txn_amount_30d", 0) > 0
                ),
                action=RuleAction.SCORE,
                score=25,
                priority=40
            ),
            Rule(
                name="new_merchant_high_amount",
                condition=lambda t, f: (
                    f.get("merchant_first_seen", 0) == 0
                    and t.amount > 500
                ),
                action=RuleAction.SCORE,
                score=20,
                priority=40
            ),
            
            # Geographic rules
            Rule(
                name="impossible_travel",
                condition=lambda t, f: f.get("travel_speed_mph", 0) > 500,
                action=RuleAction.SCORE,
                score=60,
                priority=60
            ),
            Rule(
                name="high_risk_country",
                condition=lambda t, f: t.country in self.high_risk_countries,
                action=RuleAction.SCORE,
                score=15,
                priority=30
            ),
        ]
    
    def evaluate(self, txn: Transaction, features: Dict) -> RuleResult:
        """Evaluate all rules and return result."""
        total_score = 0
        triggered_rules = []
        
        # Sort by priority (highest first)
        sorted_rules = sorted(
            [r for r in self.rules if r.enabled],
            key=lambda r: -r.priority
        )
        
        for rule in sorted_rules:
            try:
                if rule.condition(txn, features):
                    triggered_rules.append(rule.name)
                    
                    if rule.action == RuleAction.DECLINE:
                        return RuleResult(
                            decision="DECLINE",
                            score=100,
                            triggered_rules=triggered_rules,
                            reason=f"Rule: {rule.name}"
                        )
                    
                    if rule.action == RuleAction.APPROVE:
                        return RuleResult(
                            decision="APPROVE",
                            score=0,
                            triggered_rules=triggered_rules,
                            reason=f"Rule: {rule.name}"
                        )
                    
                    if rule.action == RuleAction.SCORE:
                        total_score += rule.score
                        
            except Exception as e:
                # Log but don't fail on rule errors
                logger.error(f"Rule {rule.name} failed: {e}")
        
        # Determine decision based on accumulated score
        if total_score >= 70:
            decision = "DECLINE"
        elif total_score >= 40:
            decision = "REVIEW"
        else:
            decision = "APPROVE"
        
        return RuleResult(
            decision=decision,
            score=total_score,
            triggered_rules=triggered_rules,
            reason=f"Score: {total_score}"
        )
```

### 3. ML Model Service

```python
class MLModelService:
    """
    ML model serving with A/B testing and shadow mode support.
    """
    
    def __init__(self):
        self.models = {}
        self.model_weights = {}
        self.shadow_models = {}
        self._load_models()
    
    def _load_models(self):
        """Load models from model registry."""
        # Production models
        self.models = {
            "xgboost_v3": self._load_model("xgboost_v3"),
            "neural_v2": self._load_model("neural_v2"),
        }
        
        # Model weights for ensemble
        self.model_weights = {
            "xgboost_v3": 0.6,
            "neural_v2": 0.4,
        }
        
        # Shadow models (for evaluation, not used in decisions)
        self.shadow_models = {
            "xgboost_v4_candidate": self._load_model("xgboost_v4_candidate"),
        }
    
    def predict(self, features: Dict) -> MLPrediction:
        """Get fraud probability from model ensemble."""
        feature_vector = self._prepare_features(features)
        
        # Get predictions from all models
        predictions = {}
        for name, model in self.models.items():
            predictions[name] = model.predict_proba(feature_vector)[0][1]
        
        # Weighted ensemble
        ensemble_score = sum(
            predictions[name] * self.model_weights[name]
            for name in predictions
        )
        
        # Run shadow models (async, for monitoring)
        self._run_shadow_models(feature_vector, features)
        
        return MLPrediction(
            fraud_probability=ensemble_score,
            model_scores=predictions,
            feature_importance=self._get_feature_importance(feature_vector)
        )
    
    def _prepare_features(self, features: Dict) -> np.ndarray:
        """Convert feature dict to model input format."""
        # Ensure consistent feature ordering
        feature_names = self._get_feature_names()
        return np.array([features.get(f, 0) for f in feature_names]).reshape(1, -1)
    
    def _get_feature_importance(self, feature_vector: np.ndarray) -> Dict[str, float]:
        """Get SHAP values for explainability."""
        # Use SHAP for model explainability
        explainer = shap.TreeExplainer(self.models["xgboost_v3"])
        shap_values = explainer.shap_values(feature_vector)
        
        feature_names = self._get_feature_names()
        return dict(zip(feature_names, shap_values[0]))
```

### 4. Decision Aggregator

```python
class DecisionAggregator:
    """
    Combines rule engine and ML model outputs into final decision.
    """
    
    def __init__(self, config: DecisionConfig):
        self.config = config
    
    def aggregate(
        self,
        rule_result: RuleResult,
        ml_prediction: MLPrediction
    ) -> FraudDecision:
        """Combine rule and ML results."""
        
        # Hard rules always win
        if rule_result.decision == "DECLINE" and rule_result.score >= 100:
            return FraudDecision(
                decision="DECLINE",
                confidence=1.0,
                reason=rule_result.reason,
                requires_review=False
            )
        
        # Combine scores
        combined_score = (
            self.config.rule_weight * (rule_result.score / 100) +
            self.config.ml_weight * ml_prediction.fraud_probability
        )
        
        # Apply thresholds
        if combined_score >= self.config.decline_threshold:
            decision = "DECLINE"
            requires_review = False
        elif combined_score >= self.config.review_threshold:
            decision = "REVIEW"
            requires_review = True
        else:
            decision = "APPROVE"
            requires_review = False
        
        return FraudDecision(
            decision=decision,
            confidence=combined_score,
            reason=self._build_reason(rule_result, ml_prediction),
            requires_review=requires_review,
            rule_score=rule_result.score,
            ml_score=ml_prediction.fraud_probability,
            triggered_rules=rule_result.triggered_rules,
            feature_importance=ml_prediction.feature_importance
        )
```

## Streaming Architecture with Kafka

```python
class FraudDetectionPipeline:
    """
    Kafka Streams-based fraud detection pipeline.
    """
    
    def __init__(self):
        self.consumer = KafkaConsumer(
            'transactions',
            bootstrap_servers=['kafka:9092'],
            group_id='fraud-detection',
            auto_offset_reset='latest'
        )
        self.producer = KafkaProducer(
            bootstrap_servers=['kafka:9092']
        )
        
        self.feature_service = FeatureEngineeringService()
        self.rule_engine = RuleEngine()
        self.ml_service = MLModelService()
        self.aggregator = DecisionAggregator()
    
    def process(self):
        """Main processing loop."""
        for message in self.consumer:
            try:
                txn = Transaction.from_json(message.value)
                
                # Extract features
                features = self.feature_service.get_features(txn)
                
                # Run rule engine
                rule_result = self.rule_engine.evaluate(txn, features)
                
                # Run ML model
                ml_prediction = self.ml_service.predict(features)
                
                # Aggregate decision
                decision = self.aggregator.aggregate(rule_result, ml_prediction)
                
                # Publish decision
                self.producer.send(
                    'fraud-decisions',
                    key=txn.id.encode(),
                    value=decision.to_json().encode()
                )
                
                # Update feature store
                self.feature_service.update_features(txn)
                
                # Log for monitoring
                self._log_decision(txn, decision)
                
            except Exception as e:
                logger.error(f"Error processing transaction: {e}")
                self._handle_error(message, e)
```

## Monitoring and Observability

```python
class FraudMetrics:
    """Prometheus metrics for fraud detection system."""
    
    def __init__(self):
        self.decision_counter = Counter(
            'fraud_decisions_total',
            'Total fraud decisions',
            ['decision', 'model_version']
        )
        
        self.latency_histogram = Histogram(
            'fraud_detection_latency_seconds',
            'Fraud detection latency',
            buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5]
        )
        
        self.score_histogram = Histogram(
            'fraud_score',
            'Distribution of fraud scores',
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        )
        
        self.false_positive_rate = Gauge(
            'fraud_false_positive_rate',
            'Current false positive rate'
        )
    
    def record_decision(self, decision: FraudDecision, latency: float):
        self.decision_counter.labels(
            decision=decision.decision,
            model_version=decision.model_version
        ).inc()
        
        self.latency_histogram.observe(latency)
        self.score_histogram.observe(decision.confidence)
```

## Interview Discussion Points

1. **How do you handle model updates without downtime?**
   - Blue-green deployment for models
   - Shadow mode testing before promotion
   - Feature flag-based rollout

2. **How do you handle cold start for new users?**
   - Population-level features as fallback
   - Stricter rules for new accounts
   - Gradual trust building

3. **How do you balance precision vs recall?**
   - Business-driven threshold tuning
   - Different thresholds for different transaction types
   - Cost-sensitive learning

4. **How do you handle adversarial attacks?**
   - Feature drift detection
   - Anomaly detection on feature distributions
   - Regular model retraining

5. **How do you ensure explainability?**
   - SHAP values for feature importance
   - Rule-based explanations
   - Audit trail for all decisions
