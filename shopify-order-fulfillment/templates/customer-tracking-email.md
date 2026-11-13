# Customer Tracking Email — template

> Send from the store's info@ address ONLY (for example
> info@fragranceempire.my). Never from a personal mailbox.
> Send AFTER the parcel is dropped off (SKILL.md Step 4) and the airway
> bill is verified (Step 5). The owner approves the exact text before
> it is sent. Fill in every [bracketed] field — never guess one.
> NO product names and NO prices anywhere in this email.
> Generate the same text with:
> `python3 scripts/order_checklist.py email --order "#1000" --tracking "NVMYXXXXXXXXXXXX"`

---

**From:** [info@storename.example]

**To:** [customer email from the order]

**Subject:** Your order [#1000] is on its way

**Body:**

Hi,

Good news — your order [#1000] is on its way.

Tracking number: [NVMYXXXXXXXXXXXX]
Track your parcel here: [https://www.ninjavan.co/en-my/tracking?id=NVMYXXXXXXXXXXXX]

Estimated delivery: 3–5 business days.

If your parcel has not arrived after 5 business days, reply to this email and we will check it for you.

Thank you for shopping with us.

[Store Name]
[store.example]
[info@store.example]

---

## Checks before sending (all must be Yes)

- [ ] From the store's info@ address only
- [ ] Subject includes the order number
- [ ] Body includes the tracking number, the tracking link, and the 3–5 business days estimate
- [ ] Body contains NO product names
- [ ] Body contains NO prices
- [ ] Tracking number matches the consignment (Step 3) and the airway bill (Step 5)
- [ ] Tracking link opens and shows the order's tracking number
- [ ] **Owner approved the exact text** — name / date:
- [ ] Sent — date / time:

## If the customer replies asking where the parcel is

1. Open the tracking link first and read what it actually shows.
2. Report the tracking status exactly as shown — do not guess a delivery date.
3. If tracking shows no movement for 3 business days after drop-off, tell the owner — do not promise the customer a new date on your own.
