

## DESIGN

The project should be a React TS Frontend using ShadCN Components, and the backend should be Python FastAPI, with the Database being a sqllite DB

## Project Overview

Build a seller rating system for DonutSMP trades. The app helps players check whether a seller is trustworthy before buying spawners, items, or other in-game goods.

The system should start small but be designed to scale. The first version needs three core API endpoints:

1. `POST /rating/{username}`
2. `GET /rating/{username}`
3. `GET /rating/{username}/summary`

The app should store individual trade ratings and expose seller reputation data.

---

## Product Requirements

### Core Concept

A user can submit a rating for a Minecraft seller. A rating records whether the seller was legit or a scammer, what was sold, and optional context about the trade.

The system should support multiple ratings per seller.

A seller should not be represented by only one boolean value. Reputation should be calculated from all submitted ratings.

---

## Data Model

Use a scalable model similar to this:

```ts
Rating {
  id: string
  sellerUsername: string
  verdict: "LEGIT" | "SCAMMER"
  itemType: string
  itemName?: string
  quantity?: number
  price?: number
  currency?: string
  description?: string
  evidenceUrl?: string
  reporterUsername?: string
  createdAt: Date
  updatedAt: Date
}

User {
  uuid: string //this should be the sellers minecraft uuid, so we can id people who change names, so the flow for rating someone would be somehow checking what uuid the persons username corresponds to, and mapping the rating to that account
  sellerUsername: string
  scamCount: number
  legitCount: number
}
```



Do not hardcode this only for spawners. Spawners should be one possible `itemType`, not the whole system.

Suggested `itemType` examples:

```ts
"SPAWNER"
"ITEM"
"MONEY"
"SERVICE"
"OTHER"
```

---

## API Endpoints

### `POST /rating/{username}`

Create a new rating for a seller.

Path parameter:

```ts
username: string
```

Request body:

```json
{
  "verdict": "LEGIT",
  "itemType": "SPAWNER",
  "itemName": "Blaze Spawner",
  "quantity": 2,
  "price": 5000000,
  "currency": "DOLLARS",
  "description": "Seller delivered after payment.",
  "evidenceUrl": "https://example.com/screenshot.png",
  "reporterUsername": "Mark"
}
```

Validation rules:

* `username` is required.
* `verdict` must be either `LEGIT` or `SCAMMER`.
* `itemType` is required.
* `description` is optional but recommended.
* `price`, `quantity`, and `evidenceUrl` are optional.
* Normalize usernames consistently, preferably lowercase for lookup while preserving display casing if needed.

Response:

```json
{
  "id": "rating_id",
  "sellerUsername": "someSeller",
  "verdict": "LEGIT",
  "itemType": "SPAWNER",
  "itemName": "Blaze Spawner",
  "quantity": 2,
  "price": 5000000,
  "currency": "DOLLARS",
  "description": "Seller delivered after payment.",
  "evidenceUrl": "https://example.com/screenshot.png",
  "reporterUsername": "Mark",
  "createdAt": "2026-05-30T00:00:00Z"
}
```

---

### `GET /rating/{username}`

Return all ratings for a seller.

Response:

```json
{
  "sellerUsername": "someSeller",
  "ratings": [
    {
      "id": "rating_id",
      "verdict": "LEGIT",
      "itemType": "SPAWNER",
      "itemName": "Blaze Spawner",
      "quantity": 2,
      "price": 5000000,
      "currency": "DOLLARS",
      "description": "Seller delivered after payment.",
      "evidenceUrl": "https://example.com/screenshot.png",
      "reporterUsername": "Mark",
      "createdAt": "2026-05-30T00:00:00Z"
    }
  ]
}
```

Return an empty array if the seller has no ratings.

---

### `GET /rating/{username}/summary`

Return reputation summary for a seller.

Response:

```json
{
  "sellerUsername": "someSeller",
  "totalRatings": 10,
  "legitCount": 8,
  "scammerCount": 2,
  "legitPercentage": 80,
  "reputation": "MOSTLY_LEGIT"
}
```

Suggested reputation labels:

```ts
"NO_DATA"
"LEGIT"
"MOSTLY_LEGIT"
"MIXED"
"RISKY"
"SCAMMER"
```

Keep the calculation simple for now, but isolate it in its own service/function so it can be changed later.

---

## Engineering Requirements

### Architecture

Use clean separation of concerns:

```txt
routes/controllers -> services -> repositories/database
```

Do not put database logic directly inside route handlers.

Recommended structure:

```txt
src/
  routes/
  controllers/
  services/
  repositories/
  models/
  validators/
  utils/
```

### Validation

Validate all request bodies before saving data.

Reject invalid ratings with clear `400 Bad Request` responses.

Example error:

```json
{
  "error": "Invalid verdict. Must be LEGIT or SCAMMER."
}
```

### Error Handling

Use consistent error responses.

Examples:

```json
{
  "error": "Seller username is required."
}
```

```json
{
  "error": "Internal server error."
}
```

Do not leak stack traces in API responses.

### Storage

Start with whichever storage layer is already configured in the project.

If no database exists yet, implement an in-memory repository first, but design the repository interface so it can be swapped for PostgreSQL, MongoDB, or another database later.

The repository should expose methods like:

```ts
createRating(rating)
getRatingsBySeller(username)
getSellerSummary(username)
```

### Testing

Add tests for:

* Creating a legit rating
* Creating a scammer rating
* Rejecting invalid verdicts
* Getting ratings for a seller
* Getting an empty rating list for an unknown seller
* Calculating seller summary correctly

### Code Style

Prioritize readable, simple code.

Avoid premature complexity.

Use explicit names like `sellerUsername`, `reporterUsername`, `verdict`, and `itemType`.

Do not use vague names like `data`, `thing`, `status`, or `value` when a more specific name exists.

---

## Future Scalability

Design the app so these features can be added later:

* User authentication
* Duplicate report prevention
* Evidence uploads
* Admin moderation
* Rating comments
* Seller search
* Item-specific reputation
* Discord bot integration
* DonutSMP leaderboard/risk list

Do not implement these yet unless specifically asked.

---

## Important Behavior

When implementing, prefer the smallest complete version that works.

Do not invent unnecessary features.

Do not hardcode DonutSMP-specific item names into the backend.

Do not assume every trade is about spawners.

Treat this as a reputation platform for Minecraft marketplace trades.
