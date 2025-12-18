# Capital One Interview Coding Samples - C#

This is a C# conversion of the Python coding samples, following SOLID design principles and Test-Driven Development (TDD).

## Project Structure

```
coding-samples-csharp/
├── CodingSamples.sln
├── src/
│   └── CodingSamples.Core/
│       ├── TransactionAnalysis/     # Suspicious account detection
│       ├── RateLimiting/            # Rate limiter implementations
│       ├── AccountMerging/          # Union-Find and DFS account merging
│       ├── Caching/                 # LRU and LFU cache implementations
│       ├── CreditCardValidation/    # Credit card validation (Luhn, etc.)
│       └── GraphProblems/           # Graph algorithms and fraud detection
└── tests/
    └── CodingSamples.Tests/
        ├── TransactionAnalysis/
        ├── RateLimiting/
        ├── AccountMerging/
        ├── Caching/
        ├── CreditCardValidation/
        └── GraphProblems/
```

## SOLID Design Principles Applied

### Single Responsibility Principle (SRP)
- Each class has a single responsibility (e.g., `LuhnValidator` only validates Luhn checksums)
- Rules for suspicious activity detection are separate classes (`HighVelocityRule`, `HighAmountRule`, `MultipleCitiesRule`)

### Open/Closed Principle (OCP)
- `SuspiciousAccountDetector` accepts a collection of `ISuspiciousActivityRule` - new rules can be added without modifying existing code
- Rate limiters implement `IRateLimiter` interface - new strategies can be added easily

### Liskov Substitution Principle (LSP)
- All rate limiter implementations can be used interchangeably through `IRateLimiter`
- Both `UnionFindAccountMerger` and `DfsAccountMerger` implement `IAccountMerger`

### Interface Segregation Principle (ISP)
- Small, focused interfaces (e.g., `ILuhnValidator`, `ICardTypeIdentifier`, `ICvvValidator`)
- Clients depend only on the interfaces they need

### Dependency Inversion Principle (DIP)
- High-level modules depend on abstractions (interfaces)
- `CreditCardValidator` depends on `ILuhnValidator`, `ICardTypeIdentifier`, etc.
- Time providers are injected for testability

## Running Tests

```bash
# Run all tests
dotnet test

# Run tests with verbose output
dotnet test --verbosity normal

# Run specific test class
dotnet test --filter "FullyQualifiedName~TransactionAnalysisTests"
```

## Modules

### 1. Transaction Analysis
Detects suspicious accounts based on:
- High velocity (>3 transactions in 60 seconds)
- High amount (>$10,000 in 60 seconds)
- Multiple cities (>2 cities in 10 minutes)

### 2. Rate Limiting
Four rate limiting strategies:
- Sliding Window Rate Limiter
- Token Bucket Rate Limiter
- Leaky Bucket Rate Limiter
- Fixed Window Rate Limiter

### 3. Account Merging
Merges accounts that share emails using:
- Union-Find (Disjoint Set Union) with path compression
- DFS-based approach

### 4. Caching
Cache implementations:
- LRU Cache (Least Recently Used)
- LFU Cache (Least Frequently Used)

### 5. Credit Card Validation
- Luhn algorithm checksum validation
- Card type identification (Visa, Mastercard, Amex, Discover)
- Expiry date validation
- CVV validation
- Card number masking

### 6. Graph Problems
- BFS and DFS traversal
- Dijkstra's shortest path
- Cycle detection
- Topological sort
- Fraud ring detection (Tarjan's SCC algorithm)
- Transaction path finding
- PageRank calculation

## Requirements

- .NET 8.0 SDK
