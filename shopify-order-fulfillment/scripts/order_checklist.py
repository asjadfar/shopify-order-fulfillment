#!/usr/bin/env python3
"""order_checklist.py — per-order fulfilment checklist tracker and
customer tracking-email generator.

Part of the shopify-order-fulfillment Claude skill.
See shopify-order-fulfillment/SKILL.md for the full workflow.

What it does:
  - Tracks one Shopify order through the 8 fulfilment steps, in a JSON
    file (default: fulfilment-orders.json in the current directory).
    A step is ticked only when it is verified — never in advance.
  - Generates the customer tracking email text from an order number and
    a tracking number. The email contains NO product names and NO
    prices — order number, tracking number, tracking link, and the
    delivery estimate only (see SKILL.md Step 7).

  Steps tracked (in order):
    order_received, whatsapp_confirmed, consignment_created,
    parcel_dropped_off, airway_bill_downloaded, packing_slip_generated,
    tracking_email_sent, order_fulfilled

Usage:
  python3 order_checklist.py new --order "#1000" --payment cod \
      --customer "Customer Name" --phone "+60 1X-XXX XXXX" \
      --total "RM 000.00"
  python3 order_checklist.py check --order "#1000" --step whatsapp_confirmed
  python3 order_checklist.py check --order "#1000" --step consignment_created \
      --tracking "NVMYXXXXXXXXXXXX"
  python3 order_checklist.py status --order "#1000"
  python3 order_checklist.py email --order "#1000" \
      --tracking "NVMYXXXXXXXXXXXX" [--store-name "Store Name"] \
      [--store-domain "store.example"] [--store-email "info@store.example"]
  python3 order_checklist.py list
  python3 order_checklist.py note --order "#1000" --text "Customer replied, OTP verified."

  Add --file <path> to any command to use a different JSON file.
  Add --date "2026-11-13 18:00" to check/note to record a specific time;
  otherwise the current local time is used.

Notes:
  - All example values above are placeholders. Use the real order
    number, payment type, customer name, phone, total, and tracking
    number from Shopify / the courier app. Never invent them.
  - --payment must be "cod" or "card".
  - check refuses to tick a step out of order: every earlier step must
    already be ticked. Use --force only if the owner confirms a step
    was genuinely done out of order, and record why with note.
  - email does NOT send anything. It prints the draft for the owner to
    approve (SKILL.md Step 7). Sending happens from the store's info@
    mailbox after approval.
  - This script stores order records locally in JSON. It contains no
    credentials and makes no network calls. Keep the JSON file out of
    any shared repo if it holds real customer details.

Requirements: Python 3, standard library only. No credentials, no network.
"""

import argparse
import json
import os
import sys
from datetime import datetime

DEFAULT_FILE = "fulfilment-orders.json"

STEPS = [
    ("order_received", "1. Order received (read in Shopify Admin)"),
    ("whatsapp_confirmed", "2. WhatsApp confirmation + OTP verified"),
    ("consignment_created", "3. Courier consignment created (COD amount checked)"),
    ("parcel_dropped_off", "4. Parcel dropped off at courier point"),
    ("airway_bill_downloaded", "5. Airway bill downloaded + verified on disk"),
    ("packing_slip_generated", "6. Packing slip generated + checked"),
    ("tracking_email_sent", "7. Customer tracking email sent (owner approved)"),
    ("order_fulfilled", "8. Order marked fulfilled in Shopify (tracking no. added)"),
]

STEP_IDS = [step_id for step_id, _ in STEPS]
STEP_LABELS = dict(STEPS)

VALID_PAYMENTS = ("cod", "card")


def now_string():
    """Current local time as 'YYYY-MM-DD HH:MM'."""
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def load_orders(path):
    """Load the orders JSON file. Returns {} when the file does not exist."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print("Could not read %s: %s" % (path, exc), file=sys.stderr)
        sys.exit(1)
    if not isinstance(data, dict):
        print("Bad data in %s: expected an object of orders." % path,
              file=sys.stderr)
        sys.exit(1)
    return data


def save_orders(path, orders):
    """Save the orders dict to the JSON file."""
    try:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(orders, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
    except OSError as exc:
        print("Could not write %s: %s" % (path, exc), file=sys.stderr)
        sys.exit(1)


def get_order(orders, order_number):
    """Return the order record, or exit with an error when missing."""
    order = orders.get(order_number)
    if order is None:
        print("No record for order %s. Create it first with the new "
              "command." % order_number, file=sys.stderr)
        sys.exit(1)
    return order


def new_order(args):
    orders = load_orders(args.file)
    if args.order in orders:
        print("Order %s already has a record. Use status to view it."
              % args.order, file=sys.stderr)
        return 1
    if args.payment not in VALID_PAYMENTS:
        print('--payment must be "cod" or "card".', file=sys.stderr)
        return 2
    orders[args.order] = {
        "order_number": args.order,
        "payment_type": args.payment,
        "customer_name": args.customer,
        "customer_phone": args.phone,
        "order_total": args.total,
        "tracking_number": "",
        "courier": "Ninja Van",
        "created": now_string(),
        "steps": {step_id: "" for step_id in STEP_IDS},
        "notes": [],
    }
    # Creating the record ticks step 1: the order was read in Admin.
    orders[args.order]["steps"]["order_received"] = now_string()
    save_orders(args.file, orders)
    print("Created checklist for order %s (%s, total %s)."
          % (args.order, args.payment.upper(), args.total))
    print("Step 1 ticked: order received. Next: WhatsApp confirmation "
          "(Step 2).")
    return 0


def check_step(args):
    orders = load_orders(args.file)
    order = get_order(orders, args.order)
    if args.step not in STEP_IDS:
        print("Unknown step %r. Steps: %s"
              % (args.step, ", ".join(STEP_IDS)), file=sys.stderr)
        return 2
    if order["steps"].get(args.step):
        print("Step %s is already ticked (%s)."
              % (args.step, order["steps"][args.step]))
        return 0
    index = STEP_IDS.index(args.step)
    if not args.force:
        missing = [s for s in STEP_IDS[:index] if not order["steps"].get(s)]
        if missing:
            print("Cannot tick %s yet — earlier step(s) not done: %s."
                  % (args.step, ", ".join(missing)), file=sys.stderr)
            print("Tick the earlier step(s) first, or use --force only if "
                  "the owner confirms the step was genuinely done out of "
                  "order (and record why with note).", file=sys.stderr)
            return 1
    stamp = args.date or now_string()
    order["steps"][args.step] = stamp
    if args.step == "consignment_created" and args.tracking:
        order["tracking_number"] = args.tracking
    if args.step == "order_fulfilled" and not order.get("tracking_number"):
        print("Warning: marking fulfilled with no tracking number recorded. "
              "Add it with: check --order %s --step consignment_created "
              "--tracking <number>" % args.order, file=sys.stderr)
    save_orders(args.file, orders)
    print("Ticked %s for order %s (%s)."
          % (STEP_LABELS[args.step], args.order, stamp))
    remaining = [s for s in STEP_IDS if not order["steps"].get(s)]
    if remaining:
        print("Next step: %s." % STEP_LABELS[remaining[0]])
    else:
        print("All 8 steps done — order %s is closed." % args.order)
    return 0


def show_status(args):
    orders = load_orders(args.file)
    order = get_order(orders, args.order)
    print("Order %s — %s — total %s — created %s"
          % (order["order_number"], order["payment_type"].upper(),
             order["order_total"], order["created"]))
    print("Customer: %s (%s)"
          % (order["customer_name"], order["customer_phone"]))
    print("Courier: %s — tracking: %s"
          % (order["courier"], order["tracking_number"] or "(not recorded)"))
    done = 0
    for step_id, label in STEPS:
        stamp = order["steps"].get(step_id, "")
        if stamp:
            print("  [x] %s — %s" % (label, stamp))
            done += 1
        else:
            print("  [ ] %s" % label)
    print("%d of %d steps done." % (done, len(STEPS)))
    if order["notes"]:
        print("Notes:")
        for note in order["notes"]:
            print("  - %s — %s" % (note["time"], note["text"]))
    if done < len(STEPS):
        print("Order %s is NOT closed yet." % args.order)
    return 0


def list_orders(args):
    orders = load_orders(args.file)
    if not orders:
        print("No orders recorded in %s yet." % args.file)
        return 0
    print("%-12s %-6s %-10s %s" % ("Order", "Pay", "Steps", "Tracking"))
    for number in sorted(orders):
        order = orders[number]
        done = sum(1 for s in STEP_IDS if order["steps"].get(s))
        print("%-12s %-6s %d/%d       %s"
              % (number, order["payment_type"].upper(), done, len(STEPS),
                 order["tracking_number"] or "-"))
    return 0


def add_note(args):
    orders = load_orders(args.file)
    order = get_order(orders, args.order)
    order["notes"].append({
        "time": args.date or now_string(),
        "text": args.text,
    })
    save_orders(args.file, orders)
    print("Note added to order %s." % args.order)
    return 0


def build_email(order_number, tracking_number, store_name, store_domain,
                store_email):
    """Build the customer tracking email. No product names, no prices."""
    tracking_url = "https://www.ninjavan.co/en-my/tracking?id=%s" % tracking_number
    subject = "Your order %s is on its way" % order_number
    body = (
        "Hi,\n"
        "\n"
        "Good news — your order %s is on its way.\n"
        "\n"
        "Tracking number: %s\n"
        "Track your parcel here: %s\n"
        "\n"
        "Estimated delivery: 3–5 business days.\n"
        "\n"
        "If your parcel has not arrived after 5 business days, reply to "
        "this email and we will check it for you.\n"
        "\n"
        "Thank you for shopping with us.\n"
        "\n"
        "%s\n"
        "%s\n"
        "%s\n" % (order_number, tracking_number, tracking_url,
                  store_name, store_domain, store_email)
    )
    return subject, body


def email_command(args):
    orders = load_orders(args.file)
    order = get_order(orders, args.order)
    tracking = args.tracking or order.get("tracking_number", "")
    if not tracking:
        print("No tracking number. Pass --tracking, or record one first "
              "with: check --order %s --step consignment_created --tracking "
              "<number>" % args.order, file=sys.stderr)
        return 1
    subject, body = build_email(
        args.order, tracking, args.store_name, args.store_domain,
        args.store_email)
    print("DRAFT ONLY — do not send until the owner approves the exact "
          "text (SKILL.md Step 7).")
    print("From: %s" % args.store_email)
    print("Subject: %s" % subject)
    print()
    print(body)
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        description="Per-order Shopify fulfilment checklist tracker and "
                    "tracking-email generator.")
    parser.add_argument("--file", default=DEFAULT_FILE,
                        help="orders JSON file (default: %(default)s)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_new = sub.add_parser("new", help="create a checklist record for an order")
    p_new.add_argument("--order", required=True, help='e.g. "#1000"')
    p_new.add_argument("--payment", required=True, choices=VALID_PAYMENTS,
                       help='"cod" or "card"')
    p_new.add_argument("--customer", required=True,
                       help='customer name, e.g. "Customer Name"')
    p_new.add_argument("--phone", required=True,
                       help='customer phone, e.g. "+60 1X-XXX XXXX"')
    p_new.add_argument("--total", required=True,
                       help='order total, e.g. "RM 000.00"')
    p_new.set_defaults(func=new_order)

    p_check = sub.add_parser("check", help="tick one fulfilment step")
    p_check.add_argument("--order", required=True)
    p_check.add_argument("--step", required=True, choices=STEP_IDS)
    p_check.add_argument("--tracking",
                         help="tracking number (with consignment_created)")
    p_check.add_argument("--date", help='timestamp, e.g. "2026-11-13 18:00"')
    p_check.add_argument("--force", action="store_true",
                         help="allow ticking out of order (owner-confirmed only)")
    p_check.set_defaults(func=check_step)

    p_status = sub.add_parser("status", help="show one order's checklist")
    p_status.add_argument("--order", required=True)
    p_status.set_defaults(func=show_status)

    p_list = sub.add_parser("list", help="list all tracked orders")
    p_list.set_defaults(func=list_orders)

    p_note = sub.add_parser("note", help="add a dated note to an order")
    p_note.add_argument("--order", required=True)
    p_note.add_argument("--text", required=True)
    p_note.add_argument("--date", help='timestamp, e.g. "2026-11-13 18:00"')
    p_note.set_defaults(func=add_note)

    p_email = sub.add_parser("email",
                             help="print the tracking-email draft (does NOT send)")
    p_email.add_argument("--order", required=True)
    p_email.add_argument("--tracking",
                         help="tracking number (defaults to the recorded one)")
    p_email.add_argument("--store-name", default="Fragrance Empire")
    p_email.add_argument("--store-domain", default="fragranceempire.my")
    p_email.add_argument("--store-email", default="info@fragranceempire.my")
    p_email.set_defaults(func=email_command)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
