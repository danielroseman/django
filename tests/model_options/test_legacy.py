from django import test
from collections import OrderedDict

from django.db.models.fields import related, CharField
from django.contrib.contenttypes.fields import GenericForeignKey

from .models import (
    BasePerson, Person
)


class OptionsBaseTests(test.TestCase):
    def eq_field_names_and_models(self, objects, names_eq, models_eq):
        fields, models = zip(*objects)
        self.assertEquals([f.name for f in fields], names_eq)
        self.assertEquals(models, models_eq)


class DataTests(OptionsBaseTests):

    def test_fields(self):
        fields = Person._meta.fields
        self.assertEquals([f.attname for f in fields], [
                          'id', 'data_abstract', 'fk_abstract_id',
                          'data_not_concrete_abstract', 'data_base',
                          'fk_base_id', 'data_not_concrete_base',
                          'baseperson_ptr_id', 'data_inherited',
                          'fk_inherited_id', 'data_not_concrete_inherited'])

    def test_local_fields(self):
        fields = Person._meta.local_fields
        self.assertEquals([f.attname for f in fields], [
                          'baseperson_ptr_id', 'data_inherited',
                          'fk_inherited_id', 'data_not_concrete_inherited'])
        self.assertTrue(all([f.rel is None or not isinstance(f.rel,
                        related.ManyToManyRel) for f in fields]))

    def test_local_concrete_fields(self):
        fields = Person._meta.local_concrete_fields
        self.assertEquals([f.attname for f in fields], [
                          'baseperson_ptr_id', 'data_inherited',
                          'fk_inherited_id'])
        self.assertTrue(all([f.column is not None
                             for f in fields]))


class M2MTests(OptionsBaseTests):

    def test_many_to_many(self):
        fields = Person._meta.many_to_many
        self.assertEquals([f.attname for f in fields], [
                          'm2m_abstract', 'm2m_base', 'friends',
                          'following', 'm2m_inherited'])
        self.assertTrue(all([isinstance(f.rel, related.ManyToManyRel)
                             for f in fields]))

    def test_many_to_many_with_model(self):
        models = OrderedDict(Person._meta.get_m2m_with_model()).values()
        self.assertEquals(models, [BasePerson, BasePerson, BasePerson, BasePerson, None])


class RelatedObjectsTests(OptionsBaseTests):

    def test_related_objects(self):
        objects = Person._meta.get_all_related_objects_with_model()
        self.eq_field_names_and_models(objects, [
            'model_options:computer',
            'model_options:watch'
        ], (BasePerson, None))

    def test_related_objects_local(self):
        objects = Person._meta.get_all_related_objects_with_model(
            local_only=True)
        self.eq_field_names_and_models(objects, [
            'model_options:watch'
        ], (None,))

    def test_related_objects_include_hidden(self):
        objects = Person._meta.get_all_related_objects_with_model(
            include_hidden=True)
        self.eq_field_names_and_models(objects, [
            u'model_options:baseperson_m2m_base',
            u'model_options:baseperson_following',
            u'model_options:baseperson_following',
            u'model_options:baseperson_friends',
            u'model_options:baseperson_friends',
            u'model_options:baseperson_m2m_abstract',
            u'model_options:computer',
            u'model_options:computerhidden',
            u'model_options:car_people',
            u'model_options:carhidden_people',
            u'model_options:person_m2m_inherited',
            u'model_options:watch', u'model_options:watchhidden',
            u'model_options:photo_people',
            u'model_options:photohidden_people'
        ], (BasePerson, BasePerson, BasePerson, BasePerson,
            BasePerson, BasePerson, BasePerson, BasePerson,
            BasePerson, BasePerson, None, None, None, None, None))

    def test_related_objects_include_hidden_local_only(self):
        objects = Person._meta.get_all_related_objects_with_model(
            include_hidden=True, local_only=True)
        self.eq_field_names_and_models(objects, [
            u'model_options:person_m2m_inherited',
            u'model_options:watch', u'model_options:watchhidden',
            u'model_options:photo_people',
            u'model_options:photohidden_people'
        ], (None, None, None, None, None))

    def test_related_objects_proxy(self):
        objects = RelatedObject._meta.get_all_related_objects_with_model(
            include_proxy_eq=True)
        self.eq_field_names_and_models(objects, [
            'model_options:relbaserelatedobjects',
            'model_options:relrelatedobjects',
            'model_options:relproxyrelatedobjects',
            'model_options:hiddenrelatedobject',
        ], (BaseRelatedObject, None, None, None))

    def test_related_objects_proxy_hidden(self):
        objects = RelatedObject._meta.get_all_related_objects_with_model(
            include_proxy_eq=True, include_hidden=True)
        self.eq_field_names_and_models(objects, [
            'model_options:relbaserelatedobjects',
            'model_options:relrelatedobjects',
            'model_options:relproxyrelatedobjects',
            'model_options:relproxyhiddenrelatedobjects',
            'model_options:hiddenrelatedobject',
        ], (BaseRelatedObject, None, None, None, None))


class RelatedM2MTests(OptionsBaseTests):

    def test_related_m2m_with_model(self):
        objects = RelatedM2M._meta.get_all_related_m2m_objects_with_model()
        self.eq_field_names_and_models(objects, [
            'model_options:relbaserelatedm2m',
            'model_options:relrelatedm2m'
        ], (BaseRelatedM2M, None))

    def test_related_m2m_local_only(self):
        objects = RelatedM2M._meta.get_all_related_many_to_many_objects(
            local_only=True)
        self.assertEquals([o.name for o in objects], [
            'model_options:relrelatedm2m'
        ])

    def test_related_m2m_asymmetrical(self):
        m2m = RelatedM2MRecursiveAsymmetrical._meta.many_to_many
        self.assertEquals([f.name for f in m2m],
                          ['following'])
        related_m2m = RelatedM2MRecursiveAsymmetrical._meta.get_all_related_many_to_many_objects()
        self.assertEquals([o.field.related_query_name() for o in related_m2m],
                          ['followers'])

    def test_related_m2m_symmetrical(self):
        m2m = RelatedM2MRecursiveSymmetrical._meta.many_to_many
        self.assertEquals([f.name for f in m2m],
                          ['friends'])
        related_m2m = RelatedM2MRecursiveSymmetrical._meta.get_all_related_many_to_many_objects()
        self.assertEquals([o.field.related_query_name() for o in related_m2m],
                          ['friends_rel_+'])


class VirtualFieldsTests(OptionsBaseTests):

    def test_virtual_fields(self):
        self.assertEquals([f.name for f in Virtual._meta.virtual_fields], [
                          'content_object'])


class GetFieldByNameTests(OptionsBaseTests):

    def test_get_data_field(self):
        field_info = Data._meta.get_field_by_name('name_abstract')
        self.assertEquals(field_info[1:], (BaseData, True, False))
        self.assertTrue(isinstance(field_info[0], CharField))

    def test_get_m2m_field(self):
        field_info = M2M._meta.get_field_by_name('m2m_base')
        self.assertEquals(field_info[1:], (BaseM2M, True, True))
        self.assertTrue(isinstance(field_info[0], related.ManyToManyField))

    def test_get_related_object(self):
        field_info = RelatedObject._meta.get_field_by_name('relrelatedobjects')
        self.assertEquals(field_info[1:], (None, False, False))
        self.assertTrue(isinstance(field_info[0], related.RelatedObject))

    def test_get_related_m2m(self):
        field_info = RelatedM2M._meta.get_field_by_name('relrelatedm2m')
        self.assertEquals(field_info[1:], (None, False, True))
        self.assertTrue(isinstance(field_info[0], related.RelatedObject))

    def test_get_virtual_field(self):
        field_info = Virtual._meta.get_field_by_name('content_object')
        self.assertEquals(field_info[1:], (None, True, False))
        self.assertTrue(isinstance(field_info[0], GenericForeignKey))
