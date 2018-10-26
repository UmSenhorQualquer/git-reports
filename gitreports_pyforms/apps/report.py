from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlInteger
from pyforms.controls import ControlButton
from pyforms.controls import ControlBarsChart
from pyforms.controls import ControlLineChart
from pyforms.controls import ControlPieChart
from pyforms.controls import ControlList
from pyforms.controls import ControlDate
from pyforms.controls import ControlCheckBox
from pyforms.controls import ControlAutoComplete
from pyforms.controls import ControlQueryList

from pyforms_web.organizers import segment, no_columns
from confapp import conf
from django.conf import settings
import pickle
from datetime import datetime, timedelta
from django.utils import timezone

from gitreports.git_stats import gitstats_per_user
from gitreports.git_reports import modifications_perweek, modifications_total

class GitReport(BaseWidget):

    UID   = 'git-report'
    TITLE = 'Git report'

    LAYOUT_POSITION = conf.ORQUESTRA_HOME_FULL
    ORQUESTRA_MENU = 'left'
    ORQUESTRA_MENU_ORDER = 20
    ORQUESTRA_MENU_ICON  = 'chart line'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._since = ControlDate('Since')
        self._until = ControlDate('Until')
        self._bars  = ControlBarsChart('Graph')
        self._pie   = ControlPieChart('Graph')
        self._apply = ControlButton('Apply', default=self.populate_graphs)
        self._lastweeks = ControlButton('Last 7 weeks', default=self.populate_last_7weeks)

        self.formset = [
            ('_since','_until','_apply', '_lastweeks'),
            '_bars',
            segment('_pie', css='overflow')
        ]

    def populate_last_7weeks(self):
        now = timezone.now()
        since = now.date() - timedelta(days=now.weekday()) - timedelta(days=7*6)
        self._since.value = since
        self._until.value = None
        self.populate_graphs()

    def populate_graphs(self):
        
        data = gitstats_per_user(
            '/Users/manager/Documents/bitbucket/core-project/', 
            recursive=True,
            since=self._since.value,
            until=self._until.value,
            authors_emails = {
                'ricardojvr@gmail.com':'Ricardo Ribeiro',
                'ricardo.ribeiro@neuro.fchampalimaud.org': 'Ricardo Ribeiro',
                'ricardo.ribeiro@research.fchampalimaud.org': 'Ricardo Ribeiro',
                'joao.bauto@neuro.fchampalimaud.org': 'João Baúto',
                'rribeiro@cnp-intranet.champalimaud.pt': 'Ricardo Ribeiro',
                'root@core.champalimaud.pt': 'Ricardo Ribeiro'
            }
        )

        authors = modifications_perweek(data)

        self._bars.value = authors

        self._pie.value  = list(modifications_total(data).items())

