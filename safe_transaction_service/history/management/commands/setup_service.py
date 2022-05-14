from typing import Dict, List, NamedTuple, Sequence, Tuple

from django.core.management.base import BaseCommand

from django_celery_beat.models import IntervalSchedule, PeriodicTask

from gnosis.eth import EthereumClientProvider
from gnosis.eth.ethereum_client import EthereumNetwork

from ...models import ProxyFactory, SafeMasterCopy


class CeleryTaskConfiguration(NamedTuple):
    name: str
    description: str
    interval: int
    period: str

    def create_task(self) -> Tuple[PeriodicTask, bool]:
        interval, _ = IntervalSchedule.objects.get_or_create(every=self.interval, period=self.period)
        periodic_task, created = PeriodicTask.objects.get_or_create(task=self.name,
                                                                    defaults={
                                                                        'name': self.description,
                                                                        'interval': interval
                                                                    })
        if periodic_task.interval != interval:
            periodic_task.interval = interval
            periodic_task.save(update_fields=['interval'])

        return periodic_task, created


TASKS = [
    CeleryTaskConfiguration('safe_transaction_service.history.tasks.index_internal_txs_task',
                            'Index Internal Txs', 13, IntervalSchedule.SECONDS),
    # CeleryTaskConfiguration('safe_transaction_service.history.tasks.index_new_proxies_task',
    #                        'Index new Proxies', 15, IntervalSchedule.SECONDS),
    CeleryTaskConfiguration('safe_transaction_service.history.tasks.index_erc20_events_task',
                            'Index ERC20 Events', 14, IntervalSchedule.SECONDS),
    CeleryTaskConfiguration('safe_transaction_service.history.tasks.process_decoded_internal_txs_task',
                            'Process Internal Txs', 2, IntervalSchedule.MINUTES),
    CeleryTaskConfiguration('safe_transaction_service.history.tasks.check_reorgs_task',
                            'Check Reorgs', 3, IntervalSchedule.MINUTES),
]

class Command(BaseCommand):
    help = 'Setup Transaction Service Required Tasks'

    def handle(self, *args, **options):
        for task in TASKS:
            _, created = task.create_task()
            if created:
                self.stdout.write(self.style.SUCCESS('Created Periodic Task %s' % task.name))
            else:
                self.stdout.write(self.style.SUCCESS('Task %s was already created' % task.name))

        self.stdout.write(self.style.SUCCESS('Setting up Safe Contract Addresses'))
        self.setup_my_network()

    def setup_my_network(self):
        SafeMasterCopy.objects.get_or_create(address='0xd9Db270c1B5E3Bd161E8c8503c55cEABeE709552',
                                             defaults={
                                                 'initial_block_number': 14922481,
                                                 'tx_block_number': 14922481,
                                             })
        ProxyFactory.objects.get_or_create(address='0xa6B71E26C5e0845f74c812102Ca7114b6a896AB2',
                                           defaults={
                                               'initial_block_number': 14922430,
                                               'tx_block_number': 14922430,
                                           })
    def _setup_safe_master_copies(self, safe_master_copies: Sequence[Tuple[str, int, str]]):
        for address, initial_block_number, version in safe_master_copies:
            safe_master_copy, _ = SafeMasterCopy.objects.get_or_create(
                address=address,
                defaults={
                    'initial_block_number': initial_block_number,
                    'tx_block_number': initial_block_number,
                    'version': version,
                }
            )
            if safe_master_copy.version != version:
                safe_master_copy.version = version
                safe_master_copy.save(update_fields=['version'])

    def _setup_safe_proxy_factories(self, safe_proxy_factories: Sequence[Tuple[str, int]]):
        for address, initial_block_number in safe_proxy_factories:
            ProxyFactory.objects.get_or_create(address=address,
                                               defaults={
                                                   'initial_block_number': initial_block_number,
                                                   'tx_block_number': initial_block_number,
                                               })