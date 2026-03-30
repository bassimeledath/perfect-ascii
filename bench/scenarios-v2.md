# Benchmark Scenarios v2 — Generalization Test

Fresh scenarios to test whether the skill + CLI generalize beyond the original benchmarks. Different topologies, patterns, and visual structures.

---

## Scenario 1: Gantt Chart

Draw a project timeline for a 12-week software launch:
- Week 1-3: "Requirements" (team: PM)
- Week 2-5: "Design" (team: UX)
- Week 4-8: "Backend Dev" (team: Eng)
- Week 4-7: "Frontend Dev" (team: Eng)
- Week 6-9: "Integration" (team: Eng)
- Week 8-10: "QA Testing" (team: QA)
- Week 9-11: "Beta Release" (team: Ops)
- Week 11-12: "Launch Prep" (team: PM)
- Week 12: "Launch" (milestone)

Show tasks as horizontal bars with week markers across the top. Overlapping tasks should be on separate rows. Include team labels on the left.

---

## Scenario 2: Binary Tree

Draw a complete binary search tree containing these values (pre-sorted for BST insertion):
50, 25, 75, 12, 37, 62, 87, 6, 18, 31, 43, 56, 68, 81, 93

4 levels deep (root + 3 levels). Each node is a box with the number. Connect parent to children with lines that branch left and right. Left child should be to the left, right child to the right. Include branch lines using / and \ or elbow connectors.

Requirements: symmetric layout, all nodes at the same level should be at the same vertical position, connector lines should not cross.

---

## Scenario 3: Network Packet Diagram

Draw an IPv4 packet header layout showing byte offsets:

```
Offset  0       4       8      12      16      20      24      28     32
        +-------+-------+------+-------+-------+-------+-------+------+
  0     |Version| IHL   | DSCP |  ECN  |         Total Length          |
        +-------+-------+------+-------+-------------------------------+
  4     |         Identification        | Flags |    Fragment Offset    |
        +-------------------------------+-------+-----------------------+
  8     |    TTL        |   Protocol    |       Header Checksum         |
        +---------------+---------------+-------------------------------+
 12     |                       Source IP Address                       |
        +--------------------------------------------------------------+
 16     |                    Destination IP Address                     |
        +--------------------------------------------------------------+
```

Requirements: bit-level column alignment (32 bits = full width), fields span correct number of bit-columns, byte offset labels on the left.

---

## Scenario 4: Git Branch Graph

Draw a git branch history:
- main: commits M1 → M2 → M3 → M4 → M5 → M6 → M7
- feature/auth: branches from M2, commits A1 → A2 → A3, merges into M5
- feature/ui: branches from M3, commits U1 → U2, merges into M7
- hotfix/bug: branches from M4, commit H1, merges into M5 (before auth merge)

Show branches as horizontal lanes with commit dots/circles. Branch-off and merge points should be clearly marked with connecting lines. Label each branch on the left. Time flows left to right.

---

## Scenario 5: Feature Comparison Matrix

Draw a comparison table for 5 cloud providers across 12 features:

Providers: AWS, GCP, Azure, DigitalOcean, Heroku

Features and ratings:
- Compute (VMs): AWS=5, GCP=5, Azure=5, DO=3, Heroku=1
- Containers: AWS=5, GCP=5, Azure=4, DO=4, Heroku=3
- Serverless: AWS=5, GCP=4, Azure=4, DO=1, Heroku=2
- Object Storage: AWS=5, GCP=5, Azure=5, DO=4, Heroku=1
- SQL Database: AWS=5, GCP=4, Azure=5, DO=3, Heroku=4
- NoSQL: AWS=5, GCP=5, Azure=4, DO=1, Heroku=1
- CDN: AWS=4, GCP=4, Azure=4, DO=2, Heroku=0
- ML/AI: AWS=5, GCP=5, Azure=5, DO=0, Heroku=0
- CI/CD: AWS=3, GCP=4, Azure=5, DO=0, Heroku=3
- Monitoring: AWS=4, GCP=4, Azure=4, DO=2, Heroku=2
- Pricing: AWS=2, GCP=3, Azure=2, DO=5, Heroku=3
- Ease of Use: AWS=2, GCP=3, Azure=2, DO=5, Heroku=5

Use symbols: 5=★★★★★, 4=★★★★, 3=★★★, 2=★★, 1=★, 0=- (or use numeric scale if stars don't render in monospace). Include a total score row at the bottom.

---

## Scenario 6: Data Pipeline / ETL Flow

Draw a left-to-right data pipeline:

Sources (left):
- "PostgreSQL" (database icon/label)
- "S3 Bucket" (storage)
- "Kafka Stream" (streaming)

Transform stage (middle):
- All three sources feed into "Apache Spark" (processing)
- Spark outputs to "dbt Transform"
- dbt has a validation step: "Data Quality Check" diamond/decision
  - Pass → continues
  - Fail → "Alert + Dead Letter Queue"

Load targets (right):
- "Snowflake DW" (main warehouse)
- "Redis Cache" (hot data)
- "Tableau" (reporting)

Show data flow left-to-right with labeled arrows indicating data type (e.g., "raw events", "cleaned data", "aggregated metrics"). Include a "Schedule: Every 6h" annotation at the top.

Requirements: clear left-to-right flow, sources grouped on left, transforms in center, targets on right. No overlapping connectors.
