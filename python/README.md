# Graph visualisation with TypeDB
This is a utility library to help construct graphs & other structures from TypeQL query results.

## Install from pip
`typedb-graph-utils` is available on [pip](https://pypi.org/project/typedb-graph-utils/).
```shell
pip install typedb-graph-utils
```

## Install from source:
1. Ensure you have build
   * `python3 -m pip install build` 
2. Build (creates files under dist/) 
   * `python3 -m build` # Creates files under dist/
3. Install from the wheel created in the previous step:
   * `python3 -m pip install dist/typedb_graph_utils-<version>-py3-none-any.whl`

## Using the library
The main component of the library is the `TypeDBAnswerConverter` abstract class, which you must implement.
A sample implementation is provided in [networkx_builder.py](typedb_graph_utils/networkx_builder.py).
Example usage: 
```python
from typedb.driver import TransactionType, Credentials, DriverOptions, TypeDB, QueryOptions
from typedb_graph_utils import NetworkXBuilder, MatplotlibVisualizer

driver = TypeDB.driver("127.0.0.1:1729", Credentials("admin", "password"), DriverOptions(is_tls_enabled=False))
DB_NAME = "typedb_graph_utils_readme"
if DB_NAME in [db.name for db in driver.databases.all()]:
    driver.databases.get(DB_NAME).delete()
driver.databases.create(DB_NAME)
with driver.transaction(DB_NAME, TransactionType.READ) as tx:
    answers = list(tx.query("match let $x = 1;", QueryOptions(include_query_structure=True)).resolve())

builder = NetworkXBuilder(answers[0].query_structure())
for (i, answer) in enumerate(answers):
   builder.add_answer(i, answer)
graph = builder.finish()
MatplotlibVisualizer.draw(graph)
```
A longer tutorial is at [tutorial.ipynb](tutorial.ipynb)

## Testing
You don't have to "install from source".
1. Manually install the library dependencies
   * `python3 -m pip install -e .`
2. Manually install the dev dependencies 
   * `python3 -m pip install -e '.[dev]'`
3. Run tests:
   * `python3 -m pytest` 

## Run the sample
I created a 'main' in the tests file to visualise the graphs created by the tests. Run it:
`python3 -m tests.test_simple`
