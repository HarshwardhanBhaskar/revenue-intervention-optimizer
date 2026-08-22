# Demo Walkthrough Guide (5-Minute Reviewer Narrative)

This guide provides the exact 5-minute presentation script for evaluating the Revenue Intervention Optimizer.

---

### 0:00 – 0:30 | The Problem Thesis
- **Narrative**: *"Most recovery tools spam customers with reminders or blind retries. But payment recovery isn't about contacting everyone—it's about asking: 'Will this customer pay BECAUSE of this intervention, and is it economically worthwhile?'"*
- **Screen**: Marketing Landing (`/`) — Highlight the headline *"Recover the revenue worth recovering"* and the thesis that `DO NOTHING` is an optimal decision.

---

### 0:30 – 1:15 | Operational Overview Dashboard
- **Narrative**: *"Here is the merchant control center. Notice the primary metric: +₹4.82L Incremental Net Revenue Recovered (+18.7% vs baseline), calculated strictly after subtracting gateway fees and discount costs."*
- **Screen**: `/overview` — Click on the **Recovery Signal Grid** cards to demonstrate interactive expansion, review the recovery yield trajectory, and review the 5-stage pipeline funnel.

---

### 1:15 – 2:15 | Live Decision Inspection
- **Narrative**: *"Let's inspect a live payment failure. We don't just show a recommendation; we show the counterfactual potential outcomes across all 5 actions, the feature vector, and the deterministic safety checklist."*
- **Screen**: `/recovery` $\to$ Click **Inspect** on an opportunity $\to$ `/recovery/[id]` — Point out **Why this action?** and **Why not alternatives?**.

---

### 2:15 – 3:00 | Counterfactual Decision Lab (Signature Feature)
- **Narrative**: *"In the Decision Lab, operators can simulate what-if scenarios in real-time. Watch what happens when we increase the discount slider on a high-value order: margin erosion causes the optimal action to switch from DISCOUNT to PAYMENT LINK."*
- **Screen**: `/decision-lab` — Adjust amount, baseline probability, and discount sliders to show dynamic argmax recalculation.

---

### 3:00 – 4:00 | Empirical Experiments & Uplift
- **Narrative**: *"We evaluated our T-Learner against a standard Retry Once baseline on a 100% held-out test set of 538 transactions. Net revenue recovered grew from ₹23.67L to ₹27.38L (+15.7%), with a 95% bootstrap confidence interval of [₹56k, ₹6.68L]."*
- **Screen**: `/experiments` — Point out the 28 times DO NOTHING was selected, saving ₹14.2k in wasted spend.

---

### 4:00 – 4:30 | Safety Guardrails & Human Sign-off
- **Narrative**: *"Probabilistic models never have direct execution authority. High-value orders exceeding ₹10,000 are automatically held in the Human Approval Queue."*
- **Screen**: `/approvals` $\to$ Click **Approve** to dispatch the Razorpay payment link. Then show `/policies` and the immutable `/audit` log.

---

### 4:30 – 5:00 | Failure Engineering & Closing
- **Narrative**: *"We engineered the system for reliability: duplicate webhooks are deduplicated via unique HMAC event keys, and double-approvals return HTTP 409 Conflict. We built an AI system that knows when to recover revenue—and when not to intervene."*
- **Screen**: `/exceptions` $\to$ Return to `/overview`.
