from datetime import timedelta
import numpy as np

def modifications_perweek(data):
    authors = {}

    xs = []
    for author, updates in data.items():
        weeks = {}

        for info in updates:
            date          = info['date']
            deletions     = info['deletions']
            insertions    = info['insertions']
            files_changed = info['files changed']
            weekdate      = date.date() + timedelta(days=6-date.weekday())
            week_index    = weekdate.isoformat()
            #week_index    = date.isocalendar()#[1]
            
            xs.append(week_index)

            if week_index not in weeks: weeks[week_index] = 0
            weeks[week_index] += insertions + deletions
            
        authors[author] = weeks

    xs = sorted(list(set(xs)))

    res = {}
    for author, weeks in authors.items():
        res[author] = [(x, weeks[x] if x in weeks else 0) for x in xs]

    return res

def modifications_total(data):
    results = {}
    for author, updates in data.items():
        total = 0

        for info in updates:
            date          = info['date']
            deletions     = info['deletions']
            insertions    = info['insertions']
            files_changed = info['files changed']
            weekdate      = date.date() - timedelta(days=date.weekday())
            week_index    = date.isocalendar()[1]
            
            total += insertions + deletions
            
        results[author] = total

    return results