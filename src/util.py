import base64, requests, datetime, pprint, json, logging, sys, smtplib, gspread, math, time, os, google.auth, pydrive, csv, os.path, calendar
from pathlib import Path
from fpdf import FPDF, HTMLMixin
from email.message import EmailMessage
from datetime import timedelta
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from simplegmail import Gmail
from pprint import pformat
from todoist_api_python.api import TodoistAPI
import __main__

pp = pprint.PrettyPrinter(indent=2)


today_yyyy_mm_dd = datetime.datetime.today().strftime('%Y-%m-%d')


school_info = {
    'LCA' : {
        'short_name': 'LCA',
        'long_name': 'Livingston Collegiate Academy',
        'sr_id': '15',
        'ps_id': '4',
        'street': '7301 Dwyer Rd',
        'city': 'New Orleans',
        'state': 'LA',
        'zip': '70126',
        'principal': 'Akeem Langham',
        'phone': '504-503-0004',
        'fax': '504-342-0322',
        'attendance_email': 'hello@livingstoncollegiate.org',
        'attendance_letter_recipient': 'rmurray@collegiateacademies.org',
        'individualized_report_reply': 'rmurray@collegiateacademies.org',
        'daily_attendance_sms': 'jfonshell@collegiateacademies.org',
        'data_manager': 'jfonshell@collegiateacademies.org',
        'staff_pto_replyto': 'tashford@collegiateacademies.org',
        'dfo_name': 'Thaise',
        'seat_time': {
            'calendar': False,
            'contact': True,
            'link': '',
            'contact_name': 'Robin Murray',
            'contact_email': 'rmurray@collegiateacademies.org'
        }
    },
    'ASA': {
        'short_name': 'ASA',
        'long_name': 'Abramson Sci Academy',
        'sr_id': '1',
        'ps_id': '1',
        'street': '5552 Read Blvd',
        'city': 'New Orleans',
        'state': 'LA',
        'zip': '70127',
        'principal': 'Anthony McElligott',
        'fax': '504-324-0171',
        'phone': '504-373-6264',
        'attendance_email': 'frontdesk@sciacademy.org',
        'attendance_letter_recipient': 'kthomas1@collegiateacademies.org,smyers@collegiateacademies.org',
        'individualized_report_reply': 'frontdesk@sciacademy.org',
        'daily_attendance_sms': 'ncowlin@collegiateacademies.org',
        'data_manager': 'ncowlin@collegiateacademies.org',
        'staff_pto_replyto': 'ncowlin@collegiateacademies.org',
        'dfo_name': 'Nora',
        'seat_time': {
            'calendar': False,
            'contact': True,
            'link': '',
           'contact_name': 'Ms. Myers',
           'contact_email': 'smyers@collegiateacademies.org'
        }
    },
    'CBR': {
        'short_name': 'CBR',
        'long_name': 'Collegiate Baton Rouge',
        'sr_id': '17',
        'ps_id': '5',
        'street': '282 Lobdell Blvd',
        'city': 'Baton Rouge',
        'state': 'LA',
        'zip': '70806',
        'principal': 'Samantha Johnson',
        'fax': '225-286-7808',
        'phone': '225-892-6962',
        'attendance_email': 'info@collegiatebr.org',
        'attendance_letter_recipient': 'krichardson@collegiateacademies.org,ahunter2@collegiateacademies.org',
        'individualized_report_reply': 'krichardson@collegiateacademies.org,ahunter2@collegiateacademies.org',
        'daily_attendance_sms': 'fsall@collegiateacademies.org',
        'data_manager': 'fsall@collegiateacademies.org',
        'staff_pto_replyto': 'krichardson@collegiateacademies.org,ahunter2@collegiateacademies.org',
        'dfo_name': 'Tyler',
        'seat_time': {
            'calendar': False,
            'contact': True,
            'link': '',
            'contact_name': 'Kimberly Richardson, and Ms. Hunter',
            'contact_email': 'krichardson@collegiateacademies.org,ahunter2@collegiateacademies.org'
        }
    },
    'GWC': {
        'short_name': 'GWC',
        'long_name': 'G.W. Carver High School',
        'sr_id': '2',
        'ps_id': '2',
        'street': '3059 Higgins Blvd',
        'city': 'New Orleans',
        'state': 'LA',
        'zip': '70126',
        'principal': 'Victor Jones',
        'fax': '504-754-7980',
        'phone': '504-308-3660',
        'attendance_email': 'info@carvercollegiate.org',
        'attendance_letter_recipient': 'amueller@collegiateacademies.org',
        'individualized_report_reply': 'amueller@collegiateacademies.org',
        'daily_attendance_sms': 'tdemuns@collegiateacademies.org',
        'data_manager': 'tdemuns@collegiateacademies.org',
        'staff_pto_replyto': 'bbienemy@collegiateacademies.org',
        'dfo_name': 'Brandy',
        'seat_time': {
            'calendar': True,
            'contact': False,
            'link': 'https://docs.google.com/document/d/1IFKwD7p12haD3GbHtzFSvtAn_fdooUMleppx4pn-5_o/edit?usp=sharing',
            'contact_name': '',
            'contact_email': ''
        }
    },
    'WLC': {
        'short_name': 'WLC',
        'long_name': 'Walter L. Cohen High School',
        'sr_id': '18',
        'ps_id': '6',
        'street': '3575 Baronne St',
        'city': 'New Orleans',
        'state': 'LA',
        'zip': '70115',
        'principal': 'Samara Levy',
        'fax': '504-395-0031',
        'phone': '504-503-1400',
        'attendance_email': 'info@walterlcohen.org',
        'attendance_letter_recipient': 'info@walterlcohen.org',
        'individualized_report_reply': 'info@walterlcohen.org',
        'daily_attendance_sms': 'jeasley@collegiateacademies.org',
        'data_manager': 'jeasley@collegiateacademies.org',
        'staff_pto_replyto': 'btaylor@collegiateacademies.org',
        'dfo_name': 'Blaire',
        'seat_time': {
            'calendar': False,
            'contact': True,
            'link': '',
            'contact_name': 'the Front Desk',
            'contact_email': 'info@walterlcohen.org'
        }
    },
    'OA': {
        'short_name': 'OA',
        'long_name': 'Opportunities Academy',
        'sr_id': '19',
        'ps_id': '7',
        'street': '2625 Thalia St',
        'city': 'New Orleans',
        'state': 'LA',
        'zip': '70113',
        'principal': 'Francesca Antonucci',
        'fax': '504-814-1721',
        'phone': '504-503-1421',
        'attendance_email': 'hello@opportunitiesacademy.org',
        'attendance_letter_recipient': 'hello@opportunitiesacademy.org',
        'individualized_report_reply': 'hello@opportunitiesacademy.org',
        'daily_attendance_sms': 'kimani@collegiateacademies.org',
        'data_manager': 'kimani@collegiateacademies.org',
        'staff_pto_replyto': 'kimani@collegiateacademies.org',
        'dfo_name': 'King Victorr',
        'seat_time': {
            'calendar': False,
            'contact': 'OA',
            'link': '',
            'contact_name': 'hello@opportunitiesacademy.org',
            'contact_email': 'hello@opportunitiesacademy.org'
        }
    },
}


# ANSI Escape Codes

# Colors
black = "\u001b[30m"
red = "\u001b[31m"
green = "\u001b[32m"
yellow = "\u001b[33m"
blue = "\u001b[34m"
magenta = "\u001b[35m"
cyan = "\u001b[36m"
white = "\u001b[37m"
reset = "\u001b[0m"


# Text Decorations
bold = "\u001b[1m"
underline = "\u001b[4m"


sys.path.append("..")
if sys.platform == 'darwin':
    log_dir = '/Users/tophermckee/cadata/logs/'
elif sys.platform == 'linux':
    log_dir = '/home/data_admin/cadata/logs/'
else:
    log_dir = '../logs/'

logging.basicConfig(
    level=logging.INFO,
    format="\n[%(levelname)s] %(asctime)s -- %(filename)s on line %(lineno)s\n\tFunction name: %(funcName)s\n\tMessage: %(message)s\n",
    datefmt='%B-%d-%Y %H:%M:%S',
    filename=f"{log_dir}{datetime.datetime.today().strftime('%Y-%m-%d')}_{Path(__main__.__file__).stem}.log",
    filemode='a'
)

attendance_letter_blocks_page1 = [
    {
        'name': 'attendance_policy_header',
        'text': "**###school_name### Attendance Policy**",
    },
    {
        'name': 'attendance_policy_explainer',
        'text': "Students can only be successful if they are present and prepared in school every day. Our curriculum is an ambitious one; every day is essential for students to keep pace.  At ###school_name###, excessive absences will not be tolerated.",
    },
    {
        'name': 'attendance_policy_warning',
        'text': "**If a student is absent without excuse for more than 9 days of the semester, the student will not receive credit for any courses they are taking during that semester.**",
    },
    {
        'name': 'attendance_requirements_header',
        'text': '**Attendance Requirements**',
    },
    {
        'name': 'attendance_requirement1',
        'text': 'Students must be present for \"60,120 minutes (equivalent to 167 six-hour school days)\" per year and 30,060 per semester',
        'bullet_level': 1,
    },
    {
        'name': 'attendance_requirement2',
        'text': 'Because our classes are semester based, students must meet attendance requirements per semester',
        'bullet_level': 1,
    },
    {
        'name': 'attendance_requirement3',
        'text': '**Based on our schedule, a student must miss no more than 9 days per semester to earn credit for their courses**',
        'bullet_level': 1,
    },
    {
        'name': 'excuse_policy_header',
        'text': 'Absences will be recorded as excused or unexcused, in accordance with our policies:',
    },
    {
        'name': 'excuse_policy1',
        'text': 'Absences will be considered **excused** if they fall into one of the following categories and documentation is submitted to the school: illness, hospital stay, medical appointments, observation of holidays of the student\'s own faith, visitation with a parent who is a member of the armed forces, death in the immediate family.',
        'bullet_level': 1,
    },
    {
        'name': 'excuse_policy2',
        'text': 'You can submit documentation by:',
        'bullet_level': 1,
    },
    {
        'name': 'excuse_policy2a',
        'text': 'Emailing it to ###attendace_email###',
        'bullet_level': 2,
    },
    {
        'name': 'excuse_policy2b',
        'text': 'Faxing it to ###fax_number###',
        'bullet_level': 2,
    },
    {
        'name': 'excuse_policy2c',
        'text': 'Bringing it to the front office',
        'bullet_level': 2,
    },
    {
        'name': 'excuse_policy3',
        'text': 'Absences will be considered **unexcused** if they do not fall into a category outlined above or if documentation is not provided.',
        'bullet_level': 1,
    },
    {
        'name': 'comms_and_ints_header',
        'text': '**Attendance Communication and Interventions**',
    },
    {
        'name': 'comms_and_ints_explainer',
        'text': 'We believe that it is important for our school staff, families, and students to have open communication around attendance. Our school will take the following steps upon each absence:',
    },
    {
        'name': 'comms_and_ints1',
        'text': '3-4 absences: The school will send a letter to the parent/guardian notifying the parent of the student\'s status and recommending a conference to develop an attendance plan in accordance with LRS 17:233.  The student\'s parent/guardian will be contacted by school staff to schedule a mandatory Attendance Conference to develop an attendance plan for the student.  All notes from the meeting and the details of the attendance plan will be documented.',
        'bullet_level': 1,
    },
    {
        'name': 'comms_and_ints2',
        'text': '5 absences: The student is considered as truant as pursuant to LRS 17:233.  A letter will be sent to the home of the student informing the parent/guardian of violation of compulsory attendance law. Supervisor of Child Welfare and Attendance may file report(s) to Municipal Court for Truancy and/or the NOLA Public Schools Office of Student Support and Attendance.',
        'bullet_level': 1,
    },
    {
        'name': 'comms_and_ints3',
        'text': '6+ absences: A school official or representative may conduct a home visit, review the attendance plan, enforce compulsory attendance law, and make recommendations to improve attendance.',
        'bullet_level': 1,
    },
]

attendance_letter_blocks_spanish_page1 = [
    {
        'name': 'attendance_policy_header',
        'text': "**Política de asistencia de ###school_name###**",
    },
    {
        'name': 'attendance_policy_explainer',
        'text': "Los estudiantes solo pueden tener éxito si están presentes y preparados en la escuela todos los días. Nuestro plan de estudios es ambicioso; cada día es esencial para que los estudiantes mantengan el ritmo. En ###school_name###, no se tolerarán ausencias excesivas.",
    },
    {
        'name': 'attendance_policy_warning',
        'text': "**Si un estudiante se ausenta sin excusa por más de 9 días del semestre, el estudiante no recibirá crédito por ningún curso que esté tomando durante ese semestre.**",
    },
    {
        'name': 'attendance_requirements_header',
        'text': '**Requisitos de asistencia**',
    },
    {
        'name': 'attendance_requirement1',
        'text': 'Los estudiantes deben estar presentes durante \"60,120 minutos (equivalente a 167 días escolares de seis horas)\" por año y 30,060 por semestre.',
        'bullet_level': 1,
    },
    {
        'name': 'attendance_requirement2',
        'text': 'Debido a que nuestras clases son semestrales, los estudiantes deben cumplir con los requisitos de asistencia por semestre.',
        'bullet_level': 1,
    },
    {
        'name': 'attendance_requirement3',
        'text': '**Según nuestro horario, un estudiante no debe perder más de 9 días por semestre para obtener crédito por sus cursos.**',
        'bullet_level': 1,
    },
    {
        'name': 'excuse_policy_header',
        'text': 'Las ausencias se registrarán como justificadas o injustificadas, de acuerdo con nuestras políticas:',
    },
    {
        'name': 'excuse_policy1',
        'text': 'Las ausencias se considerarán **justificadas** si caen en una de las siguientes categorías y se presenta documentación a la escuela: enfermedad, estadía en el hospital, citas médicas, observación de días festivos de la fe del estudiante, visitas con un padre que es miembro de las fuerzas armadas fuerzas, muerte en la familia inmediata.',
        'bullet_level': 1,
    },
    {
        'name': 'excuse_policy2',
        'text': 'Puede enviar la documentación por:',
        'bullet_level': 1,
    },
    {
        'name': 'excuse_policy2a',
        'text': 'Enviándolo por correo electrónico a ###attendace_email###',
        'bullet_level': 2,
    },
    {
        'name': 'excuse_policy2b',
        'text': 'Enviándolo por fax a ###fax_number###',
        'bullet_level': 2,
    },
    {
        'name': 'excuse_policy2c',
        'text': 'Llevándolo a la oficina principal',
        'bullet_level': 2,
    },
    {
        'name': 'excuse_policy3',
        'text': 'Las ausencias se considerarán **injustificadas** si no entran en una de las categorías descritas anteriormente o si no se proporciona documentación.',
        'bullet_level': 1,
    },
    {
        'name': 'comms_and_ints_header',
        'text': '**Asistencia Comunicación e Intervenciones**',
    },
    {
        'name': 'comms_and_ints_explainer',
        'text': 'Creemos que es importante que el personal de nuestra escuela, las familias y los estudiantes tengan una comunicación abierta sobre la asistencia. Nuestra escuela tomará los siguientes pasos en cada ausencia:',
    },
    {
        'name': 'comms_and_ints1',
        'text': '3-4 ausencias: La escuela enviará una carta al padre/tutor notificando al padre sobre el estado del estudiante y recomendando una reunión para desarrollar un plan de asistencia de acuerdo con LRS 17:233. El personal de la escuela se comunicará con el padre/tutor del estudiante para programar una conferencia de asistencia obligatoria para desarrollar un plan de asistencia para el estudiante. Se documentarán todas las notas de la reunión y los detalles del plan de asistencia.',
        'bullet_level': 1,
    },
    {
        'name': 'comms_and_ints2',
        'text': '5 ausencias: El estudiante se considera ausente sin permiso conforme a LRS 17:233. Se enviará una carta a la casa del estudiante informando al padre/tutor de la violación de la ley de asistencia obligatoria. El Supervisor de Asistencia y Bienestar Infantil puede presentar informes ante el Tribunal Municipal de Absentismo Escolar y/o la Oficina de Asistencia y Apoyo Estudiantil de las Escuelas Públicas de NOLA.',
        'bullet_level': 1,
    },
    {
        'name': 'comms_and_ints3',
        'text': 'Más de 6 ausencias: un funcionario o representante de la escuela puede realizar una visita al hogar, revisar el plan de asistencia, hacer cumplir la ley de asistencia obligatoria y hacer recomendaciones para mejorar la asistencia.',
        'bullet_level': 1,
    },
]

attendance_letter3_blocks_page2 = [
    {
        'name': 'page2_header',
        'text': 'Re: Attendance Warning',
    },
    {
        'name': 'page2_paragraph1',
        'text': '**You are receiving this letter because your child has 3 or more Unexcused Absences and/or Tardies.** Under the law, students are required to attend school regularly and must attend a minimum number of days of school to earn credit and be eligible for promotion to the next grade.  Your child is in danger of not being promoted to the next grade.',
    },
    {
        'name': 'page2_paragraph2',
        'text': 'A representative from the school will contact you via phone to schedule a mandatory attendance conference.  In this conference, your child\'s attendance record will be reviewed and a plan will be put into place that they must follow in order to be eligible for promotion or graduation.',
    },
    {
        'name': 'page2_paragraph3',
        'text': '**If your child does not meet the school\'s attendance requirements, they may not earn credit for their courses and may have to complete the same grade next year.  Failure to adhere to the requirements of your scholar\'s attendance plan will also result in a referral to Municipal Court.**',
    },
    {
        'name': 'page2_paragraph4',
        'text': 'Please review our attendance policy on the reverse of this letter.  You can contact ###school_name### at ###school_phone### to discuss your child\'s attendance and your next steps. We look forward to having your student attend school on a daily basis so we can continue their pathway to college success.',
    }
]

attendance_letter3_blocks_spanish_page2 = [
    {
        'name': 'page2_header',
        'text': 'Re: Advertencia de asistencia',
    },
    {
        'name': 'page2_paragraph1',
        'text': '**Está recibiendo esta carta porque su hijo/a tiene 3 o más ausencias y/o tardanzas injustificadas.** Según la ley, los estudiantes deben asistir a la escuela con regularidad y deben asistir a una cantidad mínima de días de escuela para obtener crédito y ser elegibles para la promoción al siguiente grado. Su hijo/a está en peligro de no pasar al siguiente grado.',
    },
    {
        'name': 'page2_paragraph2',
        'text': 'Un representante de la escuela se comunicará con usted por teléfono para programar una conferencia de asistencia obligatoria. En esta conferencia, se revisará el registro de asistencia de su hijo/a y se establecerá un plan que debe seguir para ser elegible para la promoción o la graduación.',
    },
    {
        'name': 'page2_paragraph3',
        'text': '**Si su hijo/a no cumple con los requisitos de asistencia de la escuela, es posible que no obtenga crédito por sus cursos y que tenga que completar el mismo grado el próximo año. El incumplimiento de los requisitos del plan de asistencia de su estudiante también resultará en una remisión al Tribunal Municipal.**',
    },
    {
        'name': 'page2_paragraph4',
        'text': 'Por favor revise nuestra política de asistencia en el reverso de esta carta. Puede comunicarse con ###school_name### al ###school_phone### para hablar sobre la asistencia de su hijo/a y sus próximos pasos. Esperamos que su estudiante asista a la escuela todos los días para que podamos continuar su camino hacia el éxito universitario.',
    }
]

attendance_letter5_blocks_page2 = [
    {
        'name': 'page2_header',
        'text': 'Re: Attendance Warning',
    },
    {
        'name': 'page2_paragraph1',
        'text': '**You are receiving this letter because your child has exceeded the maximum number of Unexcused Absences and/or Tardies allowed by law and is now considered truant.**  Louisiana requires students to attend school for a certain number of days to be promoted to the next grade and earn credit for a course. Under the law, students are required to attend school regularly and must attend a minimum number of days of school to earn credit and be eligible for promotion to the next grade.  Your child is in danger of not being promoted to the next grade because he or she has been absent more than the time allotted by the state.',
    },
    {
        'name': 'page2_paragraph2',
        'text': 'A representative from the school will contact you via phone to schedule a mandatory attendance hearing.  In this hearing, your child\'s attendance record will be reviewed and a plan will be put into place that they must follow in order to be eligible for promotion or graduation.',
    },
    {
        'name': 'page2_paragraph3',
        'text': '**If your child does not meet the school\'s attendance requirements, they may not earn credit for their courses and may have to complete the same grade next year.  Failure to adhere to the requirements of your scholar\'s attendance plan will also result in a referral to Municipal Court.**',
    },
    {
        'name': 'page2_paragraph4',
        'text': 'Please review our attendance policy on the reverse of this letter.  You can contact ###school_name### at ###school_phone### to discuss your child\'s attendance and your next steps. We look forward to having your student attend school on a daily basis so we can continue their pathway to college success.',
    }
]

attendance_letter10_blocks_page2 = [
    {
        'name': 'page2_header',
        'text': 'Re: Attendance Warning',
    },
    {
        'name': 'page2_paragraph1',
        'text': '**You are receiving this letter because your child has 10 or more unexcused absences for the semester.**',
    },
    {
        'name': 'page2_paragraph2',
        'text': '**Your child will not be able to earn credit for their courses unless they submit excuse notes and/or attend attendance recovery to get to 9 or fewer absences.**',
    },
    {
        'name': 'page2_paragraph3',
        'text': 'Please review our attendance policy on the reverse of this letter.  You can contact ###school_name### at ###school_phone### to discuss your child\'s attendance and your next steps. We look forward to having your student attend school on a daily basis so we can continue their pathway to college success.',
    }
]

attendance_letter5_blocks_spanish_page2 = [
    {
        'name': 'page2_header',
        'text': 'Re: Advertencia sobre asistencia escolar',
    },
    {
        'name': 'page2_paragraph1',
        'text': '**Usted está recibiendo esta carta porque su hijo(a) ha excedido el número máximo de faltas y/o retardos injustificados permitidas por la ley y ahora se lo considera ausente.** En el estado de Louisiana se requiere que los estudiantes asistan a la escuela por una cierta cantidad de días para ser promovidos al siguiente grado y obtener crédito por un curso. Según la ley, los estudiantes deben asistir a la escuela con regularidad y deben asistir a una cantidad mínima de días de escuela para obtener crédito y ser elegibles para la promoción al siguiente grado. Su hijo está en peligro de no ser promovido al siguiente grado porque ha estado ausente más tiempo del asignado por el estado.',
    },
    {
        'name': 'page2_paragraph2',
        'text': 'Un representante de la escuela se comunicará con usted por teléfono para programar una audiencia de asistencia obligatoria. En esta audiencia, se revisará el registro de asistencia de su hijo(a) y se establecerá un plan que debe seguir para ser elegible para la promoción o la graduación.',
    },
    {
        'name': 'page2_paragraph3',
        'text': '**Si su hijo(a) no cumple con los requisitos de asistencia de la escuela, es posible que no obtenga crédito por sus cursos y que tenga que completar el mismo grado el próximo año. El incumplimiento de los requisitos del plan de asistencia de su estudiante también resultará en una remisión al Tribunal Municipal.**',
    },
    {
        'name': 'page2_paragraph4',
        'text': 'Por favor reviste el reglamento de asistencia escolar adjunta a esta carta. Si desea discutir los detalles sobre la situación de su hijo(a), puede comunicarse con ###school_name### al teléfono ###school_phone### para saber cuáles son los siguientes pasos. Esperamos que su estudiante asista a la escuela todos los días para que podamos continuar su camino hacia el éxito universitario.',
    }
]

attendance_letter10_blocks_spanish_page2 = [
    {
        'name': 'page2_header',
        'text': 'Re: Advertencia sobre asistencia escolar',
    },
    {
        'name': 'page2_paragraph1',
        'text': '**Esta recibiendo este comunicado porque su hijo(a) ha acumulado diez o más faltas injustificadas en lo que va del semestre.**',
    },
    {
        'name': 'page2_paragraph2',
        'text': '**Su hijo(a) no obtendrá créditos para sus cursos salvo si nos entregan justificantes para las faltas o bien si asisten a sesiones de recuperación de faltas para tener nueve faltas o menos.**',
    },
    {
        'name': 'page2_paragraph3',
        'text': 'Por favor reviste el reglamento de asistencia escolar adjunta a esta carta. Si desea discutir los detalles sobre la situación de su hijo(a), puede comunicarse con ###school_name### al teléfono ###school_phone### para saber cuáles son los siguientes pasos. Esperamos que su estudiante asista a la escuela todos los días para que podamos continuar su camino hacia el éxito universitario.',
    }
]

oa_attendance_letter_blocks = [
    {
        'name': 'oa_paragraph1',
        'text': 'You are receiving this letter because your student has exceeded **3 Unexcused Absences** from school this year.  This is cause for concern at Opportunities Academy, as when students are absent from school, they are unlikely to receive required service minutes outlined in his or her IEP and see stymied progress toward their IEP goals.',
    },
    {
        'name': 'oa_paragraph1',
        'text': 'Attendance is the first step in ensuring that students consistently have the chance to practice the essential skills they are working on to become a more independent and fulfilled adult. Attending daily helps students to practice responsibility and develop the habits necessary for being able to maintain employment. In addition, daily attendance is essential for students to achieve their transition goals.',
    },
    {
        'name': 'oa_paragraph1',
        'text': 'If there are barriers your family is facing in getting your student to school, we can discuss those and connect you with any resources available to support your family in getting your student to school each day. You can contact Opportunities Academy at 504-503-1421. We look forward to having your student in school each day and thank you for your partnership.',
    }
]

if sys.platform == 'darwin':
    credentials_path = '/Users/tophermckee/cadata/creds.json'
elif sys.platform == 'linux':
    credentials_path = '/home/data_admin/cadata/creds.json'

if sys.platform == 'darwin':
    service_account_credentials_path = '/Users/tophermckee/cadata/ca-data-administrator.json'
elif sys.platform == 'linux':
    service_account_credentials_path = '/home/data_admin/cadata/ca-data-administrator.json'

with open(credentials_path) as file:
    credentials = json.load(file)

with open(service_account_credentials_path) as file:
    service_account = json.load(file)


def sr_api_pull(search_key: str, parameters: dict = {}, page_limit: int = None) -> list:
    counter = 0
    """A blank function for returning an endpoint for Schoolrunner. Logs its progress in the logs folder and logs its outputs as a json file."""
    items = []
    headers = {'Authorization': 'Basic ' + base64.b64encode(bytes(f"{credentials['sr_email']}:{credentials['sr_pass']}", "UTF-8")).decode("ascii")}
    page_params = {key: value for (key, value) in parameters.items() if key != 'expand'}
    logging.info(f"🤞 Finding number of pages for {' '.join(search_key.split('-'))} 🤞")
    request = requests.get(f"https://ca.schoolrunner.org/api/v1/{search_key}?", params=page_params,headers=headers)
    response = request.json()
    logging.info(f"This request's URL is {request.url}")
    logging.info(f"There are {response['meta']['total_pages']} page(s) of {' '.join(search_key.split('-'))}.")
    if page_limit == None:
        for page in range(response['meta']['total_pages']):
            logging.info(f"Pulling page {page + 1} of {response['meta']['total_pages']} page(s)")
            this_response = requests.get(f"https://ca.schoolrunner.org/api/v1/{search_key}?page={page + 1}", params=parameters, headers=headers).json()
            logging.info(f"🏗️ Processing page {page + 1} of {response['meta']['total_pages']} page(s) 🏗️")
            for item in this_response['results'][search_key.replace('-', '_')]:
                items.append(item)
                counter += 1
        logging.info(f"🎉 Done pulling {' '.join(search_key.split('-'))}! 🎉")
    else:
        for page in range(page_limit):
            logging.info(f"Pulling page {page + 1} of {page_limit} pages [limited]")
            this_response = requests.get(f"https://ca.schoolrunner.org/api/v1/{search_key}?page={page + 1}",params=parameters, headers=headers).json()
            logging.info(f"🏗️ Processing page {page + 1} of {page_limit} pages [limited] 🏗️")
            for item in this_response['results'][search_key.replace('-', '_')]:
                items.append(item)
                counter += 1
        logging.info(f"🎉 Done pulling {' '.join(search_key.split('-'))}! 🎉\n")
    
    if sys.platform == 'darwin':
        json_log_dir = '/Users/tophermckee/cadata/logs/json/'
    elif sys.platform == 'linux':
        json_log_dir = '/home/data_admin/cadata/logs/json/'
    else:
        json_log_dir = '../logs/json/'

    if counter >= 5000:
        logging.info(f"{json_log_dir}{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}_{search_key}.json would be {counter} lines long. Skipping dumping the file.")
    else:
        os.makedirs(json_log_dir, exist_ok=True)
        with open(f"{json_log_dir}{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}_{search_key}.json", "w") as file:
            logging.info('dumping json info to logs folder')
            json.dump(items, file, indent=4)

    return items


def convert_yyyy_mm_dd_date(date_string: str) -> datetime.date:
    year = int(date_string[0:4])
    month = int(date_string[5:7])
    day = int(date_string[8:10])

    return datetime.datetime(year, month, day)


def return_term_dates(term_bin_id: str) -> tuple:
    """Returns the start and end dates of a given term in Schoolrunner."""
    if term_bin_id == None:
        raise Exception("Did not find a matching term bin for this date -- erroring out.")
    term_bins = sr_api_pull(
        search_key='term-bins',
        parameters={
            'term_bin_ids': term_bin_id,
            'expand': 'school_id'
        }
    )
    logging.info(f"{term_bins[0]['long_name']} (Term ID {term_bins[0]['term_bin_id']}) starts on {term_bins[0]['start_date']} and ends on {term_bins[0]['end_date']}")
    return term_bins[0]['start_date'], term_bins[0]['end_date']


def return_this_sr_term(search_term: str, school: str) -> str:
    """Finds the term based on the type of term you look up (semester, quarter, etc.)"""
    terms = sr_api_pull(
        search_key='term-bins',
        parameters={
            "school_ids": school_info[school]['sr_id'],
            'expand': 'term_bin_type'
        }
    )

    for term in terms:
        start_date = convert_yyyy_mm_dd_date(term['start_date'])
        end_date = convert_yyyy_mm_dd_date(term['end_date'])
        if search_term.lower() in term['long_name'].lower() and start_date <= datetime.datetime.now() <= end_date:
            logging.info(f"Found term {term['long_name']} - {term['term_bin_id']}")
            return term['term_bin_id']


def log_communication(
        student_id: str,
        communication_method_id: str,
        communication_type_id: str,
        staff_member_id: str,
        school_id: str,
        contact_person: str = '',
        comments: str = '',
        sandbox: bool = False) -> dict:
    """Used to log a communication in Schoolrunner for any school. Will require
    most parameters that Schoolrunner requires and will also take a comment &
    person contacted just to make the log more useful. These are optional params"""
    payload = {
        'school_id': school_id,
        'student_id': student_id,
        'communication_method_id': communication_method_id,
        'communication_type_id': communication_type_id,
        'staff_member_id': staff_member_id,
        'contact_person': contact_person,
        'date': today_yyyy_mm_dd,
        'comments': comments
    }

    params = {
        'Content-Type': 'application/json'
    }

    headers = {'Authorization': 'Basic ' + base64.b64encode(bytes(f"{credentials['sr_email']}:{credentials['sr_pass']}", "UTF-8")).decode("ascii")}

    logging.info(f'Logging communication for {student_id}')
    
    try:
        if sandbox:
            response = requests.post(f"https://ca.sandbox.schoolrunner.org/api/v1/communications", json=payload, params=params, headers=headers).json()
            logging.info(f"Successful log for {student_id} -- {response}")
            return response
        else:
            response = requests.post(f"https://ca.schoolrunner.org/api/v1/communications", json=payload, params=params, headers=headers).json()
            logging.info(f"Successful log for {student_id} -- {response}")
            return response
    except Exception as error:
        logging.error(f"Unsuccessful log for {student_id} - {error}", exc_info=True)


def send_email(
        recipient: str = '',
        text_body: str = '',
        subject_line: str = '',
        html_body: str = '',
        bcc: str = '',
        cc: str = '',
        reply_to: str = '',
        attachment: str = '',
        sender_string: str = '') -> bool:
    """Sends an email from the CA Data Email. Returns `True` or `False` if sent successfully."""
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        try:
            smtp.login(credentials['cadata_email_addr'], credentials['python_gmail_app_password'])
        except Exception as error:
            logging.error(f"Error at SSL login for {recipient} -- {error}", exc_info=True)
            smtp.quit()

        msg = EmailMessage()
        msg['Subject'] = subject_line
        msg['From'] = credentials['cadata_email_addr'] if sender_string == '' else sender_string
        msg['To'] = recipient
        if cc != '':
            msg['Cc'] = cc
        if bcc != '':
            msg['Bcc'] = bcc
        msg.set_content(text_body)
        if html_body != '':
            msg.add_alternative(html_body, subtype='html')
        if reply_to != '':
            msg['reply-to'] = reply_to
        if attachment != '':
            with open(attachment, 'rb') as content_file:
                content = content_file.read()
                msg.add_attachment(content, maintype='application', subtype='pdf', filename=attachment)

        logging.info(f"\n🤞 Attempting email for to:{recipient} 🤞")
        try:
            smtp.send_message(msg)
            logging.info(f"🍾 Email sent for to:{recipient} 🍾")
            smtp.quit()
            return True
        except Exception as error_inside:
            logging.error(f"Error at send for to:{recipient} -- error: {error_inside}", exc_info=True)
            smtp.quit()
            return False


def extract_sr_student_attribute(attr_list: list, attr_key: str):
    """Takes the nasty list of student attributes that is attached to students
    and will return the currently active version for the provided key"""
    for attr in attr_list:
        if attr['active'] == '1' and attr['student_attr_type']['attr_key'] == attr_key:
            return attr['value']


def extract_sr_student_detail(detail_list: list, detail_key: str):
    """Takes the nasty list of student details that is attached to students
    and will return the currently active version for the provided key"""
    for detail in detail_list:
        if detail['active'] == '1' and detail_key in detail:
            return detail[detail_key]


def today_is_a_school_day(school: str, school_id: str, print_response: bool = False) -> bool:
    params = {
        'school_ids': school_id,
        'max_date': datetime.datetime.now().strftime('%Y-%m-%d'),
        'min_date': datetime.datetime.now().strftime('%Y-%m-%d')
    }

    headers = {'Authorization': 'Basic ' + base64.b64encode(bytes(f"{credentials['sr_email']}:{credentials['sr_pass']}", "UTF-8")).decode("ascii")}
    response = requests.get('https://ca.schoolrunner.org/api/v1/calendar_days?', params=params, headers=headers).json()

    if print_response:
        print(response)

    calendar_days = response['results'].get('calendar_days', [])
    if not calendar_days:
        logging.warning(f"No calendar day data found for {school.upper()} on {datetime.datetime.now().strftime('%Y-%m-%d')}. Assuming not a school day.")
        return False
    if calendar_days[0].get('in_session', '0') == '0':
        logging.info(f"Today is not a school day at {school.upper()}")
        return False
    else:
        logging.info(f"Today is a school day at {school.upper()}")
        return True


def return_current_sr_term(term_type: str, school: str) -> str:
    terms = sr_api_pull(
        search_key='term-bins',
        parameters={
            'school_ids': school_info[school]['sr_id'],
            'expand': 'term_bin_type'
        }
    )

    for term in terms:
        try:
            start_date = convert_yyyy_mm_dd_date(term['start_date'])
            end_date = convert_yyyy_mm_dd_date(term['end_date'])
            if term_type.lower() in term['long_name'].lower() and start_date <= datetime.datetime.today() and datetime.datetime.today() <= end_date:
                logging.info(f"Found term {term['long_name']} - {term['term_bin_id']}")
                return term['term_bin_id']
        except AttributeError as attr_error:
            logging.error(f"Error with a term -- it probably doesn\'t have a long name -- {attr_error}", exc_info=True)
        except TypeError as type_error:
            logging.error(f"Error with a termin -- its dates are wonky -- {type_error}", exc_info=True)
        except Exception as error:
            logging.error(f"Error with a term -- {error}", exc_info=True)


def return_term_start_date(term_type: str, school: str) -> str:
    return return_term_dates(return_current_sr_term(term_type, school))[0]


def return_term_end_date(term_type: str, school: str) -> str:
    return return_term_dates(return_current_sr_term(term_type, school))[1]


def return_numeric_column(num):
    alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    if num > 26:
        return f"{alphabet[math.ceil(num / 26) - 2]}{alphabet[(num % 26) - 1]}".upper()
    else:
        return alphabet[num - 1].upper()


def return_googlesheet_by_key(spreadsheet_key: str, sheet_name: str) -> gspread.Worksheet:
    from oauth2client.service_account import ServiceAccountCredentials
    scope = [
        "https://spreadsheets.google.com/feeds",
        'https://www.googleapis.com/auth/spreadsheets',
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name('../ca-data-administrator-f52c3e758490.json', scope)
    client = gspread.authorize(creds)
    return client.open_by_key(spreadsheet_key).worksheet(sheet_name)


def update_googlesheet_by_key(spreadsheet_key:str = '', sheet_name: str = '', data: list = [], starting_cell: str = '') -> None:
    try:
        logging.info(f"🤞 Attempting to copy to {spreadsheet_key} {sheet_name}!{starting_cell}:{return_numeric_column(len(data[0]))} 🤞")
        sheet_to_update = return_googlesheet_by_key(spreadsheet_key, sheet_name)
        sheet_to_update.batch_clear([f"{starting_cell}:{return_numeric_column(len(data[0]))}"])
        sheet_to_update.update(starting_cell, data, value_input_option='USER_ENTERED')
        logging.info(f"🎉 Copy completed successfully! 🎉")
    except Exception as error:
        logging.error(f"Error copying -- {error}", exc_info=True)

def return_googlesheet_values_by_key(spreadsheet_key: str = '', sheet_name: str = '', range: str = ''):
    from oauth2client.service_account import ServiceAccountCredentials
    scope = [
        "https://spreadsheets.google.com/feeds",
        'https://www.googleapis.com/auth/spreadsheets',
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name('../ca-data-administrator-f52c3e758490.json', scope)
    client = gspread.authorize(creds)
    if range != '':
        return client.open_by_key(spreadsheet_key).worksheet(sheet_name).get(range)
    else:
        return client.open_by_key(spreadsheet_key).worksheet(sheet_name).get_all_values()


def return_monday(timestamp: str) -> str:
    date_to_convert = convert_yyyy_mm_dd_date(timestamp)
    monday = (date_to_convert - timedelta(days = date_to_convert.weekday())).strftime('%Y-%m-%d')
    return monday

def generate_page_content(pdf_instance: FPDF, school: str, block_list: list) -> None:
    for block in block_list:
        if 'bullet_level' in block:
            if block['bullet_level'] == 1:
                pdf_instance.set_x(10)
                pdf_instance.multi_cell(w=5, h=4, txt="\x95", new_x="END", new_y="LAST")
                pdf_instance.multi_cell(
                    w=0,
                    h=4,
                    new_x="LMARGIN",
                    new_y="NEXT",
                    txt=block['text']
                        .replace("###school_name###", school_info[school]['long_name'])
                        .replace('###school_phone###', school_info[school]['phone'])
                        .replace('###attendace_email###', school_info[school]['attendance_email'])
                        .replace('###fax_number###', school_info[school]['fax']),
                    markdown=True
                )
                pdf_instance.multi_cell(w=0, h=4, new_x="LMARGIN", new_y="NEXT", txt='')
            elif block['bullet_level'] == 2:
                pdf_instance.set_x(20)
                pdf_instance.multi_cell(w=5, h=4, txt="\x95", new_x="END", new_y="LAST")
                pdf_instance.multi_cell(
                    w=0,
                    h=4,
                    new_x="LMARGIN",
                    new_y="NEXT",
                    txt=block['text']
                        .replace("###school_name###", school_info[school]['long_name'])
                        .replace('###school_phone###', school_info[school]['phone'])
                        .replace('###attendace_email###', school_info[school]['attendance_email'])
                        .replace('###fax_number###', school_info[school]['fax']),
                    markdown=True
                )
                pdf_instance.multi_cell(w=0, h=4, new_x="LMARGIN", new_y="NEXT", txt='')
        else:
            pdf_instance.multi_cell(
                w=0,
                h=4,
                new_x="LMARGIN",
                new_y="NEXT",
                txt=block['text']
                        .replace("###school_name###", school_info[school]['long_name'])
                        .replace('###school_phone###', school_info[school]['phone'])
                        .replace('###attendace_email###', school_info[school]['attendance_email'])
                        .replace('###fax_number###', school_info[school]['fax']),
                markdown=True
            )
            pdf_instance.multi_cell(w=0, h=4, new_x="LMARGIN", new_y="NEXT", txt='')


def google_auth_flow():
    SCOPES = [
        'https://www.googleapis.com/auth/drive.metadata.readonly',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive',
    ]

    drive_creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('../token.json'):
        drive_creds = Credentials.from_authorized_user_file('../token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not drive_creds or not drive_creds.valid:
        if drive_creds and drive_creds.expired and drive_creds.refresh_token:
            drive_creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '../ca-data-administrator.json', SCOPES)
            drive_creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('../token.json', 'w') as token:
            token.write(drive_creds.to_json())

    return drive_creds

def create(file_name, mime_type, folder_id=None):
    """
    This function creates a new file on Google Drive.
    Requires the following arguments:
        1 - name to give the file
        2 - the mime type of the file being created
            (e.g., text/csv) reference -- https://developers.google.com/drive/api/guides/ref-export-formats
        3 - optional value for the Google folder ID where the file will be saved
   
    See documentation:
    https://developers.google.com/drive/api/v3/reference/files/create
    """

    drive_creds = google_auth_flow()

    try:
        service = build('drive', 'v3', credentials=drive_creds)
    
        logging.info(f'creating {file_name} on google drive in folder {folder_id}...')

        file_metadata = {
            'name': file_name,
            'mimeType': mime_type
        }
        
        if folder_id is not None:
            file_metadata['parents'] = [folder_id]
        
        results = service.files().create(body=file_metadata).execute()
        file_id = results['id']
        
        logging.info(f"file created with id: {file_id}\n")

    except Exception as err:
        logging.error(f"creating {file_name} on google drive in folder {folder_id} -- {err}", exc_info=True)
   
    return file_id


def upload_basic(drive_name, local_path, mimetype, folder_id):
    """Insert new file.
    Returns : Id's of the file uploaded
    """
    
    drive_creds = google_auth_flow()

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=drive_creds)

        file_metadata = {
            'name': drive_name,
            'parents': [folder_id]
        }
        media = MediaFileUpload(local_path,
                                mimetype=mimetype)
        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, media_body=media,
                                      fields='id').execute()
        logging.info(f'Successful upload -- file ID: {file.get("id")}')

    except HttpError as error:
        logging.error(F'An error occurred: {error}', exc_info=True)
        file = None

    return file.get('id')

def get_typeform(typeform_id):
    typeform_token = credentials['typeform_token']
    
    headers = {
        'Authorization': f'Bearer {typeform_token}',
    }

    try:
        logging.info(f"🤞 Attempting to retrieve Typeform with ID {typeform_id} 🤞")
        typeform_request = requests.get(f'https://api.typeform.com/forms/{typeform_id}', headers=headers).json()
        logging.info(f"🎉 Successful retrieved Typeform with ID {typeform_id} 🎉")
    except Exception as err:
        logging.error(f"Error retrieving Typeform with ID {typeform_id}: {err}", exc_info=True)

    return typeform_request

def get_powerschool_token():
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(bytes(f"{credentials['ps_client_id']}:{credentials['ps_client_secret']}", "UTF-8")).decode("ascii"),
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
    }

    params = {
        'grant_type': 'client_credentials'
    }

    response = requests.post(f"https://collegiateacademies.powerschool.com/oauth/access_token/", data=params, headers=headers).json()

    return response['access_token']


def powerschool_powerquery(query_name, payload):
    ps_token = get_powerschool_token()
    output = []

    try:
        url = f"https://collegiateacademies.powerschool.com/ws/schema/query/{query_name}"

        params = {
            'pagesize': 0  # this is used to stream records, might need to update requests to stream records
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {ps_token}"
        }

        payload = json.dumps(payload)
        logging.info(f"🤞 Attempting to query {query_name} 🤞")
        response = requests.post(url, data=payload, params=params, headers=headers)
        logging.info(f"🎉 Query completed successfully! 🎉")

        for record in response.json()['record']:
            output.append(record)

    except Exception as error:
        logging.error(f"Error getting powerschool data -- {error}", exc_info=True)

    return output


def today_is_monday() -> datetime.date:
    if datetime.date.today().weekday() == 0:
        logging.info(f"{datetime.date.today()} a Monday, sorry everyone.")
        return True
    else:
        logging.info(f"Today is not Monday, {datetime.date.today()} is a {datetime.date.today().strftime('%A')}")
        return False


def start_date_of_previous_month() -> datetime.date:
    if datetime.date.today().month == 1:
        return datetime.date(datetime.date.today().year - 1, 12, 1)
    else:
        return datetime.date(datetime.date.today().year, datetime.date.today().month - 1, 1)


def end_date_of_previous_month() -> datetime.date:
    if datetime.date.today().month == 1:
        month_range = calendar.monthrange(datetime.date.today().year - 1, 12)
        return datetime.date(datetime.date.today().year - 1, 12, month_range[1])
    else:
        month_range = calendar.monthrange(datetime.date.today().year, datetime.date.today().month - 1)
        return datetime.date(datetime.date.today().year, datetime.date.today().month - 1, month_range[1])


def start_date_of_current_month() -> datetime.date:
    return datetime.date(datetime.date.today().year, datetime.date.today().month, 1)


def end_date_of_current_month() -> datetime.date:
    month_range = calendar.monthrange(datetime.date.today().year, datetime.date.today().month)
    return datetime.date(datetime.date.today().year, datetime.date.today().month, month_range[1])