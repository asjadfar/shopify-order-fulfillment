# Shopify Order Fulfilment Skill

A Claude skill for end-to-end Shopify order fulfilment, built from Asjad's real fulfilment work on his live store. Claude handles all the work end to end — order check, WhatsApp confirmation, courier consignment, drop-off, airway bill, packing slip, customer tracking email, and marking the order fulfilled — with the owner involved only for the decisions, accounts/sign-ins/money and approval gates. It is modeled on the live store Fragrance Empire, a complete Shopify store with 155 products, 18 brands, COD + Stripe card payments, and Ninja Van fulfilment across Malaysia.

## What it does

Takes one order from arrival to fulfilled in one repeatable workflow:

1. **Order arrives** — read the order, tell COD from card-paid, flag anything odd before touching it.
2. **WhatsApp confirmation + OTP** — confirmation sent after purchase; unverified orders marked High Risk after 1 hour; no consignment for an unconfirmed COD order.
3. **Courier consignment (Ninja Van)** — Shopify Orders list → select order → Actions → "Create Ninja Van Orders"; verify the COD amount badge before confirming; "Is pickup required?" = No; status becomes Pending Pickup. Creating the consignment does NOT mark the order fulfilled.
4. **Drop-off** — parcel dropped at a Ninja Van point by the shop, confirmed before the checklist moves on.
5. **Airway bill** — PDF downloaded and verified on disk (it is generated asynchronously — a failed download is retried later, never claimed as saved).
6. **Packing slip** — generated in Shopify, checked against the order, saved with the airway bill.
7. **Customer tracking email** — from the store's info@ address, order number in the subject, tracking number + tracking link + 3–5 business days estimate in the body, NO product names or prices. Owner approves the exact text before it is sent.
8. **Mark fulfilled in Shopify** — with the tracking number (`fulfilmentCreate`; `notifyCustomer` false unless the owner approves a notification email). Only after drop-off.

Plus: the operating model (store under the owner's control only, shop staff have NO Shopify access, the owner sends BOTH prints as WhatsApp documents), COD vs card-paid differences, and what to do when a customer does not respond (attempt contact, then cancel in Shopify Admin on the owner's instruction — never by API call).

## Who does what — Claude handles all the work end to end

Claude runs every step — order check, confirmation draft, consignment steps, airway-bill and packing-slip checks, tracking-email draft, fulfilment record. The owner is involved only at three points: (1) decisions only the owner can make (cancel an unresponsive order or keep waiting, approve a fulfilment notification email, any refund or price change); (2) accounts, sign-ins and money (Shopify Admin, courier app, store email mailbox, payments/refunds — all on the owner's own device); and (3) approval gates (tracking email text before it is sent, any cancellation). The three device-bound exceptions are Shopify Admin access (browser with the owner's sign-in, or Admin API with an access token the owner creates), physical parcel handling (the shop packs and drops off; Claude prepares the prints and the handover note), and WhatsApp confirmation (the store's confirmation app sends it; Claude drafts and records). Everything else is Claude's work — do not hand it back to the owner as homework.

## The live example store

- **Store:** Fragrance Empire — https://fragranceempire.my
- **Platform:** Shopify, Basic plan, Horizon theme, currency MYR, timezone Asia/Kuala_Lumpur, market Malaysia
- **Catalog:** 155 products = 142 single products + 13 bundles, 18 brands
- **Payments:** Cash on Delivery (COD) + card payments via Stripe (Visa, Mastercard, Amex, JCB, Discover, Diners, Apple Pay, Google Pay)
- **Shipping:** Standard, FREE, 3–5 business days across Malaysia
- **Fulfilment:** Ninja Van — one consignment per order, parcel dropped off at a Ninja Van point, no pickup
- **Order confirmation:** WhatsApp confirmation + OTP verification; unverified orders marked High Risk after 1 hour
- **Customer email:** from the store's info@ address only
- **Built by:** Asjad Farooq, Shopify Store Designer — Fiverr gig https://www.fiverr.com/s/L34yBpA

## Service tiers (the seller's real packages)

| Tier | Products | Pages | Delivery | Revisions |
|---|---|---|---|---|
| Basic | 10 | 5 | 3 days | Unlimited |
| Standard | 30 | 8 | 5 days | Unlimited |
| Premium | 50 | 10 | 7 days | Unlimited |

Prices: Basic $80, Standard $180, Premium $350. A fulfilment workflow is part of running a store built under any tier — ask the owner which tier the store was built under if that matters for the engagement, and do not promise a bigger scope than the tier covers without agreement.

## Files

```
shopify-order-fulfillment/
├── README.md                                  # this file
└── shopify-order-fulfillment/
    ├── SKILL.md                               # the Claude skill — the workflow itself
    ├── scripts/
    │   └── order_checklist.py                 # per-order checklist tracker + tracking-email generator
    └── templates/
        ├── per-order-checklist.md             # one checklist per order, Steps 1–8 + no-response log
        ├── customer-tracking-email.md         # customer tracking email template (no product names/prices)
        └── shop-handover-note.md              # WhatsApp handover note for sending both prints to the shop
```

## Setup

### 1. Get the order first

Every order starts with its order number, payment type (COD or card-paid), customer name and phone, and order total — all from Shopify Admin. Do not start fulfilment from a screenshot, a message, or memory. Create the checklist record first (`scripts/order_checklist.py new ...`, Step 1 of `SKILL.md`).

### 2. Choose the fulfilment route (one of these)

**Route A — Shopify Admin in the browser (recommended).** The owner signs in to Shopify Admin on their own device and approves each step, or approves a browser session. Claude prepares everything (checklist, consignment steps, email draft) and the owner applies it in Admin. No API key needed. Cancellations always use this route.

**Route B — Shopify Admin API with a custom app.** The owner creates a custom app in Shopify Admin, sets the needed access scopes, and creates an access token on their own device. The skill then follows the API steps (for example `fulfilmentCreate` in Step 8). This is more setup, and it is the only route that lets an agent change an order without the browser.

Do not use any other route. Do not paste API keys, passwords or credentials into the skill files, into chat, or into a repo — credentials live only in the owner's secure storage.

### 3. The two prints

The owner generates BOTH prints — packing slip + airway bill — and sends them as WhatsApp documents to the shop for printing, packing and handover. Shop staff have NO Shopify access. Claude never sends anything to the shop or the partner directly; Claude prepares the files and the handover note, and the owner sends them.

### 4. Use in Claude

Copy the `shopify-order-fulfillment/` folder into a Claude skills directory (for example a Claude Code skills folder, or a repo Claude is pointed at), or keep this whole repo and point Claude at `shopify-order-fulfillment/SKILL.md`. Then ask Claude to run the workflow, for example: "Fulfil Shopify order #1000 using the shopify-order-fulfillment skill. It is a COD order."

## Honest limits — read before using

- **No direct Shopify connection.** Claude does not have a built-in Shopify connection. Order changes go through the browser (owner's sign-in + approval) or the Shopify Admin API with an access token the owner sets up. Never claim direct auto-fulfilment without one of those.
- **No credentials in the skill.** No API keys, passwords, access tokens, bank details or secrets are stored in these files. If a step needs a login or a payment detail, the owner does it on their own device.
- **No customer email without approval.** The tracking email is drafted and stopped at the approval gate. Send it only after the owner approves the exact text.
- **No cancellation without the owner's instruction, and never by API call.** Cancellations go through Shopify Admin on the owner's device.
- **Never claim a file is saved without verifying it on disk.** The airway bill PDF is generated asynchronously — check it exists, is greater than 0 bytes, and opens before calling it ready.
- **Never invent customer details, order numbers or tracking numbers.** Every fact comes from Shopify or the courier app. All examples in this skill use placeholder data only.
- **Never mark an order fulfilled before the parcel is with the courier.** Creating a consignment does NOT mark the order fulfilled.
- **Never promise a delivery date.** The promise is the store's delivery estimate (3–5 business days for Fragrance Empire).

## How to run one order

1. Create the checklist record (`scripts/order_checklist.py new ...`) and read the order (Step 1).
2. Run WhatsApp confirmation + OTP (Step 2) — do not create a consignment for an unconfirmed COD order.
3. Create the Ninja Van consignment, verifying the COD amount badge first (Step 3).
4. Drop off, download and verify the airway bill, generate the packing slip (Steps 4–6).
5. Draft the tracking email, get the owner's approval, send it from the info@ address (Step 7).
6. Mark the order fulfilled in Shopify with the tracking number (Step 8), then close the loop (Step 10).
7. If the customer does not respond, use Step 9 — attempt contact, then cancel in Admin only on the owner's instruction.
