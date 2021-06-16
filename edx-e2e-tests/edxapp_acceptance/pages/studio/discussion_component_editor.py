"""
Discussion component editor in studio
"""


from edxapp_acceptance.pages.common.utils import click_css
from edxapp_acceptance.pages.studio.xblock_editor import XBlockEditorView


class DiscussionComponentEditor(XBlockEditorView):
    """
    Discussion Editor view in studio
    """
    @property
    def edit_discussion_field_values(self):
        """
        Get field values of discussion edit dialogue.
        Returns:
             list: A list of string indicating field values
        """
        return self.q(css='.field-data-control').attrs('value')

    def set_field_val(self, field_display_name, field_value):
        """
        If editing, set the value of a field.
        """
        selector = u'.xblock-studio_view li.field label:contains("{}") + input'.format(field_display_name)
        script = "$(arguments[0]).val(arguments[1]).change();"
        self.browser.execute_script(script, selector, field_value)

    def save(self):
        """
        Clicks save button.
        """
        click_css(self, '.save-button')
