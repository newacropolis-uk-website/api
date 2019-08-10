from celery import Celery


class NewAcropolisCelery(Celery):
    def init_app(self, app):
        if app.config['ENVIRONMENT'] == 'test':
            return

        if not app.config['CELERY_BROKER_URL']:
            app.logger.info('Celery broker URL not set')
            return

        super(NewAcropolisCelery, self).__init__(
            app.import_name,
            broker=app.config['CELERY_BROKER_URL'],
        )

        app.logger.info('Setting up celery: %s', app.config['CELERY_BROKER_URL'])

        self.conf.update(app.config)

        class ContextTask(self.Task):
            def __call__(self, *args, **kwargs):  # noqa
                with app.app_context():
                    return self.run(*args, **kwargs)

        self.Task = ContextTask
