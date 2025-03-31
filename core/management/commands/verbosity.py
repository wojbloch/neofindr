from django.core.management.base import BaseCommand
from utils.helpers import cfg_get_verbosity, cfg_set_verbosity, CustomLogger

class Command(BaseCommand):
    help = 'set verbosity level for logging'

    def add_arguments(self, parser):
        parser.add_argument('level', type=str, help="verbosity level: '0' for WARNING, 'v' for INFO, 'vv' for DEBUG")

    def handle(self, *args, **options):
        level = options['level']
        try:
            current_level = cfg_get_verbosity()
            if current_level == level:
                self.stdout.write(self.style.WARNING(f'verbosity is already set to {level}'))
                return
            custom_logger = CustomLogger()
            custom_logger.set_verbosity(level)
            self.stdout.write(self.style.SUCCESS(f'log verbosity set to {level}'))
        except ValueError as e:
            self.stderr.write(self.style.ERROR(str(e)))