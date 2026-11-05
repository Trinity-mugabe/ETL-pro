# Building a Retail Data Pipeline

This project prepares Walmart weekly grocery sales for holiday-related supply
and demand analysis.

## Data sources

- `grocery_sales`: a PostgreSQL table containing store IDs, sales dates, and
  weekly sales.
- `extra_data.parquet`: complementary holiday, store, department, and economic
  data.

## Expected outputs

The pipeline should create and export:

- `clean_data.csv`: `Store_ID`, `Month`, `Dept`, `IsHoliday`,
  `Weekly_Sales`, `CPI`, and `Unemployment`.
- `agg_data.csv`: monthly `Weekly_Sales` aggregates.

The Python entry point is `retail_data_pipeline.py`. Run this query in your
PostgreSQL SQL cell, then pass the resulting `grocery_sales` DataFrame to the
pipeline:

```sql
SELECT * FROM grocery_sales;
```

```python
from retail_data_pipeline import run_pipeline

clean_data, agg_data = run_pipeline(grocery_sales)
```

The pipeline expects `extra_data.parquet` in the current directory by default.
You can override the input and output paths with the optional arguments to
`run_pipeline`.

Install dependencies with:

```shell
python -m pip install -r requirements.txt
```
