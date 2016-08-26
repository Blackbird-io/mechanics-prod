# PROPRIETARY AND CONFIDENTIAL
# Property of Blackbird Logical Applications, LLC
# Copyright Blackbird Logical Applications, LLC 2016
# NOT TO BE CIRCULATED OR REPRODUCED WITHOUT PRIOR WRITTEN APPROVAL

# Blackbird Environment
# Module: serializers.chef.unit_chef
"""

Module defines a class that represents arbitrarily rich BusinessUnit instances
as a collection of linked Excel worksheets.
====================  =========================================================
Attribute             Description
====================  =========================================================

DATA:
n/a

FUNCTIONS:
n/a

CLASSES:
UnitChef              class containing methods to chop BusinessUnits into
                      dynamic Excel structures
====================  =========================================================
"""




# Imports
import openpyxl as xlio

from ._chef_tools import add_scenario_selector, group_lines
from .cell_styles import CellStyles
from .data_types import TypeCodes
from .field_names import FieldNames
from .formulas import FormulaTemplates
from .line_chef import LineChef
from .sheet_style import SheetStyle
from .tab_names import TabNames

from chef_settings import SCENARIO_SELECTORS, VALUATION_TAB_COLOR, \
                            APPLY_COLOR_TO_DECEMBER, DECEMBER_COLOR
from data_structures.modelling import common_events
from openpyxl.styles import PatternFill



# Constants
# n/a

# Module Globals
_INVALID_CHARS = r"\/*[]:?"
# Excel forbids the use of these in sheet names.
REPLACEMENT_CHAR = None
# When the replacement character is None, UnitChef will remove all bad chars
# from sheet titles.

bad_char_table = {ord(c): REPLACEMENT_CHAR for c in _INVALID_CHARS}
# May be this should be on the UnitChef class itself

cell_styles = CellStyles()
field_names = FieldNames()
formula_templates = FormulaTemplates()
sheet_style = SheetStyle()
tab_names = TabNames()
type_codes = TypeCodes()

get_column_letter = xlio.utils.get_column_letter

line_chef = LineChef()


# Classes
class UnitChef:
    """

    One tab per unit
    Children first
    Arbitrarily recursive (though should max out at sheet limit; alternatively,
    book should prohibit new sheets after that? or can have 2 limits: a soft
    limit where ModelChopper shifts into different representation mode, and a
    hard limit, where you just cant create any more sheets.)

    Most non-public methods force keyword-based arg entry to avoid potentially
    confusing erros (switching rows for columns, etc.)

    Methods generally leave current row pointing to their last completed
    (filled) row.

    ====================  =====================================================
    Attribute             Description
    ====================  =====================================================

    DATA:
    MAX_CONSOLIDATION_ROWS = 15
    MAX_LINKS_PER_CELL = 1

    MAX_TITLE_CHARACTERS = 30
    SHOW_GRID_LINES = False
    ZOOM_SCALE = 80

    FUNCTIONS:
    add_items_to_area()   adds dictionary items to specified area
    chop_multi()          returns sheet with a SheetData instance at sheet.bb,
                          also spreads financials, life, parameters of units
    chop_unit()           returns sheet with a SheetData instance at sheet.bb
    ====================  =====================================================
    """
    MAX_CONSOLIDATION_ROWS = 15
    MAX_LINKS_PER_CELL = 1

    MAX_TITLE_CHARACTERS = 30

    LABEL_COLUMN = 2
    MASTER_COLUMN = 4
    VALUE_COLUMN = 6

    TITLE_ROW = 3
    VALUES_START_ROW = 6

    SCENARIO_ROW = 2


    def add_items_to_area(self, *pargs, sheet, area, items, active_column,
                          set_labels=True, format_func=None, hardcoded=False,
                          preference_order=[]):
        """


        UnitChef.add_items_to_area() -> Worksheet

        --``sheet`` must be an instance of Worksheet
        --``area`` must be an instance of Area
        --``items`` must be a dictionary of items to add
        --``active_column`` must be current column index
        --``set_labels`` must be a boolean; whether or not to label row
        --``format_func`` is a function to use on cells for formatting
        Method adds names to Area in sorted order.  Method starts work after
        the current row and expects sheet to come with parameters unless you
        specify the label and master column.
        """

        parameters = getattr(sheet.bb, field_names.PARAMETERS)
        label_column = parameters.columns.get_position(field_names.LABELS)
        master_column = parameters.columns.get_position(field_names.MASTER)

        sheet_style.set_column_width(sheet, master_column)

        starting = sheet.bb.current_row or 0
        new_row = starting + 1

        for name in self._sort_bypreference(items, preference_order or []):
            value = items[name]

            # Register the new row
            area.rows.by_name[name] = new_row

            # Add the label
            if set_labels:
                label_cell = sheet.cell(column=label_column, row=new_row)
                label_cell.value = name
                # Or run through labels routine

            # Add the master value (from this period)
            master_cell = sheet.cell(column=master_column, row=new_row)
            master_cell.value = value
            cell_styles.format_parameter(master_cell)
            cell_styles.format_hardcoded(master_cell)

            # Link the period to the master
            current_cell = sheet.cell(column=active_column, row=new_row)
            link = formula_templates.ADD_COORDINATES
            link = link.format(coordinates=master_cell.coordinate)
            current_cell.set_explicit_value(link, data_type=type_codes.FORMULA)
            cell_styles.format_parameter(current_cell)

            if format_func:
                format_func(master_cell)
                format_func(current_cell)

            sheet.bb.current_row = new_row
            group_lines(sheet)
            new_row += 1

        return sheet

    def chop_multi(self, *pargs, book, unit):
        """


        UnitChef.chop_multi() -> Worksheet

        --``book`` must be a Workbook
        --``unit`` must be an instance of BusinessUnit

        Method recursively walks through ``unit`` and components and chops them
        into Excel format.  Method also spreads financials, parameters, and
        life of the unit.
        """

        # 1.   Chop the children
        before_kids = len(book.worksheets)
        children = unit.components.get_ordered()

        for child in children:
            self.chop_multi(book=book, unit=child)

        # 2.   Chop the parent
        #
        # In this block, we have to set the current row to the place where the
        # last area ends before running the breadth-wise routines. Otherwise,
        # they would treat the ending row of the last period as their own
        # starting row, and the spreadsheet would look like a staircase.

        # 2.1.   set up the unit sheet and spread params
        sheet = self._create_unit_sheet(book=book, unit=unit,
                                        index=before_kids)
        sheet.bb.outline_level += 1

        # 2.2.   spread life
        sheet.bb.current_row += 1
        sheet = self._add_unit_life(sheet=sheet, unit=unit)
        param_area = getattr(sheet.bb, field_names.PARAMETERS)
        for snapshot in unit:
            sheet.bb.current_row = param_area.rows.ending + 1
            self._add_unit_life(sheet=sheet, unit=snapshot, set_labels=False)
        sheet.bb.outline_level -= 1

        # 2.3. add unit size
        sheet.bb.current_row += 2
        self._add_unit_size(sheet=sheet, unit=unit, set_labels=True)
        for snapshot in unit:
            sheet.bb.current_row = sheet.bb.size.rows.ending
            self._add_unit_size(sheet=sheet, unit=snapshot, set_labels=False)

        sheet.bb.outline_level += 1
        group_lines(sheet, sheet.bb.size.rows.ending)
        sheet.bb.outline_level -= 1

        # 2.4.  spread fins
        current = sheet.bb.time_line.columns.get_position(unit.period.end)
        fins_dict = self._add_financials(sheet=sheet, unit=unit,
                                         column=current)

        for snapshot in unit:
            sheet.bb.current_row = sheet.bb.size.rows.ending
            column = sheet.bb.time_line.columns.get_position(
                snapshot.period.end)
            # Load balance from prior column!!!

            self._add_financials(sheet=sheet, unit=snapshot, column=column,
                                 set_labels=False)

            # Should make sure rows align here from one period to the next.
            # Main problem lies in consolidation logic.

        # 2.5 add area and statement labels and sheet formatting
        sheet_style.style_sheet(sheet)

        for statement, row in fins_dict.items():
            cell_styles.format_area_label(sheet, statement, row)

        # # 2.6 add selector cell
        #   Make scenario label cells
        self._add_scenario_selector_logic(book, sheet)

        # Color the December columns
        if APPLY_COLOR_TO_DECEMBER:
            for date, column in sheet.bb.time_line.columns.by_name.items():
                if date.month == 12:
                    for row in range(1, sheet.max_row+1):
                        cell = sheet.cell(column=column, row=row)
                        cell.fill = PatternFill(start_color=DECEMBER_COLOR,
                                                end_color=DECEMBER_COLOR,
                                                fill_type='solid')

        return sheet

    def chop_multi_valuation(self, *pargs, book, unit, index, recur=False):
        """


        UnitChef.chop_multi_valuation() -> Worksheet

        --``book`` must be a Workbook
        --``unit`` must be an instance of BusinessUnit

        Method recursively walks through ``unit`` and components and will chop
        their valuation if any exists.
        """

        # 1.   Chop the children
        if recur:
            before_kids = len(book.worksheets)
            children = unit.components.get_ordered()

            for child in children:
                index = book.get_index(child.xl.sheet) - 1
                self.chop_multi_valuation(book=book, unit=child,
                                          index=index, recur=recur)

        # 2.6 add valuation tab, if any exists for unit
        if unit.financials.has_valuation:
            self._add_valuation_tab(book, unit, index=index)

    # *************************************************************************#
    #                          NON-PUBLIC METHODS                              #
    # *************************************************************************#

    def _add_statement_rows(self, sheet, statement, title=None):
        """

        UnitChef._add_statement() -> AxisGroup

        """
        statement_group = sheet.bb.row_axis.get_group('statements')
        statement_group.calc_size()

        offset = 1 if statement_group.size else 0
        name = title or statement.name
        statement_rows = statement_group.add_group(name, offset=offset)
        statement_rows.add_group('title', title=name, size=1)
        statement_rows.add_group('matter', size=0)

        return statement_rows

    def _add_financials(self, *pargs, sheet, unit, column, set_labels=True):
        """

        UnitChef._add_financials() -> dict

        Method adds financials to worksheet and returns a dictionary of the
        statements added to the worksheet and their starting rows
        """
        fins_dict = dict()

        sheet.bb.row_axis.add_group(
            'statements',
            offset=sheet.bb.current_row + 1
        )

        for statement in unit.financials.ordered:
            if statement is not None:
                sheet.bb.current_row += 1
                sheet.bb.outline_level = 0

                if statement is unit.financials.ending:
                    statement_row = sheet.bb.current_row + 1
                    fins_dict["Starting Balance Sheet"] = statement_row

                    statement_rows = self._add_statement_rows(
                        sheet, statement, title='Starting Balance Sheet'
                    )
                    line_chef.chop_starting_balance(
                          sheet=sheet,
                          unit=unit,
                          column=column,
                          row_container=statement_rows,
                          set_labels=set_labels
                    )
                    sheet.bb.need_spacer = False

                statement_row = sheet.bb.current_row + 1
                fins_dict[statement.tags.name] = statement_row

                statement_rows = self._add_statement_rows(sheet, statement)
                line_chef.chop_statement(
                    sheet=sheet,
                    statement=statement,
                    column=column,
                    row_container=statement_rows,
                    set_labels=set_labels,
                )

        # We're done with the first pass of chopping financials, now go back
        # and try to resolve problem_line issues.
        while sheet.bb.problem_lines:
            dr_data, materials = sheet.bb.problem_lines.pop()
            line_chef.attempt_reference_resolution(sheet, dr_data, materials)

        return fins_dict

    def _add_life_analysis(self, sheet, unit, active_column, set_labels=True):
        """


        UnitChef._add_life_analysis() -> Worksheet

        Method adds unit life for a single period to show unit state
        (alive/dead/etc.), age, etc.  Method assumes events are filled out.
        """
        parameters = getattr(sheet.bb, field_names.PARAMETERS)
        timeline = getattr(sheet.bb, field_names.TIMELINE)

        active_row = sheet.bb.current_row + 1

        label_column = parameters.columns.get_position(field_names.LABELS)
        time_line_row = timeline.rows.get_position(field_names.TITLE)

        fs = formula_templates
        set_label = line_chef._set_label

        events = sheet.bb.events
        life = sheet.bb.life

        birth = sheet.cell(
            column=active_column,
            row=events.rows.get_position(common_events.KEY_BIRTH)
        )
        death = sheet.cell(
            column=active_column,
            row=events.rows.get_position(common_events.KEY_DEATH)
        )
        conception = sheet.cell(
            column=active_column,
            row=events.rows.get_position(common_events.KEY_CONCEPTION)
        )

        cell_styles.format_date(birth)
        cell_styles.format_date(death)
        cell_styles.format_date(conception)

        cells = dict()
        cells["birth"] = birth
        cells["death"] = death
        cells["conception"] = conception

        # 1. Add ref_date
        sheet.bb.life.rows.by_name[field_names.REF_DATE] = active_row
        if set_labels:
            set_label(
                label=field_names.REF_DATE,
                sheet=sheet,
                row=active_row,
                column=label_column
            )

        ref_date = sheet.cell(column=active_column, row=active_row)
        cell_styles.format_date(ref_date)
        group_lines(sheet, row=active_row)

        time_line = sheet.cell(column=active_column, row=time_line_row)

        cells["ref_date"] = ref_date
        formula = fs.LINK_TO_COORDINATES.format(coordinates=time_line.coordinate)
        ref_date.value = formula

        del formula
        # Make sure each cell gets its own formula by deleting F after use.

        # Move down one row
        group_lines(sheet, row=active_row + 1)
        active_row += 1

        # 1. Add period start date
        sheet.bb.life.rows.by_name[field_names.START_DATE] = active_row
        if set_labels:
            set_label(
                label=field_names.START_DATE,
                sheet=sheet,
                row=active_row,
                column=label_column
            )

        start_date = sheet.cell(column=active_column, row=active_row)

        cell_styles.format_date(start_date)
        group_lines(sheet, row=active_row)
        cell_styles.format_date(start_date)
        start_date.value = unit.period.start

        # Move down two rows (to leave one blank)
        group_lines(sheet, row=active_row + 1)
        active_row += 2

        # 2. Add age
        sheet.bb.life.rows.by_name[field_names.AGE] = active_row
        if set_labels:
            set_label(
                label=field_names.AGE,
                sheet=sheet,
                row=active_row,
                column=label_column
            )

        age = sheet.cell(column=active_column, row=active_row)
        cell_styles.format_parameter(age)
        group_lines(sheet, row=active_row)

        cells["age"] = age
        cos = {k: v.coordinate for k, v in cells.items()}
        formula = fs.COMPUTE_AGE_IN_DAYS.format(**cos)

        age.set_explicit_value(formula, data_type=type_codes.FORMULA)
        del formula

        # Move row down
        active_row += 1

        # 3. Add alive
        life.rows.by_name[field_names.ALIVE] = active_row
        if set_labels:
            set_label(
                label=field_names.ALIVE,
                sheet=sheet,
                row=active_row,
                column=label_column
            )

        alive = sheet.cell(column=active_column, row=active_row)
        cell_styles.format_parameter(alive)
        group_lines(sheet, row=active_row)

        cells["alive"] = alive
        cos["alive"] = alive.coordinate
        formula = fs.IS_ALIVE.format(**cos)

        alive.set_explicit_value(formula, data_type=type_codes.FORMULA)
        del formula

        # Move row down
        active_row += 1

        # 4. Add span (so we can use it as the denominator in our percent
        #    computation below).
        life.rows.by_name[field_names.SPAN] = active_row
        if set_labels:
            set_label(
                label=field_names.SPAN,
                sheet=sheet,
                row=active_row,
                column=label_column
            )

        span = sheet.cell(column=active_column, row=active_row)
        cell_styles.format_parameter(span)
        group_lines(sheet, row=active_row)

        cells[field_names.SPAN] = span
        cos[field_names.SPAN] = span.coordinate
        formula = fs.COMPUTE_SPAN_IN_DAYS.format(**cos)

        span.set_explicit_value(formula, data_type=type_codes.FORMULA)
        del formula

        # Move row down
        active_row += 1

        # 5. Add percent
        life.rows.by_name[field_names.PERCENT] = active_row
        if set_labels:
            set_label(
                label=field_names.PERCENT,
                sheet=sheet,
                row=active_row,
                column=label_column
            )

        percent = sheet.cell(column=active_column, row=active_row)

        formula = fs.COMPUTE_AGE_IN_PERCENT.format(**cos)

        percent.set_explicit_value(formula, data_type=type_codes.FORMULA)

        group_lines(sheet, row=active_row)

        sheet.bb.current_row = active_row+1

        # Return sheet
        return sheet

    def _add_life_events(self, *pargs, sheet, unit, active_column):
        """


        UnitChef._add_life_events() -> Worksheet


        Method adds life events to unit Worksheet and returns updated sheet.
        Expects sheet to include areas for events and parameters.
        Runs through add_items() [which is why we get name-based sorting]
        """
        events = sheet.bb.events
        parameters = getattr(sheet.bb, field_names.PARAMETERS)

        active_row = sheet.bb.current_row
        master_column = parameters.columns.get_position(field_names.MASTER)

        existing_names = unit.life.events.keys() & events.rows.by_name.keys()
        new_names = unit.life.events.keys() - existing_names

        # Write values for existing events
        for name in existing_names:

            existing_row = events.rows.get_position(name)

            master_cell = sheet.cell(column=master_column, row=existing_row)
            active_cell = sheet.cell(column=active_column, row=existing_row)
            cell_styles.format_date(master_cell)

            event_date = unit.life.events[name]

            active_cell.value = event_date

            group_lines(sheet, existing_row)

            if master_cell.value == active_cell.value:
                link_template = formula_templates.ADD_COORDINATES
                link = link_template.format(coordinates=master_cell.coordinate)

                active_cell.set_explicit_value(link,
                                               data_type=type_codes.FORMULA)

                cell_styles.format_date(active_cell)

        # Now add
        new_events = dict()
        for name in new_names:
            new_events[name] = unit.life.events[name]

        self.add_items_to_area(
            sheet=sheet,
            area=events,
            items=new_events,
            active_column=active_column,
            format_func=cell_styles.format_date,
            preference_order=unit.life.ORDER
        )
        # Method will update current row to the last filled position.

        return sheet

    def _add_scenario_selector_logic(self, book, sheet):
        scen_tab = book.get_sheet_by_name(tab_names.SCENARIOS)
        src_sheet = scen_tab.title
        src_row = scen_tab.bb.general.rows.by_name[field_names.SELECTOR]

        scen_area = getattr(scen_tab.bb, field_names.PARAMETERS)
        num_col = scen_area.columns.by_name[field_names.CUSTOM_CASE]
        src_col = get_column_letter(num_col)

        info = dict(sheet=src_sheet, alpha_column=src_col, row=src_row)

        active_label_cell = sheet.cell(column=self.LABEL_COLUMN,
                                       row=self.SCENARIO_ROW)
        active_label_cell.value = field_names.IN_EFFECT

        template = formula_templates.LINK_TO_CELL_ON_SHEET
        link = template.format(**info)
        scen_cell = sheet.cell(column=self.MASTER_COLUMN,
                               row=self.SCENARIO_ROW)
        scen_cell.value = link

        if SCENARIO_SELECTORS:
            label_column = self.LABEL_COLUMN
            add_scenario_selector(sheet, label_column, self.SCENARIO_ROW,
                                  book.scenario_names)
        else:
            cell_styles.format_scenario_selector_cells(sheet,
                                                       self.LABEL_COLUMN,
                                                       self.MASTER_COLUMN,
                                                       self.SCENARIO_ROW,
                                                       active=False)

    def _add_unit_life(self, *pargs, sheet, unit, column=None,
                       set_labels=True):
        """


        UnitChef._add_unit_life() -> Worksheet

        Method adds life Area to unit sheet and delegates to
        UnitChef._add_life_events() and UnitChef._add_lif_analysis()
        Expects to get sheet with current row pointing to a blank
        Will start writing on current row
        """
        sheet_data = sheet.bb
        active_column = column

        if not active_column:
            end = unit.period.end
            active_column = sheet_data.time_line.columns.get_position(end)

        if not getattr(sheet_data, "life", None):
            sheet.bb.add_area("life")

        if not getattr(sheet_data, "events", None):
            sheet.bb.add_area("events")

        first_life_row = sheet.bb.current_row + 1
        first_event_row = first_life_row + 9
        # Leave nine rows for basic life layout

        sheet.bb.current_row = first_event_row
        sheet = self._add_life_events(
            sheet=sheet,
            unit=unit,
            active_column=active_column
        )

        sheet.bb.current_row = first_life_row
        sheet = self._add_life_analysis(
            sheet=sheet,
            unit=unit,
            active_column=active_column,
            set_labels=set_labels
        )

        sheet.bb.current_row = sheet.bb.events.rows.ending

        # Move current row down to the bottom (max_row() probably best here).
        return sheet

    def _add_unit_size(self, *pargs, sheet, unit, column=None,
                       set_labels=True):
        """


        UnitChef._add_unit_size() -> Worksheet

        Method adds "size" Area to unit sheet and populates it with values.
        Will start writing on current row.
        """
        active_column = column

        if not active_column:
            end = unit.period.end
            active_column = sheet.bb.time_line.columns.get_position(end)

        parameters = getattr(sheet.bb, field_names.PARAMETERS)
        master_column = parameters.columns.get_position(field_names.MASTER)

        if not getattr(sheet.bb, field_names.SIZE, None):
            size = sheet.bb.add_area(field_names.SIZE)

            item_dict = dict()
            item_dict[field_names.SIZE_LABEL] = unit.size

            self.add_items_to_area(
                sheet=sheet,
                area=size,
                items=item_dict,
                active_column=active_column,
                set_labels=set_labels,
                format_func=cell_styles.format_integer)

            size.rows.by_name[field_names.SIZE_LABEL] = sheet.bb.current_row
        else:
            size = getattr(sheet.bb, field_names.SIZE)

        # Write values for existing events
        existing_row = size.rows.get_position(field_names.SIZE_LABEL)

        master_cell = sheet.cell(column=master_column,
                                 row=existing_row)
        active_cell = sheet.cell(column=active_column,
                                 row=existing_row)

        active_cell.value = unit.size

        if master_cell.value == active_cell.value:
            link_template = formula_templates.ADD_COORDINATES
            link = link_template.format(coordinates=master_cell.coordinate)

            active_cell.set_explicit_value(link,
                                           data_type=type_codes.FORMULA)

        cell_styles.format_integer(active_cell)

        return sheet

    def _add_unit_params(self, *pargs, sheet, unit, timeline_params,
                         set_labels=True):
        """


        UnitChef._add_unit_params() -> Worksheet

        - Add any new unit parameters, place master value in MASTER column
        - Check on timeline_params and update with hardcoded value as applicable
        """
        parameters = getattr(sheet.bb, field_names.PARAMETERS)
        time_line = getattr(sheet.bb, field_names.TIMELINE)

        period_column = time_line.columns.get_position(unit.period.end)

        ex_params = unit.parameters.keys() & parameters.rows.by_name.keys()
        new_params = unit.parameters.keys() - ex_params

        for param in timeline_params:
            # check for updates
            if param in unit.parameters:
                this_row = parameters.rows.by_name[param]
                this_col = period_column
                cell = sheet.cell(column=this_col, row=this_row)

                cell.value = unit.parameters[param]
                cell_styles.format_hardcoded(cell)

        unit_params = ex_params - timeline_params

        template = formula_templates.LINK_TO_COORDINATES
        for param in unit_params:
            this_row = parameters.rows.by_name[param]
            this_col = period_column

            master_cell = sheet.cell(row=this_row, column=self.MASTER_COLUMN)

            cell = sheet.cell(column=this_col, row=this_row)
            cell.value = unit.parameters[param]
            cell_styles.format_parameter(cell)

            # check if exists and matches MASTER, if so, link to MASTER,
            # otherwise overwrite with hardcoded value
            if cell.value == master_cell.value:
                info = dict(coordinates=master_cell.coordinate)
                link = template.format(**info)
                cell.set_explicit_value(link, data_type=type_codes.FORMULA)
            else:
                cell_styles.format_hardcoded(cell)

        template = formula_templates.LINK_TO_COORDINATES
        for param in sorted(new_params):
            if parameters.rows.ending:
                # there are existing parameters
                this_row = parameters.rows.ending+1
            else:
                # there are NO existing parameters
                this_row = self.VALUES_START_ROW

            this_col = period_column

            parameters.rows.by_name[param] = this_row

            master_cell = sheet.cell(row=this_row, column=self.MASTER_COLUMN)
            master_cell.value = unit.parameters[param]
            cell_styles.format_parameter(master_cell)
            cell_styles.format_hardcoded(master_cell)

            label_cell = sheet.cell(row=this_row, column=self.LABEL_COLUMN)
            label_cell.value = param

            cell = sheet.cell(column=this_col, row=this_row)
            info = dict(coordinates=master_cell.coordinate)
            link = template.format(**info)
            cell.set_explicit_value(link, data_type=type_codes.FORMULA)
            cell_styles.format_parameter(cell)

        for row in parameters.rows.by_name.values():
            group_lines(sheet, row=row)

        sheet.bb.current_row = parameters.rows.ending

        return sheet

    def _add_valuation_tab(self, book, unit, index=None):
        """


        UnitChef._add_valuation_tab() -> Worksheet

        --``book`` must be a Workbook
        --``unit`` must be an instance of BusinessUnit

        Method creates a valuation tab and chops unit valuation statement.
        """

        # 1.0   set up the unit sheet and spread params
        if not index:
            index = len(book.worksheets)

        if index == 1:
            name = "Valuation"
        else:
            name = unit.name + ' val'

        sheet = self._create_unit_sheet(book=book, unit=unit,
                                        index=index, name=name,
                                        current_only=True)

        sheet.bb.outline_level += 1

        # 1.1   set-up life
        sheet.bb.current_row += 1
        sheet = self._add_unit_life(sheet=sheet, unit=unit)
        sheet.bb.outline_level -= 1

        # 1.2  Add Valuation statement
        sheet.bb.current_row = sheet.bb.events.rows.ending
        sheet.bb.current_row += 1

        current = sheet.bb.time_line.columns.get_position(unit.period.end)
        sheet_style.set_column_width(sheet, current, width=22)

        statement_row = sheet.bb.current_row + 1
        statement = unit.financials.valuation
        line_chef.chop_statement(
            sheet=sheet,
            statement=statement,
            column=current,
            set_labels=True)

        # 1.5 add area and statement labels and sheet formatting
        sheet_style.style_sheet(sheet)
        cell_styles.format_area_label(sheet, statement.name, statement_row)

        # # 1.6 add selector cell
        #   Make scenario label cells
        self._add_scenario_selector_logic(book, sheet)

        sheet.sheet_properties.tabColor = VALUATION_TAB_COLOR

        return sheet

    def _create_unit_sheet(self, *pargs, book, unit, index, name=None,
                           current_only=False):
        """


        UnitChef._create_unit_sheet() -> Worksheet


        Returns sheet with current row pointing to last parameter row
        """

        if not name:
            name = unit.tags.name

        if name in book:
            rev_name = name + " ..." + str(unit.id.bbid)[-8:]
            name = rev_name

            if name in book:
                name = str(unit.id.bbid)

        name = name.translate(bad_char_table)
        name = name[:self.MAX_TITLE_CHARACTERS]
        # Replace forbidden characters, make sure name is within length limits

        sheet = book.create_sheet(name, index)

        req_rows = len(unit.components.by_name) // self.MAX_LINKS_PER_CELL
        req_rows = min(req_rows, self.MAX_CONSOLIDATION_ROWS)
        req_rows = max(1, req_rows)

        sheet.bb.consolidation_size = req_rows
        # Compute the amount of rows we will use for consolidation on this
        # sheet. In future periods, the number of kids may grow or shrink.
        # LineChef will modify the number of links in each cell to make sure
        # the full consolidation work always takes up the same amount of row
        # space, to make sure our spreadsheet aligns.

        unit.xl.set_sheet(sheet)

        # Hide sheets for units below a certain depth. The depth should be a
        # Chef-level constant. Use ``sheet_state := "hidden"`` to implement.
        self._link_to_time_line(book=book, sheet=sheet, unit=unit,
                                current_only=current_only)

        val_col = sheet.bb.time_line.columns.get_position(unit.period.end)
        param_area = getattr(sheet.bb, field_names.PARAMETERS)
        param_area.columns.by_name[field_names.VALUES] = val_col
        # At this point, sheet.bb.current_row will point to the last parameter.

        # Freeze panes:
        corner_row = sheet.bb.time_line.rows.ending
        corner_row += 1

        corner_col = param_area.columns.get_position(field_names.MASTER)
        corner_col += 1

        corner_cell = sheet.cell(column=corner_col, row=corner_row)
        sheet.freeze_panes = corner_cell

        # Return sheet
        return sheet

    def _link_to_area(self, source_sheet, local_sheet, area_name, group=False,
                      keep_format=True, current_only=False, num_cols=1):
        """


        UnitChef._link_to_area() -> Worksheet

        --``source_sheet`` must be a Worksheet
        --``local_sheet`` must be a Worksheet
        --``area_name`` must be the string name of an Area
        --``group`` must be a boolean (NOT USED)
        --``keep_format`` must be a boolean; whether or not to keep source
            formatting

        Method links area with the name ``area_name`` in the ``local_sheet ``
        to the ``source_sheet``.  Will keep source formatting if
        ``keep_format`` is true.
        """
        # <-------------------------------------------------------------------------------------------------------SHOULD BE PUBLIC ROUTINE
        source_area = getattr(source_sheet.bb, area_name)
        local_area = getattr(local_sheet.bb, area_name, None)

        if local_area is None:
            local_area = local_sheet.bb.add_area(area_name)

        local_area.update(source_area)
        coordinates = {"sheet": source_sheet.title}

        for row in source_area.rows.by_name.values():
            source_row = (source_area.rows.starting or 0) + row
            local_row = (local_area.rows.starting or 0) + row

            if group:
                group_lines(local_sheet, row=local_row)

            if current_only:
                use_columns = sorted(source_area.columns.by_name.values())
                use_columns = use_columns[0:num_cols]
            else:
                use_columns = source_area.columns.by_name.values()

            for column in use_columns:

                source_column = (source_area.columns.starting or 0) + column
                local_column = (local_area.columns.starting or 0) + column

                local_cell = local_sheet.cell(column=local_column,
                                              row=local_row)

                cos = coordinates.copy()
                cos["row"] = source_row
                cos["alpha_column"] = get_column_letter(source_column)

                link = formula_templates.LINK_TO_CELL_ON_SHEET.format(**cos)
                local_cell.set_explicit_value(link,
                                              data_type=type_codes.FORMULA)

                if keep_format:
                    source_cell = source_sheet.cell(column=source_column,
                                                    row=source_row)
                    local_cell.number_format = source_cell.number_format

            local_sheet.bb.current_row = local_row

        return local_sheet

    def _link_to_time_line(self, *pargs, book, sheet, unit,
                           current_only=False):
        """


        UnitChef._link_to_time_line() -> Worksheet


        Link sheet to book's time_line.
        Force keyword-entry for book and sheet to make sure we feed in the
        right arguments.
        """
        source = book.get_sheet_by_name(tab_names.SCENARIOS)
        source_area = getattr(source.bb, field_names.TIMELINE)

        param_area = sheet.bb.add_area(field_names.PARAMETERS)
        timeline_area = sheet.bb.add_area(field_names.TIMELINE)

        # First add labels for parameters
        active_row = self.VALUES_START_ROW
        active_column = self.LABEL_COLUMN
        param_area.columns.by_name[field_names.LABELS] = self.LABEL_COLUMN
        param_area.columns.by_name[field_names.MASTER] = self.MASTER_COLUMN

        template = formula_templates.ADD_CELL_FROM_SHEET
        source_label_column = source_area.columns.by_name[field_names.LABELS]
        src_col = get_column_letter(source_label_column)

        src_params = set(source_area.rows.by_name.keys()) - {field_names.TITLE}

        for param in sorted(src_params):
            src_row = source_area.rows.by_name[param]
            param_area.rows.by_name[param] = active_row
            cell = sheet.cell(column=active_column, row=active_row)

            info = dict(sheet=source.title, alpha_column=src_col, row=src_row)
            link = template.format(**info)
            cell.set_explicit_value(link, data_type=type_codes.FORMULA)

            active_row += 1

        # Next add timeline header row and parameters from Scenarios tab

        # save for later
        time_params = param_area.rows.by_name.copy()
        time_params = time_params.keys()
        timeline_area.rows.by_name[field_names.TITLE] = self.TITLE_ROW

        template = formula_templates.ADD_CELL_FROM_SHEET
        src_vals = set(source_area.columns.by_name.keys())-{field_names.LABELS}

        if current_only:
            src_vals = [unit.period.end]

        active_column = self.VALUE_COLUMN
        for date in sorted(src_vals):
            active_row = self.TITLE_ROW
            src_row = source_area.rows.by_name[field_names.TITLE]

            # make header cell
            col_num = source_area.columns.by_name[date]
            src_col = get_column_letter(col_num)

            timeline_area.columns.by_name[date] = active_column
            cell = sheet.cell(column=active_column, row=active_row)

            info = dict(sheet=source.title, alpha_column=src_col, row=src_row)
            link = template.format(**info)
            cell.set_explicit_value(link, data_type=type_codes.FORMULA)
            cell_styles.format_date(cell)

            # now link parameters to value cells
            for param in src_params:
                src_row = source_area.rows.by_name[param]
                active_row = param_area.rows.by_name[param]

                cell = sheet.cell(column=active_column, row=active_row)

                info = dict(sheet=source.title, alpha_column=src_col,
                            row=src_row)
                link = template.format(**info)
                cell.set_explicit_value(link, data_type=type_codes.FORMULA)
                cell_styles.format_parameter(cell)

            sheet_style.set_column_width(sheet, active_column)

            active_column += 1

        sheet.bb.outline_level += 1

        # Add unit parameters and update TimeLine/Period params as necessary
        self._add_unit_params(sheet=sheet, unit=unit,
                              timeline_params=time_params)

        if not current_only:
            for snapshot in unit:
                self._add_unit_params(sheet=sheet, unit=snapshot,
                                      timeline_params=time_params)

        sheet.bb.outline_level -= 1

        return sheet

    def _sort_bypreference(self, items, preference_order=[]):
        """


        UnitChef._sort_bypreference() -> list (of items' keys)

        --``items`` is any dict
        --``preference_order`` any iterable giving the sorted order of items;
            items' keys which are not in preference_order will be tacked on at
            the end in sorted order
        """
        result = []

        for k in preference_order:
            if k in items:
                result.append(k)

        leftover = set(items.keys()) - set(result)
        result.extend(sorted(leftover))

        return result
