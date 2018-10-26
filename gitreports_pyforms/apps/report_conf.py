from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlInteger
from pyforms.controls import ControlButton
from pyforms.controls import ControlBarsChart
from pyforms.controls import ControlLineChart
from pyforms.controls import ControlPieChart
from pyforms.controls import ControlList
from pyforms.controls import ControlList
from pyforms.controls import ControlDate
from pyforms.controls import ControlCheckBox
from pyforms.controls import ControlAutoComplete
from pyforms.controls import ControlQueryList
from pyforms.controls import ControlCheckBoxList

from pyforms_web.organizers import segment, no_columns
from confapp import conf
from django.conf import settings

from datetime import datetime, timedelta
from django.utils import timezone

from gitreports.git_stats import gitstats_per_user
from gitreports.git_reports import modifications_perweek, modifications_total

import json, os

class ConfGitReport(BaseWidget):

    UID   = 'conf-git-report'
    TITLE = 'Conf git report'

    LAYOUT_POSITION = conf.ORQUESTRA_NEW_TAB
    ORQUESTRA_MENU = 'left'
    ORQUESTRA_MENU_ORDER = 1
    ORQUESTRA_MENU_ICON  = 'chart line'

    CONF_FILENAME = 'git-report-config.json'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._repos   = ControlCheckBoxList('Repositories', headers=['', 'Repositories paths'])
        self._authors = ControlCheckBoxList('Authors', headers=['', 'Author name', 'Email'])
        self._load    = ControlButton('Load', default=self.load_data)
        self._save    = ControlButton('Save', default=self.save_data)
        
        self.formset = [
            no_columns('_load','_save'),
            '_repos',
            '_authors'
        ]

        if os.path.exists(self.CONF_FILENAME):
            with open(self.CONF_FILENAME, 'r') as infile:
                self._repos.value, self._authors.value = json.load(infile)

    def save_data(self):
        use_repos   = self._repos.value
        use_authors = self._authors.value

        with open(self.CONF_FILENAME, 'w') as outfile:
            data = use_repos, use_authors
            json.dump( data, outfile)

    def load_data(self):

        data, repos, authors_emails = gitstats_per_user(
            settings.GIT_REPOSITORIES_FOLDER, 
            recursive = True
        )

        self._repos.value = [(True, path) for path in repos]
        self._authors.value = [(True, name, email) for name, email in authors_emails.items()]