# https://opentelemetry.io/docs/languages/python/instrumentation/
from typing import Iterable

from opentelemetry import metrics, trace
from opentelemetry.metrics import CallbackOptions, Observation
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

provider = TracerProvider()
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)

# Sets the global default tracer provider
trace.set_tracer_provider(provider)

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer("my.tracer.name")

metric_reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
provider = MeterProvider(metric_readers=[metric_reader])

# Sets the global default meter provider
metrics.set_meter_provider(provider)

# Creates a meter from the global meter provider
meter = metrics.get_meter("my.meter.name")

work_counter = meter.create_counter(
    "work.counter", unit="1", description="Counts the amount of work done"
)


def do_work():
    # count the work being doing
    work_counter.add(1, {"work.type": "my_work_type"})
    with tracer.start_as_current_span("parent") as parent:
        work_counter.add(1, {"work.type": "my_work_type"})
        # do some work that 'parent' tracks
        print("doing some work...")
        # Create a nested span to track nested work
        with tracer.start_as_current_span("child") as child:
            work_counter.add(1, {"work.type": "my_work_type"})
            # do some work that 'child' tracks
            print("doing some nested work...")
            # the nested span is closed when it's out of scope
            do_child_work()

        # This span is also closed when it goes out of scope


@tracer.start_as_current_span("do_child_work")
def do_child_work():
    work_counter.add(1, {"work.type": "my_work_type"})
    print("doing some child work...")


def scrape_config_versions(options: CallbackOptions) -> Iterable[Observation]:
    r = requests.get(
        "http://configserver/version_metadata", timeout=options.timeout_millis / 10**3
    )
    for metadata in r.json():
        yield Observation(
            metadata["version_num"], {"config.name": metadata["version_num"]}
        )


meter.create_observable_gauge(
    "config.version",
    callbacks=[scrape_config_versions],
    description="The active config version for each configuration",
)


if __name__ == "__main__":
    do_work()
