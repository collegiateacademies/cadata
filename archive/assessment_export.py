import sys
sys.path.append("..")
from src.util import *


def assessments_export():
    assessments = sr_api_pull(
        search_key="assessments",
        parameters={
            'min_date': '2022-07-01',
            'active': '1',
            'expand': 'school, staff_member, assessment_type, assessment_courses, assessment_section_period_links.section_period.section.course_definition'
        }
    )

    term_bins = sr_api_pull(
        search_key="term-bins",
        parameters={
            'active': '1'
        }
    )

    output = [['School', 'PowerSchool Course', 'SR Course', 'Sections', 'Teacher ID', 'Teacher', 'Term Bin', 'Week of', 'Name', 'Assessment ID']]

    for assessment in assessments:
        
        ps_course_list = []
        sr_course_list = []
        section_list = []

        for sr_course in assessment['assessment_courses']:
            sr_course_list.append(sr_course['display_name'])

        for section in assessment['assessment_section_period_links']:
            if section['section_period']['section_id'] not in section_list:
                section_list.append(f"{section['section_period']['section_id']}")
            if section['section_period']['section']['course_definition']['display_name'] not in ps_course_list:
                ps_course_list.append(f"{section['section_period']['section']['course_definition']['display_name']}")

        term_bin_output = ''
        for term_bin in term_bins:
            if term_bin['start_date'] is not None:
                term_start_date = convert_yyyy_mm_dd_date(term_bin['start_date'])
            if term_bin['end_date'] is not None:
                term_end_date = convert_yyyy_mm_dd_date(term_bin['end_date'])
            assessment_date = convert_yyyy_mm_dd_date(assessment['date'])

            if term_start_date <= assessment_date and term_end_date >= assessment_date and assessment['school_id'] == term_bin['school_id'] and 'quarter' in term_bin['long_name'].lower():
                term_bin_output = term_bin['short_name']

        if len(ps_course_list) == 0:
            output.append([
                assessment['school']['short_name'],
                assessment['assessment_section_period_links'][0]['section_period']['section']['course_definition']['display_name'] if len(assessment['assessment_section_period_links']) > 0 else "No Course",
                ','.join(sr_course_list),
                ','.join(section_list),
                assessment['staff_member']['sis_id'],
                assessment['staff_member']['display_name'],
                term_bin_output,
                return_monday(assessment['date']),
                assessment['display_name'],
                assessment['assessment_id']
            ])
        
        for x in range(len(ps_course_list)):
            output.append([
                assessment['school']['short_name'],
                ps_course_list[x],
                ','.join(sr_course_list),
                ','.join(section_list),
                assessment['staff_member']['sis_id'],
                assessment['staff_member']['display_name'],
                term_bin_output,
                return_monday(assessment['date']),
                assessment['display_name'],
                assessment['assessment_id']
            ])

    update_googlesheet_by_key(
        spreadsheet_key='1gaMzfvMbG1O7Nh1-sWc_UupVzKl5xFyyFZAHSodLMps',
        sheet_name='assessments',
        data=output,
        starting_cell='A1'
    )
    
    # This little guy is for later down the line if we decide to sort this sheet
    # return_googlesheet_by_key(spreadsheet_key='1gaMzfvMbG1O7Nh1-sWc_UupVzKl5xFyyFZAHSodLMps', sheet_name='assessments').sort((6, 'asc'), (0, 'asc'), (4, 'asc'), range = f'A2:{return_numeric_column(len(output[0]))}{len(output)}')