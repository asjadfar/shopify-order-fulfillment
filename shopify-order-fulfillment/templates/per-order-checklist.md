# Per-Order Checklist — Shopify order fulfilment

> Complete one copy per order. An order is NOT closed until every box
> below is ticked. Tick a step only when it is verified — never in
> advance, never on assumption. Fill in every [bracketed] field with
> the real value from Shopify or the courier app — never guess one.
> All values in the worked example are placeholders.

## Order

- **Order number:** [#1000]
- **Order date / time:**
- **Customer name:** [Customer Name]
- **Customer phone:** [+60 1X-XXX XXXX]
- **Delivery address:** [as on the order in Shopify Admin]
- **Items / quantities:** [as on the order — count only, no prices here]
- **Order total:** [RM 000.00]
- **Payment type (circle one):** COD / Card-paid
- **Payment status in Shopify:** [Pending / Paid]
- **Courier:** Ninja Van
- **Tracking number:** [NVMYXXXXXXXXXXXX]
- **Checklist started by / date:**

## Step 1 — Order arrives: read it before touching it

- [ ] Order opened in Shopify Admin > Orders; number, customer, address, items, total noted above
- [ ] Payment method + status noted (COD = Pending; card-paid = Paid)
- [ ] Anything odd flagged to the owner (no phone number, incomplete address, wrong quantity/total): [none / describe]

## Step 2 — WhatsApp order confirmation + OTP verification

- [ ] Confirmation message sent (WhatsApp confirmation flow, after purchase)
- [ ] Result (circle one): OTP verified / Replied, OTP not completed — owner asked / No reply
- [ ] Date / time of confirmation:
- [ ] High Risk flag after 1 hour with no verification: [ ] Yes — owner told / [ ] No
- [ ] COD order: consignment NOT created before confirmation: [ ] Confirmed

## Step 3 — Courier consignment (Ninja Van)

- [ ] Shopify Admin > Orders > order selected > Actions > "Create Ninja Van Orders"
- [ ] Recipient name, phone, delivery address checked against the order: [ ] Match
- [ ] **COD amount badge verified before confirming:** COD amount = order total exactly (COD order) / no COD collection (card-paid order): [ ] Verified — amount: [RM 000.00 / none]
- [ ] "Is pickup required?" = No: [ ] Yes
- [ ] Consignment confirmed — status: Pending Pickup
- [ ] Tracking number recorded above: [ ] Yes

## Step 4 — Drop the parcel at a courier point

- [ ] Packing slip + airway bill sent to the shop as WhatsApp documents (owner sent them — see `templates/shop-handover-note.md`)
- [ ] Shop confirmed drop-off to the owner (message / drop-off receipt): [ ] Yes — date / time:
- [ ] Drop-off problem reported (point closed, parcel refused, label unreadable): [none / describe]

## Step 5 — Airway bill (verify it, do not assume it)

- [ ] Airway bill PDF downloaded from the courier app / Shopify
- [ ] File verified on disk: exists, size > 0 bytes, opens as a PDF: [ ] Yes — file path:
- [ ] Order number + tracking number printed on it match the order: [ ] Yes
- [ ] Download failed: [ ] No / [ ] Yes — retried at: ___ / downloaded from courier app: [ ] Yes
- [ ] Airway bill sent to the shop (owner, as WhatsApp document): [ ] Yes

## Step 6 — Packing slip

- [ ] Packing slip generated (Shopify Admin > order > Print > Packing slip)
- [ ] Checked: order number correct, every item + quantity matches the order, delivery address matches: [ ] Yes
- [ ] Packing slip saved with the airway bill (order folder): [ ] Yes
- [ ] Packing slip sent to the shop (owner, as WhatsApp document): [ ] Yes

## Step 7 — Customer tracking email (owner approves first)

- [ ] Email drafted from `templates/customer-tracking-email.md` (or `scripts/order_checklist.py email ...`)
- [ ] From the store's info@ address only: [ ] Yes — address: [info@___]
- [ ] Subject includes the order number: [ ] Yes
- [ ] Body includes tracking number + tracking link + 3–5 business days estimate: [ ] Yes
- [ ] Body contains NO product names and NO prices: [ ] Checked
- [ ] **Owner approved the exact text:** [ ] Yes — name / date:
- [ ] Email sent: [ ] Yes — date / time:

## Step 8 — Mark fulfilled in Shopify (with the tracking number)

- [ ] Done AFTER drop-off (Step 4) and after the tracking email (Step 7)
- [ ] Order marked fulfilled with the tracking number + courier (Ninja Van): [ ] Yes
- [ ] `notifyCustomer` = false, unless the owner approved a notification email: [ ] false / [ ] approved notification sent
- [ ] Order shows Fulfilled in Shopify, tracking number visible: [ ] Verified — date / time:

## Step 9 — No response / cancellation log (only if needed)

| Date / time | Attempt / action | Result |
|---|---|---|
| | Reminder sent (WhatsApp) | |
| | Owner told — decision: | |
| | Cancelled in Shopify Admin (owner) + consignment cancelled in courier app | |

- **Cancellation reason (if cancelled):** [customer did not respond / cancelled at customer's request / other: ___]
- **Cancelled by owner in Shopify Admin (never by API call):** [ ] Yes — date / time:

## Step 10 — After fulfilment

- [ ] Tracking shows Delivered — delivery date:
- [ ] COD order: payment still pending until courier remits cash — normal, not an error: [ ] Noted
- [ ] Review request went out on schedule (if enabled: 1 day after fulfilment, follow-up after 5 days): [ ] Yes / [ ] N/A
- [ ] Customer problem reported: [none / describe + owner told]

## Close-out

- **Order closed:** [ ] Yes — all 8 steps ticked — date / time:
- **Still open (say plainly which step and why):**
- **Checklist filed with the order record:** [ ] Yes
