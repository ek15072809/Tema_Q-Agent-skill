---
name: xlsx
description: Generate advanced Microsoft Excel (.xlsx) files with openpyxl. Multi-sheet, formulas, charts, conditional formatting, data validation, defined names, pivot-style aggregation. Use for any real spreadsheet task.
---

# XLSX Skill

## Overview
Generate `.xlsx` files with the `openpyxl` library.
Output path: `/home/z/my-project/download/<filename>.xlsx`

## Required Library
```bash
pip install openpyxl
```

## Bundled Helper Module
**`skill/xlsx/scripts/xlsx_skill.py`** provides reusable helpers:
`new_wb`, `make_sheet`, `write_row`, `write_rows`,
`color_scale`, `highlight_equal`, `add_dropdown`,
`add_bar_chart`, `add_line_chart`, `define_name`, `save`.

Formula strings (`=SUM(...)`, `=VLOOKUP(...)`, `=XLOOKUP(...)` etc.) are
**not** wrapped — write them inline so the spreadsheet stays readable.

```python
import sys; sys.path.insert(0, "skill/xlsx/scripts")
from xlsx_skill import new_wb, make_sheet, write_rows, add_dropdown, save
```
Run `python skill/xlsx/scripts/xlsx_skill.py` to write a demo workbook and verify the install.

## Standard Template

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.workbook.defined_name import DefinedName

wb = Workbook()

# Shared styles
FONT_HEADER = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
FILL_HEADER = PatternFill('solid', fgColor='1A1A1A')
FONT_BODY = Font(name='Calibri', size=10)
THIN_BORDER = Border(
    left=Side(style='thin', color='CCCCCC'),
    right=Side(style='thin', color='CCCCCC'),
    top=Side(style='thin', color='CCCCCC'),
    bottom=Side(style='thin', color='CCCCCC'),
)
ALIGN_CENTER = Alignment(horizontal='center', vertical='center', wrap_text=True)
ALIGN_LEFT = Alignment(horizontal='left', vertical='center', wrap_text=True)
```

## Sheet with Header Row

```python
def make_sheet(wb, name, headers, col_widths=None):
    ws = wb.create_sheet(name)
    for i, h in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=i, value=h)
        cell.font = FONT_HEADER
        cell.fill = FILL_HEADER
        cell.alignment = ALIGN_CENTER
        cell.border = THIN_BORDER
        if col_widths and i <= len(col_widths):
            ws.column_dimensions[get_column_letter(i)].width = col_widths[i-1]
    ws.row_dimensions[1].height = 28
    ws.freeze_panes = 'A2'  # freeze header row
    return ws

def write_row(ws, row_idx, values):
    for i, v in enumerate(values, start=1):
        cell = ws.cell(row=row_idx, column=i, value=v)
        cell.font = FONT_BODY
        cell.border = THIN_BORDER
        if isinstance(v, (int, float)):
            cell.alignment = Alignment(horizontal='right', vertical='center')
        else:
            cell.alignment = ALIGN_LEFT
```

## Key Formula Patterns

### Basic Aggregation
```python
# SUM
ws['D1'] = 'Total'
ws['D2'] = '=SUM(B2:B100)'

# AVERAGE
ws['D3'] = '=AVERAGE(B2:B100)'

# COUNTIF
ws['D4'] = '=COUNTIF(C2:C100,"Done")'

# SUMIF
ws['D5'] = '=SUMIF(C2:C100,"Done",B2:B100)'
```

### Lookup
```python
# VLOOKUP
ws['E2'] = '=VLOOKUP(A2,Sheet2!A:C,3,FALSE)'

# XLOOKUP (recommended, modern Excel)
ws['F2'] = '=XLOOKUP(A2,Sheet2!A:A,Sheet2!C:C,"Not found")'

# INDEX + MATCH (most flexible)
ws['G2'] = '=INDEX(Sheet2!C:C,MATCH(A2,Sheet2!A:A,0))'
```

### Array Formulas
```python
# Dynamic arrays (Excel 365+)
ws['H2'] = '=FILTER(A2:C100,C2:C100="Done")'
ws['H3'] = '=SORT(UNIQUE(A2:A100))'
ws['I2'] = '=SUMPRODUCT((B2:B100>100)*(C2:C100="Done"))'
```

### Date Functions
```python
ws['J2'] = '=TODAY()'
ws['J3'] = '=EDATE(J2,3)'            # 3 months later
ws['J4'] = '=NETWORKDAYS(J2,J3)'     # business days
ws['J5'] = '=WEEKDAY(J2,2)'          # day of week (1=Mon)
```

### Text Functions
```python
ws['K2'] = '=CONCAT(A2,"-",B2)'
ws['K3'] = '=TEXT(C2,"#,##0")'
ws['K4'] = '=LEFT(A2,3)'
ws['K5'] = '=SUBSTITUTE(A2,"old","new")'
```

## Conditional Formatting

```python
# Color scale (data-bar alternative)
ws.conditional_formatting.add(
    'B2:B100',
    ColorScaleRule(
        start_type='min', start_color='FF6B6B',
        mid_type='percentile', mid_value=50, mid_color='FFEB3B',
        end_type='max', end_color='4CAF50'
    )
)

# Cell-value rules
ws.conditional_formatting.add(
    'C2:C100',
    CellIsRule(operator='equal', formula=['"Done"'],
               fill=PatternFill('solid', fgColor='C8E6C9'))
)
ws.conditional_formatting.add(
    'C2:C100',
    CellIsRule(operator='equal', formula=['"Pending"'],
               fill=PatternFill('solid', fgColor='FFCDD2'))
)
```

## Data Validation (Dropdowns)

```python
dv = DataValidation(
    type='list',
    formula1='"Pending,In Progress,Done,On Hold"',
    allow_blank=True
)
dv.error = 'Invalid value'
dv.errorTitle = 'Input Error'
ws.add_data_validation(dv)
dv.add('C2:C100')
```

## Chart Insertion

```python
def add_bar_chart(ws, title, data_ref, cats_ref, anchor='E2'):
    chart = BarChart()
    chart.type = 'col'
    chart.style = 10
    chart.title = title
    chart.y_axis.title = 'Value'
    chart.x_axis.title = 'Category'

    data = Reference(ws, min_col=data_ref[0], min_row=data_ref[1],
                     max_row=data_ref[2])
    cats = Reference(ws, min_col=cats_ref[0], min_row=cats_ref[1],
                     max_row=cats_ref[2])
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    chart.height = 10
    chart.width = 18
    ws.add_chart(chart, anchor)

def add_line_chart(ws, title, data_ref, cats_ref, anchor='E20'):
    chart = LineChart()
    chart.title = title
    chart.style = 12
    data = Reference(ws, min_col=data_ref[0], min_row=data_ref[1],
                     max_row=data_ref[2])
    cats = Reference(ws, min_col=cats_ref[0], min_row=cats_ref[1],
                     max_row=cats_ref[2])
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    ws.add_chart(chart, anchor)
```

## Defined Names

```python
def define_name(wb, name, sheet, range_str):
    """Assign a name to a range so formulas stay readable."""
    defn = DefinedName(name=name,
                       attr_text=f"'{sheet}'!{range_str}")
    wb.defined_names[name] = defn

# Usage
define_name(wb, 'SalesData', 'Sheet1', 'A2:D100')
ws['F1'] = '=SUM(SalesData)'
```

## Pivot Alternative (Formula Aggregation)

openpyxl cannot create real pivot tables. Build an aggregation sheet with SUMIF/COUNTIF instead:

```python
def make_pivot_like(wb, src_sheet, dest_name, key_col, val_col):
    """SUMIF-based aggregation sheet."""
    ws = wb.create_sheet(dest_name)
    ws['A1'] = 'Item'
    ws['B1'] = 'Count'
    ws['C1'] = 'Total'
    ws['D1'] = 'Average'
    # ... (UNIQUE extraction → SUMIF/COUNTIF per item)
```

## Output Workflow

1. **Clarify requirements**: purpose (aggregation / analysis / report / input form), sheet count, data volume
2. **Design structure**: input sheet → aggregation sheet → output sheet → dashboard
3. **Generate script**: `/home/z/my-project/scripts/gen_xlsx_<name>.py`
4. **Run**: `python scripts/gen_xlsx_<name>.py`
5. **Verify**: formula errors, #REF!, column widths, print area

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| #REF! error | Sheet-name refs must be `'Sheet Name'!` (quoted when space) |
| #VALUE! | Mixing strings and numbers inside a formula |
| Column too narrow | `column_dimensions['A'].width = 20` |
| Header not frozen | `ws.freeze_panes = 'A2'` mandatory |
| Page break awkward | `ws.page_setup.orientation = 'landscape'` |
| File won't open | Confirm `wb.save()` ran without error |

## Best Practices

- One sheet, one purpose (separate input / calc / display)
- Keep input and calculation sheets separate (prevents accidental edits)
- Use defined names for readability
- Freeze header row + color it
- Numbers right-aligned, text left-aligned
- For large datasets, consider `read_only=False` + `write_only=True`
