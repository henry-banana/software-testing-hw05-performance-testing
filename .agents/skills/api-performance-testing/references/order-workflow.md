# Worked example. Order workflow

The EShop assignment uses one six-step order workflow across its measured profiles. Prepare a local disposable backend at the pinned commit. Build the plans and the synthetic CSV with `python -B scripts/build_plans.py`. Run the Smoke profile from the assignment runbook before applying load.

| Step | Evidence to inspect |
| --- | --- |
| Auth | Login returns a token and the user matches the assigned CSV row |
| Read | Product list contains the fixture ID and detail matches its ID and price |
| Transaction | Cart confirms the add. Checkout returns an order identifier |
| Verification | The same user's order history lists that identifier as the newest pending order |

The smoke run used two different accounts and completed 1194 HTTP samples with six sampler labels and zero errors. The first fixture check found an incorrect price for product 5. The first JMeter launch with Java 25 then failed before collecting samples. A verified fixture and Java 21 were used on the successful run. These two failures were environment and data preparation findings.

Use `scripts/analyze_jtl.py` to read a measured result directory. It reconciles sample and error counts against JMeter's HTML statistics. Read window RPS from the request samples that completed in the selected interval. The successful order-history sampler separately counts workflows completed.
