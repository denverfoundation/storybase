from django.test import TestCase
from django.utils import translation
from models import Organization, OrganizationTranslation

class OrganizationModelTest(TestCase):
    def _create_organization(self, name, language):
        org = Organization()
        org.save()
        trans = OrganizationTranslation(name=name, language=language,
            organization=org)
        trans.save()
        return org

    def test_get_translated_field(self):
        """
        Tests that you can get a translated field as if it were the model's own
        """
        org_name_en = "Mile High Connects"
        org = self._create_organization(org_name_en, "en")
        self.assertEqual(org.name, org_name_en)

    def test_get_translated_field_default_fallback(self):
        """
        Tests that if a translated field doesn't exist in the current
        language, it falls back to the default language.
        """
        org_name_en = "Mile High Connects"
        org = self._create_organization(org_name_en, "en")
        translation.activate('es')
        self.assertEqual(org.name, org_name_en)

    def test_get_translated_field_first_fallback(self):
        """
        Tests that if a translated field doesn't exist in the current
        language, and it doesn't exist in the default language, the 
        first available language is used
        """
        org_name_es = "Mile High Conecta"
        org = self._create_organization(org_name_es, 'es')
        translation.activate('en')
        self.assertEqual(org.name, org_name_es)
