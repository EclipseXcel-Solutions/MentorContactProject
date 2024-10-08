

class FormBuilderSteps():

    FORM_DETAILS = 'FORM_DETAILS'
    SECTION_CREATION = 'SECTION_CREATION'
    GRID_CREATION = 'GRID_CREATION'

    def get_next(self, current_step):

        if current_step == self.FORM_DETAILS:
            return self.SECTION_CREATION
        if current_step == self.SECTION_CREATION:
            return self.GRID_CREATION
