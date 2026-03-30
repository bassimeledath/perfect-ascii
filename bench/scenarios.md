# Benchmark Scenarios

Each scenario describes a diagram to generate. The tester must follow the current SKILL.md to produce each one, then visually validate alignment.

---

## Scenario 1: Multi-branch flowchart

Draw a flowchart for a user login system:
- Start node
- "Enter credentials" process box
- "Valid?" diamond decision
- If yes: "Check 2FA enabled?" diamond
  - If yes: "Send 2FA code" process -> "Verify code" process -> "Code valid?" diamond -> success or "Retry (max 3)" loop back
  - If no: "Grant access" terminal
- If no from "Valid?": "Increment attempts" process -> "Attempts >= 3?" diamond
  - If yes: "Lock account" terminal
  - If no: loop back to "Enter credentials"

Requirements: at least 10 boxes/diamonds, clear arrow labels (yes/no), no overlapping lines.

---

## Scenario 2: Sequence diagram with 4 actors

Draw a sequence diagram for an e-commerce checkout:
- Actors: User, Frontend, API Server, Payment Gateway, Database
- Flow:
  1. User -> Frontend: Click checkout
  2. Frontend -> API Server: POST /checkout
  3. API Server -> Database: Validate cart
  4. Database --> API Server: Cart valid
  5. API Server -> Payment Gateway: Charge card
  6. Payment Gateway --> API Server: Payment approved
  7. API Server -> Database: Create order
  8. Database --> API Server: Order #12345
  9. API Server --> Frontend: Order confirmation
  10. Frontend --> User: Show receipt
- Include a note box between steps 5-6: "Timeout after 30s"
- Use solid arrows (->) for requests, dashed arrows (-->) for responses

Requirements: actors spaced evenly, lifelines perfectly vertical, all arrows aligned to their source/destination lifelines.

---

## Scenario 3: Entity-relationship diagram

Draw an ER diagram for a school system with these entities:
- Student (id, name, email, enrollment_date)
- Course (id, title, credits, department)
- Professor (id, name, email, office)
- Enrollment (student_id, course_id, grade, semester)
- Department (id, name, building)

Relationships:
- Student --< Enrollment >-- Course (many-to-many through Enrollment)
- Professor --< Course (one-to-many: professor teaches courses)
- Department --< Professor (one-to-many)
- Department --< Course (one-to-many)

Requirements: entities as labeled boxes with attribute lists, relationship lines with cardinality markers (1, N, M), no crossing lines if possible.

---

## Scenario 4: Layered architecture diagram

Draw a 4-layer architecture diagram:

Layer 1 (top) - "Presentation Layer":
  Three boxes side by side: "Web App", "Mobile App", "CLI Tool"

Layer 2 - "API Gateway Layer":
  One wide box: "API Gateway / Load Balancer"

Layer 3 - "Service Layer":
  Four boxes side by side: "Auth Service", "Order Service", "Inventory Service", "Notification Service"

Layer 4 (bottom) - "Data Layer":
  Three boxes: "PostgreSQL", "Redis Cache", "S3 Storage"

Requirements: each layer labeled on the left, boxes within a layer horizontally aligned, vertical connectors between layers, all boxes in a layer have the same height.

---

## Scenario 5: State machine diagram

Draw a state machine for a TCP connection:
- States: CLOSED, LISTEN, SYN_SENT, SYN_RECEIVED, ESTABLISHED, FIN_WAIT_1, FIN_WAIT_2, CLOSE_WAIT, CLOSING, LAST_ACK, TIME_WAIT
- Key transitions:
  - CLOSED -> LISTEN (passive open)
  - CLOSED -> SYN_SENT (active open / send SYN)
  - LISTEN -> SYN_RECEIVED (recv SYN / send SYN+ACK)
  - SYN_SENT -> ESTABLISHED (recv SYN+ACK / send ACK)
  - SYN_RECEIVED -> ESTABLISHED (recv ACK)
  - ESTABLISHED -> FIN_WAIT_1 (close / send FIN)
  - ESTABLISHED -> CLOSE_WAIT (recv FIN / send ACK)
  - FIN_WAIT_1 -> FIN_WAIT_2 (recv ACK)
  - FIN_WAIT_1 -> CLOSING (recv FIN / send ACK)
  - FIN_WAIT_2 -> TIME_WAIT (recv FIN / send ACK)
  - CLOSE_WAIT -> LAST_ACK (close / send FIN)
  - CLOSING -> TIME_WAIT (recv ACK)
  - LAST_ACK -> CLOSED (recv ACK)
  - TIME_WAIT -> CLOSED (timeout)

Requirements: 11 state boxes with labeled transition arrows. States should be laid out to minimize crossing arrows. Each transition arrow must be labeled with its trigger.

---

## Scenario 6: Complex table with nested headers

Draw a table showing quarterly sales data:

```
Region     | Q1 2025          | Q2 2025          | Q3 2025          | Q4 2025          | Annual
           | Rev    | Growth  | Rev    | Growth  | Rev    | Growth  | Rev    | Growth  | Total
-----------+--------+---------+--------+---------+--------+---------+--------+---------+--------
North      | $1.2M  | +12%    | $1.4M  | +15%    | $1.1M  | -8%     | $1.8M  | +22%    | $5.5M
South      | $890K  | +5%     | $920K  | +3%     | $1.0M  | +9%     | $1.1M  | +10%    | $3.9M
East       | $2.1M  | +18%   | $2.3M  | +10%    | $2.0M  | -13%    | $2.8M  | +40%    | $9.2M
West       | $1.5M  | +8%    | $1.6M  | +7%     | $1.7M  | +6%     | $1.9M  | +12%    | $6.7M
-----------+--------+---------+--------+---------+--------+---------+--------+---------+--------
Total      | $5.7M  |         | $6.2M  |         | $5.8M  |         | $7.6M  |         | $25.3M
```

Requirements: all columns perfectly aligned, header spanning works correctly, separator lines align with column boundaries, numbers right-aligned within cells.
