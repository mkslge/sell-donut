---
name: donutsmp-discord-review-ingest
description: Process scraped DonutSMP Discord messages and upload verified scam reports or legit vouches relevant to the website through POST /rating/{username}. Use when given scraped Discord messages that may contain Minecraft usernames and rating claims.
---

# DonutSMP Discord Review Ingest

Use this skill when handling scraped Discord messages for DonutSMP seller reviews.

## Goal

Only turn a message into a backend rating when all of these are true:

1. The message clearly describes a scam or a legit vouch.
2. The message contains a Minecraft username.
3. The message is about a trade, sale, or seller interaction that fits the website's rating context.
4. The message is a real report, not a rumor, joke, or discussion.

If any condition is missing, do not upload it.

If all conditions are met, upload it immediately through the backend API.

## Ignore

- Messages without a username
- Messages that do not clearly say scam or legit vouch
- Messages that are not about a trade, sale, or seller interaction

## Extraction Rules

- Use the Minecraft username from the message as the path parameter.
- Keep the username as written in the message unless a canonical version is known from the source.
- Prefer a short, factual summary of the rating in `reviewText`.
- For legit vouches, keep the same extraction rules and set `outcome` to `LEGIT`.
- Include evidence links or screenshots in `evidenceUrl` when present.
- Do not invent details that are not in the message.
- Deduplicate before uploading. Use message id, URL, or a stable hash if available.
- If the backend rejects a payload for length or validation, retry once with a shorter,
  tighter summary before skipping it.

## Upload

Send accepted reports to:

`POST /rating/{username}`

Map the payload like this:

- `outcome`: `SCAMMER` for scam reports, `LEGIT` for confirmed positive vouches
- `tradeCategory`: short category that matches the trade, such as `spawners`, `money`, `gear`, or `other`
- `tradeDescription`: short, factual phrase describing the transaction
- `reviewText`: concise summary from the message
- `evidenceUrl`: optional source link
- `reporterUsername`: optional scraper or reporter name if known
- `quantity`, `price`, `currency`: only when the message states them clearly

Do not write to the database directly.

If you are processing a batch of scraped messages, post each accepted report as
you find it. Do not wait for manual confirmation unless the user explicitly
asks for a review-only pass.

## Gate Before Upload

Before posting, verify:

- the username is present
- the rating claim is explicit
- the report is tied to a trade or seller interaction
- the report is not already uploaded
- the payload is factual and minimal
- Make sure you shorted the message so it doesnt get blocked by the reporter field limit
- If a field is too long, shorten `reviewText` first into one factual sentence.
- If it still fails, drop optional fields such as `reporterUsername` or `evidenceUrl`
  before giving up.
- Never invent a replacement reporter name just to satisfy the length check.

If the report fails any check, skip it.

## Default Action

When a scraped message passes the gate, the agent should:

1. extract the seller username
2. build the payload
3. `POST /rating/{username}`
4. record that the report was submitted
5. DO NOT CALL THEM "BATCH UPLOAD", you can mentioned they were ported from discord


## Example command:
curl -sS -X POST 'http://127.0.0.1:8000/rating/nanula2511' -H 'Content-Type: application/json' -H
  │ 'x-forwarded-for: 198.51.101.20' --data-raw '{"outcome":"LEGIT","tradeCategory":"OTHER","tradeDescription":"Base sale
  │ vouch","reporterUsername":"NichtLuis1","reviewText":"NichtLuis1 vouched nanula2511 for selling a base for 100m; the

Do not keep accepted reports in a pending state unless the user explicitly asks
for staging or review mode.
