"""Generate the three JMeter plans and their deterministic EShop CSV fixture."""

import argparse
import csv
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDENT_ID = "23120262"
DEFAULT_DATE = "20261124"
LABELS = ("01 Login", "02 Product list", "03 Product detail", "04 Add to cart",
          "05 Checkout", "06 Order history")
PLANS = {
    "Load": ("SummaryReport", "Summary Report", [(16, 0, 15, 100)]),
    "Stress": ("StatVisualizer", "Aggregate Report", [
        (16, 0, 6, 200), (32, 40, 6, 160), (48, 80, 6, 120),
        (96, 120, 6, 80), (192, 160, 6, 40),
    ]),
    "Spike": ("ViewResultsFullVisualizer", "View Results Tree", [
        (16, 0, 8, 100), (112, 30, 2, 26),
    ]),
}

FIXTURE = """\
if (vars.get('email') == null) {
    def path = props.getProperty('fixture')
    def file = path ? new File(path) : new File(
        org.apache.jmeter.services.FileServer.getFileServer().getBaseDir(),
        '../data/workflow.csv')
    int slot = Integer.parseInt(Parameters) + ctx.getThreadNum()
    def rows = file.readLines('UTF-8')
    def names = rows[0].split(',', -1)
    def values = rows[slot + 1].split(',', -1)
    names.eachWithIndex { name, i -> vars.put(name, values[i]) }
}
vars.remove('token')
vars.remove('orderId')
"""

ASSERT = """\
if (!prev.isSuccessful()) return
def fail = { reason ->
    AssertionResult.setFailure(true)
    AssertionResult.setFailureMessage(reason)
}
try {
    if (prev.getResponseCode() != '200') {
        fail('Expected HTTP 200')
        return
    }
    def body = new groovy.json.JsonSlurper().parseText(prev.getResponseDataAsString())
    int productId = vars.get('product_id').toInteger()
    switch (Parameters) {
        case 'login':
            if (!(body.token instanceof String) || !body.token || body.user?.email != vars.get('email')) {
                fail('Expected token and matching account')
                return
            }
            vars.put('token', body.token)
            break
        case 'list':
            if (!(body instanceof List) || !body.any { it.id == productId }) fail('Fixture product absent')
            break
        case 'detail':
            if (body.id != productId || body.price?.toString() != vars.get('total_amount')) fail('Wrong product or price')
            break
        case 'cart':
            if (body.message != 'Added to cart') fail('Cart confirmation absent')
            break
        case 'checkout':
            if (!(body.orderId instanceof Number) || body.orderId <= 0) {
                fail('Valid orderId missing')
                return
            }
            vars.put('orderId', body.orderId.toString())
            break
        case 'history':
            def order = (body instanceof List && body) ? body[0] : null
            if (order?.id?.toString() != vars.get('orderId')
                || order.status != 'pending'
                || order.total_amount?.toString() != vars.get('total_amount')) {
                fail('New pending order absent or mismatched in history')
            }
            break
    }
} catch (Exception ignored) {
    fail('Unexpected JSON response')
}
"""


@dataclass(frozen=True)
class Request:
    method: str
    path: str
    label: str
    check: str
    payload: str | None = None
    auth: bool = False


REQUESTS = [
    Request("POST", "/api/login", LABELS[0], "login",
            '{"email":"${email}","password":"${password}"}'),
    Request("GET", "/api/products", LABELS[1], "list"),
    Request("GET", "/api/products/${product_id}", LABELS[2], "detail"),
    Request("POST", "/api/cart", LABELS[3], "cart",
            '{"id":${product_id},"quantity":1,"price":${total_amount}}', auth=True),
    Request("POST", "/api/checkout", LABELS[4], "checkout",
            '{"total_amount":${total_amount},"shipping_address":"${shipping_address}"}', auth=True),
    Request("GET", "/api/orders/my-orders", LABELS[5], "history", auth=True),
]


def prop(parent, name, value, kind="stringProp"):
    item = ET.SubElement(parent, kind, name=name)
    item.text = str(value)
    return item


def element(parent, name, testclass):
    return ET.SubElement(parent, "elementProp", name=name, elementType=testclass)


def test_element(tree, testclass, gui, name, enabled=True):
    node = ET.SubElement(tree, testclass, guiclass=gui, testclass=testclass,
                         testname=name, enabled=str(enabled).lower())
    return node, ET.SubElement(tree, "hashTree")


def groovy(tree, kind, name, script, params):
    node, _ = test_element(tree, kind, "TestBeanGUI", name)
    for key, value in (("scriptLanguage", "groovy"), ("parameters", params),
                       ("filename", ""), ("cacheKey", "true"), ("script", script)):
        prop(node, key, value)


def add_request(tree, request, offset):
    node, children = test_element(tree, "HTTPSamplerProxy", "HttpTestSampleGui", request.label)
    args = element(node, "HTTPsampler.Arguments", "Arguments")
    entries = ET.SubElement(args, "collectionProp", name="Arguments.arguments")
    if request.payload:
        param = element(entries, "", "HTTPArgument")
        prop(param, "HTTPArgument.always_encode", "false", "boolProp")
        prop(param, "Argument.value", request.payload)
        prop(param, "Argument.metadata", "=")
        prop(node, "HTTPSampler.postBodyRaw", "true", "boolProp")
    options = {
        "domain": "127.0.0.1", "port": "${__P(port,3000)}", "protocol": "http",
        "path": request.path, "method": request.method, "implementation": "HttpClient4",
        "connect_timeout": "2000", "response_timeout": "5000",
    }
    for key, value in options.items():
        prop(node, "HTTPSampler." + key, value)
    prop(node, "HTTPSampler.follow_redirects", "false", "boolProp")
    prop(node, "HTTPSampler.use_keepalive", "true", "boolProp")

    if request.payload or request.auth:
        headers, _ = test_element(children, "HeaderManager", "HeaderPanel", "Request headers")
        entries = ET.SubElement(headers, "collectionProp", name="HeaderManager.headers")
        values = []
        if request.payload:
            values.append(("Content-Type", "application/json"))
        if request.auth:
            values.append(("Authorization", "Bearer ${token}"))
        for name, value in values:
            header = element(entries, "", "Header")
            prop(header, "Header.name", name)
            prop(header, "Header.value", value)

    if request.check == "login":
        groovy(children, "JSR223PreProcessor", "Bind CSV row to VU", FIXTURE, offset)
        timer, _ = test_element(children, "UniformRandomTimer", "UniformRandomTimerGui", "Pace workflow")
        prop(timer, "ConstantTimer.delay", "${__P(think_min,850)}")
        prop(timer, "RandomTimer.range", "${__P(think_range,300)}")
    groovy(children, "JSR223Assertion", "Validate " + request.check, ASSERT, request.check)


def add_threads(parent, scenario, stage, offset, profile):
    count, delay, ramp, duration = profile
    name = f"{scenario.lower()}-{stage:02d}-add{count:03d}"
    group, tree = test_element(parent, "ThreadGroup", "ThreadGroupGui", name)
    prop(group, "ThreadGroup.on_sample_error", "startnextloop")
    controller = element(group, "ThreadGroup.main_controller", "LoopController")
    prop(controller, "LoopController.continue_forever", "false", "boolProp")
    prop(controller, "LoopController.loops", "-1")
    prop(group, "ThreadGroup.scheduler", "true", "boolProp")
    for name, value in (("num_threads", count), ("ramp_time", ramp),
                        ("delay", delay), ("duration", duration)):
        prop(group, "ThreadGroup." + name, f"${{__P({name}_{stage},{value})}}")
    for request in REQUESTS:
        add_request(tree, request, offset)


def write_plan(scenario, date, output):
    gui, listener_name, stages = PLANS[scenario]
    name = f"{STUDENT_ID}_{scenario}_{date}"
    root = ET.Element("jmeterTestPlan", version="1.2", properties="5.0", jmeter="5.6.3")
    plan, tree = test_element(ET.SubElement(root, "hashTree"), "TestPlan", "TestPlanGui", name)
    prop(plan, "TestPlan.comments", "One EShop order workflow. HTTP load is restricted to 127.0.0.1.")
    prop(plan, "TestPlan.serialize_threadgroups", "false", "boolProp")
    offset = 0
    for stage, profile in enumerate(stages, 1):
        add_threads(tree, scenario, stage, offset, profile)
        offset += profile[0]
    test_element(tree, "ResultCollector", gui, listener_name, enabled=False)
    ET.indent(root, space="  ")
    ET.ElementTree(root).write(output / f"{name}.jmx", encoding="UTF-8", xml_declaration=True)


def write_fixture(output):
    products = [(1, 30000000), (2, 28000000), (3, 45000000),
                (4, 6000000), (5, 4000000)]
    with (output / "workflow.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["email", "password", "product_id", "total_amount", "shipping_address"])
        for slot in range(384):
            product, price = products[slot % len(products)]
            writer.writerow([f"vu{slot + 1:03d}@hw05.example.test", f"Hw05Fixture{slot + 1:03d}",
                             product, price, f"HW05 Test Address {slot + 1:03d}"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default=DEFAULT_DATE)
    parser.add_argument("--scenario", choices=PLANS)
    args = parser.parse_args()
    if args.scenario:
        write_plan(args.scenario, args.date, ROOT / "test-plans")
        return
    write_fixture(ROOT / "data")
    for scenario in PLANS:
        write_plan(scenario, args.date, ROOT / "test-plans")


if __name__ == "__main__":
    main()
