from django.test import TestCase
from django.utils import translation
from storybase.utils import slugify
from models import (Organization, OrganizationTranslation, Project,
    ProjectTranslation)

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

    def test_auto_slug(self):
        name = 'Mile High Connects'
        organization = Organization()
        organization.save()
        organization_translation = OrganizationTranslation(name=name, organization=organization)
        self.assertEqual(organization_translation.slug, '')
        organization_translation.save()
        self.assertEqual(organization_translation.slug, slugify(name))

class ProjectModelTest(TestCase):
    def test_auto_slug(self):
        name = 'The Metro Denver Regional Equity Atlas'
        project = Project()
        project.save()
        project_translation = ProjectTranslation(name=name, project=project)
        self.assertEqual(project_translation.slug, '')
        project_translation.save()
        self.assertEqual(project_translation.slug, slugify(name))
