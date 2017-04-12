# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: xl_parser
"""

Module provides tools for parsing an excel file into Financials values.

====================  =========================================================
Attribute             Description
====================  =========================================================

DATA:

FUNCTIONS:
add_projections()          creates a EngineModel with projections values from xl

_build_fins_from_sheet()    builds LineItem structure
_check_xl_projections()     checks if upload xl projections is the right format
_populate_fins_from_sheet() writes projected line values to financials


CLASSES:
n/a
====================  =========================================================
"""



# Imports
import bb_exceptions
import openpyxl as xlio
import json

from openpyxl.formula import Tokenizer
from data_structures.serializers.chef.model_chef import ModelChef
from data_structures.modelling.business_unit import BusinessUnit
from data_structures.modelling.line_item import LineItem
from data_structures.modelling.time_line import TimeLine
from data_structures.modelling.time_period import TimePeriod
from data_structures.modelling.driver import Driver

from formula_manager import local_catalog as FC
from datetime import datetime, date, timedelta




# Other Globals
# EXCEL LOCATIONS:
# Note that first row in excel is 1, But first row in a row_list is row_list[0]
STATEMENT_COL = None
LINE_TITLE_COL = None
LINE_NAME_COL = None
PARENT_NAME_COL = None
COMPARISON_COL = None
SUM_DETAILS_COL = None
REPORT_COL = None
MONITOR_COL = None
PARSE_FORMULA_COL = None
ADD_TO_PATH_COL = None
BEHAVIOR_COL = None
ALERT_COMMENTARY_COL = None
STATUS_COL = None
TAGS_COL = None
FIRST_PERIOD_COL = None  # First column with a period date and line values

DATES_ROW = 1
TIMELINE_ROW = 2    # "Actual" or "Forecast"
FIRST_ROW = 3  # First row with LineItem data

MC = ModelChef()


def add_projections(xl_serial, engine_model):
    """


    add_projections(xl_serial, engine_model) -> EngineModel()

    --``xl_serial``     serialized string of an Excel workbook (".xlsx")
    --``engine_model``  instance of Engine Model

    Function takes a serialized Excel workbook in a specific format
    and converts it to an EngineModel with LineItem values. Model input will
    determine which model card on the web page we are adding projections to.

    Function delegates to:
        _check_xl_projections()
        _build_fins_from_sheet()
        _populate_fins_from_sheet()

    """
    model = engine_model

    # 1) Extract xl_serial. Make sure it is in the right format
    wb = xlio.load_workbook(xl_serial, data_only=True)  # Includes Values Only
    wb_f = xlio.load_workbook(xl_serial, data_only=False)  # Includes Formulas

    # For testing local excel files:
    # filename = r"C:\Workbooks\Forecast_Rimini8.xlsx"
    # wb = xlio.load_workbook(filename=filename, data_only=True)

    sheet = wb.worksheets[0]
    sheet_f = wb_f.worksheets[0]

    # Make sure sheet is valid format
    _check_xl_projection(sheet)

    model.tags.add(sheet.title.casefold())  # Tab Name triggers topic path

    # 2) Align model.time_line to ref_date. Add additional periods as needed
    header_row = sheet.rows[0]
    xl_dates = []
    for cell in header_row[FIRST_PERIOD_COL-1:]:
        if isinstance(cell.value, datetime):
            xl_dates.append(cell.value.date())

    first_date = xl_dates[0]
    if isinstance(first_date, str):
        first_date = datetime.strptime(first_date, "%Y-%m-%d").date()

    # set default timeline to only contain relevant dates
    new_timeline = TimeLine(model)
    model.set_timeline(new_timeline, overwrite=True)
    # model.time_line.build(first_date, fwd=len(xl_dates)-1, year_end=False)
    model.time_line.build(first_date, fwd=0, year_end=False)
    model.change_ref_date(first_date)

    proj_tl = model.time_line

    company = model.get_company()
    if not company:
        company = BusinessUnit(model.name)
        model.set_company(company)
        model.target = company

    # 3) Determine Line Structure from Excel upload
    _build_fins_from_sheet(company, sheet)

    # 4) Make sure actuals timeline has same structure
    actl_tl = model.get_timeline('monthly', name='actual')
    if not actl_tl:
        actl_tl = TimeLine(model)
        model.set_timeline(actl_tl, resolution='monthly', name='actual')

    # 5) Write values to both actuals and projected.
    _populate_fins_from_sheet(model, sheet, sheet_f)

    return model


def revise_projections(xl_serial, engine_model):
    """


    revise_projections(xl_serial, engine_model) -> EngineModel()

    --``xl_serial``     serialized string of an Excel workbook (".xlsx")
    --``engine_model``  instance of Engine Model

    Function revises projection values while keeping existing actuals values
    Function takes a serialized Excel workbook in a specific format
    and converts it to an EngineModel with LineItem values. 
    
    Function delegates to:
        _check_xl_projections()
        _build_fins_from_sheet()
        _populate_fins_from_sheet()

    """
    model = engine_model

    # 1) Extract xl_serial. Make sure it is in the right format
    wb = xlio.load_workbook(xl_serial, data_only=True)  # Includes Values Only
    wb_f = xlio.load_workbook(xl_serial, data_only=False)  # Includes Formulas

    # For testing local excel files:
    # filename = r"C:\Workbooks\Forecast_Rimini8.xlsx"
    # wb = xlio.load_workbook(filename=filename, data_only=True)

    sheet = wb.worksheets[0]
    sheet_f = wb_f.worksheets[0]

    # Make sure sheet is valid format
    _check_xl_projection(sheet)

    company = model.get_company()

    # 3) Determine Line Structure from Excel upload
    _build_fins_from_sheet(company, sheet)

    # 4) Make sure actuals timeline has same structure
    actl_tl = model.get_timeline('monthly', name='actual')
    if not actl_tl:
        actl_tl = TimeLine(model)
        model.set_timeline(actl_tl, resolution='monthly', name='actual')

    # 5) Write values to both actuals and projected.
    _populate_fins_from_sheet(model, sheet, sheet_f)



def _check_xl_projection(sheet):
    """


    _check_xl_projection(sheet) -> None

    --``sheet`` is an instance of openpyxl.WorkSheets

    Function checks if the uploaded excel sheet is in the right format.
    Raises Error if format is violated. Function also finds and sets the Column
    numbers for each field.
    """

    header_row = sheet.rows[0]

    # Next few columns can be in any order
    global STATEMENT_COL
    global LINE_TITLE_COL
    global LINE_NAME_COL
    global PARENT_NAME_COL
    global COMPARISON_COL
    global SUM_DETAILS_COL
    global REPORT_COL
    global MONITOR_COL
    global PARSE_FORMULA_COL
    global ADD_TO_PATH_COL
    global BEHAVIOR_COL
    global ALERT_COMMENTARY_COL
    global TAGS_COL
    global FIRST_PERIOD_COL
    global STATUS_COL

    for cell in header_row:
        if cell.value == "STATEMENT":
            STATEMENT_COL = cell.col_idx
        elif cell.value == "LINE_TITLE":
            LINE_TITLE_COL = cell.col_idx
        elif cell.value == "LINE_NAME":
            LINE_NAME_COL = cell.col_idx
        elif cell.value == "LINE_PARENT_NAME":
            PARENT_NAME_COL = cell.col_idx
        elif cell.value == "COMPARISON":
            COMPARISON_COL = cell.col_idx
        elif cell.value == "SUM_DETAILS":
            SUM_DETAILS_COL = cell.col_idx
        elif cell.value == "REPORT":
            REPORT_COL = cell.col_idx
        elif cell.value == "MONITOR":
            MONITOR_COL = cell.col_idx
        elif cell.value == "PARSE_FORMULA":
            PARSE_FORMULA_COL = cell.col_idx
        elif cell.value in ("ADD_TO_PATH", "TOPIC_FORMULA"):
            ADD_TO_PATH_COL = cell.col_idx
        elif cell.value == "BEHAVIOR":
            BEHAVIOR_COL = cell.col_idx
        elif cell.value == "ALERT_COMMENTARY":
            ALERT_COMMENTARY_COL = cell.col_idx
        elif cell.value == "STATUS":
            STATUS_COL = cell.col_idx
        elif cell.value == "TAGS":
            TAGS_COL = cell.col_idx
        elif isinstance(cell.value, datetime):
            FIRST_PERIOD_COL = cell.col_idx
            break

    if STATEMENT_COL is None:
        c = "No STATEMENT header!"
        raise bb_exceptions.ExcelPrepError(c)
    if LINE_TITLE_COL is None:
        c = "No LINE_TITLE header!"
        raise bb_exceptions.ExcelPrepError(c)
    if LINE_NAME_COL is None:
        c = "No LINE_NAME header!"
        raise bb_exceptions.ExcelPrepError(c)
    if PARENT_NAME_COL is None:
        c = "No LINE_PARENT_NAME header!"
        raise bb_exceptions.ExcelPrepError(c)

    # print(COMPARISON_COL,
    #       SUM_DETAILS_COL,
    #       REPORT_COL,
    #       MONITOR_COL,
    #       PARSE_FORMULA_COL,
    #       ADD_TO_PATH_COL,
    #       BEHAVIOR_COL,
    #       TAGS_COL,
    #       FIRST_PERIOD_COL)

    # Make sure everything after FIRST_PERIOD_COL is all in a date format.
    for cell in header_row[FIRST_PERIOD_COL-1:]:
        if cell.value is None and cell is header_row[FIRST_PERIOD_COL-1:][-1]:
            # Sometimes the last blank column cell is read in
            continue
        if not isinstance(cell.value, datetime):
            # # print(cell.value, type(cell.value))
            c = "Header in %s is not a datetime obj!" % cell.coordinate
            raise bb_exceptions.ExcelPrepError(c)


def _build_fins_from_sheet(bu, sheet):
    """


    _build_fins_from_sheet(financials, sheet) -> None

    --``bu`` is the instance of Business Unit we want build Financials on
    --``sheet`` is an instance of openpyxl.WorkSheet

    Function extracts information from 'sheet' to build the LineItem structure
    in 'financials'. Functions creates new statements if necessary.
    """
    financials = bu.financials  # SSOT Fins

    line = None

    # Loop through each row that contains LineItem information
    for row in sheet.iter_rows(row_offset=FIRST_ROW-1, column_offset=0):
        if not row[STATEMENT_COL-1].value:
            if line:
                line.xl.format.blank_row_after = True
            # Skip blank rows
            continue

        full_statement_name = row[STATEMENT_COL-1].value.casefold()
        statement_name = full_statement_name.split()[0]
        # IE: full_statement_name -> "Ending Balance Sheet"
        #     statement_name -> "ending"

        if statement_name in ("parameter", "parameters"):
            # Ignore parameters
            continue

        line_name = row[LINE_NAME_COL-1].value
        if not line_name:
            continue  # Must have line name

        line_title = row[LINE_TITLE_COL-1].value
        if not line_title:
            continue  # Must have line title

        parent_name = row[PARENT_NAME_COL-1].value or ""  # Always need a str.

        # # print(statement_name, line_name, parent_name)

        if not getattr(financials, statement_name, None):
            financials.add_statement(statement_name)
        statement = getattr(financials, statement_name)

        # Look for line in most specific area in case there are same names
        parent = statement.find_first(parent_name)
        line = statement.find_first(line_name)
        if line and line.relationships.parent is not statement:
            if parent:
                line = parent.find_first(line_name)
            else:
                # If line is already a detail, create a new line w/ same name
                line = None

        # # print("P:",parent)
        # # print("L:",line)
        if parent_name in ('', None, " "):
            if line:
                # Do nothing if top level line already exists
                pass
            else:
                # Add the top level lines to statement
                line = LineItem(line_name)
                statement.append(line)
        elif not parent and not line:
            # Create a parent line assuming it will be moved later
            parent = LineItem(parent_name)
            line = LineItem(line_name)
            statement.append(parent)
            parent.append(line)
        elif not parent and line:
            if line.relationships.parent is statement:
                # Remove old line with any details, attach to correct parent
                line = statement.find_first(line_name, remove=True)
                parent = LineItem(parent_name)
                statement.append(parent)
                parent.append(line)
            else:
                # If line is already a detail of another line, create new branch
                # 2 details can have the same name, but under different parents
                parent = LineItem(parent_name)
                line = LineItem(line_name)
                statement.append(parent)
                parent.append(line)
        elif parent and not line:
            line = LineItem(line_name)
            parent.append(line)
        elif parent and line:
            # Remove old line with any details, attach to correct parent
            line = statement.find_first(line_name, remove=True)
            parent.append(line)

        # Set line title must happen after line name is set
        line.set_title(line_title)

        # Add comparison ("<" or ">") as a tag for KPI and Covenant analysis
        if COMPARISON_COL:
            comparison_str = row[COMPARISON_COL-1].value
            if comparison_str in ('<', '<=', '>', '>='):
                # Only tag valid comparisons
                line.tags.add(comparison_str)

        # Add sum_details attribute if FALSE (TRUE is default for blank cells)
        if SUM_DETAILS_COL:
            sum_details = row[SUM_DETAILS_COL-1].value
            if sum_details in ("False", "FALSE", False, "No"):
                line.sum_details = False

        # Tag line with which summary report we want to display it on.
        if REPORT_COL:
            report_str = row[REPORT_COL-1].value
            if report_str:
                if report_str.casefold() in ('kpi', 'covenants', 'overall'):
                    # Only tag valid comparisons
                    line.tags.add(report_str)

        if MONITOR_COL:
            monitor_bool = row[MONITOR_COL-1].value
            if monitor_bool in ("True", "TRUE", True, "Yes"):
                line.tags.add('monitor')

        if PARSE_FORMULA_COL:
            parse_formula_bool = row[PARSE_FORMULA_COL-1].value
            if parse_formula_bool in ("True", "TRUE", True, "Yes"):
                line.tags.add('parse formula')

        if ADD_TO_PATH_COL:
            topic_formula_bool = row[ADD_TO_PATH_COL - 1].value
            if topic_formula_bool in ("True", "TRUE", True, "Yes"):
                new_path_line = LineItem(line.name)
                bu.stage.path.append(new_path_line)
                line.tags.add('topic formula')

        if ALERT_COMMENTARY_COL:
            alert_bool = row[ALERT_COMMENTARY_COL - 1].value
            if alert_bool in ("True", "TRUE", True, "Yes"):
                new_path_line = LineItem(line.name + " alert")
                new_path_line.tags.add('alert commentary')
                bu.stage.path.append(new_path_line)
                line.tags.add('alert commentary')

        # Tag line with one or more tags.
        tags_str = row[TAGS_COL-1].value
        if tags_str:
            tags_list = tags_str.split(",")
            for t in tags_list:
                new_tag = t.strip()  # Remove white space from both sides
                line.tags.add(new_tag)


def _populate_fins_from_sheet(engine_model, sheet, sheet_f):
    """


    _populate_fins_from_sheet() -> None

    --``engine_model`` is the instance of EngineModel
    --``sheet`` is an instance of openpyxl.WorkSheet with Values
    --``sheet_f`` is an instance of openpyxl.WorkSheet with Formulas as str

    Function extracts LineItem values from 'sheet' and writes them to
    'financials' for multiple periods. Function assumes that the structure
    for financials is already in place for every period.
    """
    model = engine_model
    bu = model.get_company()
    proj_tl = model.get_timeline('monthly', name='default')
    actl_tl = model.get_timeline('monthly', name='actual')
    ssot_fins = bu.financials

    # Loop across periods (Left to Right on Excel)
    for col in sheet.columns[FIRST_PERIOD_COL-1:]:
        dt = col[0].value.date()
        timeline_name = col[TIMELINE_ROW-1].value

        start_dt = date(dt.year, dt.month, 1)
        end_dt = date(dt.year, dt.month, 28)
        while end_dt.month == start_dt.month:
            end_dt += timedelta(1)
        end_dt -= timedelta(1)

        # Always add a proj_pd regardless of if something is forecast or actual
        proj_pd = proj_tl.find_period(dt)
        if not proj_pd:
            proj_pd = TimePeriod(start_date=start_dt,
                                 end_date=end_dt,
                                 model=model)
            proj_tl.add_period(proj_pd)

        actl_pd = actl_tl.find_period(dt)
        if timeline_name in ("True", "TRUE", True, "ACTUAL", "Actual"):
            if not actl_pd:
                actl_pd = TimePeriod(start_date=start_dt,
                                     end_date=end_dt,
                                     model=model)
                actl_tl.add_period(actl_pd)

        # Loop across Lines (Top to Down on Excel)
        for cell in col[FIRST_ROW-1:]:
            # Skip blank cells
            if cell.value in (None, ""):
                continue

            row_num = cell.row
            col_num = cell.col_idx

            statement_str = sheet.cell(row=row_num, column=STATEMENT_COL).value
            if not statement_str:
                continue
            statement_name = statement_str.split()[0].casefold()
            line_name = sheet.cell(row=row_num, column=LINE_NAME_COL).value
            parent_name = sheet.cell(row=row_num, column=PARENT_NAME_COL).value

            # Handle rows where we just want to add a parameter value
            if statement_name in ("parameters", "parameter"):
                if parent_name in ("Timeline", "timeline"):
                    if cell.value is not None:
                        actl_tl.parameters.add({line_name: cell.value})
                        proj_tl.parameters.add({line_name: cell.value})
                else:
                    if actl_pd:
                        actl_pd.parameters.add({line_name: cell.value})
                    if proj_pd:
                        proj_pd.parameters.add({line_name: cell.value})
                # # print("Param", cell.value)
                continue

            # # print(statement_name, line_name, parent_name)
            if actl_pd:
                actl_fins = bu.get_financials(actl_pd)
                actl_stmt = getattr(actl_fins, statement_name, None)
            proj_fins = bu.get_financials(proj_pd)
            proj_stmt = getattr(proj_fins, statement_name, None)

            # Always match number formats
            ssot_stmt = getattr(ssot_fins, statement_name)
            ssot_line = ssot_stmt.find_first(line_name)
            if cell.number_format and not ssot_line.xl.format.number_format:
                ssot_line.xl.format.number_format = cell.number_format

            # Status column
            if STATUS_COL:
                status_str = sheet.cell(row=row_num, column=STATUS_COL).value

                if status_str:
                    try:
                        status_dict = json.loads(status_str)
                    except ValueError:
                        c = "Invalid JSON String: " + status_str
                        raise bb_exceptions.BBAnalyticalError(c)

                    required_keys = {"style"}
                    missing_keys = required_keys - status_dict.keys()
                    if len(missing_keys) > 0:
                        c = "Missing Keys: " + missing_keys
                        raise bb_exceptions.BBAnalyticalError(c)

                    # If a key is "0.8", turn it into 0.8
                    for key in status_dict:
                        try:
                            float(key)
                        except ValueError:
                            continue
                        else:
                            status_value = status_dict.pop(key)
                            status_dict[float(key)] = status_value

                    # ssot_line.rules = status_dict
                    bu.stage.work_space[ssot_line.name] = status_dict

            # Behaviour column
            if BEHAVIOR_COL:
                behavior_str = sheet.cell(row=row_num, column=BEHAVIOR_COL).value

                if behavior_str:
                    try:
                        behavior_dict = json.loads(behavior_str)
                    except ValueError:
                        c = "Invalid JSON String: " + behavior_str
                        raise bb_exceptions.BBAnalyticalError(c)

                    required_keys = {"source", "statement", "horizon", "operation"}
                    if len(required_keys - behavior_dict.keys()) == 0:
                        if behavior_dict['operation'] == 'sum':
                            if not ssot_line.get_driver():
                                f_id = FC.by_name["rolling sum over time."]
                                formula = FC.issue(f_id)
                                data = dict()
                                data['source line'] = behavior_dict["source"]
                                data['statement'] = behavior_dict["statement"]
                                data['periods'] = behavior_dict["horizon"]
                                if behavior_dict.get('scale'):
                                    data['scale'] = behavior_dict['scale']

                                driver = model.drivers.get_or_create(
                                    line_name.casefold(),
                                    data,
                                    formula)
                                ssot_line.assign_driver(driver.id.bbid)
                    continue  # Don't parse or hardcode line if behavior exists

            # Look to see if Formula should be automatically imported
            cell_f = sheet_f.cell(row=row_num, column=col_num)

            can_parse = _parse_formula(sheet, cell_f, bu)

            # Otherwise, set the lowest level lines to a hardcoded value
            if can_parse is False:
                # Always populate projected statement. (Include Historical Actuals)
                _populate_line_from_cell(cell, line_name, parent_name, proj_stmt)

                if timeline_name in ("True", "TRUE", True, "ACTUAL", "Actual"):
                    _populate_line_from_cell(cell, line_name, parent_name, actl_stmt)


def _parse_formula(sheet, cell_f, bu):
    """


    _parse_formula(sheet, cell_f, bu) -> bool

    --``sheet`` is an instance of openpyxl.WorkSheet with Values
    --``cell_f`` is an instance of openpyxl.Cell with Formulas as str
    --``bu`` is the instance of EngineModel.BusinessUnit

    Function takes a formula string from excel and creates a driver that will
    provide the same value in the Blackbird Engine. Function returns False if
    it was not able to parse the formula and True if the driver was added.
    """

    row = cell_f.row
    col = cell_f.col_idx

    cell = sheet.cell(row=row, column=col)  # data only cell
    if cell.value is None:
        return False

    parse_formula_bool_cell = sheet.cell(row=row, column=PARSE_FORMULA_COL)
    if parse_formula_bool_cell.value not in ("True", "TRUE", True, "Yes"):
        return False

    line_name = sheet.cell(row=row, column=LINE_NAME_COL).value
    parent_name = sheet.cell(row=row, column=PARENT_NAME_COL).value
    stmt_name = sheet.cell(row=row, column=STATEMENT_COL).value

    stmt_str = stmt_name.casefold().split()[0]
    statement = getattr(bu.financials, stmt_str)

    ancestors = [line_name]
    if parent_name:
        ancestors.insert(0, parent_name)  # Insert in 1st position
    line = statement.find_first(*ancestors)

    if not line:
        print("No line found!", ancestors)
        return False

    formula_str = cell_f.value

    tok = Tokenizer(formula_str)
    try:
        tok.parse()
    except TypeError:
        # This Error will trigger if formula_str is not a str
        # # print(formula_str, type(formula_str))
        return False

    # # print("\n".join("%15s%15s%15s" % (i.value, i.type, i.subtype) for i in
    #                 Tokenizer("=$A$1*12+B1").items))

    if not isinstance(formula_str, str):
        return False
    elif "!" in formula_str:
        return False  # Don't include other tabs "=Sheet2!A1"
    else:
        for t in tok.items:
            if t.type == "FUNC" and t.subtype in ("OPEN", "CLOSE"):
                # # print(t.value)
                if t.value in ("IF(", "MAX(", "MIN(", "ROUND(", ")"):
                    # Allow simple functions like "=MAX(A1,B1)"
                    pass
                else:
                    # Don't include all other functions like "=SUM(A1)"
                    return False
            if ":" in t.value and t.subtype == "RANGE":
                return False  # Don't include ranged sources "A1:A8"

    f_id = FC.by_name["custom formula from tokens."]
    formula = FC.issue(f_id)

    # if col == FIRST_PERIOD_COL:  # Only insert drivers in first column
    if not line.get_driver():
        data = dict()

        i = 0
        for t in tok.items:
            i += 1

            t_name = "token%02d" % i  # token01, token02, ... token99
            t_type = t_name + "_type"
            t_fixed_dt = t_name + "_fixed_date"
            t_rel_pd = t_name + "_relative_pd"

            # # print("Token Attr:", t_name, t.value, t.type, t.subtype)

            if t.type == "OPERAND" and t.subtype == "NUMBER":  # "100"
                data[t_name] = t.value
                data[t_type] = "constant"

            elif t.type == "OPERAND" and t.subtype == "LOGICAL":  # "TRUE"
                if t.value == "TRUE":
                    data[t_name] = True
                elif t.value == "FALSE":
                    data[t_name] = False
                # data[t_name] = t.value.title()  # "FALSE" -> "False"
                data[t_type] = "constant"

            elif t.type == "OPERAND" and t.subtype == "TEXT":  # "EBITDA < 0"
                # Should move these into bb_settings later
                ALLOWABLE_TEXT = [
                    "EBITDA<=0",
                    "Net Debt<=0",
                    "Overperforming",
                    "Performing",
                    "Needs Review",
                ]
                # t.value might be '"EBITDA<="'
                if t.value[1:-1] in ALLOWABLE_TEXT:
                    data[t_name] = t.value
                else:
                    data[t_name] = ""

                data[t_type] = "constant"

            elif t.type == "OPERAND" and t.subtype == "RANGE":  # "A1"
                source_addr = t.value
                source_cell = sheet.cell(source_addr)
                source_row = source_cell.row
                source_col = source_cell.col_idx

                source_line_name = sheet.cell(row=source_row,
                                              column=LINE_NAME_COL).value
                source_statement = sheet.cell(row=source_row,
                                              column=STATEMENT_COL).value
                source_statement = source_statement.split()[0].casefold()
                data[t_name] = source_line_name
                data[t_type] = "source"
                data[t_name + "_statement"] = source_statement
                if source_addr[0] == "$":
                    # Fixed Dates (source is always same column)
                    data[t_fixed_dt] = sheet.cell(row=DATES_ROW,
                                                  column=source_col).value
                elif source_col != cell_f.col_idx:
                    # Relative Periods (n periods past or future)
                    data[t_rel_pd] = source_col - cell_f.col_idx

            elif t.type == "OPERATOR-INFIX":  # +, -, *, /, =
                if t.value == "=":
                    # Equality comparisons are "=" in Excel and "==" in Python
                    data[t_name] = t.value = "=="
                else:
                    data[t_name] = t.value
                data[t_type] = "operator"

            elif t.type == "OPERATOR-PREFIX":  # 1st character +, -, *, /, =
                data[t_name] = t.value
                data[t_type] = "operator"

            elif t.type == "PAREN":  # "(" or ")"
                data[t_name] = t.value
                data[t_type] = "operator"

            elif t.type == "FUNC":
                if t.value in ("MAX(", "MIN(", "ROUND("):
                    # Excel functions same as lower case Python functions
                    data[t_name] = t.value.casefold()
                else:
                    # Excel functions require a custom Python function ie "IF()"
                    data[t_name] = t.value
                data[t_type] = "operator"

            elif t.type == "SEP" and t.subtype == "ARG":
                data[t_name] = t.value.casefold()
                data[t_type] = "operator"

        model = bu.relationships.model
        driver = model.drivers.get_or_create(line_name.casefold(), data,
                                             formula)
        line.assign_driver(driver.id.bbid)

    return True


def _populate_line_from_cell(cell, line_name, parent_name, statement):
    """


    _populate_fins_from_sheet() -> None

    --``cell``        Cell() instance from Openpyxl
    --``line_name``   string, name of LineItem we want to write to
    --``parent_name`` string or None, name of
    --``statement``   Statement() instance

    Function writes a hardcoded line value to a statement
    """
    value = cell.value
    if value is None:
        return

    parent = statement.find_first(parent_name or "")
    if parent:
        line = parent.find_first(line_name)
    else:
        line = statement.find_first(line_name)

    if line._details and line.sum_details:
        pass
        # if line.value is not None:
        #     if abs(value - line.value) > 0.1:  # Decimals
        #         # print("Upload Value:", value)
        #         # print("Detail Sum:", line.value)
        #         # print(line)
        #         c = "Warning! Sum of details do not match expected line value!"
        #         # print(c)
                # raise bb_exceptions.ExcelPrepError(c)
    else:
        line.set_value(value, "uploaded projections", override=True)
        line.set_hardcoded(True)

        # If the line is a hardcoded value, set a direct reference in excel
        sheet = cell.parent
        full_address = "'" + sheet.title + "'!" + cell.coordinate
        line.xl.reference.direct_source = full_address
        line._update_stored_xl()
