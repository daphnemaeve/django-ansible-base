from django.apps import AppConfig

from ansible_base.api_documentation.customizations import apply_authentication_customizations, apply_oauth2_customizations


class ApiDocumentationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ansible_base.api_documentation'
    label = 'dab_api_documentation'

    def ready(self):
        from django.conf import settings

        if 'ansible_base.authentication' in settings.INSTALLED_APPS:
            apply_authentication_customizations()

        if 'ansible_base.oauth2_provider' in settings.INSTALLED_APPS:
            apply_oauth2_customizations()

        # Import filter extensions to register them with drf-spectacular
        if 'ansible_base.rest_filters' in settings.INSTALLED_APPS and 'ansible_base.api_documentation' in settings.INSTALLED_APPS:
            # If this service is using DAB rest filters and api documentation, load our filter extensions for OpenAPI
            from ansible_base.api_documentation import filter_extensions  # noqa: F401

        self._ensure_spectacular_hooks(settings)

    @staticmethod
    def _ensure_spectacular_hooks(settings):
        spectacular = getattr(settings, 'SPECTACULAR_SETTINGS', None)
        if spectacular is None:
            return

        dab_hooks = {
            'PREPROCESSING_HOOKS': [
                'ansible_base.api_documentation.preprocessing_hooks.collect_ai_description_metadata',
            ],
            'POSTPROCESSING_HOOKS': [
                'ansible_base.api_documentation.postprocessing_hooks.add_x_ai_description',
                'ansible_base.api_documentation.postprocessing_hooks.inject_clean_text_patterns',
            ],
        }
        for key, hooks in dab_hooks.items():
            existing = spectacular.get(key, [])
            for hook in hooks:
                if hook not in existing:
                    existing.append(hook)
            spectacular[key] = existing
