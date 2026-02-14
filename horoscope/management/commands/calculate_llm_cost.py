from django.core.management.base import BaseCommand

from core.containers import container


class Command(BaseCommand):
    help = 'Calculate LLM token usage and cost for all horoscopes'

    def handle(self, *args, **options):
        llm_usage_repo = container.horoscope.llm_usage_repository()
        summary = llm_usage_repo.get_usage_summary()

        if not summary:
            self.stdout.write('No LLM usage data found.')
            return

        self.stdout.write('\nLLM Usage Summary')
        self.stdout.write('=' * 70)

        grand_input = 0
        grand_output = 0
        grand_count = 0

        for row in summary:
            model_name = row['model']
            input_tokens = row['total_input_tokens'] or 0
            output_tokens = row['total_output_tokens'] or 0
            count = row['count'] or 0

            grand_input += input_tokens
            grand_output += output_tokens
            grand_count += count

            self.stdout.write(f'\nModel: {model_name}')
            self.stdout.write(f'  Horoscopes generated: {count}')
            self.stdout.write(f'  Input tokens:  {input_tokens:>12,}')
            self.stdout.write(f'  Output tokens: {output_tokens:>12,}')
            self.stdout.write(f'  Total tokens:  {input_tokens + output_tokens:>12,}')

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('Grand Total')
        self.stdout.write(f'  Horoscopes generated: {grand_count}')
        self.stdout.write(f'  Input tokens:  {grand_input:>12,}')
        self.stdout.write(f'  Output tokens: {grand_output:>12,}')
        self.stdout.write(f'  Total tokens:  {grand_input + grand_output:>12,}')
        self.stdout.write('')
