from django import forms

from categories.base import CategoryBaseAdminForm
from categories.settings import ALLOW_SLUG_CHANGE

from storybase.utils import slugify
from storybase_taxonomy.models import Category, CategoryTranslation

class CategoryAdminForm(CategoryBaseAdminForm):
    class Meta:
        model = Category
        # TODO: explicitly list fields
        fields = '__all__'


class CategoryTranslationAdminForm(forms.ModelForm):
    class Meta:
        model = CategoryTranslation
        # TODO: explicitly list fields
        fields = '__all__'

    def clean(self):
        super(CategoryTranslationAdminForm, self).clean()

        # Validate slug is valid in that level
	# Moved this logic from categories.base.CategoryBaseAdminForm.clean()
	# to the translation model's form (because that's where the slug
	# lives)
	related_model_name = self._meta.model.__name__.lower()
	category = self.cleaned_data.get('category')
        kwargs = {}
        if category.parent is None:
            kwargs['parent__isnull'] = True
        else:
            kwargs['parent__pk'] = int(category.parent.id)
	slug_field = '%s__slug' % related_model_name
        this_level_slugs = [c[slug_field] for c in
			    category.__class__.objects.filter(**kwargs).values(
				    'id', slug_field)
                            if c['id'] != category.id]
        if self.cleaned_data['slug'] in this_level_slugs:
            raise forms.ValidationError("The slug must be unique among "
                                        "the items at its level.")
	return self.cleaned_data


    def clean_slug(self):
        if self.instance is None or not ALLOW_SLUG_CHANGE:
            self.cleaned_data['slug'] = slugify(self.cleaned_data['name'])
        return self.cleaned_data['slug'][:50]
