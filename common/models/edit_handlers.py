import datetime
from django.forms.utils import pretty_name
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from wagtail.wagtailadmin.edit_handlers import EditHandler


class BaseReadOnlyPanel(EditHandler):
    def render(self):
        value = getattr(self.instance, self.attr)
        if isinstance(value, datetime.date):
            value = value.strftime('%A, %B %d, %Y %X')
        if callable(value):
            value = value()
        return format_html('<div style="padding-top: 1.2em;">{}</div>', value)

    def render_as_object(self):
        return format_html(
            '<li class="object">'
            '<h2><label for={}>{}</h2>'
            '<fieldset><legend>{}</legend>'
            '<div class="field">{}</div>'
            '</li>',
            self.label, self.label, self.label, self.render())

    def render_as_field(self):
        return format_html(
            '<div class="field">'
            '<label>{}{}</label>'
            '<div class="field-content">{}</div>'
            '</div>',
            self.label, _(':'), self.render())


class ReadOnlyPanel:
    def __init__(self, attr, label=None, classname=''):
        self.attr = attr
        self.label = pretty_name(self.attr) if label is None else label
        self.classname = classname

    def bind_to_model(self, model):
        return type(str(_('ReadOnlyPanel')), (BaseReadOnlyPanel,),
                    {'attr': self.attr, 'label': self.label,
                     'classname': self.classname})
