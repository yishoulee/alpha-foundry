# Alpha Foundry performance audit — 2026-10-29

The implementation supports **vectorized signal generation with sequential portfolio accounting**. The historical 52,490 bars/sec example is not disproved, but its original conditions cannot be reconstructed from the inspected repository. New measurements below are controlled synthetic, in-memory measurements of the combined engine path, not a reproduction of that historical run or a fully vectorized-engine benchmark.

## Pinned source snapshots

- [Alpha Foundry](https://github.com/yishoulee/alpha-foundry/tree/e9bfb38473e5b45ec8946694b7757c13897608e7): `e9bfb38473e5b45ec8946694b7757c13897608e7` (`main`).
- [GitHub profile](https://github.com/yishoulee/yishoulee/blob/2e4d1728ca5c93c769ce0cc15e691f5d7a349f39/README.md): `2e4d1728ca5c93c769ce0cc15e691f5d7a349f39` (`main`).
- [Website homepage](https://github.com/yishoulee/yishoulee.github.io/blob/d43ab1cd725b4327d25a237b496163ed95576411/content/index.md): `d43ab1cd725b4327d25a237b496163ed95576411` (`v4`).

Retrieved application and test files were checked against their GitHub blob SHA-1 hashes before execution. No application, dependency, or test source was changed for this audit.

## Claims and disposition

| Claim | Finding and correction |
| --- | --- |
| Vectorized signal generation | Retain. [Momentum](https://github.com/yishoulee/alpha-foundry/blob/e9bfb38473e5b45ec8946694b7757c13897608e7/strategies/momentum.py) uses rolling means and `np.where`; [mean reversion](https://github.com/yishoulee/alpha-foundry/blob/e9bfb38473e5b45ec8946694b7757c13897608e7/strategies/mean_reversion.py) uses rolling statistics, `np.where`, and forward filling. |
| “Vectorized research path above 52,000 bars/s” | Remove from both portfolio summaries. It conflates vectorized signals with combined engine throughput. Replace with “Vectorized Pandas/NumPy signal generation with sequential portfolio accounting.” |
| Fully vectorized backtesting engine | Unsupported. [Engine](https://github.com/yishoulee/alpha-foundry/blob/e9bfb38473e5b45ec8946694b7757c13897608e7/core/engine.py) calls `Portfolio.process_signal()` sequentially through `combined.iterrows()`. |
| 52,490 bars/sec in 0.0245 seconds | Retain only as clearly labelled unverified historical example output. The [original README](https://github.com/yishoulee/alpha-foundry/blob/e9bfb38473e5b45ec8946694b7757c13897608e7/README.md) does not record hardware, package versions, data snapshot, strategy, row count, repeated timings, or logging conditions for that output. No exact reproduction is claimed. |
| Ten years of data processed in milliseconds | Remove as a general claim: “ten years” does not specify frequency or row count, and the historical workload is unidentified. Any new timing must identify its precise workload and whether it measures signals or the combined engine. |
| Timing instrumentation ensures high-frequency scalability | Remove. The engine records elapsed time; neither this instrumentation nor this audit establishes high-frequency suitability or a portable throughput guarantee. |
| A successful demo uses real 0050.TW data | Qualify. [main.py](https://github.com/yishoulee/alpha-foundry/blob/e9bfb38473e5b45ec8946694b7757c13897608e7/main.py) uses 500 synthetic bars when download fails or returns empty. The fallback is selected in `main.py`, not automatically inside the loader. Logs must establish provenance; chart titles alone cannot do so. |
| Tests validate performance | Unsupported. [test_engine.py](https://github.com/yishoulee/alpha-foundry/blob/e9bfb38473e5b45ec8946694b7757c13897608e7/tests/test_engine.py) checks mock calls and result fields/return arithmetic; there are no timing thresholds or benchmark fixtures in the inspected test suite. Describe these as unit tests; live download integration was not validated. |

## What the reported timer measures

`BacktestEngine.run()` uses `time.time()` around signal generation, the inner join, and sequential portfolio processing. `bars_per_sec = len(data) / total_duration`. The separate loop timer starts after the join, so signal time plus loop time need not equal total time.

The numerator is input rows, not explicitly counted processed rows. An arbitrary strategy with missing, extra, or duplicate index entries could change the joined row count. The two built-in strategies preserve the input index; the audit explicitly checked unique indexes, joined row counts, and portfolio equity row counts for every run.

Data retrieval/generation, engine construction, `get_results()`, tear-sheet calculations, and plotting are outside the internal timer. The [reporting code](https://github.com/yishoulee/alpha-foundry/blob/e9bfb38473e5b45ec8946694b7757c13897608e7/core/reporting.py) prints these engine metrics; it does not run an independent performance benchmark.

## Execution limits and test results

The ordinary `python -m unittest discover tests` attempt completed 10 tests but had two test-module import errors: `test_engine` and `test_data_loader` could not import missing `yfinance`. An isolated `pip install yfinance` attempt returned “No matching distribution found for yfinance.” This is an environment limitation, not a demonstrated application defect.

For the scoped offline audit, the harness below inserts a `yfinance` import shim only when the package is unavailable. Its `download()` raises an error if called. The real loader, engine, strategies, portfolio, and numerical libraries are executed unchanged. No downloader is called by the benchmark; the repository's downloader tests already mock that call.

Under this explicitly limited harness, **17 tests passed, with zero errors or failures**. This is not an unqualified pass of the normal installed application. No live Yahoo Finance download, complete `main.py` run, financial report, chart, or performance regression test was validated.

## Controlled measurements

Run recorded at `2026-10-29T23:16:14.139600+08:00` (Asia/Taipei).

| Environment | Recorded value |
| --- | --- |
| python | `3.12.14 (main, Aug 25 2026, 14:00:49) [Clang 22.1.3 ]` |
| numpy | `2.3.5` |
| pandas | `2.2.3` |
| os | `Linux-6.18.55-x86_64-with-glibc2.39` |
| cpu | `AMD EPYC 9V74 80-Core Processor` |
| logical_cpus | `9` |
| cpu_quota | `800000 100000` |
| memory_limit_bytes | `8589934592` |
| yfinance_import_shim | `True` |

The container exposes 9 logical CPUs, with a CPU quota equivalent to 8 CPUs and an 8 GiB memory limit. CPU affinity, frequency and competing host workloads were not controlled. These are measurements from one shared environment, not cross-machine performance guarantees.

- Data: the unchanged `DataLoader.generate_dummy_data(days=n)`, reseeded with `np.random.seed(20261029)` for each size; 500 and 10,000 daily synthetic OHLCV bars. Price columns are float64; volume is int64. No real-market data was used.
- Strategies: momentum (20/50 windows) and mean reversion (window 20, 2 standard deviations), matching `main.py`. Capital 100,000; transaction cost 0.002; slippage 0.0005.
- Three warm-up calls, then 15 recorded calls per strategy/size for each of two separate measurements: signal-only and combined engine. Fresh strategy/portfolio/engine per engine call. Data generated once per size outside timing; setup and `gc.collect()` outside timing; garbage collection enabled.
- Logging disabled with `logging.disable(logging.CRITICAL)`; this differs from the demo defaults and can affect throughput. No download time, report time, or object setup is included.
- Combined results retain the engine's existing `time.time()` measurement. An outer monotonic `perf_counter_ns()` timer checks the complete `engine.run()` call. Signal-only timings independently wrap `generate_signals()` with `perf_counter_ns()`. All raw samples are retained below.

| Strategy | Bars | Independent signal median (ms) | Combined engine median (ms) | Median input bars/sec | Input bars/sec min–max | Outer-call median (ms) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| momentum_20_50 | 500 | 1.209 | 8.132 | 61,487 | 55,948–63,996 | 8.150 |
| mean_reversion_20_2 | 500 | 1.662 | 8.430 | 59,315 | 53,500–60,517 | 8.452 |
| momentum_20_50 | 10,000 | 1.520 | 138.778 | 72,058 | 65,379–78,752 | 138.819 |
| mean_reversion_20_2 | 10,000 | 2.504 | 138.994 | 71,946 | 63,832–79,845 | 139.031 |

These observations show that throughput in the vicinity of the historical example is plausible under specific synthetic conditions. They do **not** verify the original 52,490 bars/sec run, establish real-market-data provenance, justify a fully vectorized-engine claim, or establish a minimum supported speed. The portfolio summaries therefore use implementation evidence without a speed headline.

Input fingerprints are SHA-256 of `data.to_csv(float_format="%.17g", lineterminator="\n").encode()`.

| Bars | Synthetic index range | Input SHA-256 |
| ---: | --- | --- |
| 500 | 2020-01-01 00:00:00 to 2021-05-14 00:00:00 | `f75b857ccb685afd145eed9e56cce00c4bb5f5ca7d1add607c69235bfc64c5e8` |
| 10,000 | 2020-01-01 00:00:00 to 2047-05-18 00:00:00 | `2539f442255a053c6701d15fc49fdc1bf4654b018d8a36899c2fbdb9560ee907` |

Dates beyond the audit date are synthetic index labels, not observed or forecast market data. Both strategies used the same data at each size; input fingerprints remained unchanged after all runs.

## Reproduction harness

Use the pinned Alpha Foundry source above, Python 3.12.14, Pandas 2.2.3, and NumPy 2.3.5. Save the following as `../benchmark_audit.py` outside the repository and run `python ../benchmark_audit.py` from its root. The audit environment lacked yfinance; the harness records whether its explicit import shim is used. It writes `../benchmark-results.json` with full metadata and samples. This code is documentation for an external audit, not an application or CI change.

```python
"""Offline audit harness; run from the pinned alpha-foundry repository root.

No application source changes. The unavailable yfinance import is satisfied by
an explicit download-blocking shim; no download/integration path is benchmarked.
"""
import gc
import hashlib
import importlib.util
import json
import logging
import os
import platform
import statistics
import sys
import time
import types
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path.cwd()))
shim_used = importlib.util.find_spec('yfinance') is None
if shim_used:
    yf = types.ModuleType('yfinance')
    def blocked_download(*args, **kwargs):
        raise RuntimeError('Downloads are disabled in this offline audit')
    yf.download = blocked_download
    sys.modules['yfinance'] = yf

import numpy as np
import pandas as pd
from core.data_loader import DataLoader
from core.engine import BacktestEngine
from core.portfolio import Portfolio
from strategies.momentum import MomentumStrategy
from strategies.mean_reversion import MeanReversionStrategy

logging.disable(logging.CRITICAL)
suite = unittest.defaultTestLoader.discover('tests')
test_result = unittest.TextTestRunner(verbosity=2).run(suite)
if not test_result.wasSuccessful():
    raise SystemExit('Offline unit tests failed')

WARMUPS, REPEATS, SEED = 3, 15, 20261029
factories = {
    'momentum_20_50': lambda: MomentumStrategy(short_window=20, long_window=50),
    'mean_reversion_20_2': lambda: MeanReversionStrategy(window=20, num_std=2),
}

def summary(values):
    return {'min': min(values), 'median': statistics.median(values), 'max': max(values)}

def digest(data):
    return hashlib.sha256(data.to_csv(float_format='%.17g', lineterminator='\n').encode()).hexdigest()

cpu = next((line.split(':',1)[1].strip() for line in Path('/proc/cpuinfo').read_text().splitlines()
            if line.startswith('model name')), 'unknown')
output = {
    'source_commit': 'e9bfb38473e5b45ec8946694b7757c13897608e7',
    'run_time_taipei': datetime.now(ZoneInfo('Asia/Taipei')).isoformat(),
    'environment': {
        'python': sys.version, 'numpy': np.__version__, 'pandas': pd.__version__,
        'os': platform.platform(), 'cpu': cpu, 'logical_cpus': os.cpu_count(),
        'cpu_quota': Path('/sys/fs/cgroup/cpu.max').read_text().strip(),
        'memory_limit_bytes': Path('/sys/fs/cgroup/memory.max').read_text().strip(),
        'yfinance_import_shim': shim_used,
    },
    'method': {
        'warmups': WARMUPS, 'repeats': REPEATS, 'seed': SEED,
        'data': 'DataLoader.generate_dummy_data; RNG reseeded for each size; no network',
        'logging': 'logging.disable(logging.CRITICAL) before tests and measurements',
        'engine_timing': 'Original time.time() boundaries, signal generation + join + sequential accounting',
        'outer_timing': 'time.perf_counter_ns around engine.run only',
        'signal_timing': 'Separate generate_signals call with time.perf_counter_ns',
        'state': 'New strategy, portfolio and engine per run; setup and gc.collect outside timing; GC enabled',
        'excluded': ['data generation', 'object construction', 'downloads', 'imports', 'results', 'reports', 'charts'],
    },
    'tests': {'run': test_result.testsRun, 'failures': len(test_result.failures), 'errors': len(test_result.errors),
              'scope': 'Offline test suite with download-blocking import shim; downloader tests use repository mocks'},
    'workloads': [],
}
loader = DataLoader()
for n in (500, 10000):
    np.random.seed(SEED)
    data = loader.generate_dummy_data(days=n)
    before = digest(data)
    assert data.index.is_unique
    for name, factory in factories.items():
        signal_samples, engine_samples = [], []
        for repeat in range(WARMUPS + REPEATS):
            strategy = factory()
            gc.collect()
            started = time.perf_counter_ns()
            signals = strategy.generate_signals(data)
            elapsed = (time.perf_counter_ns() - started) / 1e9
            assert signals.index.equals(data.index)
            assert len(data.join(signals, how='inner')) == n
            if repeat >= WARMUPS:
                signal_samples.append(elapsed)
        for repeat in range(WARMUPS + REPEATS):
            portfolio = Portfolio(initial_capital=100000, transaction_cost=0.002, slippage=0.0005)
            engine = BacktestEngine(loader, portfolio, factory())
            gc.collect()
            started = time.perf_counter_ns()
            engine.run(data)
            outer_elapsed = (time.perf_counter_ns() - started) / 1e9
            assert len(portfolio.equity_curve) == n
            assert engine.execution_metrics['bars_processed'] == n
            if repeat >= WARMUPS:
                engine_samples.append({**engine.execution_metrics, 'outer_seconds': outer_elapsed})
        assert digest(data) == before
        row = {
            'strategy': name, 'bars': n, 'input_sha256_csv': before,
            'columns': {c: str(t) for c,t in data.dtypes.items()},
            'index_start': str(data.index[0]), 'index_end': str(data.index[-1]),
            'signal_only_seconds': summary(signal_samples),
            'engine_total_seconds': summary([x['Total Duration'] for x in engine_samples]),
            'engine_signal_seconds': summary([x['Signal Gen Time'] for x in engine_samples]),
            'engine_loop_seconds': summary([x['Backtest Loop Time'] for x in engine_samples]),
            'engine_bars_per_sec': summary([x['bars_per_sec'] for x in engine_samples]),
            'outer_seconds': summary([x['outer_seconds'] for x in engine_samples]),
            'signal_samples_seconds': signal_samples, 'engine_samples': engine_samples,
        }
        output['workloads'].append(row)
        print(name, n, json.dumps({k: row[k] for k in ('signal_only_seconds','engine_total_seconds','engine_bars_per_sec')}), flush=True)
Path('../benchmark-results.json').write_text(json.dumps(output, indent=2) + '\n')
```

## Raw recorded timings

Each line below is one recorded engine run; all durations are seconds. `signal_only_s` is the corresponding sample number from a **separate** signal-only series, not another timer within that engine run. Bars/sec can be recalculated as `bars / total_s`. Warm-ups are excluded.

```csv
strategy,bars,sample,total_s,engine_signal_s,loop_s,outer_s,signal_only_s
momentum_20_50,500,1,0.00804758071899414,0.001336812973022461,0.00630640983581543,0.008068482,0.001209437
momentum_20_50,500,2,0.008356332778930664,0.0012662410736083984,0.006679058074951172,0.008376865,0.001140403
momentum_20_50,500,3,0.00816035270690918,0.0014388561248779297,0.006285905838012695,0.008181471,0.001170038
momentum_20_50,500,4,0.007812976837158203,0.0012009143829345703,0.006191730499267578,0.007829623,0.001170208
momentum_20_50,500,5,0.007883071899414062,0.001218557357788086,0.0062007904052734375,0.007902141,0.0013112
momentum_20_50,500,6,0.008257627487182617,0.0012958049774169922,0.006571531295776367,0.008278637,0.001180063
momentum_20_50,500,7,0.007886886596679688,0.0011873245239257812,0.006310224533081055,0.007905257,0.001499262
momentum_20_50,500,8,0.007950782775878906,0.0012772083282470703,0.006279706954956055,0.007971206,0.001293033
momentum_20_50,500,9,0.008056402206420898,0.0013594627380371094,0.006253480911254883,0.008076453,0.001276367
momentum_20_50,500,10,0.008375406265258789,0.0014069080352783203,0.006493330001831055,0.008397526,0.001160364
momentum_20_50,500,11,0.008486747741699219,0.0012576580047607422,0.006758928298950195,0.008508854,0.00112521
momentum_20_50,500,12,0.008131742477416992,0.0013365745544433594,0.006335735321044922,0.008150474,0.001229297
momentum_20_50,500,13,0.007967233657836914,0.0013041496276855469,0.006262302398681641,0.007986659,0.001198741
momentum_20_50,500,14,0.00837850570678711,0.0013935565948486328,0.006526947021484375,0.008421132,0.001266132
momentum_20_50,500,15,0.008936882019042969,0.0017848014831542969,0.006584882736206055,0.008958469,0.001279772
mean_reversion_20_2,500,1,0.008904218673706055,0.001750946044921875,0.006706714630126953,0.008927052,0.001543389
mean_reversion_20_2,500,2,0.008379697799682617,0.0016932487487792969,0.00628972053527832,0.008398927,0.001512543
mean_reversion_20_2,500,3,0.008343696594238281,0.001592397689819336,0.006330966949462891,0.008364287,0.001723099
mean_reversion_20_2,500,4,0.008379697799682617,0.0017054080963134766,0.00627589225769043,0.008401782,0.001480064
mean_reversion_20_2,500,5,0.009084939956665039,0.0016369819641113281,0.007021427154541016,0.009109055,0.001534555
mean_reversion_20_2,500,6,0.008388757705688477,0.0017125606536865234,0.006273746490478516,0.008408713,0.001467705
mean_reversion_20_2,500,7,0.009345769882202148,0.0016989707946777344,0.0072519779205322266,0.009366381,0.001542327
mean_reversion_20_2,500,8,0.008715629577636719,0.0016825199127197266,0.006628513336181641,0.008736346,0.001769519
mean_reversion_20_2,500,9,0.00833272933959961,0.0016579627990722656,0.006281852722167969,0.008352678,0.001665312
mean_reversion_20_2,500,10,0.008429527282714844,0.001726388931274414,0.006308794021606445,0.008451627,0.001575287
mean_reversion_20_2,500,11,0.008492231369018555,0.0018088817596435547,0.00624394416809082,0.00851326,0.001902999
mean_reversion_20_2,500,12,0.008262157440185547,0.0015785694122314453,0.006256580352783203,0.008281591,0.001862137
mean_reversion_20_2,500,13,0.008888006210327148,0.001768350601196289,0.006648540496826172,0.00891275,0.001857701
mean_reversion_20_2,500,14,0.008504867553710938,0.0017309188842773438,0.006330251693725586,0.008524165,0.001661897
mean_reversion_20_2,500,15,0.008324384689331055,0.0016756057739257812,0.006255149841308594,0.008343514,0.002209249
momentum_20_50,10000,1,0.12698149681091309,0.0016596317291259766,0.12482786178588867,0.12701877,0.001519874
momentum_20_50,10000,2,0.13649630546569824,0.0018689632415771484,0.13412165641784668,0.136536008,0.00149047
momentum_20_50,10000,3,0.13441205024719238,0.0021300315856933594,0.13156557083129883,0.134476824,0.001541125
momentum_20_50,10000,4,0.13484668731689453,0.001710653305053711,0.1326448917388916,0.134885638,0.001675247
momentum_20_50,10000,5,0.12946438789367676,0.0016579627990722656,0.12732243537902832,0.129500568,0.00143134
momentum_20_50,10000,6,0.1391897201538086,0.001718759536743164,0.13685965538024902,0.139225057,0.001562096
momentum_20_50,10000,7,0.14082860946655273,0.0028939247131347656,0.13727617263793945,0.140867885,0.001388025
momentum_20_50,10000,8,0.14742517471313477,0.001617431640625,0.14485406875610352,0.147463835,0.001497239
momentum_20_50,10000,9,0.13208937644958496,0.0016548633575439453,0.12994170188903809,0.132128516,0.001554695
momentum_20_50,10000,10,0.13880419731140137,0.0017616748809814453,0.1365511417388916,0.13884023,0.001528586
momentum_20_50,10000,11,0.1408703327178955,0.0018754005432128906,0.1384439468383789,0.140907906,0.001851521
momentum_20_50,10000,12,0.1529550552368164,0.0031316280364990234,0.14915108680725098,0.152993363,0.001599733
momentum_20_50,10000,13,0.1296236515045166,0.0017275810241699219,0.1273491382598877,0.129660618,0.001449357
momentum_20_50,10000,14,0.14593195915222168,0.0021529197692871094,0.14299893379211426,0.145969029,0.001496368
momentum_20_50,10000,15,0.1387779712677002,0.0016565322875976562,0.13662958145141602,0.138818697,0.001421095
mean_reversion_20_2,10000,1,0.14335894584655762,0.0027985572814941406,0.13986825942993164,0.143399469,0.002077662
mean_reversion_20_2,10000,2,0.13860273361206055,0.0021409988403320312,0.13599705696105957,0.138637926,0.00228966
mean_reversion_20_2,10000,3,0.13609957695007324,0.00244903564453125,0.13302135467529297,0.136138616,0.002794398
mean_reversion_20_2,10000,4,0.12524199485778809,0.0021088123321533203,0.12259984016418457,0.125300768,0.002503602
mean_reversion_20_2,10000,5,0.1566600799560547,0.002572298049926758,0.15345454216003418,0.15669943,0.002513596
mean_reversion_20_2,10000,6,0.15437984466552734,0.002466440200805664,0.15125513076782227,0.154421268,0.002132023
mean_reversion_20_2,10000,7,0.14858484268188477,0.002415895462036133,0.14566898345947266,0.148627573,0.002157761
mean_reversion_20_2,10000,8,0.12591814994812012,0.002361297607421875,0.12304043769836426,0.125979288,0.002277492
mean_reversion_20_2,10000,9,0.13477563858032227,0.0022497177124023438,0.1320335865020752,0.134816519,0.002430181
mean_reversion_20_2,10000,10,0.13568615913391113,0.002167940139770508,0.1330118179321289,0.135726111,0.003947781
mean_reversion_20_2,10000,11,0.14099764823913574,0.002228975296020508,0.1381990909576416,0.141035838,0.002507037
mean_reversion_20_2,10000,12,0.13875126838684082,0.0024902820587158203,0.1357574462890625,0.13878806,0.0027485
mean_reversion_20_2,10000,13,0.14017844200134277,0.00286102294921875,0.13672733306884766,0.140220523,0.002346706
mean_reversion_20_2,10000,14,0.14220952987670898,0.002213716506958008,0.13950848579406738,0.142251404,0.003057934
mean_reversion_20_2,10000,15,0.1389937400817871,0.0023980140686035156,0.1360490322113037,0.139031307,0.002686616
```
