# Query Performance: Indexing `created_at`

## Target query

`post_list` sorts posts by `created_at DESC` (via `Meta.ordering` on `Post`).
This is exercised directly by:

```sql
SELECT * FROM hub_post ORDER BY created_at DESC LIMIT 20;
```

Measured against a table of ~50,000 `Post` rows, generated via:

```bash
python manage.py generate_bulk_posts --count=50000
```

## Before adding an index

```
Limit  (cost=2740.63..2740.68 rows=20 width=111) (actual time=19.034..19.040 rows=20 loops=1)
  ->  Sort  (cost=2740.63..2865.64 rows=50004 width=111) (actual time=19.030..19.033 rows=20 loops=1)
        Sort Key: created_at DESC
        Sort Method: top-N heapsort  Memory: 33kB
        ->  Seq Scan on hub_post  (cost=0.00..1410.04 rows=50004 width=111) (actual time=0.007..6.913 rows=50004 loops=1)
Planning Time: 0.785 ms
Execution Time: 19.164 ms
```

Postgres reads all 50,004 rows (`Seq Scan`), then sorts all of them in memory
(`Sort`, top-N heapsort) before returning the top 20. Both steps are driven by
the absence of any index that already stores rows in `created_at` order.

## After adding an index

Migration: `hub/migrations/0002_post_post_created_at_idx.py`

```python
class Meta:
    ordering = ["-created_at"]
    indexes = [
        models.Index(fields=["-created_at"], name="post_created_at_idx"),
    ]
```

```
Limit  (cost=0.29..1.18 rows=20 width=111) (actual time=0.794..0.825 rows=20 loops=1)
  ->  Index Scan using post_created_at_idx on hub_post  (cost=0.29..2219.35 rows=50004 width=111) (actual time=0.793..0.820 rows=20 loops=1)
Planning Time: 1.867 ms
Execution Time: 0.894 ms
```

Postgres walks the index directly in already-sorted order and stops after
the first 20 rows. No `Seq Scan`, no separate `Sort` step.

## Result

| | Before | After |
|---|---|---|
| Plan | Seq Scan → Sort → Limit | Index Scan → Limit |
| Execution Time | 19.164 ms | 0.894 ms |
| Improvement | — | ~21x faster |

## Why this matters

Without the index, every request to `post_list` forces Postgres to scan and
sort the entire `hub_post` table just to return the newest 20 posts. As the
table grows, this cost grows with it. The index lets Postgres retrieve rows
already in the required order, so the cost of returning the newest 20 posts
stays roughly constant regardless of total table size.