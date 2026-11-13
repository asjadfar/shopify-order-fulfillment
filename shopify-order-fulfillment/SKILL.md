---
name: shopify-order-fulfillment
description: End-to-end Shopify order fulfilment — Claude takes one order from arrival to fulfilled (COD vs card-paid check, WhatsApp confirmation + OTP verification, Ninja Van consignment, parcel drop-off, airway bill, packing slip, customer tracking email from the store info@ address, mark fulfilled in Shopify with tracking number). Modeled on the live store Fragrance Empire (fragranceempire.my — Malaysia, MYR, COD + Stripe card payments, Standard FREE 3–5 business days, Ninja Van). Use when the user asks to fulfil, process, ship, track, or close a Shopify order, create a courier consignment, send a tracking email, or set up an order-fulfilment workflow.
---

# Shopify Order Fulfilment

## When to use

Use this skill when the user asks to fulfil a Shopify order, process a new order, confirm an order, create a courier consignment, print an airway bill or packing slip, send a customer a tracking email, mark an order fulfilled, or handle an order where the customer does not respond. The end result is one order fully closed — parcel with the courier, customer emailed with tracking, and Shopify marked fulfilled — not a half-finished order.

Do not use it for building a store, adding products, or changing prices (use the shopify-store-automation skill for a store build), for marketplace orders (Amazon, Etsy, eBay), or for a platform other than Shopify, unless the user explicitly asks to adapt it.

## Who does what — Claude handles all the work end to end

Claude runs every step of the workflow below — telling COD from card-paid, drafting the WhatsApp confirmation, creating the courier consignment steps, checking the airway bill and packing slip, drafting the customer tracking email, and marking the order fulfilled. The owner is involved only at these points:

1. **Decisions only the owner can make** — whether an unresponsive customer's order is cancelled or kept waiting, whether a fulfilment notification email goes to the customer, and any refund, discount, or price change on an order. Claude drafts and recommends; the owner decides.
2. **Accounts, sign-ins and money** — Shopify Admin sign-in, the courier app / account, the store email mailbox, and any payment or refund. These happen on the owner's own device, with the owner's own details. Claude never handles the owner's password, bank details, or payment credentials.
3. **Approval gates** — the owner approves the tracking email text before it is sent (Step 7), and approves any cancellation (Step 9). Nothing is sent to a customer and no order is cancelled without that approval.

Three device-bound exceptions, stated honestly so the "end to end" claim is not overstated:

- **Shopify Admin access:** Claude works through the owner's Shopify Admin (browser, with the owner's sign-in) or through the Shopify Admin API with an access token the owner creates in a custom app. Claude never invents store credentials and never logs in as the owner.
- **Physical parcel handling:** the shop staff pack the parcel and hand it to the courier. Claude prepares the two print files (packing slip + airway bill) and the handover note; the owner sends them to the shop (see "Operating model" below). Claude never claims a parcel was dropped off until the owner or the shop confirms it.
- **WhatsApp confirmation:** the confirmation message and OTP check go through the store's WhatsApp confirmation app / flow (for example Cartsaver). Claude drafts the message and records the result; the app itself sends it.

Everything else — the per-order checklist, the consignment steps, the airway-bill and packing-slip checks, the tracking-email draft, the fulfilment record — is Claude's work. Do not hand any of it back to the owner as homework.

## Store facts — the live reference store (do not invent others)

Fragrance Empire (https://fragranceempire.my) is the live store this skill is modeled on. Use its real, verified facts as the reference example. Do not invent a different reference store.

- **Store:** Fragrance Empire, fragranceempire.my, Shopify Basic plan, Horizon theme, currency MYR, timezone Asia/Kuala_Lumpur, market Malaysia.
- **Catalog:** 155 products = 142 single products + 13 bundles, 18 brands.
- **Payments:** Cash on Delivery (COD) active; card payments live through a Stripe card-payments provider (Visa, Mastercard, Amex, JCB, Discover, Diners, plus Apple Pay and Google Pay). Shopify Payments is not available in Malaysia — do not promise it for a Malaysia store, and check availability for the owner's country before promising any gateway.
- **Shipping:** exactly one rate — Standard, FREE, 3–5 business days, across Malaysia.
- **Trust block on product pages:** Ordered = today, Packed = +1 day, Delivered = +2 days; subtext "Dispatched in 24 hours."
- **Fulfilment courier:** Ninja Van. One consignment per order, created from Shopify. Parcel dropped off at a Ninja Van point (no pickup).
- **Order confirmation:** WhatsApp order confirmation + OTP verification (Cartsaver-style flow). Unverified orders are marked High Risk after 1 hour.
- **Customer email:** sent from the store's info@ address only (for example info@fragranceempire.my for Fragrance Empire). Never send customer email from a personal mailbox.
- **Seller services (Fiverr gig https://www.fiverr.com/s/L34yBpA):** Basic $80 — 10 products, 5 pages, 3 days; Standard $180 — 30 products, 8 pages, 5 days; Premium $350 — 50 products, 10 pages, 7 days. Unlimited revisions on all three packages.

## Operating model — who does what, and who is never contacted

This is the model the reference store runs on. Follow it exactly unless the owner states a different model for their store.

- **The store is under the owner's control ONLY.** Shop staff have NO Shopify access. They never log in to Shopify, never see the Admin, and never change an order.
- **The owner generates BOTH prints** — the packing slip AND the airway bill — and sends them as WhatsApp documents to the shop for printing, packing, and handover to the courier.
- **Claude never informs the partner / shop directly.** Claude prepares the files and the handover note; the owner sends them. Do not message, email, or call the shop or the partner on Claude's own initiative.
- **One order, one checklist.** Every order gets its own copy of `templates/per-order-checklist.md` (or one record in `scripts/order_checklist.py`). An order is not "done" until every box on its checklist is ticked and the fulfilment record is saved.

## COD vs card-paid — how to tell them apart and what changes

Check the payment status on the order in Shopify Admin before doing anything else. It changes what must happen before the parcel moves.

| | COD order | Card-paid order |
|---|---|---|
| **How to tell** | Payment status: Pending / awaiting payment. Payment method: Cash on Delivery. | Payment status: Paid. Payment method: card (Visa / Mastercard / Amex / JCB / Discover / Diners, Apple Pay, Google Pay). |
| **WhatsApp confirmation** | **Required.** Do not create the consignment until the customer confirms (Step 2). An unconfirmed COD order is the highest fake-order risk. | Still send the confirmation message (it is the store's standard step), but a paid order is already verified by the payment itself. Do not hold a paid order hostage to a reply — if the customer does not reply, proceed after one reminder (Step 9). |
| **COD amount on the consignment** | Must be verified before confirming (Step 3). The COD amount on the consignment must equal the order total exactly. If it does not match, stop and fix it — never send a parcel with the wrong COD amount. | No COD amount. The consignment is prepaid / zero COD. Check the badge shows no COD collection before confirming. |
| **Money collection** | The courier collects cash from the customer on delivery and remits it to the store. The order stays "payment pending" in Shopify until the remittance arrives — that is normal, not an error. | Money is already with the store (via the card gateway). Nothing to collect on delivery. |
| **Cancellation risk** | Higher — a customer who never confirms may never accept the parcel. Follow Step 9. | Lower — the customer has already paid. Cancel only on the customer's request or the owner's instruction. |

Never mark a COD order as paid in Shopify. Never mark a card-paid order as unpaid. Never change the payment method on an order to make the checklist easier.

## Hard limits — state them honestly, do not work around them

- **No credentials in the skill.** Never put an API key, password, access token, bank detail or secret in a skill file, in chat, or in a repo. Logins, bank details and gateway setup happen on the owner's own device.
- **No customer email without owner approval.** Draft the tracking email (Step 7) and stop. Send it only after the owner approves the exact text. A changed tracking number needs a fresh draft, not a silent edit to a sent email.
- **No cancellation without the owner's instruction.** Cancellations go through Shopify Admin (browser, owner's sign-in), never through an API call on Claude's own initiative. Claude prepares the cancellation note and the owner cancels it in Admin.
- **Never claim a file is saved without verifying it exists on disk.** The airway bill PDF is generated asynchronously (Step 5) — a download that fails, or a file that is 0 bytes, is not a saved airway bill. Check the file exists and opens before telling the owner it is ready.
- **Never invent customer details, order numbers, or tracking numbers.** Every name, phone number, address, order number and tracking number comes from Shopify or the courier app. If a fact is missing, ask — do not fill it in. All examples in this skill use placeholder data only (for example "Customer Name", "+60 1X-XXX XXXX", "NVMYXXXXXXXXXXXX", order "#1000").
- **Never put product names or prices in the customer tracking email.** The tracking email (Step 7) contains the order number, the tracking number, the tracking link, and the delivery estimate — nothing that identifies what was bought or what it cost.
- **Never mark an order fulfilled before the parcel is with the courier.** Fulfilment in Shopify (Step 8) happens after drop-off, never before. Creating a consignment does NOT mark the order fulfilled — that is a separate step.
- **Never contact the shop or the partner directly.** The owner is the only person who sends the prints and the handover note to the shop (see "Operating model").
- **Never promise a delivery date.** The promise is "3–5 business days" (or the owner's own delivery time). A courier delay is reported as a delay, not hidden and not re-promised.

## Workflow — one order, Steps 1–8 in order

Work the steps in order for each order. Do not skip a step because it looks small — confirmation, the COD check, and the airway-bill verification are the steps that prevent fake orders, wrong collections, and parcels with no label. Track every order with `scripts/order_checklist.py` or a copy of `templates/per-order-checklist.md`.

### Step 1 — Order arrives: read it before touching it

1. Open the order in Shopify Admin > Orders. Note the order number, the date and time, the customer's name, phone number, and delivery address, the items and quantities, and the order total.
2. Note the payment method and payment status (see "COD vs card-paid" above). This decides how Step 2 and Step 3 run.
3. Check the order for anything odd before proceeding: no phone number, an address that is incomplete or does not match the delivery area, a quantity that looks like a mistake, or a total that does not match the items. Flag anything odd to the owner — do not silently fix an order.
4. Create the order's checklist record: `python3 scripts/order_checklist.py new --order "#1000" --payment cod --customer "Customer Name" --phone "+60 1X-XXX XXXX" --total "RM 000.00"` (use the real order number, payment type, and total; placeholder values shown here are examples only). Tick "order received".

### Step 2 — WhatsApp order confirmation + OTP verification

This is the store's fake-order filter. Do it for every order, and do it before creating the consignment for a COD order.

1. The confirmation message goes out after purchase through the store's WhatsApp confirmation flow (for example Cartsaver). It asks the customer to confirm the order and complete OTP verification on the phone number given at checkout.
2. Draft the confirmation message for the owner / app to send. It states the order number, the order total, and that the customer should reply to confirm and complete the OTP step. It does not list product names or prices beyond the total the customer already saw at checkout.
3. Record the result on the checklist:
   - **Confirmed (OTP verified):** proceed to Step 3.
   - **Confirmed by reply, OTP not completed:** ask the owner whether to proceed — do not decide this alone.
   - **No reply:** wait, then follow Step 9 (attempt contact, then cancel only on the owner's instruction).
4. **Unverified orders are marked High Risk after 1 hour.** That is the app's own rule: after 1 hour with no verification, the order is flagged High Risk. A High Risk flag does not cancel the order by itself — it means do not ship it until the owner decides (Step 9).
5. Never create a consignment for an unconfirmed COD order. For a card-paid order with no reply, one reminder is enough — then proceed (Step 9).

### Step 3 — Create the courier consignment (Ninja Van)

Do this in Shopify Admin, on the owner's device / approved session, after Step 2 clears the order.

1. Go to Shopify Admin > Orders, open the order, select it (tick the order), then Actions > "Create Ninja Van Orders".
2. On the consignment screen, check every field against the order before confirming:
   - Recipient name, phone number, and delivery address — exactly as on the order.
   - Parcel contents / item count — matches the order.
   - **COD amount badge — verify it before confirming.** For a COD order, the COD amount must equal the order total exactly. For a card-paid order, it must show no COD collection. If the amount is wrong, stop — do not confirm, and tell the owner what is wrong.
3. Set **"Is pickup required?" to No.** The parcel is dropped off at a Ninja Van point (Step 4); no courier pickup is booked.
4. Confirm the consignment. The consignment status becomes **Pending Pickup**.
5. Record the tracking number on the checklist as soon as it appears. The tracking number is the courier's number (for example a Ninja Van number in the form `NVMYXXXXXXXXXXXX` — placeholder format; use the real number from the app).
6. **Creating the consignment does NOT mark the Shopify order fulfilled.** The Shopify order stays unfulfilled until Step 8. If anyone reports the order as "fulfilled" at this point, correct them — the parcel has not left yet.

### Step 4 — Drop the parcel at a courier point

1. The owner sends the packing slip and airway bill to the shop as WhatsApp documents (Step 5 and Step 6 produce them; the handover note is in `templates/shop-handover-note.md`). The shop prints both, packs the order, attaches the airway bill to the parcel, and takes it to a Ninja Van point.
2. The shop confirms the drop-off to the owner (message or photo of the drop-off receipt, if the shop sends one). Claude records the confirmation on the checklist — a drop-off is only "done" when the owner or the shop confirms it, never on assumption.
3. If the shop reports a problem at the drop-off point (point closed, parcel refused, label unreadable), stop and tell the owner. Do not re-route the parcel to a different courier without the owner's instruction.
4. Tick "parcel dropped off" only after that confirmation. The tracking status may still show Pending Pickup for a while after drop-off — that is the courier's system catching up, not a failed drop-off.

### Step 5 — Download the airway bill (verify it, do not assume it)

The airway bill is the courier label that goes on the parcel. It is generated by the courier app — asynchronously, so it may not be ready the moment the consignment is created.

1. Download the airway bill PDF from the courier app / Shopify (Ninja Van order view) once it is available.
2. **Verify the file before claiming it is saved:** check it exists on disk, its size is greater than 0 bytes, and it opens as a PDF. Check the order number and tracking number printed on it match the order.
3. **If a download fails, retry later or download from the courier app.** Do not keep retrying a failed download in a loop, and never tell the owner the airway bill is ready when the file is missing, 0 bytes, or will not open. Record the failure and the retry time on the checklist.
4. Save the verified PDF where the owner can find it (the order's folder, named by order number), and send it to the shop only through the owner (see "Operating model" — the owner sends both prints as WhatsApp documents).

### Step 6 — Generate the packing slip

1. Generate the packing slip from Shopify Admin (order > Print > Packing slip, or the store's packing-slip flow). It lists the items in the order, the quantities, and the delivery address — it is for the shop packer, not the customer.
2. Check it before sending: order number correct, every item and quantity matches the order, delivery address matches the order. A packing slip that lists the wrong items causes the wrong parcel.
3. Save the packing slip with the airway bill (same order folder). The owner sends both to the shop as WhatsApp documents, with the handover note from `templates/shop-handover-note.md`.
4. Tick "packing slip generated" only after the file is checked and saved.

### Step 7 — Send the customer a tracking email (owner approves first)

Send this after the parcel is dropped off (Step 4) and the airway bill is verified (Step 5). Never send it before drop-off.

1. Draft the email from `templates/customer-tracking-email.md`, or generate it with `python3 scripts/order_checklist.py email --order "#1000" --tracking "NVMYXXXXXXXXXXXX"`. Fill in only the order number, the tracking number, the tracking link, and the store's details.
2. **Rules for the email body:**
   - Send from the store's info@ address only (for example info@fragranceempire.my). Never from a personal mailbox.
   - Subject includes the order number (for example "Your order #1000 is on its way").
   - Body includes: the tracking number, the tracking link, and the estimated delivery time (3–5 business days, or the owner's own delivery time).
   - **NO product names and NO prices in the body.** The customer already has the order confirmation for that; the tracking email is only about the parcel.
   - Keep it short, polite, and in the store's language (English for Fragrance Empire).
3. **Stop and get the owner's approval for the exact text.** Send only after approval. Record the send time on the checklist.
4. If the customer replies asking where the parcel is, check the tracking link first and report what it actually shows — do not guess a delivery date.

### Step 8 — Mark the order fulfilled in Shopify (with the tracking number)

This is the step that closes the order in Shopify. Do it last, after drop-off and after the tracking email is sent (or approved to send).

1. In Shopify Admin, open the order and mark it fulfilled with the tracking number and the courier name (Ninja Van). Via the Admin API, this is a `fulfilmentCreate` call on the order with the tracking number and the courier — use the API only if the owner set up API access; otherwise do it in Admin in the browser.
2. **Notification setting:** set `notifyCustomer` to `false` unless the owner approves a notification email. The customer already received the tracking email in Step 7 — do not send them a second, duplicate fulfilment email without the owner's approval.
3. Verify the order now shows Fulfilled, with the tracking number visible and the courier named. If it does not, do not tick the checklist — find out why and fix it.
4. Tick "order fulfilled" on the checklist, record the fulfilment date and time, and save the completed checklist. The order is now closed. Any later question about it (delivery, return, refund) starts from this saved record.

## Step 9 — When a customer does not respond (and cancellations)

Use this whenever Step 2 gets no reply, or a customer stops responding mid-order.

1. **Attempt contact first.** Send one reminder through the same channel (WhatsApp confirmation flow). Keep the reminder short: order number, total, and that the order is waiting on their confirmation. Record the date and time of each attempt on the checklist.
2. **Check the risk flag.** An unverified order is marked High Risk after 1 hour. Do not ship a High Risk COD order. A card-paid order with no reply may proceed after one reminder — the payment already verifies the customer.
3. **Wait for the owner's instruction.** Claude recommends (cancel, or keep waiting and for how long), but the owner decides. Never cancel on Claude's own initiative.
4. **Cancellation goes through Shopify Admin, not an API call.** The owner cancels the order in Admin (browser, owner's sign-in), with the reason recorded (for example "customer did not respond" / "cancelled at customer's request"). If a courier consignment was already created, cancel that too in the courier app, so no parcel goes out for a cancelled order.
5. **If the customer replies after cancellation**, tell the owner at once — do not re-create the order or re-ship without the owner's instruction.
6. **If the customer asks to cancel**, confirm the request with the owner, cancel in Admin as above, and tell the customer the order is cancelled. Do not charge a paid customer and keep the parcel — a paid cancelled order is refunded through the owner's normal refund step, on the owner's instruction.

## Step 10 — After fulfilment (close the loop, do not reopen it)

1. Watch for the courier delivery: when tracking shows Delivered, record the delivery date on the checklist. A COD order's payment stays pending in Shopify until the courier remits the cash — that is normal.
2. If the review-request flow is enabled (for example Judge.me: request 1 day after fulfilment, follow-up after 5 days), confirm the request went out on schedule. Never write a review for the customer.
3. If the customer reports a problem (parcel late, damaged, wrong item), tell the owner with the tracking status and the order record — do not promise a replacement or refund without the owner's instruction.
4. File the completed checklist with the order. The next order starts a fresh checklist — never reuse one order's checklist for another.

## How to run one order

1. Create the checklist record (`scripts/order_checklist.py new ...`, Step 1).
2. Work Steps 1–8 in order, ticking each step in the tracker as it is verified — not before.
3. Use Step 9 if the customer does not respond; use Step 10 after fulfilment.
4. Hand the owner the completed checklist at the end: order number, payment type, tracking number, drop-off confirmation, tracking-email send time, and fulfilment date. If any step is unticked, say so plainly — an order with an unticked step is not closed.
